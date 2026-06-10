import flet as ft
import asyncio
import httpx
import os
from datetime import date
import mock_data

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


# API helpers (admin-scoped)

async def _req(method: str, endpoint: str, params=None, json_data=None):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}{endpoint}"
            kw = dict(params=params, timeout=10.0)
            if method == "GET":
                r = await client.get(url, **kw)
            elif method == "POST":
                r = await client.post(url, json=json_data, **kw)
            elif method == "PATCH":
                r = await client.patch(url, json=json_data, **kw)
            elif method == "DELETE":
                r = await client.delete(url, **kw)
            else:
                return {"error": "bad method"}
            r.raise_for_status()
            return r.json() if r.status_code != 204 else {}
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
            return {"error": f"({e.response.status_code}) {detail}"}
        except Exception as ex:
            return {"error": str(ex)}


async def api_get_all_students(email): return await _req("GET", "/admin/students/all", {"email": email})
async def api_register_student(email, data): return await _req("POST", "/admin/students/register", {"email": email}, data)
async def api_update_student(email, uid, data): return await _req("PATCH", f"/admin/students/update/{uid}", {"email": email}, data)
async def api_delete_student(email, uid): return await _req("DELETE", f"/admin/students/delete/{uid}", {"email": email})

async def api_get_all_users(email): return await _req("GET", "/admin/students/all", {"email": email})
async def api_register_staff(email, data): return await _req("POST", "/admin/staff/register", {"email": email}, data)
async def api_update_staff(email, uid, data): return await _req("POST", f"/admin/staff/update", {"email": email, "UserID": uid}, data)
async def api_delete_staff(email, uid): return await _req("DELETE", f"/admin/staff/delete/{uid}", {"email": email})

async def api_get_food_costs(email): return await _req("GET", "/admin/food/costs", {"email": email})
async def api_create_food(email, data): return await _req("POST", "/admin/food_items/create", {"email": email}, data)
async def api_update_food(email, iid, data): return await _req("PATCH", f"/admin/food_items/update/{iid}", {"email": email}, data)
async def api_delete_food(email, iid): return await _req("DELETE", f"/admin/food_items/delete/{iid}", {"email": email})

async def api_get_mess_off_history(email): return await _req("GET", "/student/mess-off/history", {"email": email})
async def api_approve_mess_off(email, rid): return await _req("POST", f"/admin/mess-off/approve/{rid}", {"email": email})
async def api_reject_mess_off(email, rid):
    return await _req("DELETE", f"/student/mess_off/cancel/{rid}", {"email": email})

async def api_get_monthly_bills(email): return await _req("GET", "/admin/monthly_billing_summary", {"email": email})
async def api_create_bill(email, data): return await _req("POST", "/admin/bills/create", {"email": email}, data)
async def api_update_bill(email, bid, data): return await _req("PATCH", f"/admin/bills/update/{bid}", {"email": email}, data)
async def api_delete_bill(email, bid): return await _req("DELETE", f"/admin/bills/delete/{bid}", {"email": email})

async def api_get_weekly_menu(email): return await _req("GET", "/menu/weekly", {"email": email})
async def api_add_menu_item(email, item_id, menu_date, meal_type):
    return await _req("POST", f"/admin/menu_schedule/{item_id}/{menu_date}/{meal_type}", {"email": email})
async def api_delete_menu_item(email, item_id, schedule_id):
    return await _req("DELETE", f"/admin/menu_schedule/{item_id}/{schedule_id}", {"email": email})

async def api_start_poll(email, data):
    # Pass email in params, and the actual poll data in the JSON body
    return await _req("POST", "/admin/poll/start", params={"email": email}, json_data=data)

async def api_get_poll_results(email):
    return await _req("GET", "/admin/poll/results", {"email": email})


class AdminPage:
    """Full admin dashboard — students, staff, food, mess-off, bills, menu."""

    TABS = [
        ("Students",  ft.Icons.PEOPLE_ROUNDED),
        ("Staff",     ft.Icons.BADGE_ROUNDED),
        ("Food Items",ft.Icons.FASTFOOD_ROUNDED),
        ("Mess Off",  ft.Icons.EVENT_BUSY_ROUNDED),
        ("Bills",     ft.Icons.RECEIPT_LONG_ROUNDED),
        ("Menu",      ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Polls", ft.Icons.POLL_ROUNDED),
    ]

    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.bg     = t["DARK_BG"]   if t["is_dark"] else t["CREAM"]
        self.card   = t["DARK_CARD"] if t["is_dark"] else t["WHITE"]
        self.card2  = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt    = t["WHITE"]     if t["is_dark"] else t["NAVY"]
        self.sub    = t["GREY"]
        self.amber  = t["AMBER"]
        self.navy   = t["NAVY"]

        self._tab   = {"v": 0}
        self.main   = ft.Container(expand=True)

    # ── Generic UI helpers

    def _loading(self, msg="Loading…"):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.amber, width=36, height=36, stroke_width=3),
                ft.Text(msg, color=self.sub, font_family="DM Sans", size=13),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
            alignment=ft.Alignment(0, 0), expand=True, padding=50,
        )

    def _snack(self, msg, ok=True):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#FFF"),
            bgcolor="#10B981" if ok else "#EF4444",
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _section_title(self, txt):
        return ft.Text(txt, size=16, weight="bold", color=self.txt, font_family="DM Sans")

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

    def _field(self, label, hint="", password=False):
        return ft.TextField(
            label=label, hint_text=hint, password=password,
            border_color=self.amber, focused_border_color=self.amber,
            label_style=ft.TextStyle(color=self.sub, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self.txt, font_family="DM Sans"),
            border_radius=10, filled=True, fill_color=self.card,
        )

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

    def _fab(self, label, icon, cb):
        return ft.FilledButton(
            content=ft.Row([
                ft.Icon(icon, size=16, color=self.navy),
                ft.Text(label, size=12, weight="bold", color=self.navy, font_family="DM Sans"),
            ], spacing=6, tight=True),
            on_click=cb,
            style=ft.ButtonStyle(
                bgcolor=self.amber, elevation=0,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            ),
        )

    def _row_card(self, controls, actions=None):
        row_ctrls = list(controls)
        if actions:
            row_ctrls.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row_ctrls, spacing=12),
            bgcolor=self.card, border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=8),
            shadow=ft.BoxShadow(blur_radius=8,
                                color=ft.Colors.with_opacity(0.05, "#000"),
                                offset=ft.Offset(0, 2)),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, "#000")),
        )

    # ── Tab sidebar ─────────────────────────────────────────────────────────

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
            width=170,
            shadow=ft.BoxShadow(blur_radius=16,
                                color=ft.Colors.with_opacity(0.07, "#000"),
                                offset=ft.Offset(0, 2)),
        )

    # ════════════════════════════════════════════════════════════════════════
    #  TAB 0 — STUDENTS
    # ════════════════════════════════════════════════════════════════════════

    async def _render_students(self, content_ref):
        content_ref.content = self._loading("Fetching students…")
        self.page.update()

        if self.is_guest:
            students = mock_data.get_students()
            data = students
        else:
            data = await api_get_all_students(self.email)
            students = [u for u in (data if isinstance(data, list) else [])
                        if u.get("Account_Type") == "Student"]

        # ── Add-student form
        f_fn   = self._field("First Name")
        f_ln   = self._field("Last Name")
        f_em   = self._field("Email", "student@seecs.edu.pk")
        f_dob  = self._field("Date of Birth", "YYYY-MM-DD")
        f_dept = self._field("Department")
        f_con  = self._field("Contact")
        f_addr = self._field("Address")
        f_fath = self._field("Father Name")
        f_host = self._field("Hostel")
        f_room = self._field("Room No.")

        async def add_student(e):
            payload = {
                "First_Name": f_fn.value, "Last_Name": f_ln.value,
                "Email": f_em.value, "DoB": f_dob.value,
                "Department": f_dept.value, "Contact_Number": f_con.value,
                "Address": f_addr.value, "Father_Name": f_fath.value,
                "Hostel_Name": f_host.value, "Room_Number": f_room.value,
            }
            if self.is_guest:
                mock_data.register_student(payload)
                ok = True
            else:
                res = await api_register_student(self.email, payload)
                ok = "error" not in (res or {})
            self._snack("Student registered!" if ok else (res or {}).get("error", "Error"), ok)
            if ok:
                await self._render_students(content_ref)

        form = ft.Container(
            content=ft.Column([
                self._section_title("Register New Student"),
                ft.Row([f_fn, f_ln, f_em], spacing=8),
                ft.Row([f_dob, f_dept, f_con], spacing=8),
                ft.Row([f_addr, f_fath], spacing=8),
                ft.Row([f_host, f_room], spacing=8),
                ft.Row([self._fab("Register", ft.Icons.PERSON_ADD_ROUNDED, add_student)],
                       alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            bgcolor=self.card2, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=16),
        )

        # ── Student list ────────────────────────────────────────────────────
        rows = []
        for s in students:
            uid = s.get("UserID")

            async def do_del(e, u=uid):
                if self.is_guest:
                    mock_data.delete_student(u)
                    ok = True
                else:
                    res = await api_delete_student(self.email, u)
                    ok = "error" not in (res or {})
                self._snack("Deleted." if ok else "Error", ok)
                if ok: await self._render_students(content_ref)

            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"{s.get('First_Name','')} {s.get('Last_Name','')}",
                            size=13, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text(s.get("Email",""), size=11, color=self.sub, font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"ID #{uid}", size=11, color=self.sub, font_family="DM Sans"),
            ], actions=[
                self._icon_btn(ft.Icons.DELETE_ROUNDED, "#EF4444", "Delete", do_del),
            ]))

        list_section = ft.Column([
            ft.Row([
                self._section_title(f"All Students ({len(students)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_students(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No students found.", color=self.sub, font_family="DM Sans"),
        ])

        content_ref.content = ft.Column([self._guest_banner(), form, list_section],
                                        scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()



    async def _render_staff(self, content_ref):
        content_ref.content = self._loading("Fetching staff…")
        self.page.update()

        if self.is_guest:
            staff_list = mock_data.get_staff()
        else:
            data = await api_get_all_users(self.email)
            staff_list = [u for u in (data if isinstance(data, list) else [])
                          if u.get("Account_Type") == "Staff"]

        f_fn  = self._field("First Name")
        f_ln  = self._field("Last Name")
        f_em  = self._field("Email")
        f_cat = self._field("Category", "e.g. Cook")

        async def add_staff(e):
            payload = {
                "First_Name": f_fn.value, "Last_Name": f_ln.value,
                "Email": f_em.value, "Category": f_cat.value,
            }
            if self.is_guest:
                mock_data.register_staff(payload)
                ok = True
            else:
                res = await api_register_staff(self.email, payload)
                ok = "error" not in (res or {})
            self._snack("Staff registered!" if ok else "Error", ok)
            if ok: await self._render_staff(content_ref)

        form = ft.Container(
            content=ft.Column([
                self._section_title("Register New Staff"),
                ft.Row([f_fn, f_ln, f_em, f_cat], spacing=8),
                ft.Row([self._fab("Register", ft.Icons.PERSON_ADD_ROUNDED, add_staff)],
                       alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            bgcolor=self.card2, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=16),
        )

        rows = []
        for s in staff_list:
            uid = s.get("UserID")

            async def do_del(e, u=uid):
                if self.is_guest:
                    mock_data.delete_staff(u)
                    ok = True
                else:
                    res = await api_delete_staff(self.email, u)
                    ok = "error" not in (res or {})
                self._snack("Deleted." if ok else "Error", ok)
                if ok: await self._render_staff(content_ref)

            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"{s.get('First_Name','')} {s.get('Last_Name','')}",
                            size=13, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text(s.get("Email",""), size=11, color=self.sub, font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"ID #{uid}", size=11, color=self.sub, font_family="DM Sans"),
            ], actions=[
                self._icon_btn(ft.Icons.DELETE_ROUNDED, "#EF4444", "Delete", do_del),
            ]))

        list_section = ft.Column([
            ft.Row([
                self._section_title(f"All Staff ({len(staff_list)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_staff(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No staff found.", color=self.sub, font_family="DM Sans"),
        ])

        content_ref.content = ft.Column([self._guest_banner(), form, list_section],
                                        scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()


    #  TAB 2 — FOOD ITEMS

    async def _render_food(self, content_ref):
        content_ref.content = self._loading("Fetching food items…")
        self.page.update()

        if self.is_guest:
            items = mock_data.get_food_costs()
        else:
            data = await api_get_food_costs(self.email)
            items = data if isinstance(data, list) else []

        f_name = self._field("Name")
        f_qty  = self._field("Quantity", "1.0")
        f_price= self._field("Price (PKR)", "0.00")

        async def add_food(e):
            payload = {
                "Name": f_name.value,
                "Quantity": float(f_qty.value or 0),
                "Price": float(f_price.value or 0),
            }
            if self.is_guest:
                mock_data.create_food(payload)
                ok = True
            else:
                res = await api_create_food(self.email, payload)
                ok = "error" not in (res or {})
            self._snack("Food item created!" if ok else "Error", ok)
            if ok: await self._render_food(content_ref)

        form = ft.Container(
            content=ft.Column([
                self._section_title("Add Food Item"),
                ft.Row([f_name, f_qty, f_price], spacing=8),
                ft.Row([self._fab("Add Item", ft.Icons.ADD_ROUNDED, add_food)],
                       alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            bgcolor=self.card2, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=16),
        )

        rows = []
        for item in items:
            iid  = item.get("Item_ID")
            cost = item.get("Estimated_Cost", 0)

            # Inline edit fields
            ef_name  = ft.TextField(value=item.get("Name",""),  expand=True,
                                    border_color=self.amber, border_radius=8,
                                    text_style=ft.TextStyle(color=self.txt, font_family="DM Sans"),
                                    filled=True, fill_color=self.card, dense=True)
            ef_price = ft.TextField(value=str(item.get("Price", "")), width=90,
                                    border_color=self.amber, border_radius=8,
                                    text_style=ft.TextStyle(color=self.txt, font_family="DM Sans"),
                                    filled=True, fill_color=self.card, dense=True)

            async def do_update(e, i=iid, nf=ef_name, pf=ef_price):
                payload = {"Name": nf.value, "Price": float(pf.value or 0)}
                if self.is_guest:
                    mock_data.update_food(i, payload)
                    ok = True
                else:
                    res = await api_update_food(self.email, i, payload)
                    ok = "error" not in (res or {})
                self._snack("Updated." if ok else "Error", ok)

            async def do_del(e, i=iid):
                if self.is_guest:
                    mock_data.delete_food(i)
                    ok = True
                else:
                    res = await api_delete_food(self.email, i)
                    ok = "error" not in (res or {})
                self._snack("Deleted." if ok else "Error", ok)
                if ok: await self._render_food(content_ref)

            rows.append(self._row_card([
                ef_name,
                ef_price,
                ft.Text(f"Cost: PKR {cost:.0f}", size=11, color=self.sub, font_family="DM Sans"),
            ], actions=[
                self._icon_btn(ft.Icons.SAVE_ROUNDED, self.amber, "Save", do_update),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, "#EF4444", "Delete", do_del),
            ]))

        list_section = ft.Column([
            ft.Row([
                self._section_title(f"Food Items ({len(items)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_food(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No food items.", color=self.sub, font_family="DM Sans"),
        ])

        content_ref.content = ft.Column([self._guest_banner(), form, list_section],
                                        scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()


    #  TAB 3 — MESS OFF REQUESTS


    async def _render_mess_off(self, content_ref):
        content_ref.content = self._loading("Fetching mess-off requests…")
        self.page.update()


        if self.is_guest:
            result = mock_data.get_mess_off_history()
            requests = result.get("status", [])
        else:
            result = await _req("GET", "/student/mess-off/history", {"email": self.email})
            requests = []
            if isinstance(result, dict) and "status" in result:
                requests = result["status"] if isinstance(result["status"], list) else []
            elif isinstance(result, list):
                requests = result

        STATUS_COLORS = {
            "Approved": ("#10B981", "#D1FAE5"),
            "Pending":  ("#F59E0B", "#FEF3C7"),
            "Rejected": ("#EF4444", "#FEE2E2"),
            "Cancelled":(self.sub, self.card2),
        }

        rows = []
        for req in requests:
            rid    = req.get("Mess_Off_ID")
            status = req.get("Status", "Pending")
            fg, bg = STATUS_COLORS.get(status, (self.sub, self.card2))

            actions = []
            if status == "Pending":
                async def do_approve(e, r=rid):
                    if self.is_guest:
                        mock_data.approve_mess_off(r)
                        ok = True
                    else:
                        res = await api_approve_mess_off(self.email, r)
                        ok = "error" not in (res or {})
                    self._snack("Approved!" if ok else "Error", ok)
                    if ok: await self._render_mess_off(content_ref)

                async def do_reject(e, r=rid):
                    if self.is_guest:
                        mock_data.reject_mess_off(r)
                        ok = True
                    else:
                        res = await api_reject_mess_off(self.email, r)
                        ok = "error" not in (res or {})
                    self._snack("Rejected." if ok else "Error", ok)
                    if ok: await self._render_mess_off(content_ref)

                actions = [
                    self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, "#10B981", "Approve", do_approve),
                    self._icon_btn(ft.Icons.CANCEL_ROUNDED,        "#EF4444", "Reject",  do_reject),
                ]

            rows.append(self._row_card([
                ft.Column([
                    ft.Text(
                        f"User #{req.get('User_ID','?')}  •  "
                        f"{req.get('Start_Date','?')} → {req.get('End_Date','?')}",
                        size=13, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text(f"Requested: {req.get('Request_Date','?')}  •  ID #{rid}",
                            size=11, color=self.sub, font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=actions))

        content_ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                self._section_title(f"Mess-Off Requests ({len(requests)})"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_mess_off(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No requests found.", color=self.sub, font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()


    #  TAB 4 — BILLS


    async def _render_bills(self, content_ref):
        content_ref.content = self._loading("Fetching billing data…")
        self.page.update()

        if self.is_guest:
            bills = mock_data.get_monthly_bills()
        else:
            data = await api_get_monthly_bills(self.email)
            bills = data if isinstance(data, list) else []

        # ── Create bill form ────────────────────────────────────────────────
        f_uid    = self._field("Student UserID")
        f_amount = self._field("Amount (PKR)")
        f_due    = self._field("Due Date", "YYYY-MM-DD")
        f_month  = self._field("Billing Month", "YYYY-MM-DD")

        async def add_bill(e):
            payload = {
                "UserID": int(f_uid.value or 0),
                "Issue_Date": date.today().isoformat(),
                "Amount": float(f_amount.value or 0),
                "Due_Date": f_due.value,
                "Month": f_month.value,
                "Status": "Unpaid",
            }
            if self.is_guest:
                mock_data.create_bill(payload)
                ok = True
            else:
                res = await api_create_bill(self.email, payload)
                ok = "error" not in (res or {})
            self._snack("Bill created!" if ok else "Error", ok)
            if ok: await self._render_bills(content_ref)

        form = ft.Container(
            content=ft.Column([
                self._section_title("Add Bill"),
                ft.Row([f_uid, f_amount, f_due, f_month], spacing=8),
                ft.Row([self._fab("Create Bill", ft.Icons.ADD_ROUNDED, add_bill)],
                       alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            bgcolor=self.card2, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=16),
        )

        STATUS_COLORS = {
            "Paid":    ("#10B981", "#D1FAE5"),
            "Unpaid":  ("#F59E0B", "#FEF3C7"),
            "Overdue": ("#EF4444", "#FEE2E2"),
        }

        rows = []
        for b in bills:
            uid    = b.get("User_ID")
            month  = b.get("Billing_Month","?")
            total  = b.get("Total_Amount", 0)
            paid   = b.get("Total_Collected", 0)
            outstanding = b.get("Outstanding", 0)

            status = "Paid" if outstanding <= 0 else "Unpaid"
            fg, bg = STATUS_COLORS.get(status, (self.sub, self.card2))

            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"User #{uid}  •  {month}",
                            size=13, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text(
                        f"Total: PKR {total:.0f}  |  Paid: PKR {paid:.0f}  |  Due: PKR {outstanding:.0f}",
                        size=11, color=self.sub, font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ]))

        list_section = ft.Column([
            ft.Row([
                self._section_title(f"Monthly Summary ({len(bills)} entries)"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_bills(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No billing data.", color=self.sub, font_family="DM Sans"),
        ])

        content_ref.content = ft.Column([self._guest_banner(), form, list_section],
                                        scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()


    #  TAB 5 — MENU


    async def _render_menu(self, content_ref):
        content_ref.content = self._loading("Fetching menu…")
        self.page.update()

        if self.is_guest:
            items = mock_data.get_weekly_menu()
        else:
            data = await api_get_weekly_menu(self.email)
            items = data if isinstance(data, list) else []

        # Add-to-menu form
        f_item_id   = self._field("Food Item ID")
        f_date      = self._field("Date", "YYYY-MM-DD")
        f_meal_type = self._field("Meal Type", "Breakfast / Lunch / Dinner")

        async def add_to_menu(e):
            if self.is_guest:
                mock_data.add_menu_item(
                    f_item_id.value.strip(),
                    f_date.value.strip(),
                    f_meal_type.value.strip(),
                )
                ok = True
            else:
                res = await api_add_menu_item(
                    self.email,
                    f_item_id.value.strip(),
                    f_date.value.strip(),
                    f_meal_type.value.strip(),
                )
                ok = "error" not in (res or {})
            self._snack("Added to menu!" if ok else "Error", ok)
            if ok: await self._render_menu(content_ref)

        form = ft.Container(
            content=ft.Column([
                self._section_title("Add Item to Menu"),
                ft.Row([f_item_id, f_date, f_meal_type], spacing=8),
                ft.Row([self._fab("Add to Menu", ft.Icons.ADD_ROUNDED, add_to_menu)],
                       alignment=ft.MainAxisAlignment.END),
            ], spacing=8),
            bgcolor=self.card2, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=16),
        )

        MEAL_COLORS = {
            "Breakfast": "#F59E0B",
            "Lunch":     "#10B981",
            "Dinner":    "#6366F1",
        }

        rows = []
        for item in items:
            iid  = item.get("Item_ID")
            sid  = item.get("Schedule_ID")
            name = item.get("Food_Item_Name","?")
            mt   = item.get("meal_type","")
            d    = item.get("Date","")
            mc   = MEAL_COLORS.get(mt, self.amber)

            async def do_del(e, i=iid, s=sid):
                if self.is_guest:
                    mock_data.delete_menu_item(i, s)
                    ok = True
                else:
                    res = await api_delete_menu_item(self.email, i, s)
                    ok = "error" not in (res or {})
                self._snack("Removed from menu." if ok else "Error", ok)
                if ok: await self._render_menu(content_ref)

            rows.append(self._row_card([
                ft.Container(
                    content=ft.Text(mt[:1], size=12, weight="bold", color=mc),
                    width=30, height=30,
                    bgcolor=ft.Colors.with_opacity(0.12, mc),
                    border_radius=8, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text(f"{d}  •  {mt}", size=11, color=self.sub, font_family="DM Sans"),
                ], expand=True, spacing=2),
                ft.Text(f"Sched #{sid}", size=10, color=self.sub, font_family="DM Sans"),
            ], actions=[
                self._icon_btn(ft.Icons.REMOVE_CIRCLE_ROUNDED, "#EF4444", "Remove", do_del),
            ]))

        list_section = ft.Column([
            ft.Row([
                self._section_title(f"Weekly Menu ({len(items)} slots)"),
                self._icon_btn(ft.Icons.REFRESH_ROUNDED, self.sub, "Refresh",
                               lambda e: asyncio.create_task(self._render_menu(content_ref))),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=6),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else
            ft.Text("No menu items.", color=self.sub, font_family="DM Sans"),
        ])

        content_ref.content = ft.Column([self._guest_banner(), form, list_section],
                                        scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    async def _render_polls(self, content_ref):
        content_ref.content = self._loading("Fetching poll data…")
        self.page.update()

        # 1. Fetch live results from backend
        if self.is_guest:
            res = mock_data.get_poll_results()
        else:
            res = await api_get_poll_results(self.email)
        poll_results = res.get("results", []) if isinstance(res, dict) else []

        # 2. Results Section UI
        result_cards = []
        for r in poll_results:
            result_cards.append(self._row_card([
                ft.Text(r.get("Name", "?"), expand=True, weight="bold", color=self.txt, font_family="DM Sans"),
                ft.Text(f"{r.get('Vote_Count', 0)} Votes", color=self.amber, weight="bold", font_family="DM Sans")
            ]))

        # 3. New Poll Form Fields
        f_meal = self._field("Meal Type", "e.g. Dinner")
        f_ids = self._field("Food Item IDs", "e.g. 102, 105")

        async def launch_poll(e):
            try:
                id_list = [int(i.strip()) for i in f_ids.value.split(",") if i.strip()]
                payload = {"meal_type": f_meal.value, "item_ids": id_list}

                if self.is_guest:
                    mock_data.start_poll(payload)
                    ok = True
                else:
                    resp = await api_start_poll(self.email, payload)
                    ok = "error" not in (resp or {})
                self._snack("Poll launched!" if ok else "Error", ok)

                if ok:  # Refresh to show the new (empty) results list
                    await self._render_polls(content_ref)
            except:
                self._snack("IDs must be numbers separated by commas", False)

        # 4. Final Assembly
        content_ref.content = ft.Column([
            self._guest_banner(),
            self._section_title("Live Poll Standings"),
            ft.Column(result_cards) if result_cards else ft.Text("No active poll results found.", color=self.sub),

            ft.Container(height=20),  # Spacer

            self._section_title("Launch New Poll"),
            ft.Container(
                content=ft.Column([
                    ft.Text("This will replace the current active poll.", size=12, color=self.sub),
                    ft.Row([f_meal, f_ids], spacing=8),
                    ft.Row([self._fab("Start Poll", ft.Icons.HOW_TO_VOTE, launch_poll)],
                           alignment=ft.MainAxisAlignment.END),
                ], spacing=12),
                bgcolor=self.card2, border_radius=14, padding=16
            )
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()

    # Tab dispatcher

    RENDERERS = [
        "_render_students",
        "_render_staff",
        "_render_food",
        "_render_mess_off",
        "_render_bills",
        "_render_menu",
        "_render_polls"
    ]

    # Build

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
        asyncio.create_task(self._render_students(content_ref))

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Admin Dashboard", size=26, weight="bold",
                            font_family="DM Sans", color=self.txt),
                    self._chip("Admin", self.amber, ft.Colors.with_opacity(0.12, self.amber)),
                ], spacing=12),
                ft.Container(height=12),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            bgcolor=self.bg, expand=True,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        )