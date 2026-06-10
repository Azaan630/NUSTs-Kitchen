import flet as ft
import asyncio
import httpx
import os

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


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


class StaffPage:
    """Read-only staff dashboard: weekly menu, food items, ingredients, recipes."""

    TABS = [
        ("Weekly Menu",  ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Food Items",   ft.Icons.FASTFOOD_ROUNDED),
        ("Ingredients",  ft.Icons.GRAIN_ROUNDED),
        ("Recipes",      ft.Icons.MENU_BOOK_ROUNDED),
    ]
    RENDERERS = [
        "_render_menu",
        "_render_food",
        "_render_ingredients",
        "_render_recipes",
    ]

    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.P = theme["P"]

    # ── UI helpers ──────────────────────────────────────────────────────────

    def _loading(self, msg="Loading..."):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.P.PRIMARY, width=36, height=36, stroke_width=3),
                ft.Text(msg, color=self.P.MUTED, font_family="DM Sans", size=13),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
            alignment=ft.Alignment(0, 0), expand=True, padding=50,
        )

    def _error(self, msg):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=self.P.ERROR, size=40),
                ft.Text(msg, color=self.P.ERROR, font_family="DM Sans", size=13,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            alignment=ft.Alignment(0, 0), padding=50,
        )

    def _snack(self, msg, ok=True):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#FFF"),
            bgcolor=self.P.SUCCESS if ok else self.P.ERROR,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _title(self, txt):
        return ft.Text(txt, size=18, weight="bold", color=self.P.TEXT_LIGHT, font_family="DM Sans")

    def _icon_btn(self, icon, color, tip, cb):
        return ft.IconButton(
            icon=icon, icon_color=color, tooltip=tip, icon_size=18, on_click=cb,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.1, color),
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.all(6),
            ),
        )

    def _chip(self, label, fg, bg):
        return ft.Container(
            content=ft.Text(label, size=10, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )

    def _row_card(self, controls, actions=None):
        row_ctrls = list(controls)
        if actions:
            row_ctrls.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row_ctrls, spacing=12),
            bgcolor=self.P.SURFACE, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            margin=ft.Margin.only(bottom=8),
            border=ft.Border.all(0.5, ft.Colors.with_opacity(0.1, self.P.WHITE)),
        )

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 0 — WEEKLY MENU
    # ════════════════════════════════════════════════════════════════════════

    async def _render_menu(self, content_ref):
        content_ref.content = self._loading("Fetching weekly menu...")
        self.page.update()

        data = await api_get_weekly_menu(self.email)
        if isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        MEAL_COLORS = {
            "Breakfast": self.P.WARNING,
            "Lunch":     self.P.SUCCESS,
            "Dinner":    self.P.SECONDARY,
        }
        MEAL_ICONS = {
            "Breakfast": ft.Icons.WB_SUNNY_ROUNDED,
            "Lunch":     ft.Icons.LIGHT_MODE_ROUNDED,
            "Dinner":    ft.Icons.NIGHTS_STAY_ROUNDED,
        }

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
                                color=self.P.PRIMARY_LT, font_family="DM Sans"),
                margin=ft.Margin.only(top=14, bottom=4),
            ))

            for mt, fit in meals.items():
                mc   = MEAL_COLORS.get(mt, self.P.PRIMARY)
                mico = MEAL_ICONS.get(mt, ft.Icons.RESTAURANT_ROUNDED)
                names = ", ".join(i.get("Food_Item_Name") or "?" for i in fit)
                avg  = fit[0].get("Ratings_Average") or fit[0].get("Avg_Rating") or 0

                sections.append(self._row_card([
                    ft.Container(
                        content=ft.Icon(mico, size=18, color=mc),
                        width=36, height=36,
                        bgcolor=ft.Colors.with_opacity(0.12, mc),
                        border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(mt, size=12, weight="bold",
                                color=mc, font_family="DM Sans"),
                        ft.Text(names, size=13, color=self.P.TEXT_LIGHT,
                                font_family="DM Sans"),
                    ], spacing=2, expand=True),
                    ft.Row([
                        ft.Icon(ft.Icons.STAR_ROUNDED, size=13, color=self.P.WARNING),
                        ft.Text(f"{float(avg):.1f}" if avg else "\u2014",
                                size=12, color=self.P.MUTED, font_family="DM Sans"),
                    ], spacing=3),
                ]))

        content_ref.content = ft.Column([
            ft.Row([
                self._title("Weekly Menu"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.P.MUTED, "Refresh",
                               lambda e: asyncio.create_task(self._render_menu(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(sections, scroll=ft.ScrollMode.ADAPTIVE) if sections else
            ft.Text("No menu available.", color=self.P.MUTED, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 1 — FOOD ITEMS + COSTS
    # ════════════════════════════════════════════════════════════════════════

    async def _render_food(self, content_ref):
        content_ref.content = self._loading("Fetching food items...")
        self.page.update()

        data = await api_get_food_costs(self.email)
        if isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        rows = []
        for item in items:
            cost = item.get("Estimated_Cost", 0)
            rows.append(self._row_card([
                ft.Container(
                    content=ft.Icon(ft.Icons.FASTFOOD_ROUNDED, size=20, color=self.P.PRIMARY_LT),
                    width=40, height=40,
                    bgcolor=ft.Colors.with_opacity(0.12, self.P.PRIMARY),
                    border_radius=12, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(item.get("Name", "?"), size=13, weight="bold",
                            color=self.P.TEXT_LIGHT, font_family="DM Sans"),
                    ft.Text(f"Est. cost: PKR {float(cost):.2f}",
                            size=11, color=self.P.MUTED, font_family="DM Sans"),
                ], spacing=2, expand=True),
                ft.Text(f"ID #{item.get('Item_ID','?')}",
                        size=11, color=self.P.MUTED, font_family="DM Sans"),
            ]))

        content_ref.content = ft.Column([
            ft.Row([
                self._title(f"Food Items ({len(items)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.P.MUTED, "Refresh",
                               lambda e: asyncio.create_task(self._render_food(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No food items.", color=self.P.MUTED, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 2 — INGREDIENTS
    # ════════════════════════════════════════════════════════════════════════

    async def _render_ingredients(self, content_ref):
        content_ref.content = self._loading("Fetching ingredients...")
        self.page.update()

        data = await api_get_ingredients(self.email)
        if isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        items = data if isinstance(data, list) else []

        rows = []
        for ing in items:
            unit_cost = ing.get("Unit_cost", 0)
            qty       = ing.get("Total_Quantity", 0)
            rows.append(self._row_card([
                ft.Container(
                    content=ft.Icon(ft.Icons.GRAIN_ROUNDED, size=18, color=self.P.SUCCESS),
                    width=36, height=36,
                    bgcolor=ft.Colors.with_opacity(0.12, self.P.SUCCESS),
                    border_radius=10, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(ing.get("Name", "?"), size=13, weight="bold",
                            color=self.P.TEXT_LIGHT, font_family="DM Sans"),
                    ft.Row([
                        self._chip(
                            f"{qty} {ing.get('Unit','')}",
                            self.P.SUCCESS,
                            ft.Colors.with_opacity(0.1, self.P.SUCCESS),
                        ),
                        ft.Text(f"PKR {float(unit_cost):.2f}/unit",
                                size=11, color=self.P.MUTED, font_family="DM Sans"),
                    ], spacing=8),
                ], spacing=4, expand=True),
                ft.Text(f"ID #{ing.get('Ingredient_ID','?')}",
                        size=10, color=self.P.MUTED, font_family="DM Sans"),
            ]))

        content_ref.content = ft.Column([
            ft.Row([
                self._title(f"Ingredients ({len(items)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.P.MUTED, "Refresh",
                               lambda e: asyncio.create_task(self._render_ingredients(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No ingredients.", color=self.P.MUTED, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 3 — RECIPES
    # ════════════════════════════════════════════════════════════════════════

    async def _render_recipes(self, content_ref):
        content_ref.content = self._loading("Fetching recipes...")
        self.page.update()

        data = await api_get_recipes(self.email)
        if isinstance(data, dict) and "error" in data:
            content_ref.content = self._error(data["error"])
            self.page.update()
            return

        rows_raw = data if isinstance(data, list) else []

        from collections import defaultdict
        grouped = defaultdict(list)
        for r in rows_raw:
            grouped[r.get("Item_ID")].append(r)

        cards = []
        for item_id, ingredients in grouped.items():
            ing_rows = [
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=self.P.PRIMARY_LT),
                    ft.Text(
                        f"{ing.get('Name','?')}  \u2014  "
                        f"{ing.get('Ingredient_Quantity','?')} {ing.get('Unit','')}",
                        size=12, color=self.P.TEXT_LIGHT, font_family="DM Sans",
                    ),
                ], spacing=8)
                for ing in ingredients
            ]
            cards.append(self._row_card([
                ft.Container(
                    content=ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=18, color=self.P.SECONDARY),
                    width=36, height=36,
                    bgcolor=ft.Colors.with_opacity(0.12, self.P.SECONDARY),
                    border_radius=10, alignment=ft.Alignment(0, 0),
                ),
                ft.Text(f"Food Item ID #{item_id}", size=13, weight="bold",
                        color=self.P.TEXT_LIGHT, font_family="DM Sans"),
            ]))
            cards.append(
                ft.Container(
                    content=ft.Column(ing_rows, spacing=4),
                    bgcolor=ft.Colors.with_opacity(0.03, self.P.WHITE),
                    border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    margin=ft.Margin.only(bottom=8),
                )
            )

        content_ref.content = ft.Column([
            ft.Row([
                self._title(f"Recipes ({len(grouped)} items)"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.P.MUTED, "Refresh",
                               lambda e: asyncio.create_task(self._render_recipes(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            ft.Column(cards, scroll=ft.ScrollMode.ADAPTIVE) if cards else
            ft.Text("No recipes found.", color=self.P.MUTED, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()
