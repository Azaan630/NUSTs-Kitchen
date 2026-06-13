import flet as ft
import asyncio
from datetime import date, timedelta
from pages.api_client import get_todays_menu, get_weekly_menu, rate_food_item, BASE_URL
import mock_data

import os
PUBLIC_BACKEND_URL = os.getenv("PUBLIC_BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


def _img_url(path):
    if not path: return None
    if path.startswith(("http://", "https://", "data:")): return path
    return f"{PUBLIC_BACKEND_URL}{path}"


class StudentHomePage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.user_id = int(user_data.get("UserID", 0))
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.bg      = t["DARK_BG"]    if t["is_dark"] else t["CREAM"]
        self.card    = t["DARK_CARD"]  if t["is_dark"] else t["WHITE"]
        self.card2   = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt     = t["WHITE"]      if t["is_dark"] else t["NAVY"]
        self.sub     = t["GREY"]
        self.amber   = t["AMBER"]
        self.navy    = t["NAVY"]

        self._view = {"weekly": False}
        self._food_cache = {}
        self.main_container = ft.Container(expand=True,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_OUT))

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

    def _food_thumb(self, item, size=44):
        cached = self._food_cache.get(item.get("Item_ID") or item.get("ItemID") or 0, {})
        path = cached.get("Image_Path") or item.get("Image_Path")
        if path:
            return ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=size, height=size),
                width=size, height=size, border_radius=10,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        return ft.Container(
            content=ft.Icon(self._food_icon(item.get("Food_Item_Name") or item.get("Name","")),
                            size=size*0.45, color=self.sub),
            width=size, height=size, bgcolor=self.card2, border_radius=10,
            alignment=ft.Alignment(0, 0),
        )

    async def _show_food_detail(self, item):
        iid = item.get("Item_ID") or item.get("ItemID") or 0
        cached = self._food_cache.get(iid, {})
        name = cached.get("Name") or item.get("Food_Item_Name") or item.get("Name", "Unknown")
        price = cached.get("Price", 0)
        qty = cached.get("Quantity", 0)
        path = cached.get("Image_Path") or item.get("Image_Path")

        rows = []
        if path:
            rows.append(ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=200, height=150),
                border_radius=12, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.Alignment(0, 0),
            ))
        rows.append(ft.Divider(height=8, color=ft.Colors.with_opacity(0.1, self.txt)))
        rows.append(ft.Row([
            ft.Text("Name", size=11, color=self.sub, font_family="DM Sans", expand=1),
            ft.Text(name, size=14, weight="bold", color=self.txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Price", size=11, color=self.sub, font_family="DM Sans", expand=1),
            ft.Text(f"Rs. {price:,.2f}", size=13, color=self.txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Quantity", size=11, color=self.sub, font_family="DM Sans", expand=1),
            ft.Text(str(qty), size=13, color=self.txt, font_family="DM Sans", expand=2),
        ]))

        recipes = []
        if self.is_guest:
            recipes = [r for r in mock_data.get_recipes() if r.get("Item_ID") == iid]
        if recipes:
            rows.append(ft.Divider(height=4, color=ft.Colors.with_opacity(0.08, self.txt)))
            rows.append(ft.Text("Ingredients", size=12, weight="bold", color=self.txt, font_family="DM Sans"))
            for r in recipes[:6]:
                rows.append(ft.Text(f"\u2022 {r.get('Name','?')} ({r.get('Ingredient_Quantity','?')} {r.get('Unit','')})",
                                    size=12, color=self.sub, font_family="DM Sans"))

        async def close(e):
            o = getattr(self, '_detail_overlay', None)
            if o and o in self.page.controls:
                self.page.remove(o)
                self._detail_overlay = None
                self.page.update()

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(name, size=18, weight="bold",
                            color=self.txt, font_family="DM Sans", expand=True),
                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=self.sub,
                                  on_click=close),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *rows,
            ], tight=True, spacing=8),
            bgcolor=self.card, border_radius=18, padding=24, width=400,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
        )
        dim = ft.Colors.with_opacity(0.5 if self.theme.get("is_dark") else 0.25, "#000")
        overlay = ft.Container(
            content=card, bgcolor=dim,
            alignment=ft.Alignment(0, 0), expand=True,
            on_click=close,
        )
        self.page.add(overlay)
        self._detail_overlay = overlay
        self.page.update()

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
        submitted = existing_rating is not None and existing_rating > 0
        rating_state = {"current": existing_rating or 0, "submitted": submitted}
        star_refs = []
        page_ref = self.page

        def render_stars(score, locked=False):
            for i, s in enumerate(star_refs):
                filled = i < score
                s.name  = ft.Icons.STAR_ROUNDED if filled else ft.Icons.STAR_BORDER_ROUNDED
                s.color = self.amber if filled else self.sub

        label = ft.Text(
            "Rated ✓" if rating_state["submitted"] else "Rate:",
            size=11,
            color=self.amber if rating_state["submitted"] else self.sub,
            font_family="DM Sans",
        )

        async def on_star_click(e, score):
            if rating_state["submitted"]:
                return
            rating_state["submitted"] = True
            rating_state["current"] = score
            render_stars(score)
            label.value = "Rated ✓"
            label.color = self.amber
            page_ref.update()

            if self.is_guest:
                mock_data.rate_food_item(self.user_id, item_id, meal_date, meal_type, score)
            else:
                await rate_food_item(
                    user_id=self.user_id,
                    item_id=item_id,
                    meal_date=meal_date,
                    meal_type=meal_type,
                    score=score,
                    email=self.email,
                )
            page_ref.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Rating saved!", color="#FFF"),
                bgcolor="#10B981",
            )
            page_ref.snack_bar.open = True
            page_ref.update()

        async def on_star_hover(e, score):
            if rating_state["submitted"]:
                return
            render_stars(score)
            page_ref.update()

        async def on_hover_leave(e):
            if rating_state["submitted"]:
                return
            render_stars(rating_state["current"])
            page_ref.update()

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

        return ft.Row([label] + stars, spacing=2)

    # ── Food item card ─────────────────────────────────────────────
    def _build_food_card(self, item, meal_date=None, show_date=False):
        name     = self._item_name(item)
        avg      = self._item_rating(item)
        meal_col = self._item_meal_type(item)
        meal_c   = self._meal_color(meal_col)
        iid = item.get("Item_ID") or item.get("ItemID") or 0
        cached = self._food_cache.get(iid, {})
        price = cached.get("Price", 0)

        avg_stars = ft.Row([
            ft.Icon(ft.Icons.STAR_ROUNDED, size=13, color=self.amber),
            ft.Text(f"{avg:.1f}", size=12, color=self.sub, font_family="DM Sans"),
        ], spacing=2)

        schedule_id        = item.get("Schedule_ID") or item.get("ScheduleID") or 0
        date_for_rating    = meal_date or date.today()
        meal_type_for_rating = meal_col
        existing_rating    = item.get("user_rating")

        star_row = self._build_stars(
            item_id=iid,
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

        price_row = ft.Row([
            ft.Text(f"PKR {price:.0f}", size=12, weight="bold",
                    color=self.amber, font_family="DM Sans"),
        ], spacing=2) if price else ft.Container()

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    self._food_thumb(item, 44),
                    ft.Column([
                        ft.Row([
                            ft.Text(
                                name, size=14, weight="bold",
                                color=self.txt, font_family="DM Sans",
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True,
                            ),
                            date_badge,
                        ], spacing=8),
                        avg_stars,
                        price_row,
                    ], spacing=2, expand=True),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=6),
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
            on_click=lambda e, it=iid: asyncio.create_task(self._show_food_detail(item)),
            ink=True,
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

    def _guest_banner(self):
        if not self.is_guest:
            return ft.Container()
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=self.navy),
                ft.Text(
                    "Guest Mode \u2014 Changes are temporary and reset on logout. "
                    "This is a demo sandbox, not real data.",
                    size=12, color=self.navy, font_family="DM Sans", expand=True,
                ),
            ], spacing=10),
            bgcolor="#FEF3C7", border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=12),
        )

    # ── Load & render ──────────────────────────────────────────────
    async def _render(self):
        self.main_container.content = self._loading()
        self.main_container.opacity = 0
        self.page.update()

        # Pre-fetch food items for image/price lookups
        self._food_cache = {}
        if self.is_guest:
            for f in mock_data.get_food_costs():
                self._food_cache[f["Item_ID"]] = f
        else:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{BASE_URL}/admin/food-items/all", params={"email": self.email}, timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list):
                            for f in data:
                                self._food_cache[f["Item_ID"]] = f
            except:
                pass

        uid = self.user_id if not self.is_guest else None

        if self._view["weekly"]:
            if self.is_guest:
                data = mock_data.get_weekly_menu()
            else:
                data = await get_weekly_menu(user_id=uid)
            if not self.is_guest and isinstance(data, dict) and "error" in data:
                body = self._error(data["error"])
            else:
                items = data if isinstance(data, list) else []
                body  = self._build_weekly(items)
        else:
            if self.is_guest:
                data = mock_data.get_todays_menu()
            else:
                data = await get_todays_menu(self.email, user_id=uid)
            if not self.is_guest and isinstance(data, dict) and "error" in data:
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
            self._guest_banner(),
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
        self.main_container.opacity = 1
        self.page.update()

    def build(self):
        asyncio.create_task(self._render())
        m = (self.page.width or 1200) < 720
        return ft.Container(
            content=self.main_container,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=12 if m else 24, vertical=20),
        )