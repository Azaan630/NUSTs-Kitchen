import flet as ft
import asyncio
from datetime import date, timedelta
from pages.api_client import get_todays_menu, get_weekly_menu, rate_food_item


class StudentHomePage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.user_id = int(user_data.get("UserID", 0))

        t = theme
        self.bg      = t["DARK_BG"]    if t["is_dark"] else t["CREAM"]
        self.card    = t["DARK_CARD"]  if t["is_dark"] else t["WHITE"]
        self.card2   = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt     = t["WHITE"]      if t["is_dark"] else t["NAVY"]
        self.sub     = t["GREY"]
        self.amber   = t["AMBER"]
        self.navy    = t["NAVY"]

        self._view = {"weekly": False}
        self.main_container = ft.Container(expand=True)

    # ── Safe key helpers ───────────────────────────────────────────
    def _item_name(self, item: dict) -> str:
        """Safely get item name regardless of API key casing."""
        return (
            item.get("Food_Item_Name")
            or item.get("Name")
            or item.get("Item_Name")
            or item.get("item_name")
            or item.get("name")
            or "Unknown"
        )

    def _item_meal_type(self, item: dict) -> str:
        """Safely get meal type regardless of API key casing."""
        mt = item.get("meal_type") or item.get("Meal_Type") or item.get("MealType")

        if mt:
            # Normalize to Title Case to match SQL ENUM exactly (e.g., 'breakfast' -> 'Breakfast')
            return mt.capitalize()
        return "Meal"

    def _item_rating(self, item: dict):
        """Safely get average rating."""
        val = (
            item.get("Ratings_Average")
            or item.get("Rating")
            or item.get("Avg_Rating")
            or 0
        )
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    # ── helpers ────────────────────────────────────────────────────
    def _loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.amber, width=40, height=40, stroke_width=3),
                ft.Text("Fetching menu…", color=self.sub, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=60,
        )

    def _error(self, msg):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#EF4444", size=48),
                ft.Text(msg, color="#EF4444", size=14, font_family="DM Sans", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.Alignment(0, 0),
            padding=60,
        )

    def _food_icon(self, name: str):
        n = (name or "").lower()
        if "biryani" in n:     return ft.Icons.RICE_BOWL_ROUNDED
        if "daal" in n:        return ft.Icons.GRAIN_ROUNDED
        if "tea" in n:         return ft.Icons.COFFEE_ROUNDED
        if "chicken" in n:     return ft.Icons.SET_MEAL_ROUNDED
        if "paratha" in n:     return ft.Icons.BREAKFAST_DINING_ROUNDED
        if "egg" in n:         return ft.Icons.EGG_ROUNDED
        if "salad" in n:       return ft.Icons.ECO_ROUNDED
        if "soup" in n:        return ft.Icons.SOUP_KITCHEN_ROUNDED
        return ft.Icons.RESTAURANT_ROUNDED

    def _meal_color(self, meal_type: str):
        mt = (meal_type or "").lower()
        if "breakfast" in mt: return "#F59E0B"
        if "lunch"     in mt: return "#10B981"
        if "dinner"    in mt: return "#6366F1"
        return self.amber

    def _meal_icon(self, meal_type: str):
        mt = (meal_type or "").lower()
        if "breakfast" in mt: return ft.Icons.WB_SUNNY_ROUNDED
        if "lunch"     in mt: return ft.Icons.LIGHT_MODE_ROUNDED
        if "dinner"    in mt: return ft.Icons.NIGHTS_STAY_ROUNDED
        return ft.Icons.RESTAURANT_ROUNDED

    # ── Star rating widget ─────────────────────────────────────────
    def _build_stars(self, item_id, schedule_id, existing_rating, meal_date, meal_type):
        stars = []
        rating_state = {
            "current": existing_rating or 0,
            "submitted": existing_rating is not None and existing_rating > 0,
        }
        star_refs = []

        def render_stars(score, locked=False):
            for i, s in enumerate(star_refs):
                filled = i < score
                s.name  = ft.Icons.STAR_ROUNDED if filled else ft.Icons.STAR_BORDER_ROUNDED
                s.color = self.amber if filled else self.sub
            self.page.update()

        async def on_star_click(e, score):
            if rating_state["submitted"]:
                return
            rating_state["current"] = score
            render_stars(score)

            result = await rate_food_item(
                user_id=self.user_id,
                item_id=item_id,
                meal_date=meal_date,
                meal_type=meal_type,
                score=score,
                email=self.email,
            )
            if result and "error" not in result:
                rating_state["submitted"] = True
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Rating saved!", color="#FFF"),
                    bgcolor="#10B981",
                )
                self.page.snack_bar.open = True
                render_stars(score, locked=True)
            else:
                err = result.get("error", "Already rated") if result else "Already rated"
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"⚠️ {err}", color="#FFF"),
                    bgcolor="#F59E0B",
                )
                self.page.snack_bar.open = True
                rating_state["submitted"] = True
            self.page.update()

        async def on_star_hover(e, score):
            if rating_state["submitted"]:
                return
            render_stars(score)

        async def on_hover_leave(e):
            if rating_state["submitted"]:
                return
            render_stars(rating_state["current"])

        for i in range(1, 6):
            score = i
            filled = i <= rating_state["current"]
            star_icon = ft.Icon(
                ft.Icons.STAR_ROUNDED if filled else ft.Icons.STAR_BORDER_ROUNDED,
                size=18,
                color=self.amber if filled else self.sub,
            )
            star_refs.append(star_icon)
            star_btn = ft.Container(
                content=star_icon,
                on_click=lambda e, s=score: asyncio.create_task(on_star_click(e, s)),
                on_hover=lambda e, s=score: (
                    asyncio.create_task(on_star_hover(e, s))
                    if e.data == "true"
                    else asyncio.create_task(on_hover_leave(e))
                ),
                tooltip=f"{score} star{'s' if score > 1 else ''}",
            )
            stars.append(star_btn)

        locked_label = ft.Text(
            "Rated ✓" if rating_state["submitted"] else "Rate:",
            size=11,
            color=self.amber if rating_state["submitted"] else self.sub,
            font_family="DM Sans",
        )

        return ft.Row([locked_label] + stars, spacing=2)

    # ── Food item card ─────────────────────────────────────────────
    def _build_food_card(self, item, meal_date=None, show_date=False):
        name     = self._item_name(item)
        avg      = self._item_rating(item)
        meal_col = self._item_meal_type(item)
        meal_c   = self._meal_color(meal_col)

        avg_stars = ft.Row([
            ft.Icon(ft.Icons.STAR_ROUNDED, size=13, color=self.amber),
            ft.Text(f"{avg:.1f}", size=12, color=self.sub, font_family="DM Sans"),
        ], spacing=2)

        schedule_id        = item.get("Schedule_ID") or item.get("ScheduleID") or 0
        date_for_rating    = meal_date or date.today()
        meal_type_for_rating = meal_col
        existing_rating    = item.get("user_rating")

        star_row = self._build_stars(
            item_id=item.get("Item_ID") or item.get("ItemID") or 0,
            schedule_id=schedule_id,
            existing_rating=existing_rating,
            meal_date=date_for_rating,
            meal_type=meal_type_for_rating,
        )

        date_badge = ft.Container()
        if show_date:
            d = item.get("Date", "")
            date_badge = ft.Container(
                content=ft.Text(str(d), size=10, color=self.sub, font_family="DM Sans"),
                bgcolor=ft.Colors.with_opacity(0.1, self.amber),
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=8,
            )

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(self._food_icon(name), size=20, color=meal_c),
                        width=40, height=40,
                        bgcolor=ft.Colors.with_opacity(0.12, meal_c),
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(
                            name,
                            size=14,
                            weight="bold",
                            color=self.txt,
                            font_family="DM Sans",
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        avg_stars,
                    ], spacing=2, expand=True),
                    date_badge,
                ], spacing=12),
                ft.Container(height=8),
                star_row,
            ], spacing=0),
            bgcolor=self.card,
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.with_opacity(0.06, "#000"),
                offset=ft.Offset(0, 2),
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, "#000")),
            animate=ft.Animation(200, "easeOut"),
        )
        return card

    # ── Today's menu builder ───────────────────────────────────────
    def _build_today(self, menu_data):
        menu_items = menu_data.get("menu", [])
        date_str   = menu_data.get("date", str(date.today()))

        if not menu_items:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.NO_MEALS_ROUNDED, size=48, color=self.sub),
                    ft.Text("No menu for today", color=self.sub, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0),
                padding=60,
            )

        groups = {}
        for item in menu_items:
            mt = self._item_meal_type(item)
            groups.setdefault(mt, []).append(item)

        sections = []
        for meal_type, items in groups.items():
            color = self._meal_color(meal_type)
            icon  = self._meal_icon(meal_type)
            header = ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=color, size=18),
                    ft.Text(
                        meal_type,
                        size=16,
                        weight="bold",
                        color=color,
                        font_family="DM Sans",
                    ),
                ], spacing=8),
                margin=ft.Margin.only(top=8, bottom=4),
            )
            sections.append(header)
            for item in items:
                sections.append(self._build_food_card(item, meal_date=date.today()))

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, color=self.amber, size=18),
                    ft.Text(
                        f"Today — {date_str}",
                        size=15,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], spacing=8),
                ft.Container(height=12),
                ft.Column(sections, scroll=ft.ScrollMode.ADAPTIVE),
            ]),
            padding=ft.Padding.only(bottom=20),
        )

    # ── Weekly menu builder ────────────────────────────────────────
    def _build_weekly(self, items):
        if not items:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_VIEW_WEEK_ROUNDED, size=48, color=self.sub),
                    ft.Text("No weekly menu available", color=self.sub, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0),
                padding=60,
            )

        from collections import OrderedDict
        date_groups = OrderedDict()
        for item in items:
            d  = str(item.get("Date", ""))
            mt = self._item_meal_type(item)
            date_groups.setdefault(d, {}).setdefault(mt, []).append(item)

        today    = str(date.today())
        sections = []

        for d, meals in date_groups.items():
            is_today = d == today
            try:
                from datetime import datetime
                weekday = datetime.strptime(d, "%Y-%m-%d").strftime("%A")
            except Exception:
                weekday = d

            day_header = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(
                            weekday[:3].upper(),
                            size=11,
                            weight="bold",
                            color=self.card if is_today else self.amber,
                            font_family="DM Sans",
                        ),
                        bgcolor=self.amber if is_today else ft.Colors.TRANSPARENT,
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    ),
                    ft.Text(d, size=13, color=self.sub, font_family="DM Sans"),
                    ft.Container(
                        content=ft.Text("Today", size=10, color=self.amber, font_family="DM Sans"),
                        visible=is_today,
                        bgcolor=ft.Colors.with_opacity(0.12, self.amber),
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    ),
                ], spacing=10),
                margin=ft.Margin.only(top=20, bottom=6),
            )
            sections.append(day_header)

            for mt, fitems in meals.items():
                color = self._meal_color(mt)
                sections.append(ft.Container(
                    content=ft.Text(mt, size=12, color=color, font_family="DM Sans", weight="bold"),
                    margin=ft.Margin.only(left=4, bottom=4),
                ))
                try:
                    meal_date = date.fromisoformat(d)
                except Exception:
                    meal_date = date.today()
                for item in fitems:
                    sections.append(
                        self._build_food_card(item, meal_date=meal_date, show_date=False)
                    )

        return ft.Column(sections, scroll=ft.ScrollMode.ADAPTIVE)

    # ── View toggle pill ───────────────────────────────────────────
    def _toggle_pill(self, on_today, on_weekly):
        today_btn = ft.Container(
            content=ft.Text("Today", size=13, font_family="DM Sans", weight="bold"),
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=20,
            bgcolor=self.amber if not self._view["weekly"] else ft.Colors.TRANSPARENT,
            on_click=lambda e: on_today(),
        )
        week_btn = ft.Container(
            content=ft.Text("This Week", size=13, font_family="DM Sans", weight="bold"),
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            border_radius=20,
            bgcolor=self.amber if self._view["weekly"] else ft.Colors.TRANSPARENT,
            on_click=lambda e: on_weekly(),
        )
        today_btn.content.color = self.card if not self._view["weekly"] else self.sub
        week_btn.content.color  = self.card if self._view["weekly"]     else self.sub

        return ft.Container(
            content=ft.Row([today_btn, week_btn], spacing=4),
            bgcolor=self.card2,
            border_radius=24,
            padding=ft.Padding.all(4),
        )

    # ── Load & render ──────────────────────────────────────────────
    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        if self._view["weekly"]:
            data = await get_weekly_menu()
            if isinstance(data, dict) and "error" in data:
                body = self._error(data["error"])
            else:
                items = data if isinstance(data, list) else []
                body  = self._build_weekly(items)
        else:
            data = await get_todays_menu(self.email)
            if isinstance(data, dict) and "error" in data:
                body = self._error(data["error"])
            else:
                body = self._build_today(data)

        def switch_today():
            self._view["weekly"] = False
            asyncio.create_task(self._render())

        def switch_weekly():
            self._view["weekly"] = True
            asyncio.create_task(self._render())

        pill = self._toggle_pill(switch_today, switch_weekly)

        self.main_container.content = ft.Column([
            ft.Row([
                ft.Text(
                    "Menu",
                    size=28,
                    weight="bold",
                    font_family="DM Sans",
                    color=self.txt,
                ),
                pill,
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color=self.sub,
                    tooltip="Refresh",
                    on_click=lambda e: asyncio.create_task(self._render()),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            body,
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()

    def build(self):
        asyncio.create_task(self._render())
        return ft.Container(
            content=self.main_container,
            bgcolor=self.bg,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
        )