import flet as ft
import asyncio
import os
import uuid
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


class ProfileDetailsPage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict, on_back=None):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.on_back = on_back
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.txt = t["text"]
        self.sub = t["sub"]
        self.acc = t["accent"]
        self.card = t["card"]
        self.bg = t["bg"]
        self.danger = t.get("danger", "#EF4444")
        self.success = t.get("success", "#34D399")
        self.warn = t.get("warn", "#FBBF24")
        self.is_dark = t.get("is_dark", True)

        self.main_container = ft.Container(
            expand=True,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
        )

        self._extra = {}
        self._loaded = False

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
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
            ]),
            expand=True,
        )
        self.page.update()

        await self._fetch_details()

        uid = self._get("UserID", 0)
        email = self._get("Email", "")
        first = self._get("First_Name", "")
        last = self._get("Last_Name", "")
        role = self._get("Account_Type", "Student")
        initials = (first[0] + (last[0] if last else "")).upper() or "U"
        profile_pic = self._get("Profile_Picture", "")
        has_pic = bool(profile_pic)

        mb = (self.page.width or 1200) < 720
        pad = 16 if mb else 40

        profile_pic_size = 120 if mb else 140

        def _info_row(label, value):
            if not value or str(value).strip() in ("", "-", "N/A"):
                return None
            mb = (self.page.width or 1200) < 720
            return ft.Container(
                content=ft.Row([
                    ft.Text(label, size=13, color=self.sub, font_family="DM Sans",
                            width=100 if not mb else 80),
                    ft.Text(str(value), size=14, weight="bold", color=self.txt, font_family="DM Sans",
                            expand=True),
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
                        ft.Text(title, size=17, weight="bold", color=self.txt, font_family="DM Sans"),
                    ], spacing=10),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.08, self.txt)),
                    ft.Column(visible, spacing=2),
                ], spacing=12),
                bgcolor=self.card,
                border_radius=18,
                padding=20,
                shadow=ft.BoxShadow(
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.06, "#000"),
                    offset=ft.Offset(0, 2),
                ),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.05, self.txt)),
            )

        def _on_pfp_click(e):
            if self.is_guest:
                return
            token = uuid.uuid4().hex
            picker_url = f"{PUBLIC_BACKEND_URL}/google-picker-ui?token={token}"
            status_text = ft.Text("", size=12)

            async def _check(e):
                try:
                    async with httpx.AsyncClient() as client:
                        r = await client.get(f"{BACKEND_URL}/picker-status/{token}", timeout=10)
                        data = r.json()
                    if data.get("status") == "done":
                        url = data.get("url", "")
                        dlgo.open = False
                        self.page.update()
                        try:
                            if not self.is_guest:
                                async with httpx.AsyncClient() as client2:
                                    await client2.patch(
                                        f"{BACKEND_URL}/users/{uid}/picture",
                                        json={"Profile_Picture": url},
                                        params={"email": email},
                                        timeout=10,
                                    )
                            self.user_data["Profile_Picture"] = url
                        except Exception:
                            pass
                        await self._render()
                    elif data.get("status") == "pending":
                        status_text.value = "Waiting for you to select an image in the Google Drive tab..."
                        status_text.color = self.warn
                        self.page.update()
                    else:
                        status_text.value = "Unexpected response. Try again."
                        status_text.color = self.danger
                        self.page.update()
                except Exception as ex:
                    status_text.value = f"Error: {ex}"
                    status_text.color = self.danger
                    self.page.update()

            def _open_tab(e):
                asyncio.create_task(self.page.launch_url(picker_url))

            dlgo = ft.AlertDialog(
                modal=True,
                title=ft.Text("Profile Picture", color=self.txt, font_family="DM Sans"),
                content=ft.Column([
                    ft.Text(
                        "Click below to open Google Drive and select an image:",
                        size=13, color=self.sub, font_family="DM Sans",
                    ),
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        "Open Google Drive Picker",
                        icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                        on_click=_open_tab,
                        style=ft.ButtonStyle(bgcolor=self.acc, color="#FFF", padding=ft.Padding.symmetric(horizontal=20, vertical=12)),
                    ),
                    ft.Container(height=4),
                    ft.Text("A new tab will open. Choose an image, then click Check below.",
                            size=12, color=self.sub, font_family="DM Sans"),
                    ft.Container(height=12),
                    ft.Row([
                        ft.ElevatedButton("Check", on_click=_check,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, self.acc), color=self.acc)),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    status_text,
                ], tight=True, spacing=4, width=380),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: setattr(dlgo, 'open', False) or self.page.update()),
                ],
            )
            self.page.show_dialog(dlgo)

        basic_rows = []
        basic_rows.append(_info_row("User ID", uid if uid != -1 else "Guest"))
        basic_rows.append(_info_row("First Name", first))
        basic_rows.append(_info_row("Last Name", last))
        basic_rows.append(_info_row("Email", email))
        basic_rows.append(_info_row("Account Type", role))
        basic_rows.append(_info_row("Sex", self._extra.get("Sex") or self._get("Sex", "")))
        basic_section = _section(ft.Icons.INFO_ROUNDED, "Basic Information", basic_rows)

        extra_rows = []
        if role == "Student":
            extra_rows.append(_info_row("Department", self._extra.get("Department")))
            extra_rows.append(_info_row("Contact Number", self._extra.get("Contact_Number")))
            extra_rows.append(_info_row("Date of Birth", self._extra.get("DoB")))
            extra_rows.append(_info_row("Address", self._extra.get("Address")))
            extra_rows.append(_info_row("Father's Name", self._extra.get("Father_Name")))
            extra_rows.append(_info_row("Hostel", self._extra.get("Hostel_Name")))
            extra_rows.append(_info_row("Room Number", self._extra.get("Room_Number")))
        elif role == "Staff":
            extra_rows.append(_info_row("Category", self._extra.get("Category") or self._extra.get("Cat")))
            extra_rows.append(_info_row("Salary", f"Rs. {self._extra['Salary']:,.0f}" if self._extra.get("Salary") else None))
            extra_rows.append(_info_row("Working Hours", self._extra.get("Working_hours")))

        role_section = None
        if extra_rows:
            lbl = f"{role} Details"
            ico = ft.Icons.SCHOOL_ROUNDED if role == "Student" else ft.Icons.BADGE_ROUNDED
            role_section = _section(ico, lbl, extra_rows)

        sections = [s for s in [basic_section, role_section] if s is not None]

        pfp_stack = ft.Stack([
            ft.Container(
                content=ft.Image(
                    src=_img_url(profile_pic), fit="cover",
                    width=profile_pic_size, height=profile_pic_size,
                ) if has_pic else ft.Text(initials, size=int(profile_pic_size * 0.4),
                    weight="bold", color="#FFF", font_family="DM Sans"),
                width=profile_pic_size,
                height=profile_pic_size,
                bgcolor=self.acc if not has_pic else None,
                border_radius=profile_pic_size // 2,
                alignment=ft.Alignment(0, 0),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(
                    blur_radius=40,
                    color=ft.Colors.with_opacity(0.3, self.acc),
                    offset=ft.Offset(0, 6),
                ),
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=20, color="#FFF"),
                width=40,
                height=40,
                bgcolor=ft.Colors.with_opacity(0.85, "#000"),
                border_radius=20,
                alignment=ft.Alignment(0, 0),
                right=4,
                bottom=4,
                on_click=_on_pfp_click,
                tooltip="Change profile picture" if not self.is_guest else None,
                ink=False,
            ),
        ])

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=22, color=self.txt),
                        padding=ft.Padding.all(8),
                        border_radius=12,
                        on_click=lambda e: self._go_back(),
                    ),
                    ft.Text("Profile Details", size=20 if mb else 24, weight="bold",
                            color=self.txt, font_family="DM Sans", expand=True),
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column([
                        pfp_stack,
                        ft.Container(height=12),
                        ft.Text(f"{first} {last}".strip(), size=22 if mb else 26, weight="bold",
                                color=self.txt, font_family="DM Sans"),
                        ft.Text(email, size=13, color=self.sub, font_family="DM Sans"),
                        ft.Container(
                            content=ft.Text(role, size=12, weight="bold",
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

        def _build_content():
            return ft.Column([
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
                        ft.Container(
                            content=_build_content(),
                            expand=True,
                            padding=pad,
                        ),
                    ], expand=True),
                ),
            ]),
            expand=True,
        )

        self.page.update()
        self.main_container.opacity = 1
        self.page.update()

    def _go_back(self):
        if self.on_back:
            self.on_back()

    def _get(self, key, default="N/A"):
        return self.user_data.get(key, default)

    async def _fetch_details(self):
        uid = self._get("UserID", 0)
        email = self._get("Email", "")
        role = self._get("Account_Type", "Student")

        if self.is_guest:
            if role == "Student":
                for s in mock_data.get_students():
                    if s.get("UserID") == uid:
                        self._extra = s
                        break
            elif role == "Staff":
                for s in mock_data.get_staff():
                    if s.get("UserID") == uid:
                        self._extra = s
                        break
        elif role in ("Student", "Staff"):
            try:
                ep = f"/admin/{role.lower()}s/details/{uid}"
                async with httpx.AsyncClient() as client:
                    r = await client.get(f"{BACKEND_URL}{ep}", params={"email": email}, timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list) and data:
                            self._extra = data[0]
            except Exception:
                pass
