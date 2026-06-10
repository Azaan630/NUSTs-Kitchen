import flet as ft
import asyncio
import httpx
import os
from datetime import date
import mock_data

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


async def _req(method, endpoint, params=None, json_data=None):
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}{endpoint}"
            kw = dict(params=params, timeout=10.0)
            if method == "GET":    r = await client.get(url, **kw)
            elif method == "POST":  r = await client.post(url, json=json_data, **kw)
            elif method == "PATCH": r = await client.patch(url, json=json_data, **kw)
            elif method == "DELETE":r = await client.delete(url, **kw)
            else: return {"error": "bad method"}
            r.raise_for_status()
            return r.json() if r.status_code != 204 else {}
        except httpx.HTTPStatusError as e:
            try: d = e.response.json().get("detail", e.response.text)
            except Exception: d = e.response.text
            return {"error": f"({e.response.status_code}) {d}"}
        except Exception as ex:
            return {"error": str(ex)}


# ── API helpers ─────────────────────────────────────────────────

def _api(table):
    return {
        "students": {
            "all":   lambda e: _req("GET", "/admin/students/all", {"email": e}),
            "register": lambda e,d: _req("POST", "/admin/students/register", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/students/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/students/delete/{i}", {"email": e}),
        },
        "staff": {
            "all":   lambda e: _req("GET", "/admin/students/all", {"email": e}),
            "register": lambda e,d: _req("POST", "/admin/staff/register", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/staff/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/staff/delete/{i}", {"email": e}),
        },
        "food": {
            "all":   lambda e: _req("GET", "/admin/food/costs", {"email": e}),
            "create": lambda e,d: _req("POST", "/admin/food-items/create", {"email": e}, d),
            "update": lambda e,i,d: _req("PATCH", f"/admin/food-items/update/{i}", {"email": e}, d),
            "delete": lambda e,i: _req("DELETE", f"/admin/food-items/delete/{i}", {"email": e}),
            "search": lambda e,q: _req("GET", "/admin/food/search", {"email": e, "q": q}),
        },
        "mess_off": {
            "history": lambda e: _req("GET", "/student/mess-off/history", {"email": e}),
            "approve": lambda e,i: _req("POST", f"/admin/mess-off/approve/{i}", {"email": e}),
            "reject":  lambda e,i: _req("DELETE", f"/student/mess-off/cancel/{i}", {"email": e}),
        },
        "bills": {
            "summary":  lambda e: _req("GET", "/admin/monthly-billing-summary", {"email": e}),
            "create":   lambda e,d: _req("POST", "/admin/bills/create", {"email": e}, d),
            "export":   lambda e: _req("GET", "/admin/bills/export-csv", {"email": e}),
            "generate": lambda e,a: _req("POST", "/admin/bills/generate-monthly", {"email": e, "amount": a}),
        },
        "menu": {
            "weekly": lambda e: _req("GET", "/menu/weekly", {"email": e}),
            "add":    lambda e,i,d,t: _req("POST", f"/admin/menu-schedule/{i}/{d}/{t}", {"email": e}),
            "delete": lambda e,i,s: _req("DELETE", f"/admin/menu-schedule/{i}/{s}", {"email": e}),
        },
        "registration": {
            "list":    lambda e,s: _req("GET", "/admin/registration-requests", {"email": e, "status": s}),
            "approve": lambda e,i,d: _req("POST", f"/admin/registration-requests/{i}/approve", {"email": e}, d),
            "reject":  lambda e,i: _req("POST", f"/admin/registration-requests/{i}/reject", {"email": e}),
        },
        "poll": {
            "start":   lambda e,d: _req("POST", "/admin/poll/start", {}, d, params={"email": e}),
            "results": lambda e: _req("GET", "/admin/poll/results", {"email": e}),
        },
        "stats": {
            "dashboard": lambda e: _req("GET", "/admin/dashboard/stats", {"email": e}),
            "activity":  lambda e: _req("GET", "/admin/activity/feed", {"email": e}),
        },
        "students_csv": lambda e: _req("GET", "/admin/students/export-csv", {"email": e}),
    }[table]


class AdminPage:
    TABS = [
        ("Dashboard", ft.Icons.DASHBOARD_ROUNDED),
        ("Students",  ft.Icons.PEOPLE_ROUNDED),
        ("Staff",     ft.Icons.BADGE_ROUNDED),
        ("Food Items",ft.Icons.FASTFOOD_ROUNDED),
        ("Mess Off",  ft.Icons.EVENT_BUSY_ROUNDED),
        ("Bills",     ft.Icons.RECEIPT_LONG_ROUNDED),
        ("Menu",      ft.Icons.RESTAURANT_MENU_ROUNDED),
        ("Polls",     ft.Icons.POLL_ROUNDED),
        ("Requests",  ft.Icons.PERSON_ADD_ALT_1_ROUNDED),
    ]

    def __init__(self, page, user_data, theme):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)
        self.tab_idx = {"v": 0}
        self.content = ft.Container(expand=True)
        self.proxy_rows = {}

    # ── helpers ─────────────────────────────────────────────────

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

    def _card(self, *controls, pad=14):
        return ft.Container(
            content=ft.Column(list(controls), spacing=10),
            bgcolor=self._clr("card"), border_radius=14,
            padding=pad,
        )

    def _stat_card(self, icon, label, value, color=None):
        c = color or self._clr("accent")
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=c),
                        bgcolor=ft.Colors.with_opacity(0.12, c),
                        width=40, height=40, border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(str(value), size=22, weight="bold", color=self._clr("text"),
                                font_family="DM Sans"),
                        ft.Text(label, size=11, color=self._clr("sub"), font_family="DM Sans"),
                    ], spacing=0, tight=True),
                ], spacing=12),
            ]),
            bgcolor=self._clr("card"), border_radius=14,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            expand=True,
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

    def _btn(self, label, icon, cb, compact=False):
        return ft.FilledButton(
            content=ft.Row([
                ft.Icon(icon, size=16, color=self._clr("text")),
                ft.Text(label, size=12, weight="bold", color=self._clr("text"),
                        font_family="DM Sans"),
            ], spacing=6, tight=True),
            on_click=cb,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.1, self._clr("accent")),
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=14 if not compact else 10, vertical=10),
            ),
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

    def _row_card(self, controls, actions=None):
        row = list(controls)
        if actions:
            row.append(ft.Row(actions, spacing=2))
        return ft.Container(
            content=ft.Row(row, spacing=12),
            bgcolor=self._clr("card"), border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=6),
        )

    def _guest_banner(self):
        if not self.is_guest: return ft.Container()
        return ft.Container(
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=self._clr("text")),
                ft.Text("Guest Mode \u2014 Changes are temporary. Demo sandbox, not real data.",
                        size=12, color=self._clr("text"), font_family="DM Sans", expand=True),
            ], spacing=10),
            bgcolor=ft.Colors.with_opacity(0.1, self._clr("warn")),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=12),
        )

    # ── Tab sidebar ────────────────────────────────────────────

    def _sidebar(self, on_select):
        items = []
        for i, (label, icon) in enumerate(self.TABS):
            sel = self.tab_idx["v"] == i
            items.append(ft.Container(
                ft.Row([
                    ft.Icon(icon, size=18, color=self._clr("accent") if sel else self._clr("sub")),
                    ft.Text(label, size=13, font_family="DM Sans",
                            weight="bold" if sel else "normal",
                            color=self._clr("text") if sel else self._clr("sub")),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.1, self._clr("accent")) if sel else ft.Colors.TRANSPARENT,
                border_radius=12,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                on_click=lambda e, idx=i: on_select(idx),
            ))
        return ft.Container(
            content=ft.Column(items, spacing=4),
            bgcolor=self._clr("card"), border_radius=16,
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            width=170,
        )

    # ════════════════════════════════════════════════════════════
    #  TAB 0 — DASHBOARD
    # ════════════════════════════════════════════════════════════

    async def _render_dashboard(self, ref):
        ref.content = self._loading()
        self.page.update()

        stats = {"total_students": 0, "total_staff": 0, "total_food_items": 0,
                 "total_ingredients": 0, "active_mess_offs": 0, "unpaid_bills": 0,
                 "pending_registration_requests": 0}
        activity = []
        if not self.is_guest:
            s = await _api("stats")["dashboard"](self.email)
            if isinstance(s, dict) and "error" not in s:
                stats = s
            act = await _api("stats")["activity"](self.email)
            if isinstance(act, list):
                activity = act

        stat_cards = ft.ResponsiveRow([
            ft.Container(self._stat_card(ft.Icons.SCHOOL_ROUNDED, "Students", stats["total_students"], self._clr("accent")), col={"sm": 4}),
            ft.Container(self._stat_card(ft.Icons.BADGE_ROUNDED, "Staff", stats["total_staff"], self._clr("accent2")), col={"sm": 4}),
            ft.Container(self._stat_card(ft.Icons.FASTFOOD_ROUNDED, "Food Items", stats["total_food_items"], self._clr("success")), col={"sm": 4}),
            ft.Container(self._stat_card(ft.Icons.CATEGORY_ROUNDED, "Ingredients", stats["total_ingredients"], self._clr("warn")), col={"sm": 3}),
            ft.Container(self._stat_card(ft.Icons.EVENT_BUSY_ROUNDED, "Active Mess Offs", stats["active_mess_offs"], self._clr("danger")), col={"sm": 3}),
            ft.Container(self._stat_card(ft.Icons.RECEIPT_ROUNDED, "Unpaid Bills", stats["unpaid_bills"], self._clr("warn")), col={"sm": 3}),
            ft.Container(self._stat_card(ft.Icons.PERSON_ADD_ALT_1_ROUNDED, "Pending Reg.", stats["pending_registration_requests"], self._clr("accent2")), col={"sm": 3}),
        ], spacing=10)

        activity_col = ft.Column([
            ft.Text("Recent Activity", size=16, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE_ROUNDED, size=8, color=self._clr("accent")),
                    ft.Text(a.get("description", ""), size=12, color=self._clr("sub"), font_family="DM Sans", expand=True),
                    ft.Text(str(a.get("event_date", "")), size=10, color=self._clr("sub"), font_family="DM Sans"),
                ], spacing=8) if isinstance(a, dict) else ft.Text("No recent activity", size=12, color=self._clr("sub"))
                for a in (activity if activity else [{"description": "No recent activity"}])
            ], spacing=6),
        ]) if activity else ft.Text("No recent activity", color=self._clr("sub"), font_family="DM Sans")

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Text("Dashboard", size=22, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Container(height=4),
            ft.Text("Overview of the mess system", size=13, color=self._clr("sub"), font_family="DM Sans"),
            ft.Container(height=16),
            stat_cards,
            ft.Container(height=20),
            self._card(activity_col),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 1 — STUDENTS
    # ════════════════════════════════════════════════════════════

    async def _render_students(self, ref):
        ref.content = self._loading(); self.page.update()
        students = (mock_data.get_students() if self.is_guest
                    else [u for u in ((await _api("students")["all"](self.email)) or []) if u.get("Account_Type") == "Student"])

        search_bar = ft.TextField(
            hint_text="Search by name or email\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data),
            expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in student_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        student_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_students(ref)

        for s in students:
            uid = s.get("UserID")
            name = f"{s.get('First_Name','')} {s.get('Last_Name','')}"
            email = s.get("Email", "")
            label = f"{name} | {email} | {uid}"
            async def do_del(e, u=uid):
                if self.is_guest: mock_data.delete_student(u)
                else:
                    r = await _api("students")["delete"](self.email, u)
                    if "error" in (r or {}): self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()
            student_rows.controls.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(email, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Students", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            ft.Container(height=4),
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            ft.Container(height=4),
            student_rows if student_rows.controls else ft.Text("No students found", color=self._clr("sub"), font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 2 — STAFF
    # ════════════════════════════════════════════════════════════

    async def _render_staff(self, ref):
        ref.content = self._loading(); self.page.update()
        staff_list = (mock_data.get_staff() if self.is_guest
                      else [u for u in ((await _api("staff")["all"](self.email)) or []) if u.get("Account_Type") == "Staff"])

        search_bar = ft.TextField(
            hint_text="Search staff\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=ft.Colors.with_opacity(0.2, self._clr("text")),
            border_radius=10, filled=True, fill_color=self._clr("card2"),
            text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
            on_change=lambda e: _filter(e.data),
            expand=True,
        )

        def _filter(q):
            q = q.lower()
            for c in staff_rows.controls:
                c.visible = q in (c.data or "").lower() if q else True
            self.page.update()

        staff_rows = ft.Column(spacing=4)

        async def refresh():
            await self._render_staff(ref)

        for s in staff_list:
            uid = s.get("UserID")
            name = f"{s.get('First_Name','')} {s.get('Last_Name','')}"
            email = s.get("Email", "")
            label = f"{name} | {email} | {uid}"
            async def do_del(e, u=uid):
                if self.is_guest: mock_data.delete_staff(u)
                else:
                    r = await _api("staff")["delete"](self.email, u)
                    if "error" in (r or {}): self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()
            staff_rows.controls.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(email, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Staff", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            staff_rows if staff_rows.controls else ft.Text("No staff found", color=self._clr("sub"), font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 3 — FOOD ITEMS
    # ════════════════════════════════════════════════════════════

    async def _render_food(self, ref):
        ref.content = self._loading(); self.page.update()
        items = (mock_data.get_food_costs() if self.is_guest
                 else (await _api("food")["all"](self.email)) or [])

        search_bar = ft.TextField(
            hint_text="Search food items\u2026", prefix_icon=ft.Icons.SEARCH_ROUNDED,
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

        async def refresh():
            await self._render_food(ref)

        for item in items:
            iid = item.get("Item_ID")
            name = item.get("Name", "")
            cost = item.get("Estimated_Cost", 0)
            price = item.get("Price", 0)
            label = f"{name} | {iid}"

            ef_name  = ft.TextField(value=name, expand=True, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"),)
            ef_price = ft.TextField(value=str(price), width=90, dense=True,
                border_color=self._clr("accent"), border_radius=8,
                text_style=ft.TextStyle(color=self._clr("text"), font_family="DM Sans"),
                filled=True, fill_color=self._clr("card"),)

            async def do_upd(e, i=iid, nf=ef_name, pf=ef_price):
                p = {"Name": nf.value, "Price": float(pf.value or 0)}
                if self.is_guest: mock_data.update_food(i, p)
                else:
                    r = await _api("food")["update"](self.email, i, p)
                    if "error" in (r or {}): self._snack(r["error"], False); return
                self._snack("Updated")

            async def do_del(e, i=iid):
                if self.is_guest: mock_data.delete_food(i)
                else:
                    r = await _api("food")["delete"](self.email, i)
                    if "error" in (r or {}): self._snack(r["error"], False); return
                self._snack("Deleted"); await refresh()

            food_rows.controls.append(self._row_card([
                ef_name, ef_price,
                ft.Text(f"Cost: PKR {cost:.0f}", size=11, color=self._clr("sub"), font_family="DM Sans"),
            ], actions=[
                self._icon_btn(ft.Icons.SAVE_ROUNDED, self._clr("accent"), "Save", do_upd),
                self._icon_btn(ft.Icons.DELETE_ROUNDED, self._clr("danger"), "Delete", do_del),
            ], data=label))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Food Items", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([search_bar], spacing=8),
            ft.Row([self._btn("Refresh", ft.Icons.REFRESH_ROUNDED, lambda e: asyncio.create_task(refresh()))], alignment=ft.MainAxisAlignment.END),
            food_rows if food_rows.controls else ft.Text("No food items", color=self._clr("sub"), font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 4 — MESS OFF
    # ════════════════════════════════════════════════════════════

    async def _render_mess_off(self, ref):
        ref.content = self._loading(); self.page.update()
        if self.is_guest:
            requests = mock_data.get_mess_off_history().get("status", [])
        else:
            result = await _api("mess_off")["history"](self.email)
            requests = result.get("status", []) if isinstance(result, dict) else (result if isinstance(result, list) else [])

        s_colors = {"Approved": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Pending": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Rejected": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger"))),
                    "Cancelled": (self._clr("sub"), self._clr("card2"))}
        rows = []
        for req in requests:
            rid = req.get("Mess_Off_ID")
            status = req.get("Status", "Pending")
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))
            acts = []
            if status == "Pending":
                async def do_app(e, r=rid):
                    if self.is_guest: mock_data.approve_mess_off(r)
                    else:
                        res = await _api("mess_off")["approve"](self.email, r)
                        if "error" in (res or {}): self._snack(res["error"], False); return
                    self._snack("Approved"); await self._render_mess_off(ref)
                async def do_rej(e, r=rid):
                    if self.is_guest: mock_data.reject_mess_off(r)
                    else:
                        res = await _api("mess_off")["reject"](self.email, r)
                        if "error" in (res or {}): self._snack(res["error"], False); return
                    self._snack("Rejected"); await self._render_mess_off(ref)
                acts = [self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, self._clr("success"), "Approve", do_app),
                        self._icon_btn(ft.Icons.CANCEL_ROUNDED, self._clr("danger"), "Reject", do_rej)]
            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"User #{req.get('User_ID','?')} \u2022 {req.get('Start_Date','?')} \u2192 {req.get('End_Date','?')}",
                            size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"ID #{rid} \u2022 {req.get('Request_Date','')}",
                            size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=acts))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Mess-Off Requests", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No requests", color=self._clr("sub")),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 5 — BILLS
    # ════════════════════════════════════════════════════════════

    async def _render_bills(self, ref):
        ref.content = self._loading(); self.page.update()
        bills = (await _api("bills")["summary"](self.email)) if not self.is_guest else mock_data.get_monthly_bills()

        async def do_export(e):
            csv_r = await _api("bills")["export"](self.email)
            if "error" not in (csv_r or {}):
                self._snack("CSV download started")
            else:
                self._snack(csv_r.get("error", "Export failed"), False)

        async def do_generate(e):
            r = await _api("bills")["generate"](self.email, 5000)
            if "error" not in (r or {}):
                self._snack(r.get("message", "Bills generated"))
                await self._render_bills(ref)
            else:
                self._snack(r.get("error", "Generation failed"), False)

        s_colors = {"Paid": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Unpaid": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Overdue": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger")))}
        rows = []
        for b in (bills if isinstance(bills, list) else []):
            uid = b.get("User_ID")
            month = b.get("Billing_Month", "?")
            total = b.get("Total_Amount", 0)
            paid = b.get("Total_Collected", 0)
            outstanding = b.get("Outstanding", 0)
            status = "Paid" if outstanding <= 0 else "Unpaid"
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))
            rows.append(self._row_card([
                ft.Column([
                    ft.Text(f"User #{uid} \u2022 {month}", size=13, weight="bold",
                            color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"Total: PKR {total:.0f} \u2022 Paid: PKR {paid:.0f} \u2022 Due: PKR {outstanding:.0f}",
                            size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ]))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Bills", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Row([
                self._btn("Export CSV", ft.Icons.DOWNLOAD_ROUNDED, do_export),
                self._btn("Generate Monthly", ft.Icons.AUTO_GRAPH_ROUNDED, do_generate),
            ], spacing=8),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No billing data", color=self._clr("sub")),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 6 — MENU
    # ════════════════════════════════════════════════════════════

    async def _render_menu(self, ref):
        ref.content = self._loading(); self.page.update()
        items = mock_data.get_weekly_menu() if self.is_guest else (await _api("menu")["weekly"](self.email)) or []

        m_colors = {"Breakfast": self._clr("warn"), "Lunch": self._clr("success"), "Dinner": self._clr("accent2")}
        rows = []
        for item in items:
            iid = item.get("Item_ID")
            sid = item.get("Schedule_ID")
            name = item.get("Name") or item.get("Food_Item_Name", "?")
            mt = item.get("meal_type", "")
            d = item.get("Date", "")
            mc = m_colors.get(mt, self._clr("accent"))
            async def do_del(e, i=iid, s=sid):
                if self.is_guest: mock_data.delete_menu_item(i, s)
                else:
                    r = await _api("menu")["delete"](self.email, i, s)
                    if "error" in (r or {}): self._snack(r["error"], False); return
                self._snack("Removed"); await self._render_menu(ref)
            rows.append(self._row_card([
                ft.Container(
                    content=ft.Text(mt[:1], size=12, weight="bold", color=mc),
                    width=30, height=30, bgcolor=ft.Colors.with_opacity(0.12, mc),
                    border_radius=8, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(f"{d} \u2022 {mt}", size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._icon_btn(ft.Icons.REMOVE_CIRCLE_ROUNDED, self._clr("danger"), "Remove", do_del),
            ]))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Menu", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(rows, scroll=ft.ScrollMode.ADAPTIVE) if rows else ft.Text("No menu items", color=self._clr("sub")),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 7 — POLLS
    # ════════════════════════════════════════════════════════════

    async def _render_polls(self, ref):
        ref.content = self._loading(); self.page.update()
        res = mock_data.get_poll_results() if self.is_guest else await _api("poll")["results"](self.email)
        poll_results = res.get("results", []) if isinstance(res, dict) else []

        result_cards = [self._row_card([
            ft.Text(r.get("Name", "?"), expand=True, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Text(f"{r.get('Vote_Count', 0)} Votes", color=self._clr("accent"), weight="bold", font_family="DM Sans"),
        ]) for r in poll_results]

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Polls", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Text("Live Results", size=14, weight="bold", color=self._clr("text"), font_family="DM Sans"),
            ft.Column(result_cards) if result_cards else ft.Text("No active poll", color=self._clr("sub"), font_family="DM Sans"),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  TAB 8 — REGISTRATION REQUESTS
    # ════════════════════════════════════════════════════════════

    async def _render_requests(self, ref):
        ref.content = self._loading(); self.page.update()
        requests = mock_data.get_registration_requests() if self.is_guest else (await _api("registration")["list"](self.email, "Pending")) or []

        s_colors = {"Pending": (self._clr("warn"), ft.Colors.with_opacity(0.12, self._clr("warn"))),
                    "Approved": (self._clr("success"), ft.Colors.with_opacity(0.12, self._clr("success"))),
                    "Rejected": (self._clr("danger"), ft.Colors.with_opacity(0.12, self._clr("danger")))}
        cards = []
        for r in requests:
            rid = r.get("RequestID")
            name = f"{r.get('First_Name','')} {r.get('Last_Name','')}"
            role = r.get("Account_Type", "")
            email = r.get("Email", "")
            info = f"{role} \u2022 {email}" + (f" \u2022 {r.get('Department','')} \u2022 {r.get('Hostel_Name','')}" if role == "Student" else f" \u2022 {r.get('Category','')}")
            status = r.get("Status", "Pending")
            fg, bg = s_colors.get(status, (self._clr("sub"), self._clr("card2")))
            acts = []
            if status == "Pending":
                async def do_app(e, ri=rid):
                    if self.is_guest: mock_data.approve_registration(ri)
                    else:
                        rr = await _api("registration")["approve"](self.email, ri, None)
                        if "error" in (rr or {}): self._snack(rr["error"], False); return
                    self._snack("Approved"); await self._render_requests(ref)
                async def do_rej(e, ri=rid):
                    if self.is_guest: mock_data.reject_registration(ri)
                    else:
                        rr = await _api("registration")["reject"](self.email, ri)
                        if "error" in (rr or {}): self._snack(rr["error"], False); return
                    self._snack("Rejected"); await self._render_requests(ref)
                acts = [self._icon_btn(ft.Icons.CHECK_CIRCLE_ROUNDED, self._clr("success"), "Approve", do_app),
                        self._icon_btn(ft.Icons.CANCEL_ROUNDED, self._clr("danger"), "Reject", do_rej)]
            cards.append(self._row_card([
                ft.Column([
                    ft.Text(name, size=13, weight="bold", color=self._clr("text"), font_family="DM Sans"),
                    ft.Text(info, size=11, color=self._clr("sub"), font_family="DM Sans"),
                ], expand=True, spacing=2),
                self._chip(status, fg, bg),
            ], actions=acts))

        ref.content = ft.Column([
            self._guest_banner(),
            ft.Row([ft.Text("Registration Requests", size=18, weight="bold", color=self._clr("text"), font_family="DM Sans")],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            ft.Column(cards, scroll=ft.ScrollMode.ADAPTIVE) if cards else ft.Text("No pending requests", color=self._clr("sub")),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.page.update()

    # ════════════════════════════════════════════════════════════
    #  BUILD
    # ════════════════════════════════════════════════════════════

    RENDERERS = [
        "_render_dashboard", "_render_students", "_render_staff",
        "_render_food", "_render_mess_off", "_render_bills",
        "_render_menu", "_render_polls", "_render_requests",
    ]

    def build(self):
        def select_tab(idx):
            self.tab_idx["v"] = idx
            sidebar.controls[0] = self._sidebar(select_tab)
            asyncio.create_task(getattr(self, self.RENDERERS[idx])(self.content))
            self.page.update()

        sidebar = ft.Column([self._sidebar(select_tab)])
        layout = ft.Row([
            sidebar,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, self._clr("text"))),
            ft.Container(content=self.content, expand=True, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
        ], expand=True, spacing=0)

        asyncio.create_task(self._render_dashboard(self.content))

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Admin", size=24, weight="bold", font_family="DM Sans", color=self._clr("text")),
                    self._chip("Admin", self._clr("accent"), ft.Colors.with_opacity(0.12, self._clr("accent"))),
                ], spacing=12),
                ft.Container(height=8),
                ft.Container(content=layout, expand=True),
            ], expand=True),
            bgcolor=self._clr("bg"), expand=True,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        )
