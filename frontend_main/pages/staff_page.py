import flet as ft
import asyncio
import httpx
import os
import mock_data

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


async def _req(endpoint, params=None):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
            r.raise_for_status()
            return r.json() if r.status_code != 204 else {}
        except httpx.HTTPStatusError as e:
            try: d = e.response.json().get("detail", e.response.text)
            except Exception: d = e.response.text
            return {"error": f"({e.response.status_code}) {d}"}
        except Exception as ex:
            return {"error": str(ex)}


class StaffPage:
    SECTIONS = [
        ("Menu",        ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Food Items",  ft.Icons.FASTFOOD_ROUNDED),
        ("Ingredients", ft.Icons.CATEGORY_ROUNDED),
        ("Recipes",     ft.Icons.BOOK_ROUNDED),
    ]

    def __init__(self, page, user_data, theme):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)
        self.section_idx = {"v": 0}
        self.content = ft.Container(expand=True)
        self.content.content = self._loading()

    def _clr(self, key, fallback=None):
        return self.theme.get(key, fallback)

    def _loading(self, msg="Loading\u2026"):
        return ft.Container(
            ft.Column([
                ft.ProgressRing(width=32, height=32, stroke_width=3, color=self._clr("accent")),
                ft.Text(msg, size=13, color=self._clr("sub"), font_family="DM Sans"),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            alignment=ft.Alignment(0, 0), expand=True,
        )

    def _snack(self, msg, ok=True):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#FFF"),
            bgcolor=self._clr("success") if ok else self._clr("danger"),
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _card(self, *controls):
        return ft.Container(
            content=ft.Column(list(controls), spacing=10),
            bgcolor=self._clr("card"), border_radius=14, padding=14,
        )

    def _row_card(self, controls, actions=None, data=None):
        row = list(controls)
        if actions: row.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row, spacing=12),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=6),
            data=data,
        )

    def _chip(self, label, fg, bg):
        return ft.Container(
            content=ft.Text(label, size=10, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )

    def _field(self, label, hint=""):
        return ft.TextField(
            label=label, hint_text=hint,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            focused_border_color=self._clr("accent"),
            label_style=ft.TextStyle(color=self._clr("sub"), size=13, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            cursor_color=self._clr("accent"),
        )

    def _guest_banner(self):
        if not self.is_guest: return ft.Container()
        return ft.Container(
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=self._clr("text")),
                ft.Text("Guest Mode \u2014 Temporary demo data",
                        size=12, color=self._clr("text"), font_family="DM Sans", expand=True),
            ], spacing=10),
            bgcolor=ft.Colors.with_opacity(0.1, self._clr("warn")),
            border_radius=10, padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=12),
        )

    # ── Sidebar ────────────────────────────────────────────────

    def _sidebar(self, on_select):
        items = []
        for i, (label, icon) in enumerate(self.SECTIONS):
            sel = self.section_idx["v"] == i
            items.append(ft.Container(
                ft.Row([
                    ft.Icon(icon, size=18, color=self._clr("accent") if sel else self._clr("sub")),
                    ft.Text(label, size=13, font_family="DM Sans",
                            weight="bold" if sel else "normal",
                            color=self._clr("text") if sel else self._clr("sub")),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.1, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                border_radius=12, padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                on_click=lambda e, idx=i: on_select(idx),
            ))
        return ft.Container(
            content=ft.Column(items, spacing=4),
            bgcolor=self._clr("card"), border_radius=16,
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            width=170,
        )

    # ── SECTION: Menu ──────────────────────────────────────────

    async def _render_menu(self, ref):
        ref.content = self._loading(); self.page.update()
        items = mock_data.get_weekly_menu() if self.is_guest else (await _req("/menu/weekly", {"email": self.email})) or []
        m_colors = {"Breakfast": self._clr("warn"), "Lunch": self._clr("success"), "Dinner": self._clr("accent2")}
        rows = []
        for item in (items if isinstance(items, list) else []):
            mt = item.get("meal_type", "")
            rows.append(self._row_card([
                ft.Container(
                    content=ft.Text(mt[:1], size=12, weight="bold", color=m_colors.get(mt, self._clr("accent"))),
                    width=30, height=30,
                    bgcolor=ft.Colors.with_opacity(0.12, m_colors.get(mt, self._clr("accent"))),
                    border_radius=8, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(item.get("Name") or item.get("Food_Item_Name", "?"), size=13,
                            weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{item.get('Date','')} \u2022 {mt}", size=11,
                            color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
            ]))
        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Weekly Menu", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No menu items", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ── SECTION: Food Items ────────────────────────────────────

    async def _render_food(self, ref):
        ref.content = self._loading(); self.page.update()
        items = mock_data.get_food_costs() if self.is_guest else (await _req("/admin/food/costs", {"email": self.email})) or []

        search = ft.TextField(
            hint_text="Search food\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data), expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in food_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        food_rows = ft.Column(spacing=4)
        for item in (items if isinstance(items, list) else []):
            name = item.get("Name", "")
            cost = item.get("Estimated_Cost", 0)
            price = item.get("Price", 0)
            label = f"{name} | {item.get('Item_ID','')}"
            food_rows.controls.append(self._row_card([
                ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans", expand=True),
                ft.Text(f"PKR {price}", size=12, color=self._clr("accent"), font_family="DM Sans"),
                ft.Text(f"Cost: PKR {cost:.0f}", size=11, color=self._clr("sub"), font_family="DM Sans"),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Food Items", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=8),
            ft.Row([search], spacing=8),
            ft.Container(height=4),
            food_rows if food_rows.controls else ft.Text("No food items", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ── SECTION: Ingredients + Low Stock ───────────────────────

    async def _render_ingredients(self, ref):
        ref.content = self._loading(); self.page.update()
        ingredients = mock_data.get_ingredients() if self.is_guest else (await _req("/analytics/ingredients", {"email": self.email})) or []

        low_stock = [i for i in (ingredients if isinstance(ingredients, list) else [])
                     if i.get("Total_Quantity", 0) < 10]

        alert = ft.Container()
        if low_stock:
            alert = self._card(
                ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=20, color=self._clr("danger")),
                        ft.Text(f"{len(low_stock)} low-stock ingredients", size=14, weight="bold",
                                color=self._clr("danger"), font_family="DM Sans")], spacing=8),
                *[self._row_card([
                    ft.Text(i.get("Name", ""), size=13, weight="bold", color=self._clr("text"), font_family="DM Sans", expand=True),
                    ft.Text(f"Qty: {i.get('Total_Quantity', 0)} {i.get('Unit', '')}",
                            size=12, color=self._clr("danger"), font_family="DM Sans"),
                ], data=i.get("Name")) for i in low_stock]
            )

        rows = ft.Column(spacing=4)
        for i in (ingredients if isinstance(ingredients, list) else []):
            rows.controls.append(self._row_card([
                ft.Text(i.get("Name", ""), size=13, weight="bold", color=self._clr("text"), font_family="DM Sans", expand=True),
                ft.Text(f"{i.get('Total_Quantity', 0)} {i.get('Unit', '')}", size=12,
                        color=self._clr("sub"), font_family="DM Sans"),
                ft.Text(f"PKR {i.get('Unit_cost', 0)}/{i.get('Unit', '')}", size=11,
                        color=self._clr("sub"), font_family="DM Sans"),
            ]))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Ingredients", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=8),
            alert,
            ft.Container(height=8) if low_stock else ft.Container(),
            rows if rows.controls else ft.Text("No ingredients", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ── SECTION: Recipes ───────────────────────────────────────

    async def _render_recipes(self, ref):
        ref.content = self._loading(); self.page.update()
        recipes = mock_data.get_recipes() if self.is_guest else (await _req("/recipes", {"email": self.email})) or []

        grouped = {}
        for r in (recipes if isinstance(recipes, list) else []):
            iid = r.get("Item_ID")
            grouped.setdefault(iid, {"item_id": iid, "ingredients": []})
            grouped[iid]["ingredients"].append(r)

        rows = ft.Column(spacing=4)
        fid = 0
        for g in grouped.values():
            fid += 1
            ing_text = ", ".join([f"{i.get('Name','?')} ({i.get('Ingredient_Quantity','?')} {i.get('Unit','')})"
                                  for i in g["ingredients"]])
            rows.controls.append(self._row_card([
                ft.Column([
                    ft.Text(f"Item #{g['item_id']}", size=13, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(ing_text, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
            ]))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Recipes", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=8),
            rows if rows.controls else ft.Text("No recipes", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ── Safe render wrapper ────────────────────────────────────

    async def _safe_render(self, method_name, ref):
        try:
            await getattr(self, method_name)(ref)
        except Exception as e:
            import traceback
            traceback.print_exc()
            ref.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=48, color=self._clr("danger")),
                ft.Text(f"Error: {e}", color=self._clr("danger"), font_family="DM Sans", size=14),
            ], alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()

    # ── BUILD ──────────────────────────────────────────────────

    RENDERERS = ["_render_menu", "_render_food", "_render_ingredients", "_render_recipes"]

    def build(self):
        def select_section(idx):
            self.section_idx["v"] = idx
            sidebar.controls[0] = self._sidebar(select_section)
            asyncio.create_task(self._safe_render(self.RENDERERS[idx], self.content))
            self.page.update()

        sidebar = ft.Column([self._sidebar(select_section)])
        layout = ft.Row([
            sidebar,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, self._clr("text"))),
            ft.Container(content=self.content, expand=True, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
        ], expand=True, spacing=0)

        asyncio.create_task(self._safe_render("_render_menu", self.content))

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Staff", size=24, weight="bold", font_family="DM Sans", color=self._clr("text")),
                    self._chip("Staff", self._clr("accent2"), ft.Colors.with_opacity(0.12, self._clr("accent2"))),
                ], spacing=12),
                ft.Container(height=8),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        )
