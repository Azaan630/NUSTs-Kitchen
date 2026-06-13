import flet as ft
import asyncio
import httpx
import os
import uuid
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
        name = item.get("Name", "Unknown")
        price = item.get("Price", 0)
        cost = item.get("Estimated_Cost", 0)
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
            ft.Text("Estimated Cost", size=11, color=sub, font_family="DM Sans", expand=1),
            ft.Text(f"Rs. {cost:,.2f}", size=13, color=txt, font_family="DM Sans", expand=2),
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

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Food Details", size=18, weight="bold",
                            color=txt, font_family="DM Sans", expand=True),
                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=sub,
                                  on_click=lambda e: asyncio.create_task(self._remove_overlay())),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *rows,
            ], tight=True, spacing=8),
            bgcolor=card_bg, border_radius=18, padding=24, width=420,
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

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Ingredient Details", size=18, weight="bold",
                            color=txt, font_family="DM Sans", expand=True),
                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=sub,
                                  on_click=lambda e: asyncio.create_task(self._remove_overlay())),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                *rows,
            ], tight=True, spacing=8),
            bgcolor=card_bg, border_radius=18, padding=24, width=420,
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
                await client.patch(f"{BASE_URL}{ep}", json={"Image_Path": url}, params={"email": self.email}, timeout=10)
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
                self._food_thumb(item, 44),
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"Cost: PKR {cost:.0f}", size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"PKR {price}", size=12, weight="bold", color=self._clr("accent"), font_family="DM Sans"),
                self._upload_img_btn("food", item.get('Item_ID')),
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
                    self._upload_img_btn("ing", i.get('Ingredient_ID')),
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
                self._upload_img_btn("ing", i.get('Ingredient_ID')),
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
