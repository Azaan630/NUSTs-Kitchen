import flet as ft
import os
import asyncio
import httpx
from dotenv import load_dotenv
from pages.home_page import StudentHomePage
from pages.profile_page import StudentProfilePage
from pages.voting_page import StudentVotingPage
from pages.mess_off_page import StudentMessOffPage
from pages.admin_page import AdminPage
from pages.staff_page import StaffPage
import mock_data

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def build_landing(page, login_click, guest_login, show_register):
    NAVY  = "#0D1B2A"
    AMBER = "#F4A228"
    GREY  = "#8A97A8"
    WHITE = "#FFFFFF"

    return ft.Container(
        content=ft.Column([
            ft.Container(height=60),
            ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=72, color=AMBER),
            ft.Container(height=16),
            ft.Text("NUST's Kitchen", size=56, weight="bold",
                    font_family="Playfair", color=WHITE),
            ft.Text("NUST SEECS Mess Portal", size=16, color=GREY,
                    font_family="DM Sans"),
            ft.Container(height=48),
            ft.Container(
                content=ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGIN_ROUNDED, color=NAVY, size=18),
                        ft.Text("Continue with Google", color=NAVY,
                                weight="bold", font_family="DM Sans", size=15),
                    ], spacing=10, tight=True),
                    on_click=login_click,
                    style=ft.ButtonStyle(
                        bgcolor=AMBER,
                        padding=ft.Padding.symmetric(horizontal=32, vertical=18),
                        shape=ft.RoundedRectangleBorder(radius=16),
                        elevation=0,
                    ),
                ),
            ),
            ft.Container(height=12),
            ft.TextButton(
                content=ft.Text("Register as new Student / Staff",
                                color=AMBER, size=13, font_family="DM Sans",
                                weight="bold"),
                on_click=lambda e: show_register(),
            ),
            ft.Container(height=28),
            ft.Text("— or try a demo —", size=12, color=GREY, font_family="DM Sans"),
            ft.Container(height=12),
            ft.Row([
                ft.OutlinedButton("Guest Student", icon=ft.Icons.SCHOOL_ROUNDED,
                    on_click=lambda e: guest_login("Student"),
                    style=ft.ButtonStyle(color=WHITE, side=ft.BorderSide(1, AMBER),
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=10))),
                ft.OutlinedButton("Guest Staff", icon=ft.Icons.BADGE_ROUNDED,
                    on_click=lambda e: guest_login("Staff"),
                    style=ft.ButtonStyle(color=WHITE, side=ft.BorderSide(1, AMBER),
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=10))),
                ft.OutlinedButton("Guest Admin", icon=ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED,
                    on_click=lambda e: guest_login("Admin"),
                    style=ft.ButtonStyle(color=WHITE, side=ft.BorderSide(1, AMBER),
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=10))),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment(0, 0), expand=True,
    )


def build_register_form(page, on_submit, on_back):
    NAVY  = "#0D1B2A"
    AMBER = "#F4A228"
    GREY  = "#8A97A8"
    WHITE = "#FFFFFF"

    role_dd = ft.Dropdown(
        label="I am a",
        options=[ft.dropdown.Option("Student"), ft.dropdown.Option("Staff")],
        value="Student", width=300,
        color=WHITE, label_style=ft.TextStyle(color=GREY, size=13),
        border_color=AMBER,
    )

    fields = {}
    for key, label, hint in [
        ("first", "First Name", "e.g. Muhammad"),
        ("last", "Last Name", "e.g. Azaan"),
        ("email", "Email", "you@seecs.edu.pk"),
        ("dob", "Date of Birth", "YYYY-MM-DD"),
        ("dept", "Department", "e.g. CS, SE, EE"),
        ("phone", "Contact Number", "03XX-XXXXXXX"),
        ("address", "Address", "e.g. H-12 NUST"),
        ("father", "Father's Name", ""),
        ("hostel", "Hostel Name", "e.g. Ghazali"),
        ("room", "Room Number", "e.g. 101"),
        ("category", "Staff Category", "Chef / Server (Staff only)"),
    ]:
        fields[key] = ft.TextField(
            label=label, hint_text=hint, width=300,
            color=WHITE, label_style=ft.TextStyle(color=GREY, size=13),
            border_color=AMBER, cursor_color=AMBER,
        )

    msg = ft.Text("", size=13, color=AMBER, font_family="DM Sans")

    async def submit(e):
        for f in fields.values():
            f.error_text = ""
            f.update()

        if not fields["first"].value or not fields["last"].value or not fields["email"].value:
            msg.value = "First Name, Last Name, and Email are required"
            msg.update()
            return

        payload = {
            "First_Name": fields["first"].value.strip(),
            "Last_Name": fields["last"].value.strip(),
            "Email": fields["email"].value.strip(),
            "Account_Type": role_dd.value,
            "DoB": fields["dob"].value.strip() or None,
            "Department": fields["dept"].value.strip() or None,
            "Contact_Number": fields["phone"].value.strip() or None,
            "Address": fields["address"].value.strip() or None,
            "Father_Name": fields["father"].value.strip() or None,
            "Hostel_Name": fields["hostel"].value.strip() or None,
            "Room_Number": fields["room"].value.strip() or None,
            "Category": fields["category"].value.strip() or None,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{BACKEND_URL}/register/request",
                    json=payload, timeout=10,
                )
            if resp.status_code == 200:
                msg.value = "Request submitted! Awaiting admin approval."
                msg.color = "#10B981"
                for f in fields.values():
                    f.value = ""
            else:
                err = resp.json().get("detail", "Unknown error")
                msg.value = f"Error: {err}"
                msg.color = "#EF4444"
        except (httpx.ConnectError, httpx.TimeoutException):
            msg.value = "Backend unreachable. Try again later."
            msg.color = "#EF4444"

        msg.update()

    return ft.Container(
        content=ft.Column([
            ft.Container(height=40),
            ft.Text("Create Account", size=32, weight="bold",
                    font_family="Playfair", color=AMBER),
            ft.Text("Admin will review and approve your request",
                    size=13, color=GREY, font_family="DM Sans"),
            ft.Container(height=20),
            role_dd,
            *[fields[k] for k in ["first", "last", "email"]],
            ft.Text("Student details (optional for Staff)", size=12,
                    color=GREY, font_family="DM Sans", italic=True),
            *[fields[k] for k in ["dob", "dept", "phone", "address",
                                   "father", "hostel", "room"]],
            fields["category"],
            msg,
            ft.Container(height=8),
            ft.FilledButton("Submit Request",
                on_click=submit,
                style=ft.ButtonStyle(
                    bgcolor=AMBER, color=NAVY, weight="bold",
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding.symmetric(horizontal=32, vertical=14),
                ),
            ),
            ft.Container(height=8),
            ft.TextButton("← Back to Login",
                on_click=lambda e: on_back(),
                style=ft.ButtonStyle(color=AMBER),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
        alignment=ft.Alignment(0, 0), expand=True,
    )


async def main(page: ft.Page):
    page.title = "RotiRouter | NUST SEECS"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.fonts = {
        "Playfair": "https://fonts.gstatic.com/s/playfairdisplay/v37/nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2",
        "DM Sans": "https://fonts.gstatic.com/s/dmsans/v14/rP2Hp2ywxg089UriCZa4ET-DNl0.woff2",
    }

    NAVY       = "#0D1B2A"
    NAVY_LIGHT = "#1A2D42"
    AMBER      = "#F4A228"
    AMBER_DIM  = "#C4821E"
    CREAM      = "#FDF6EC"
    CREAM2     = "#F5ECD8"
    DARK_BG    = "#0A1520"
    DARK_CARD  = "#111E2E"
    DARK_CARD2 = "#172338"
    WHITE      = "#FFFFFF"
    GREY       = "#8A97A8"

    is_dark = {"v": False}

    def bg():    return DARK_BG   if is_dark["v"] else CREAM
    def card():  return DARK_CARD if is_dark["v"] else WHITE
    def text():  return WHITE     if is_dark["v"] else NAVY
    def sub():   return GREY      if is_dark["v"] else "#5A6A7A"

    provider = ft.auth.GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        redirect_url=os.getenv("OAUTH_REDIRECT_URL", "http://localhost:8550/oauth_callback"),
    )

    def get_user_data():
        return getattr(page, "current_user_data", {})

    def get_val(key, default="N/A"):
        return get_user_data().get(key, default)

    async def show_dashboard():
        page.clean()
        page.bgcolor = bg()
        page.update()

        current_index = {"v": 0}
        page_content = ft.Container(expand=True, padding=0)

        dark_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED, icon_color=AMBER, icon_size=22,
            tooltip="Toggle dark mode",
            on_click=lambda e: toggle_dark(e),
        )

        def toggle_dark(e):
            is_dark["v"] = not is_dark["v"]
            dark_btn.icon = (
                ft.Icons.LIGHT_MODE_OUTLINED if is_dark["v"] else ft.Icons.DARK_MODE_OUTLINED
            )
            page.bgcolor = bg()
            dock_container.bgcolor = DARK_CARD if is_dark["v"] else WHITE
            top_bar.bgcolor = DARK_CARD if is_dark["v"] else WHITE
            load_page(current_index["v"])
            page.update()

        _logout_btn = ft.IconButton(
            icon=ft.Icons.LOGOUT_ROUNDED, icon_color=GREY, icon_size=22,
            tooltip="Logout", on_click=logout_click,
        )

        first = get_val("First_Name", "U")
        last  = get_val("Last_Name", "")
        initials = (first[0] + (last[0] if last else "")).upper()

        avatar = ft.Container(
            content=ft.Text(initials, size=13, weight="bold", color=WHITE),
            width=36, height=36, bgcolor=AMBER, border_radius=18,
            alignment=ft.Alignment(0, 0),
        )

        name_chip = ft.Container(
            content=ft.Row([avatar, ft.Text(f"{first} {last}".strip(), size=13,
                weight="bold", color=text(), font_family="DM Sans")], spacing=8),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=ft.Colors.with_opacity(0.08, AMBER), border_radius=20,
        )

        top_bar = ft.Container(
            content=ft.Row([
                ft.Text("RotiRouter", size=22, weight="bold",
                        font_family="Playfair", color=AMBER),
                ft.Row([name_chip, dark_btn, _logout_btn], spacing=4),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            bgcolor=WHITE,
            shadow=ft.BoxShadow(blur_radius=20,
                color=ft.Colors.with_opacity(0.08, "#000000"),
                offset=ft.Offset(0, 2)),
        )

        NAV_ITEMS = [
            {"icon": ft.Icons.RESTAURANT_MENU_ROUNDED, "label": "Menu",     "index": 0},
            {"icon": ft.Icons.HOW_TO_VOTE_ROUNDED,      "label": "Vote",     "index": 1},
            {"icon": ft.Icons.PERSON_ROUNDED,            "label": "Profile",  "index": 2},
            {"icon": ft.Icons.CALENDAR_TODAY_ROUNDED,    "label": "Mess Off", "index": 3},
        ]

        dock_items = []

        def make_dock_btn(item):
            idx = item["index"]
            is_sel = current_index["v"] == idx
            btn = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(item["icon"], size=24,
                            color=AMBER if is_sel else GREY),
                        width=48, height=48,
                        bgcolor=ft.Colors.with_opacity(0.15, AMBER) if is_sel else ft.Colors.TRANSPARENT,
                        border_radius=16, alignment=ft.Alignment(0, 0),
                        animate=ft.Animation(200, "easeOut"),
                    ),
                    ft.Text(item["label"], size=10,
                        color=AMBER if is_sel else GREY,
                        font_family="DM Sans", weight="bold" if is_sel else "normal"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=ft.Padding.symmetric(horizontal=8, vertical=8),
                on_click=lambda e, i=idx: load_page(i),
                border_radius=16, animate=ft.Animation(200, "easeOut"),
                tooltip=item["label"],
            )
            dock_items.append(btn)
            return btn

        dock_row = ft.Row(
            [make_dock_btn(item) for item in NAV_ITEMS],
            alignment=ft.MainAxisAlignment.CENTER, spacing=4,
        )

        dock_container = ft.Container(
            content=dock_row, bgcolor=WHITE, border_radius=32,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            shadow=ft.BoxShadow(blur_radius=32, spread_radius=0,
                color=ft.Colors.with_opacity(0.18, "#000000"),
                offset=ft.Offset(0, 8)),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, "#000000")),
        )

        dock_wrapper = ft.Container(
            content=dock_container, alignment=ft.Alignment(0, 0),
            padding=ft.Padding.only(bottom=20),
        )

        def refresh_dock():
            for i, item in enumerate(NAV_ITEMS):
                is_sel = current_index["v"] == item["index"]
                inner = dock_items[i].content
                icon_box = inner.controls[0]
                label    = inner.controls[1]
                icon_box.content.color = AMBER if is_sel else GREY
                icon_box.bgcolor = (
                    ft.Colors.with_opacity(0.15, AMBER) if is_sel else ft.Colors.TRANSPARENT
                )
                label.color  = AMBER if is_sel else GREY
                label.weight = "bold" if is_sel else "normal"
            dock_container.bgcolor = DARK_CARD if is_dark["v"] else WHITE
            page.update()

        def load_page(index):
            current_index["v"] = index
            page_content.content = None
            page.update()

            ud = page.current_user_data
            role = ud.get("Account_Type", "Student")

            theme = {
                "is_dark":  is_dark["v"],
                "is_guest": ud.get("is_guest", False),
                "NAVY": NAVY, "AMBER": AMBER, "CREAM": CREAM,
                "DARK_BG": DARK_BG, "DARK_CARD": DARK_CARD, "GREY": GREY,
                "WHITE": WHITE, "AMBER_DIM": AMBER_DIM,
                "NAVY_LIGHT": NAVY_LIGHT, "CREAM2": CREAM2, "DARK_CARD2": DARK_CARD2,
            }

            if role == "Admin":
                page_content.content = AdminPage(page, ud, theme).build()
                refresh_dock(); page.update(); dock_wrapper.visible = False
                return

            if role == "Staff":
                page_content.content = StaffPage(page, ud, theme).build()
                refresh_dock(); page.update(); dock_wrapper.visible = False
                return

            dock_wrapper.visible = True
            pages = [StudentHomePage, StudentVotingPage, StudentProfilePage, StudentMessOffPage]
            if 0 <= index < len(pages):
                page_content.content = pages[index](page, ud, theme).build()

            refresh_dock()
            page.update()

        body = ft.Column([
            top_bar,
            ft.Container(content=page_content, expand=True),
            dock_wrapper,
        ], spacing=0, expand=True)

        page.add(body)
        load_page(0)
        page.update()

    async def on_login(e: ft.LoginEvent):
        if e.error:
            page.add(ft.Text(f"Auth Error: {e.error}", color="red"))
            page.update()
            return

        while not (page.auth and page.auth.user):
            await asyncio.sleep(0.2)

        email = page.auth.user.get("email")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_URL}/users/verify",
                    params={"email": email},
                    timeout=10,
                )
            if response.status_code == 200:
                data = response.json()
                if "user_details" in data:
                    page.current_user_data = data["user_details"]
                    await show_dashboard()
                else:
                    raise KeyError("user_details missing")
            else:
                page.clean()
                page.add(ft.Icon(ft.Icons.GPP_BAD, color="red", size=50),
                         ft.Text("Unauthorized NUST Entity"))
        except (httpx.ConnectError, httpx.TimeoutException):
            page.clean()
            page.add(ft.Text("Cannot reach backend. Please try again later.", color="red"))
        except Exception as ex:
            page.add(ft.Text(f"Error: {str(ex)}", color="red"))

        page.update()

    page.on_login = on_login

    async def login_click(e):
        await page.login(provider, scope=["email", "profile"])

    def guest_login(role):
        mock_data.init_session()
        name_map = {"Student": ("Guest", "Student"), "Staff": ("Guest", "Staff"), "Admin": ("Guest", "Admin")}
        first, last = name_map[role]
        page.current_user_data = {
            "UserID": -1, "First_Name": first, "Last_Name": last,
            "Email": f"guest.{role.lower()}@demo.app", "Account_Type": role,
            "is_guest": True,
        }
        page.theme_mode = ft.ThemeMode.LIGHT
        page.update()
        asyncio.create_task(show_dashboard())

    def logout_click(e):
        is_dark["v"] = False
        page.current_user_data = {}
        page.auth = None
        page.clean()
        page.bgcolor = "#0D1B2A"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.add(build_landing(page, login_click, guest_login, show_register_page))
        page.update()

    register_mode = {"v": False}

    def show_landing():
        register_mode["v"] = False
        page.clean()
        page.bgcolor = "#0D1B2A"
        page.add(build_landing(page, login_click, guest_login, show_register_page))
        page.update()

    def show_register_page():
        register_mode["v"] = True
        page.clean()
        page.bgcolor = "#0D1B2A"
        page.add(build_register_form(page, None, show_landing))
        page.update()

    if page.auth and page.auth.user and hasattr(page, "current_user_data"):
        await show_dashboard()
    else:
        show_landing()
    page.update()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)
