import flet as ft
import asyncio
import httpx
import os
import mock_data

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


# ── Lightweight API helpers (staff-scoped, all read-only) ────────────────────

async def _req(endpoint: str, params=None):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}{endpoint}", params=params, timeout=10.0)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            return {"error": f"({e.response.status_code}) {detail}"}
        except Exception as ex:
            return {"error": str(ex)}


async def api_get_weekly_menu(email):   return await _req("/menu/weekly",         {"email": email})
async def api_get_food_costs(email):    return await _req("/admin/food/costs",    {"email": email})
async def api_get_ingredients(email):   return await _req("/analytics/ingredients",{"email": email})
async def api_get_recipes(email):       return await _req("/recipes",              {"email": email})


# ── StaffPage ────────────────────────────────────────────────────────────────

class StaffPage:
    """Read-only staff dashboard: weekly menu, food items, ingredients, recipes."""

    TABS = [
        ("Weekly Menu",  ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Food Items",   ft.Icons.FASTFOOD_ROUNDED),
        ("Ingredients",  ft.Icons.GRAIN_ROUNDED),
        ("Recipes",      ft.Icons.MENU_BOOK_ROUNDED),
    ]

    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.bg    = t["DARK_BG"]   if t["is_dark"] else t["CREAM"]
        self.card  = t["DARK_CARD"] if t["is_dark"] else t["WHITE"]
        self.card2 = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt   = t["WHITE"]     if t["is_dark"] else t["NAVY"]
        self.sub   = t["GREY"]
        self.amber = t["AMBER"]
        self.navy  = t["NAVY"]

        self._tab  = {"v": 0}
        self.main  = ft.Container(expand=True)

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

    # ── Generic UI helpers ──────────────────────────────────────────────────

    def _loading(self, msg="Loading…"):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.amber, width=36, height=36, stroke_width=3),
                ft.Text(msg, color=self.sub, font_family="DM Sans", size=13),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
            alignment=ft.Alignment(0, 0), expand=True, padding=50,
        )

    def _error(self, msg):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#EF4444", size=40),
                ft.Text(msg, color="#EF4444", font_family="DM Sans", size=13,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.Alignment(0, 0), padding=50,
        )

    def _section_title(self, txt):
        return ft.Text(txt, size=16, weight="bold", color=self.txt, font_family="DM Sans")

    def _icon_btn(self, icon, color, tip, cb):
        return ft.IconButton(icon=icon, icon_color=color, tooltip=tip,
                             icon_size=18, on_click=cb,
                             style=ft.ButtonStyle(padding=ft.Padding.all(4)))

    def _chip(self, label, fg, bg):
        return ft.Container(
            content=ft.Text(label, size=10, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )

    def _info_row(self, label, value, label_w=130):
        return ft.Row([
            ft.Text(label, size=12, color=self.sub, font_family="DM Sans", width=label_w),
            ft.Text(str(value), size=12, color=self.txt, font_family="DM Sans",
                    weight="bold", expand=True),
        ], spacing=8)

    def _card(self, controls, accent=None):
        accent = accent or self.amber
        return ft.Container(
            content=ft.Column(controls, spacing=6),
            bgcolor=self.card, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(blur_radius=8,
                                color=ft.Colors.with_opacity(0.05, "#000"),
                                offset=ft.Offset(0, 2)),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.07, "#000")),
        )

    # ── Sidebar ─────────────────────────────────────────────────────────────

    def _build_sidebar(self, on_select):
        items = []
        for i, (label, icon) in enumerate(self.TABS):
            is_sel = self._tab["v"] == i
            items.append(ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=18,
                            color=self.amber if is_sel else self.sub),
                    ft.Text(label, size=13, font_family="DM Sans",
                            weight="bold" if is_sel else "normal",
                            color=self.amber if is_sel else self.sub),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.12, self.amber) if is_sel else ft.Colors.TRANSPARENT,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                on_click=lambda e, idx=i: on_select(idx),
                animate=ft.Animation(180, "easeOut"),
            ))
        return ft.Container(
            content=ft.Column(items, spacing=4),
            bgcolor=self.card, border_radius=16,
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            width=160,
            shadow=ft.BoxShadow(blur_radius=16,
                                color=ft.Colors.with_opacity(0.07, "#000"),
                                offset=ft.Offset(0, 2)),
        )

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 0 — WEEKLY MENU
    # ════════════════════════════════════════════════════════════════════════

    async def _render_menu(self, content_ref):
        content_ref.content = self._loading("Fetching weekly menu…")
        self.page.update()

        if self.is_guest:
            data = mock_data.get_weekly_menu()
        else:
            data = await api_get_weekly_menu(self.email)
        if not self.is_guest and isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        MEAL_COLORS = {
            "Breakfast": "#F59E0B",
            "Lunch":     "#10B981",
            "Dinner":    "#6366F1",
        }
        MEAL_ICONS = {
            "Breakfast": ft.Icons.WB_SUNNY_ROUNDED,
            "Lunch":     ft.Icons.LIGHT_MODE_ROUNDED,
            "Dinner":    ft.Icons.NIGHTS_STAY_ROUNDED,
        }

        # Group by date → meal_type
        from collections import OrderedDict
        date_groups = OrderedDict()
        for item in items:
            d  = str(item.get("Date", ""))
            mt = item.get("meal_type", "")
            date_groups.setdefault(d, {}).setdefault(mt, []).append(item)

        sections = []
        for d, meals in date_groups.items():
            try:
                from datetime import datetime
                weekday = datetime.strptime(d, "%Y-%m-%d").strftime("%A, %d %b")
            except Exception:
                weekday = d

            sections.append(ft.Container(
                content=ft.Text(weekday, size=14, weight="bold",
                                color=self.amber, font_family="DM Sans"),
                margin=ft.Margin.only(top=14, bottom=4),
            ))

            for mt, fit in meals.items():
                mc   = MEAL_COLORS.get(mt, self.amber)
                mico = MEAL_ICONS.get(mt, ft.Icons.RESTAURANT_ROUNDED)
                names = ", ".join(i.get("Food_Item_Name") or "?" for i in fit)
                avg  = fit[0].get("Ratings_Average") or fit[0].get("Avg_Rating") or 0

                sections.append(self._card([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(mico, size=18, color=mc),
                            width=36, height=36,
                            bgcolor=ft.Colors.with_opacity(0.12, mc),
                            border_radius=10, alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            ft.Text(mt, size=12, weight="bold",
                                    color=mc, font_family="DM Sans"),
                            ft.Text(names, size=13, color=self.txt,
                                    font_family="DM Sans"),
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR_ROUNDED, size=13, color=self.amber),
                            ft.Text(f"{float(avg):.1f}" if avg else "—",
                                    size=12, color=self.sub, font_family="DM Sans"),
                        ], spacing=3),
                    ], spacing=10),
                ], accent=mc))

        content_ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                self._section_title("Weekly Menu"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_menu(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(sections, scroll=ft.ScrollMode.ADAPTIVE) if sections else
            ft.Text("No menu available.", color=self.sub, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 1 — FOOD ITEMS + COSTS
    # ════════════════════════════════════════════════════════════════════════

    async def _render_food(self, content_ref):
        content_ref.content = self._loading("Fetching food items…")
        self.page.update()

        if self.is_guest:
            data = mock_data.get_food_costs()
        else:
            data = await api_get_food_costs(self.email)
        if not self.is_guest and isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        rows = []
        for item in items:
            cost = item.get("Estimated_Cost", 0)
            rows.append(self._card([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.FASTFOOD_ROUNDED, size=18, color=self.amber),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.12, self.amber),
                        border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(item.get("Name","?"), size=13, weight="bold",
                                color=self.txt, font_family="DM Sans"),
                        ft.Text(f"Est. cost: PKR {float(cost):.2f}",
                                size=11, color=self.sub, font_family="DM Sans"),
                    ], spacing=2, expand=True),
                    ft.Text(f"ID #{item.get('Item_ID','?')}",
                            size=11, color=self.sub, font_family="DM Sans"),
                ], spacing=10),
            ]))

        content_ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                self._section_title(f"Food Items ({len(items)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_food(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No food items.", color=self.sub, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 2 — INGREDIENTS
    # ════════════════════════════════════════════════════════════════════════

    async def _render_ingredients(self, content_ref):
        content_ref.content = self._loading("Fetching ingredients…")
        self.page.update()

        if self.is_guest:
            data = mock_data.get_ingredients()
        else:
            data = await api_get_ingredients(self.email)
        if not self.is_guest and isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        rows = []
        for ing in items:
            unit_cost = ing.get("Unit_cost", 0)
            qty       = ing.get("Total_Quantity", 0)
            rows.append(self._card([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.GRAIN_ROUNDED, size=18, color="#10B981"),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.12, "#10B981"),
                        border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(ing.get("Name","?"), size=13, weight="bold",
                                color=self.txt, font_family="DM Sans"),
                        ft.Row([
                            self._chip(
                                f"{qty} {ing.get('Unit','')}",
                                "#10B981",
                                ft.Colors.with_opacity(0.1, "#10B981"),
                            ),
                            ft.Text(f"PKR {float(unit_cost):.2f}/unit",
                                    size=11, color=self.sub, font_family="DM Sans"),
                        ], spacing=8),
                    ], spacing=4, expand=True),
                    ft.Text(f"ID #{ing.get('Ingredient_ID','?')}",
                            size=10, color=self.sub, font_family="DM Sans"),
                ], spacing=10),
            ], accent="#10B981"))

        content_ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                self._section_title(f"Ingredients ({len(items)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_ingredients(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No ingredients.", color=self.sub, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 3 — RECIPES
    # ════════════════════════════════════════════════════════════════════════

    async def _render_recipes(self, content_ref):
        content_ref.content = self._loading("Fetching recipes…")
        self.page.update()

        if self.is_guest:
            data = mock_data.get_recipes()
        else:
            data = await api_get_recipes(self.email)
        if not self.is_guest and isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        rows_raw = data if isinstance(data, list) else []

        # Group by Item_ID
        from collections import defaultdict
        grouped = defaultdict(list)
        for r in rows_raw:
            grouped[r.get("Item_ID")].append(r)

        cards = []
        for item_id, ingredients in grouped.items():
            ing_rows = [
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=self.amber),
                    ft.Text(
                        f"{ing.get('Name','?')}  —  "
                        f"{ing.get('Ingredient_Quantity','?')} {ing.get('Unit','')}",
                        size=12, color=self.txt, font_family="DM Sans",
                    ),
                ], spacing=8)
                for ing in ingredients
            ]
            cards.append(self._card([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=18, color="#6366F1"),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.12, "#6366F1"),
                        border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(f"Food Item ID #{item_id}", size=13, weight="bold",
                            color=self.txt, font_family="DM Sans"),
                ], spacing=10),
                ft.Container(height=4),
                ft.Column(ing_rows, spacing=4),
            ], accent="#6366F1"))

        content_ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                self._section_title(f"Recipes ({len(grouped)} items)"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_recipes(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(cards, scroll=ft.ScrollMode.ADAPTIVE) if cards else
            ft.Text("No recipes found.", color=self.sub, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ── Tab dispatcher ──────────────────────────────────────────────────────

    RENDERERS = [
        "_render_menu",
        "_render_food",
        "_render_ingredients",
        "_render_recipes",
    ]

    # ── Build ───────────────────────────────────────────────────────────────

    def build(self):
        content_ref = ft.Container(expand=True)

        def select_tab(idx):
            self._tab["v"] = idx
            sidebar_col.controls[0] = self._build_sidebar(select_tab)
            asyncio.create_task(getattr(self, self.RENDERERS[idx])(content_ref))
            self.page.update()

        sidebar_col = ft.Column([self._build_sidebar(select_tab)])

        layout = ft.Row([
            sidebar_col,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, "#000")),
            ft.Container(content=content_ref, expand=True,
                         padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
        ], expand=True, spacing=0)

        # Load first tab
        asyncio.create_task(self._render_menu(content_ref))

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Staff Portal", size=26, weight="bold",
                            font_family="DM Sans", color=self.txt),
                    self._chip("Staff", "#10B981",
                               ft.Colors.with_opacity(0.12, "#10B981")),
                ], spacing=12),
                ft.Container(height=12),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            bgcolor=self.bg, expand=True,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        )