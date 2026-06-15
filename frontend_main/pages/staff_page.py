import flet as ft
import asyncio
import httpx
import os
import uuid
import mock_data

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")

from .api_client import get_headers as _api_headers


async def _req(endpoint, params=None):
    async with httpx.AsyncClient() as client:
        try:
            headers = _api_headers()
            r = await client.get(f"{BASE_URL}{endpoint}", params=params, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json() if r.status_code != 204 else {}
        except httpx.HTTPStatusError as e:
            try: d = e.response.json().get("detail", e.response.text)
            except Exception: d = e.response.text
            return {"error": f"({e.response.status_code}) {d}"}
        except Exception as ex:
            return {"error": str(ex)}


PUBLIC_BACKEND_URL = os.getenv("PUBLIC_BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


def _img_url(path):
    if not path: return None
    if path.startswith(("http://", "https://", "data:")): return path
    return f"{PUBLIC_BACKEND_URL}{path}"


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
        self.content = ft.Container(expand=True,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT))
        self.content.content = self._loading()
        self._recipe_dlg = None

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

    def _row_card(self, controls, actions=None, data=None, on_click=None):
        row = list(controls)
        if actions: row.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row, spacing=12),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=6),
            data=data, on_click=on_click, ink=on_click is not None,
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

    def _food_thumb(self, item, size=44):
        path = item.get("Image_Path")
        if path:
            return ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=size, height=size),
                width=size, height=size, border_radius=10,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        return ft.Container(
            content=ft.Icon(ft.Icons.FASTFOOD_ROUNDED, size=size*0.45, color=self._clr("sub")),
            width=size, height=size, bgcolor=self._clr("card2"), border_radius=10,
            alignment=ft.Alignment(0, 0),
        )

    def _ing_thumb(self, item, size=44):
        path = item.get("Image_Path")
        if path:
            return ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=size, height=size),
                width=size, height=size, border_radius=10,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        return ft.Container(
            content=ft.Icon(ft.Icons.CATEGORY_ROUNDED, size=size*0.45, color=self._clr("sub")),
            width=size, height=size, bgcolor=self._clr("card2"), border_radius=10,
            alignment=ft.Alignment(0, 0),
        )

    def _show_food_detail(self, item):
        t = self.theme
        sub = t.get("sub")
        txt = t.get("text")
        card_bg = t.get("card")
        name = item.get("Name") or item.get("Food_Item_Name", "Unknown")
        price = item.get("Price", 0)
        qty = item.get("Quantity", 0)
        path = item.get("Image_Path")

        rows = []
        if path:
            rows.append(ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=200, height=150),
                border_radius=12, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.Alignment(0, 0),
            ))
        rows.append(ft.Divider(height=8, color=ft.Colors.with_opacity(0.1, txt)))
        rows.append(ft.Row([
            ft.Text("Name", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(name, size=14, weight="bold", color=txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Price", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(f"Rs. {price:,.2f}", size=13, color=txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Quantity", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(str(qty), size=13, color=txt, font_family="DM Sans", expand=2),
        ]))

        iid = item.get("Item_ID")
        if iid:
            recipes = []
            if self.is_guest:
                recipes = [r for r in mock_data.get_recipes() if r.get("Item_ID") == iid]
            else:
                import asyncio
                try:
                    r = asyncio.run(_req("/recipes", {"email": self.email}))
                    recipes = [r for r in (r if isinstance(r, list) else []) if r.get("Item_ID") == iid]
                except: pass
            if recipes:
                rows.append(ft.Divider(height=4, color=ft.Colors.with_opacity(0.08, txt)))
                rows.append(ft.Text("Ingredients", size=12, weight="bold", color=txt, font_family="DM Sans"))
                for r in recipes[:6]:
                    rows.append(ft.Text(f"\u2022 {r.get('Name','?')} ({r.get('Ingredient_Quantity','?')} {r.get('Unit','')})",
                                        size=12, color=sub, font_family="DM Sans"))

        max_h = (self.page.height or 700) * 0.85
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Food Details", size=18, weight="bold",
                            color=txt, font_family="DM Sans", expand=True),
                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=sub,
                                  on_click=lambda e: self._remove_overlay()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *rows,
            ], spacing=8, scroll=ft.ScrollMode.ADAPTIVE),
            bgcolor=card_bg, border_radius=18, padding=24, width=420,
            height=max_h,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
        )
        self._show_overlay(card)

    def _show_ingredient_detail(self, item):
        t = self.theme
        sub = t.get("sub")
        txt = t.get("text")
        card_bg = t.get("card")
        name = item.get("Name", "Unknown")
        qty = item.get("Total_Quantity", 0)
        unit = item.get("Unit", "")
        cost = item.get("Unit_cost", 0)
        path = item.get("Image_Path")

        rows = []
        if path:
            rows.append(ft.Container(
                content=ft.Image(src=_img_url(path), fit="cover", width=200, height=150),
                border_radius=12, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                alignment=ft.Alignment(0, 0),
            ))
        rows.append(ft.Divider(height=8, color=ft.Colors.with_opacity(0.1, txt)))
        rows.append(ft.Row([
            ft.Text("Name", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(name, size=14, weight="bold", color=txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Quantity", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(f"{qty} {unit}", size=13, color=txt, font_family="DM Sans", expand=2),
        ]))
        rows.append(ft.Row([
            ft.Text("Unit Cost", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(f"Rs. {cost:,.2f}/{unit}", size=13, color=txt, font_family="DM Sans", expand=2),
        ]))

        max_h = (self.page.height or 700) * 0.85
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Ingredient Details", size=18, weight="bold",
                            color=txt, font_family="DM Sans", expand=True),
                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=sub,
                                  on_click=lambda e: self._remove_overlay()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *rows,
            ], spacing=8, scroll=ft.ScrollMode.ADAPTIVE),
            bgcolor=card_bg, border_radius=18, padding=24, width=420,
            height=max_h,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
        )
        self._show_overlay(card)

    def _remove_overlay(self):
        o = getattr(self, '_active_overlay', None)
        if o and o in self.page.controls:
            self.page.remove(o)
            self._active_overlay = None
            self.page.update()

    def _show_overlay(self, card):
        dim = ft.Colors.with_opacity(0.5 if self.theme.get("is_dark") else 0.25, "#000")
        overlay = ft.Container(
            content=card, bgcolor=dim,
            alignment=ft.Alignment(0, 0), expand=True,
            on_click=lambda e: self._remove_overlay(),
        )
        self.page.add(overlay)
        self._active_overlay = overlay
        self.page.update()

    # ── Image Upload ─────────────────────────────────────────────

    async def _do_update_item_image(self, url, etype, eid):
        if self.is_guest:
            if etype == "food":
                mock_data.update_food(eid, {"Image_Path": url})
            else:
                mock_data.update_ingredient(eid, {"Image_Path": url})
        else:
            ep = f"/admin/food-items/{eid}/image" if etype == "food" else f"/admin/ingredients/{eid}/image"
            async with httpx.AsyncClient() as client:
                await client.patch(f"{BASE_URL}{ep}", json={"Image_Path": url}, params={"email": self.email}, headers=_api_headers(), timeout=10)
        self._snack("Image updated")
        await self._safe_render(self.RENDERERS[self.section_idx["v"]], self.content)

    def _upload_img_btn(self, etype, eid):
        return ft.IconButton(
            icon=ft.Icons.UPLOAD_FILE_ROUNDED, icon_size=16,
            icon_color=self._clr("accent"), tooltip="Change photo",
            on_click=lambda e: asyncio.create_task(self._trigger_upload(etype, eid)),
        )

    async def _trigger_upload(self, etype, eid):
        token = uuid.uuid4().hex
        upload_url = f"{PUBLIC_BACKEND_URL}/upload-ui?token={token}"
        status_text = ft.Text("", size=12, color=self._clr("sub"))
        async def check(_):
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{BASE_URL}/upload-status/{token}", timeout=10)
                    data = r.json()
                if data.get("status") == "done":
                    status_text.value = "Complete!"
                    status_text.color = ft.Colors.GREEN
                    dlg.open = False
                    self.page.update()
                    await self._do_update_item_image(data.get("url", ""), etype, eid)
                elif data.get("status") == "pending":
                    status_text.value = "Not yet uploaded. Open the link, upload, then Check."
                    status_text.color = ft.Colors.AMBER
                    self.page.update()
                else:
                    status_text.value = "Unexpected response from server. Please ensure the backend is updated and try again."
                    status_text.color = ft.Colors.RED
                    self.page.update()
            except Exception as ex:
                status_text.value = f"Error: {ex}"
                self.page.update()
        def close(_):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            title=ft.Text("Upload Image", color=self._clr("text")),
            content=ft.Column([
                ft.Text("Open the link in a new tab, upload your image, then click Check:", size=13, color=self._clr("text")),
                ft.TextField(value=upload_url, read_only=True, expand=True),
                ft.ElevatedButton("Check Upload", on_click=check, style=ft.ButtonStyle(bgcolor=self._clr("accent"), color="#FFF")),
                status_text,
            ], tight=True, spacing=10, width=380),
            actions=[ft.TextButton("Cancel", on_click=close)],
        )
        self.page.show_dialog(dlg)

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

    def _is_mobile(self):
        return (self.page.width or 1200) < 720

    def _sidebar(self, on_select):
        mobile = self._is_mobile()
        items = []
        for i, (label, icon) in enumerate(self.SECTIONS):
            sel = self.section_idx["v"] == i
            items.append(ft.Container(
                content=ft.Icon(icon, size=20, color=self._clr("accent") if sel else self._clr("sub")),
                bgcolor=ft.Colors.with_opacity(0.12, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda e, idx=i: on_select(idx),
                tooltip=label,
            ) if mobile else ft.Container(
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
        if mobile:
            return ft.Container(
                content=ft.Row(items, scroll=ft.ScrollMode.AUTO, spacing=6),
                bgcolor=self._clr("card"), border_radius=14,
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                visible=False,
            )
        return ft.Container(
            content=ft.Column(items, spacing=4),
            bgcolor=self._clr("card"), border_radius=16,
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            width=170,
        )

    def _bottom_nav(self, on_select):
        items = []
        for i, (label, icon) in enumerate(self.SECTIONS):
            sel = self.section_idx["v"] == i
            items.append(ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(icon, size=20,
                            color=self._clr("accent") if sel else self._clr("sub")),
                        width=40, height=40,
                        bgcolor=ft.Colors.with_opacity(0.12, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                        border_radius=12, alignment=ft.Alignment(0, 0),
                        animate=ft.Animation(200, "easeOut"),
                    ),
                    ft.Text(label, size=8,
                        color=self._clr("accent") if sel else self._clr("sub"),
                        font_family="DM Sans", weight="bold" if sel else "normal"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                on_click=lambda e, idx=i: on_select(idx),
                tooltip=label,
            ))
        return ft.Container(
            content=ft.Row(items, scroll=ft.ScrollMode.AUTO, spacing=4,
                           alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=self._clr("card"), border_radius=24,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            margin=ft.Margin.only(bottom=12),
        )

    # ── SECTION: Menu ──────────────────────────────────────────

    async def _render_menu(self, ref):
        ref.content = self._loading(); self.page.update()
        items = mock_data.get_weekly_menu() if self.is_guest else (await _req("/menu/weekly", {"email": self.email})) or []
        m_colors = {"Breakfast": self._clr("warn"), "Lunch": self._clr("success"), "Dinner": self._clr("accent2")}

        food_map = {}
        if self.is_guest:
            for f in mock_data.get_food_costs():
                food_map[f.get("Item_ID")] = f
        else:
            food_list = await _req("/admin/food/costs", {"email": self.email}) or []
            for f in (food_list if isinstance(food_list, list) else []):
                food_map[f.get("Item_ID")] = f

        rows = []
        for item in ((items if isinstance(items, list) else []) if items else (items.get("menu", []) if isinstance(items, dict) else [])):
            if not isinstance(item, dict): continue
            mt = item.get("meal_type", "")
            iid = item.get("Item_ID")
            food_info = food_map.get(iid, {})
            enriched = {**item, "Image_Path": food_info.get("Image_Path", ""), "Price": food_info.get("Price", 0)}
            rows.append(self._row_card([
                self._food_thumb(enriched, 36),
                ft.Container(
                    content=ft.Text(mt[:1], size=10, weight="bold", color=m_colors.get(mt, self._clr("accent"))),
                    width=26, height=26,
                    bgcolor=ft.Colors.with_opacity(0.12, m_colors.get(mt, self._clr("accent"))),
                    border_radius=6, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(item.get("Name") or item.get("Food_Item_Name", "?"), size=13,
                            weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{item.get('Date','')} \u2022 {mt}", size=11,
                            color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
            ], on_click=lambda e, it=enriched: self._show_food_detail(it)))
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
            price = item.get("Price", 0)
            label = f"{name} | {item.get('Item_ID','')}"
            food_rows.controls.append(self._row_card([
                self._food_thumb(item, 44),
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"PKR {price:.0f}", size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"PKR {price}", size=12, weight="bold", color=self._clr("accent"), font_family="DM Sans"),
            ], data=label, on_click=lambda e, it=item: self._show_food_detail(it)))

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
                    self._ing_thumb(i, 36),
                    ft.Text(i.get("Name", ""), size=13, weight="bold", color=self._clr("text"), font_family="DM Sans", expand=True),
                ft.Text(f"Qty: {i.get('Total_Quantity', 0)} {i.get('Unit', '')}",
                        size=12, color=self._clr("danger"), font_family="DM Sans"),
                ], data=i.get("Name"), on_click=lambda e, it=i: self._show_ingredient_detail(it)) for i in low_stock]
            )

        rows = ft.Column(spacing=4)
        for i in (ingredients if isinstance(ingredients, list) else []):
            rows.controls.append(self._row_card([
                self._ing_thumb(i, 44),
                ft.Column([
                    ft.Text(i.get("Name", ""), size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{i.get('Total_Quantity', 0)} {i.get('Unit', '')}", size=12,
                            color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"PKR {i.get('Unit_cost', 0)}/{i.get('Unit', '')}", size=11,
                        color=self._clr("sub"), font_family="DM Sans"),
            ], on_click=lambda e, it=i: self._show_ingredient_detail(it)))

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
        raw = (mock_data.get_recipes_detailed() if self.is_guest
               else (await _req("/recipes/detailed", {"email": self.email})) or [])

        grouped = {}
        for r in (raw if isinstance(raw, list) else []):
            iid = r.get("Item_ID")
            grouped.setdefault(iid, {"Item_ID": iid, "Item_Name": r.get("Item_Name", f"Item #{iid}"),
                                     "Item_Image": r.get("Item_Image", ""), "Price": r.get("Price", 0),
                                     "Ratings_Average": r.get("Ratings_Average", 0), "ingredients": []})
            grouped[iid]["ingredients"].append(r)

        rows = ft.Column(spacing=6)

        for g in grouped.values():
            def make_handler(g_data):
                async def handler(e):
                    dlg = self._recipe_popup(g_data)
                    self._recipe_dlg = dlg
                    self.page.open(dlg)
                return handler
            card = self._row_card([
                ft.Container(
                    ft.Image(src=g.get("Item_Image", ""), width=48, height=48,
                             fit="cover", border_radius=8,
                             error_content=ft.Icon(ft.Icons.RESTAURANT_MENU, size=24, color=self._clr("sub"))),
                    width=48, height=48, border_radius=8,
                    shadow=ft.BoxShadow(blur_radius=3, color="#00000020"),
                ),
                ft.Column([
                    ft.Text(g["Item_Name"], size=14, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{len(g['ingredients'])} ingredient{'s' if len(g['ingredients']) != 1 else ''}  •  Rs. {g['Price']:.0f}",
                            size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
            ], on_click=make_handler(g))
            rows.controls.append(card)

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Recipes", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=8),
            rows if rows.controls else ft.Text("No recipes", color=self._clr("sub")),
        ], alignment=ft.MainAxisAlignment.START, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    def _recipe_popup(self, g):
        item_id = g["Item_ID"]
        title = ft.Text(g["Item_Name"], size=20, weight="bold", color="#1a1a2e", font_family="DM Sans")
        status_text = ft.Text("", size=11, color=self._clr("success"), font_family="DM Sans")

        price_rating = ft.Row([
            ft.Text(f"Price: Rs. {g['Price']:.0f}", size=13, color="#555", font_family="DM Sans"),
            ft.Text(f"★ {g['Ratings_Average']:.1f}", size=13, color="#e67e22", font_family="DM Sans"),
        ], spacing=12)

        ing_rows = ft.Column(spacing=6)

        def build_ing_rows():
            ing_rows.controls.clear()
            for ing in g["ingredients"]:
                i_ing_id = ing.get("Ingredient_ID")
                def make_edit_handler(iid=i_ing_id, ing=ing):
                    async def h(e):
                        await self._edit_recipe_ingredient(g, iid, ing, build_ing_rows, status_text)
                    return h
                def make_del_handler(iid=i_ing_id):
                    async def h(e):
                        await self._delete_recipe_ingredient(g, iid, build_ing_rows, status_text)
                    return h
                ing_rows.controls.append(
                    ft.Container(
                        ft.Row([
                            ft.Container(
                                ft.Image(src=ing.get("Ingredient_Image", ""),
                                         width=36, height=36, fit="cover",
                                         border_radius=6, error_content=ft.Icon(ft.Icons.RESTAURANT, size=20)),
                                width=36, height=36, border_radius=6,
                                shadow=ft.BoxShadow(blur_radius=2, color="#00000020"),
                            ),
                            ft.Column([
                                ft.Text(ing.get("Ingredient_Name", ""), size=13, weight="bold",
                                        color="#1a1a2e", font_family="DM Sans"),
                                ft.Text(f"{ing.get('Ingredient_Quantity', 0)} {ing.get('Unit', '')}  "
                                        f"(Stock: {ing.get('Ingredient_Stock', 0)} {ing.get('Unit', '')})",
                                        size=11, color="#777", font_family="DM Sans"),
                            ], spacing=1, expand=True),
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_size=18, icon_color="#3B82F6",
                                          on_click=make_edit_handler(i_ing_id, ing)),
                            ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_size=18, icon_color="#EF4444",
                                          on_click=make_del_handler(i_ing_id)),
                        ]),
                        padding=8, border_radius=8,
                        bgcolor="#f0f0f5",
                    )
                )
            self.page.update()

        build_ing_rows()

        async def add_ingredient(e):
            from .api_client import get_headers as _gh
            ings_raw = mock_data.get_ingredients() if self.is_guest else (await _req("/analytics/ingredients", {"email": self.email})) or []
            ing_items = []
            qty_field = ft.TextField(hint_text="Qty", dense=True, width=80,
                text_align=ft.TextAlign.CENTER,
                border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=6,
                text_style=ft.TextStyle(size=12, font_family="DM Sans"),
                filled=True, fill_color="#f0f0f5")
            sel_dd = ft.Dropdown(dense=True, expand=True, options=[], label="Select Ingredient")

            for ing_ in (ings_raw if isinstance(ings_raw, list) else []):
                iid_ = ing_.get("Ingredient_ID")
                nm_ = ing_.get("Name", "")
                sel_dd.options.append(ft.dropdown.Option(str(iid_), f"{nm_} ({ing_.get('Unit','')})"))
                ing_items.append(ing_)

            async def save_new():
                sel_val = sel_dd.value
                qty_val = (qty_field.value or "").strip()
                if not sel_val or not qty_val:
                    status_text.value = "Select ingredient and quantity"; status_text.color = self._clr("danger"); self.page.update(); return
                try:
                    qty = float(qty_val)
                    if qty <= 0: raise ValueError
                except ValueError:
                    status_text.value = "Invalid quantity"; status_text.color = self._clr("danger"); self.page.update(); return
                ing_id = int(sel_val)
                sel_ing = next((x for x in ing_items if x.get("Ingredient_ID") == ing_id), {})
                if self.is_guest:
                    g["ingredients"].append({"Ingredient_ID": ing_id, "Ingredient_Name": sel_ing.get("Name",""),
                        "Ingredient_Image": sel_ing.get("Image_Path",""), "Unit": sel_ing.get("Unit",""),
                        "Ingredient_Quantity": qty, "Ingredient_Stock": sel_ing.get("Total_Quantity", 0)})
                else:
                    ep = f"/admin/add-recipe/{item_id}/{ing_id}/{qty}"
                    r = await _req("POST", ep, {"email": self.email})
                    if isinstance(r, dict) and "error" in r:
                        status_text.value = f"Error: {r['error']}"; status_text.color = self._clr("danger"); self.page.update(); return
                build_ing_rows()
                status_text.value = "Ingredient added"; status_text.color = self._clr("success")
                self.page.close(add_dlg)

            add_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Add Ingredient", size=16, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                content=ft.Column([sel_dd, qty_field, ft.Container(height=8)], width=300, tight=True),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self.page.close(add_dlg)),
                    ft.FilledButton("Add", style=ft.ButtonStyle(bgcolor=self._clr("accent"), color="#FFF"),
                                    on_click=lambda e: asyncio.ensure_future(save_new())),
                ],
            )
            self.page.open(add_dlg)

        ing_header_row = ft.Row([
            ft.Text("Ingredients", size=15, weight="bold", color="#1a1a2e", font_family="DM Sans", expand=True),
            ft.IconButton(ft.Icons.ADD_CIRCLE_ROUNDED, icon_size=20, icon_color=self._clr("accent"),
                          tooltip="Add Ingredient", on_click=lambda e: asyncio.ensure_future(add_ingredient(e))),
        ])

        body = ft.Column([
            title,
            ft.Container(height=6),
            price_rating,
            ft.Divider(height=16, color="#ddd"),
            ing_header_row,
            ft.Container(height=6),
            status_text,
            ing_rows,
        ], spacing=2, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        content = ft.Container(
            ft.Column([
                ft.Container(
                    ft.Image(src=g.get("Item_Image", ""), width=None, height=180,
                             fit="cover", border_radius=ft.BorderRadius(12, 12, 0, 0),
                             error_content=ft.Container(
                                 ft.Icon(ft.Icons.RESTAURANT_MENU, size=64, color="#bbb"),
                                 height=180, alignment=ft.Alignment(0, 0))),
                    border_radius=ft.BorderRadius(12, 12, 0, 0), clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                ft.Container(body, padding=16, expand=True),
            ], spacing=0, expand=True),
            width=420, border_radius=12,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000040"),
        )

        return ft.AlertDialog(
            content=content,
            actions=[ft.TextButton("Close", on_click=lambda e: self.page.close(self._recipe_dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(12),
        )

    async def _edit_recipe_ingredient(self, g, ing_id, ing_data, rebuild, status_text):
        item_id = g["Item_ID"]
        qty_field = ft.TextField(value=str(ing_data.get("Ingredient_Quantity", 0)), dense=True, width=120,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")), border_radius=6,
            text_style=ft.TextStyle(size=13, font_family="DM Sans"),
            filled=True, fill_color="#f0f0f5")

        async def save_edit():
            val = (qty_field.value or "").strip()
            try:
                qty = float(val)
                if qty <= 0: raise ValueError
            except ValueError:
                status_text.value = "Invalid quantity"; status_text.color = self._clr("danger"); self.page.update(); return
            if self.is_guest:
                for ing in g["ingredients"]:
                    if ing.get("Ingredient_ID") == ing_id:
                        ing["Ingredient_Quantity"] = qty; break
            else:
                ep = f"/admin/recipe/update/{item_id}/{ing_id}"
                r = await _req("PATCH", ep, {"email": self.email}, {"Ingredient_Quantity": qty})
                if isinstance(r, dict) and "error" in r:
                    status_text.value = f"Error: {r['error']}"; status_text.color = self._clr("danger"); self.page.update(); return
            rebuild()
            status_text.value = "Updated"; status_text.color = self._clr("success")
            self.page.close(edit_dlg)

        edit_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {ing_data.get('Ingredient_Name','')}", size=16, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            content=ft.Column([ft.Text("Quantity:", size=12, color=self._clr("sub"), font_family="DM Sans"), qty_field], width=280, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(edit_dlg)),
                ft.FilledButton("Update", style=ft.ButtonStyle(bgcolor=self._clr("accent"), color="#FFF"),
                                on_click=lambda e: asyncio.ensure_future(save_edit())),
            ],
        )
        self.page.open(edit_dlg)

    async def _delete_recipe_ingredient(self, g, ing_id, rebuild, status_text):
        item_id = g["Item_ID"]

        async def confirm_delete():
            if self.is_guest:
                g["ingredients"] = [ing for ing in g["ingredients"] if ing.get("Ingredient_ID") != ing_id]
            else:
                ep = f"/admin/recipe/{item_id}/{ing_id}"
                r = await _req("DELETE", ep, {"email": self.email})
                if isinstance(r, dict) and "error" in r:
                    status_text.value = f"Error: {r['error']}"; status_text.color = self._clr("danger"); self.page.update(); return
            rebuild()
            status_text.value = "Deleted"; status_text.color = self._clr("success")
            self.page.close(del_dlg)

        del_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete", size=16, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            content=ft.Text("Remove this ingredient from the recipe?", size=13, color=self._clr("sub"), font_family="DM Sans"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(del_dlg)),
                ft.FilledButton("Delete", style=ft.ButtonStyle(bgcolor="#EF4444", color="#FFF"),
                                on_click=lambda e: asyncio.ensure_future(confirm_delete())),
            ],
        )
        self.page.open(del_dlg)

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
        mobile = self._is_mobile()

        def select_section(idx):
            self.section_idx["v"] = idx
            if not mobile:
                sidebar.controls[0] = self._sidebar(select_section)
            else:
                bn.controls[0] = self._bottom_nav(select_section)
            self.content.opacity = 0
            self.page.update()
            async def _do():
                await asyncio.sleep(0.05)
                await self._safe_render(self.RENDERERS[idx], self.content)
                self.content.opacity = 1
                self.page.update()
            asyncio.create_task(_do())

        if mobile:
            sidebar = ft.Column([self._sidebar(select_section)])
            bn = ft.Column([self._bottom_nav(select_section)])
            layout = ft.Column([
                ft.Container(content=self.content, expand=True,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8)),
                bn,
            ], expand=True, spacing=6)
        else:
            sidebar = ft.Column([self._sidebar(select_section)])
            layout = ft.Row([
                sidebar,
                ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, self._clr("text"))),
                ft.Container(content=self.content, expand=True,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
            ], expand=True, spacing=0)

        asyncio.create_task(self._safe_render("_render_menu", self.content))

        hp = 12 if mobile else 20
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Staff", size=20 if mobile else 24, weight="bold",
                            font_family="DM Sans", color=self._clr("text")),
                    self._chip("Staff", self._clr("accent2"), ft.Colors.with_opacity(0.12, self._clr("accent2"))),
                ], spacing=12),
                ft.Container(height=4 if mobile else 8),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=hp, vertical=12 if mobile else 16),
        )
