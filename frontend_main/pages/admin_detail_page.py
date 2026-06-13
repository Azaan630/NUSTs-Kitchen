import flet as ft
import asyncio
import os
import httpx
import mock_data

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
PUBLIC_BACKEND_URL = os.getenv("PUBLIC_BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


def _img_url(path):
    if not path:
        return None
    if path.startswith(("http://", "https://", "data:")):
        return path
    return f"{PUBLIC_BACKEND_URL}{path}"


def _ensure_list(data):
    if isinstance(data, dict) and "error" in data:
        return []
    return data if isinstance(data, list) else []


class AdminDetailPage:
    def __init__(self, page: ft.Page, theme: dict, person: dict, role: str,
                 admin_email: str, is_guest: bool = False, on_back=None):
        self.page = page
        self.theme = theme
        self.person = person
        self.role = role
        self.admin_email = admin_email
        self.is_guest = is_guest
        self.on_back = on_back

        t = theme
        self.txt = t["text"]
        self.sub = t["sub"]
        self.acc = t["accent"]
        self.card = t["card"]
        self.bg = t["bg"]
        self.danger = t.get("danger", "#EF4444")
        self.success = t.get("success", "#34D399")
        self.warn = t.get("warn", "#FBBF24")

        self._extra = {}
        self._bills = []
        self._loaded = False

        self.main_container = ft.Container(
            expand=True,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
        )

    def build(self):
        asyncio.create_task(self._render())
        return ft.Container(
            content=self.main_container,
            expand=True,
        )

    async def _render(self):
        self.main_container.content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.ProgressRing(color=self.acc, width=36, height=36, stroke_width=3),
                    alignment=ft.Alignment(0, 0), expand=True,
                ),
            ]), expand=True,
        )
        self.page.update()

        await self._fetch_details()
        await self._fetch_bills()

        d = self.person
        first = d.get("First_Name", "")
        last = d.get("Last_Name", "")
        email = d.get("Email", "")
        role_label = self.role.title()
        initials = (first[0] + (last[0] if last else "")).upper() or "U"
        profile_pic = d.get("Profile_Picture", "")
        has_pic = bool(profile_pic)

        mb = (self.page.width or 1200) < 720
        pad = 16 if mb else 40
        pfp_size = 120 if mb else 140

        def _info_row(label, value):
            if not value or str(value).strip() in ("", "-", "N/A"):
                return None
            w = 100 if not mb else 80
            return ft.Container(
                content=ft.Row([
                    ft.Text(label, size=13, color=self.sub, font_family="DM Sans", width=w),
                    ft.Text(str(value), size=14, weight="bold", color=self.txt,
                            font_family="DM Sans", expand=True),
                ], spacing=6),
                padding=ft.Padding.symmetric(vertical=7),
            )

        def _section(icon, title, rows):
            visible = [r for r in rows if r is not None]
            if not visible:
                return None
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=18, color=self.acc),
                            padding=ft.Padding.all(6),
                            bgcolor=ft.Colors.with_opacity(0.1, self.acc),
                            border_radius=10,
                        ),
                        ft.Text(title, size=17, weight="bold", color=self.txt,
                                font_family="DM Sans"),
                    ], spacing=10),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.08, self.txt)),
                    ft.Column(visible, spacing=2),
                ], spacing=12),
                bgcolor=self.card, border_radius=18, padding=20,
                shadow=ft.BoxShadow(blur_radius=20,
                    color=ft.Colors.with_opacity(0.06, "#000"), offset=ft.Offset(0, 2)),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.05, self.txt)),
            )

        pfp_stack = ft.Stack([
            ft.Container(
                content=ft.Image(src=_img_url(profile_pic), fit="cover",
                    width=pfp_size, height=pfp_size,
                ) if has_pic else ft.Text(initials,
                    size=int(pfp_size * 0.4), weight="bold", color="#FFF", font_family="DM Sans"),
                width=pfp_size, height=pfp_size,
                bgcolor=self.acc if not has_pic else None,
                border_radius=pfp_size // 2, alignment=ft.Alignment(0, 0),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(blur_radius=40,
                    color=ft.Colors.with_opacity(0.3, self.acc), offset=ft.Offset(0, 6)),
            ),
        ])

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=22, color=self.txt),
                        padding=ft.Padding.all(8), border_radius=12,
                        on_click=lambda e: self._go_back(),
                    ),
                    ft.Text(f"{role_label} Profile", size=20 if mb else 24,
                            weight="bold", color=self.txt, font_family="DM Sans", expand=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column([
                        pfp_stack,
                        ft.Container(height=12),
                        ft.Text(f"{first} {last}".strip(), size=22 if mb else 26,
                                weight="bold", color=self.txt, font_family="DM Sans"),
                        ft.Text(email, size=13, color=self.sub, font_family="DM Sans"),
                        ft.Container(
                            content=ft.Text(role_label, size=12, weight="bold",
                                            color=self.acc, font_family="DM Sans"),
                            bgcolor=ft.Colors.with_opacity(0.12, self.acc),
                            border_radius=10,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    alignment=ft.Alignment(0, 0),
                ),
            ], spacing=4),
            margin=ft.Margin.only(bottom=20),
        )

        # Basic info rows
        basic_rows = []
        basic_rows.append(_info_row("User ID", d.get("UserID", "")))
        basic_rows.append(_info_row("First Name", first))
        basic_rows.append(_info_row("Last Name", last))
        basic_rows.append(_info_row("Email", email))
        basic_rows.append(_info_row("Sex", self._extra.get("Sex") or d.get("Sex", "")))
        basic_section = _section(ft.Icons.INFO_ROUNDED, "Basic Information", basic_rows)

        # Role-specific rows
        extra_rows = []
        if self.role == "student":
            extra_rows.append(_info_row("Department", self._extra.get("Department")))
            extra_rows.append(_info_row("Contact Number", self._extra.get("Contact_Number")))
            extra_rows.append(_info_row("Date of Birth", self._extra.get("DoB")))
            extra_rows.append(_info_row("Address", self._extra.get("Address")))
            extra_rows.append(_info_row("Father's Name", self._extra.get("Father_Name")))
            extra_rows.append(_info_row("Hostel", self._extra.get("Hostel_Name")))
            extra_rows.append(_info_row("Room Number", self._extra.get("Room_Number")))
        elif self.role == "staff":
            extra_rows.append(_info_row("Category", self._extra.get("Category") or self._extra.get("Cat")))
            extra_rows.append(_info_row("Salary", f"Rs. {self._extra['Salary']:,.0f}" if self._extra.get("Salary") else None))
            extra_rows.append(_info_row("Working Hours", self._extra.get("Working_hours")))

        role_section = None
        if extra_rows:
            icon = ft.Icons.SCHOOL_ROUNDED if self.role == "student" else ft.Icons.BADGE_ROUNDED
            role_section = _section(icon, f"{role_label} Details", extra_rows)

        sections = [s for s in [basic_section, role_section] if s is not None]

        # Billing history (students only)
        if self.role == "student" and self._bills:
            bill_rows = []
            for b in self._bills:
                month = b.get("Month") or b.get("Billing_Month", "")
                total = b.get("Amount", b.get("Total_Amount", 0))
                paid = b.get("Total_Collected", 0)
                outstanding = total - paid
                status = b.get("Status", "Unpaid")
                fg = self.success if status == "Paid" else (self.warn if "unpaid" in status.lower() else self.danger)
                bg = ft.Colors.with_opacity(0.1, fg)
                bill_rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"Month: {month}", size=13, weight="bold",
                                        color=self.txt, font_family="DM Sans"),
                                ft.Text(f"Amount: PKR {total:,.0f}  |  Paid: PKR {paid:,.0f}  |  Due: PKR {outstanding:,.0f}",
                                        size=11, color=self.sub, font_family="DM Sans"),
                            ], expand=True, spacing=2),
                            ft.Container(
                                content=ft.Text(status, size=10, weight="bold",
                                                color=fg, font_family="DM Sans"),
                                bgcolor=bg, border_radius=6,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                            ),
                        ], spacing=8),
                        bgcolor=self.card, border_radius=12,
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.05, self.txt)),
                    )
                )
            bill_section = _section(ft.Icons.RECEIPT_LONG_ROUNDED, "Billing History", bill_rows)
            if bill_section:
                sections.append(bill_section)

        content_col = ft.Column([
            header,
            ft.Container(
                content=ft.Column(sections, spacing=16),
                padding=ft.Padding.symmetric(horizontal=0),
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=0)

        self.main_container.content = ft.Container(
            content=ft.Stack([
                ft.Container(expand=True, gradient=self.theme.get("bg_gradient",
                    ft.LinearGradient(colors=[self.bg, self.bg]))),
                ft.Container(
                    content=ft.Column([
                        ft.Container(content=content_col, expand=True, padding=pad),
                    ], expand=True),
                ),
            ]), expand=True,
        )
        self.page.update()
        self.main_container.opacity = 1
        self.page.update()

    def _go_back(self):
        if self.on_back:
            self.on_back()

    def _clr(self, key, fallback=None):
        return self.theme.get(key, fallback)

    async def _fetch_details(self):
        uid = self.person.get("UserID")
        if not uid:
            return
        if self.is_guest:
            if self.role == "student":
                for s in mock_data.get_students():
                    if s.get("UserID") == uid:
                        self._extra = s
                        break
            elif self.role == "staff":
                for s in mock_data.get_staff():
                    if s.get("UserID") == uid:
                        self._extra = s
                        break
        else:
            ep = f"/admin/{self.role}s/details/{uid}"
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{BACKEND_URL}{ep}",
                                         params={"email": self.admin_email}, timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list) and data:
                            self._extra = data[0]
            except Exception:
                pass

    async def _fetch_bills(self):
        if self.role != "student":
            return
        uid = self.person.get("UserID")
        if not uid:
            return
        if self.is_guest:
            all_bills = mock_data.get_my_bills()
            self._bills = [b for b in all_bills if b.get("User_ID") == uid]
        else:
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{BACKEND_URL}/admin/{uid}/bill-status",
                                         params={"email": self.admin_email}, timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list):
                            self._bills = data
            except Exception:
                pass
