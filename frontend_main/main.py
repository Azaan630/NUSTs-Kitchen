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

# ══════════════════════════════════════════════════════════════════
#  COLOUR PALETTE — dark default, minimalist modern
# ══════════════════════════════════════════════════════════════════
SLATE_900 = "#0F172A"
SLATE_800 = "#1E293B"
SLATE_700 = "#334155"
SLATE_600 = "#475569"
SLATE_500 = "#64748B"
SLATE_400 = "#94A3B8"
SLATE_200 = "#E2E8F0"
SLATE_100 = "#F1F5F9"
SLATE_50  = "#F8FAFC"
SKY_400   = "#38BDF8"
SKY_600   = "#0284C7"
VIOLET_400= "#A78BFA"
EMERALD_400= "#34D399"
ROSE_400  = "#FB7185"
AMBER_400 = "#FBBF24"
WHITE     = "#FFFFFF"

is_dark = {"v": True}

def make_theme():
    d = is_dark["v"]
    return {
        "is_dark":  d,
        "is_guest": False,
        "bg":      SLATE_900 if d else SLATE_50,
        "card":    SLATE_800 if d else WHITE,
        "card2":   SLATE_700 if d else SLATE_200,
        "text":    SLATE_100 if d else SLATE_900,
        "sub":     SLATE_500,
        "accent":  SKY_400,
        "accent2": VIOLET_400,
        "success": EMERALD_400,
        "danger":  ROSE_400,
        "warn":    AMBER_400,
        # backward-compat aliases so all pages work without rewriting
        "NAVY":       SLATE_900,
        "AMBER":      SKY_400,
        "CREAM":      SLATE_900 if d else SLATE_50,
        "WHITE":      WHITE,
        "GREY":       SLATE_500,
        "DARK_BG":    SLATE_900 if d else SLATE_50,
        "DARK_CARD":  SLATE_800 if d else WHITE,
        "DARK_CARD2": SLATE_700 if d else SLATE_200,
        "NAVY_LIGHT": SLATE_800,
        "AMBER_DIM":  SKY_600,
        "CREAM2":     SLATE_700 if d else SLATE_200,
    }


def build_landing(page, login_click, guest_login, show_register):
    t = make_theme()
    bg  = t["DARK_BG"]
    acc = t["accent"]
    sub = t["sub"]

    return ft.Container(
        content=ft.Column([
            ft.Container(height=80),
            ft.Container(
                content=ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=56, color=acc),
                bgcolor=ft.Colors.with_opacity(0.1, acc),
                width=96, height=96, border_radius=48,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=20),
            ft.Text("NUST's Kitchen", size=40, weight="bold",
                    font_family="Playfair", color=t["text"]),
            ft.Text("Mess Portal \u2022 SEECS", size=14, color=sub,
                    font_family="DM Sans"),
            ft.Container(height=48),
            ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOGIN_ROUNDED, color=SLATE_900, size=18),
                    ft.Text("Continue with Google", color=SLATE_900,
                            weight="bold", font_family="DM Sans", size=14),
                ], spacing=10, tight=True),
                on_click=login_click,
                style=ft.ButtonStyle(
                    bgcolor=acc, padding=ft.Padding.symmetric(horizontal=36, vertical=16),
                    shape=ft.RoundedRectangleBorder(radius=12), elevation=0,
                ),
            ),
            ft.Container(height=16),
            ft.Row([
                ft.Container(height=1, bgcolor=sub, expand=True),
                ft.Container(
                    content=ft.Text("or", size=12, color=sub, font_family="DM Sans"),
                    padding=ft.Padding.symmetric(horizontal=12),
                ),
                ft.Container(height=1, bgcolor=sub, expand=True),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=16),
            ft.Row([
                ft.OutlinedButton(text, on_click=lambda e, r=text: guest_login(r),
                    style=ft.ButtonStyle(color=t["text"],
                        side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, t["text"])),
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10)))
                for text in ["Guest Student", "Guest Staff", "Guest Admin"]
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            ft.Container(height=24),
            ft.TextButton(
                content=ft.Text("New here? Register as Student / Staff",
                                color=acc, size=13, font_family="DM Sans"),
                on_click=lambda e: show_register(),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment(0, 0), expand=True,
    )


def build_register_form(page, on_submit, on_back):
    t = make_theme()
    acc = t["accent"]
    sub = t["sub"]

    role_dd = ft.Dropdown(
        label="Role",
        options=[ft.dropdown.Option("Student"), ft.dropdown.Option("Staff")],
        value="Student", width=320,
        color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
        border_color=ft.Colors.with_opacity(0.3, t["text"]),
    )

    fields = {}
    for key, label, hint in [
        ("first", "First Name", "e.g. Ali"),
        ("last", "Last Name", "e.g. Khan"),
        ("email", "Email", "you@seecs.edu.pk"),
        ("dob", "Date of Birth", "YYYY-MM-DD"),
        ("dept", "Department", "CS, SE, EE"),
        ("phone", "Contact", "03XX-XXXXXXX"),
        ("address", "Address", "H-12 NUST"),
        ("father", "Father's Name", ""),
        ("hostel", "Hostel", "Ghazali"),
        ("room", "Room No.", "101"),
        ("category", "Staff Category", "Chef / Server"),
    ]:
        fields[key] = ft.TextField(
            label=label, hint_text=hint, width=320,
            color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
            border_color=ft.Colors.with_opacity(0.3, t["text"]),
            cursor_color=acc, border_radius=10,
        )

    msg = ft.Text("", size=13, color=acc, font_family="DM Sans")

    async def submit(e):
        for f in fields.values():
            f.error_text = ""
            f.update()
        if not fields["first"].value or not fields["last"].value or not fields["email"].value:
            msg.value = "First Name, Last Name, and Email are required"
            msg.update(); return
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
                resp = await client.post(f"{BACKEND_URL}/register/request", json=payload, timeout=10)
            if resp.status_code == 200:
                msg.value = "Request submitted! Awaiting admin approval."
                msg.color = t["success"]
                for f in fields.values(): f.value = ""
            else:
                msg.value = f"Error: {resp.json().get('detail', 'Unknown error')}"
                msg.color = t["danger"]
        except (httpx.ConnectError, httpx.TimeoutException):
            msg.value = "Backend unreachable. Try again later."
            msg.color = t["danger"]
        msg.update()

    return ft.Container(
        content=ft.Column([
            ft.Container(height=40),
            ft.Container(
                content=ft.Icon(ft.Icons.PERSON_ADD_ALT_1_ROUNDED, size=36, color=acc),
                bgcolor=ft.Colors.with_opacity(0.1, acc),
                width=64, height=64, border_radius=32, alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=16),
            ft.Text("Create Account", size=26, weight="bold",
                    font_family="Playfair", color=t["text"]),
            ft.Text("Admin will review your request", size=13, color=sub, font_family="DM Sans"),
            ft.Container(height=20),
            role_dd, ft.Container(height=4),
            *[fields[k] for k in ["first", "last", "email"]],
            ft.Container(height=12),
            fields["category"],
            *[fields[k] for k in ["dob", "dept", "phone", "address", "father", "hostel", "room"]],
            ft.Container(height=12),
            msg,
            ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.SEND_ROUNDED, color=SLATE_900, size=16),
                    ft.Text("Submit Request", color=SLATE_900, weight="bold",
                            font_family="DM Sans", size=14),
                ], spacing=8, tight=True),
                on_click=submit,
                style=ft.ButtonStyle(bgcolor=acc,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding.symmetric(horizontal=32, vertical=14), elevation=0),
            ),
            ft.Container(height=8),
            ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, color=acc, size=16),
                    ft.Text("Back to Login", color=acc, size=13, font_family="DM Sans"),
                ], spacing=4, tight=True),
                on_click=lambda e: on_back(),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
        alignment=ft.Alignment(0, 0), expand=True,
    )


async def main(page: ft.Page):
    page.title = "RotiRouter | NUST SEECS"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.fonts = {
        "Playfair": "https://fonts.gstatic.com/s/playfairdisplay/v37/nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2",
        "DM Sans": "https://fonts.gstatic.com/s/dmsans/v14/rP2Hp2ywxg089UriCZa4ET-DNl0.woff2",
    }

    provider = ft.auth.GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        redirect_url=os.getenv("OAUTH_REDIRECT_URL", "http://localhost:8550/oauth_callback"),
    )

    def get_val(key, default="N/A"):
        return getattr(page, "current_user_data", {}).get(key, default)

    async def show_dashboard():
        page.clean()
        t = make_theme()
        page.bgcolor = t["bg"]
        page.update()

        current_index = {"v": 0}
        page_content = ft.Container(expand=True, padding=0)

        def toggle_dark(e):
            is_dark["v"] = not is_dark["v"]
            t = make_theme()
            page.bgcolor = t["bg"]
            top_bar.bgcolor = t["card"]
            dock_container.bgcolor = t["card"]
            load_page(current_index["v"])
            page.update()

        dark_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED, icon_color=t["text"], icon_size=20,
            tooltip="Toggle theme", on_click=lambda e: toggle_dark(e),
        )

        async def logout_click(e):
            is_dark["v"] = True
            page.current_user_data = {}
            page.clean()
            page.bgcolor = SLATE_900
            page.theme_mode = ft.ThemeMode.DARK
            page.add(build_landing(page, login_click, guest_login, show_register_page))
            page.update()

        _logout_btn = ft.IconButton(
            icon=ft.Icons.LOGOUT_ROUNDED, icon_color=t["sub"], icon_size=20,
            tooltip="Logout", on_click=lambda e: asyncio.create_task(logout_click(e)),
        )

        first = get_val("First_Name", "U")
        last  = get_val("Last_Name", "")
        initials = (first[0] + (last[0] if last else "")).upper()

        avatar = ft.Container(
            content=ft.Text(initials, size=12, weight="bold", color=WHITE),
            width=32, height=32, bgcolor=t["accent"], border_radius=16,
            alignment=ft.Alignment(0, 0),
        )

        name_chip = ft.Container(
            content=ft.Row([avatar, ft.Text(f"{first} {last}".strip(), size=13,
                weight="bold", color=t["text"], font_family="DM Sans")], spacing=8),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.08, t["accent"]), border_radius=16,
        )

        top_bar = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=18, color=t["accent"]),
                        bgcolor=ft.Colors.with_opacity(0.12, t["accent"]),
                        width=32, height=32, border_radius=8, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("RotiRouter", size=20, weight="bold",
                            font_family="Playfair", color=t["accent"]),
                ], spacing=10),
                ft.Row([name_chip, dark_btn, _logout_btn], spacing=2),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding.symmetric(horizontal=20, vertical=8),
            bgcolor=t["card"],
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
                        content=ft.Icon(item["icon"], size=22,
                            color=t["accent"] if is_sel else t["sub"]),
                        width=44, height=44,
                        bgcolor=ft.Colors.with_opacity(0.12, t["accent"]) if is_sel else ft.Colors.TRANSPARENT,
                        border_radius=14, alignment=ft.Alignment(0, 0),
                        animate=ft.Animation(200, "easeOut"),
                    ),
                    ft.Text(item["label"], size=9,
                        color=t["accent"] if is_sel else t["sub"],
                        font_family="DM Sans", weight="bold" if is_sel else "normal"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                on_click=lambda e, i=idx: load_page(i),
                border_radius=14,
                tooltip=item["label"],
            )
            dock_items.append(btn)
            return btn

        dock_row = ft.Row(
            [make_dock_btn(item) for item in NAV_ITEMS],
            alignment=ft.MainAxisAlignment.CENTER, spacing=4,
        )

        dock_container = ft.Container(
            content=dock_row, bgcolor=t["card"], border_radius=28,
            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
        )

        dock_wrapper = ft.Container(
            content=dock_container, alignment=ft.Alignment(0, 0),
            padding=ft.Padding.only(bottom=16),
        )

        def refresh_dock():
            t = make_theme()
            for i, item in enumerate(NAV_ITEMS):
                is_sel = current_index["v"] == item["index"]
                inner = dock_items[i].content
                icon_box = inner.controls[0]
                label    = inner.controls[1]
                icon_box.content.color = t["accent"] if is_sel else t["sub"]
                icon_box.bgcolor = (
                    ft.Colors.with_opacity(0.12, t["accent"]) if is_sel else ft.Colors.TRANSPARENT
                )
                label.color  = t["accent"] if is_sel else t["sub"]
                label.weight = "bold" if is_sel else "normal"
            dock_container.bgcolor = t["card"]
            page.update()

        def load_page(index):
            current_index["v"] = index
            page_content.content = None
            page.update()
            ud = page.current_user_data
            role = ud.get("Account_Type", "Student")
            theme = make_theme()
            theme["is_guest"] = ud.get("is_guest", False)

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
            page.add(ft.Text(f"Auth Error: {e.error}", color=ROSE_400))
            page.update()
            return
        while not (page.auth and page.auth.user):
            await asyncio.sleep(0.2)
        email = page.auth.user.get("email")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BACKEND_URL}/users/verify", params={"email": email}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "user_details" in data:
                    page.current_user_data = data["user_details"]
                    await show_dashboard()
                else:
                    raise KeyError("user_details missing")
            else:
                page.clean()
                page.add(ft.Icon(ft.Icons.GPP_BAD, color=ROSE_400, size=50),
                         ft.Text("Unauthorized NUST Entity"))
        except (httpx.ConnectError, httpx.TimeoutException):
            page.clean()
            page.add(ft.Text("Cannot reach backend. Please try again later.", color=ROSE_400))
        except Exception as ex:
            page.add(ft.Text(f"Error: {str(ex)}", color=ROSE_400))
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
        asyncio.create_task(show_dashboard())

    register_mode = {"v": False}

    def show_landing():
        register_mode["v"] = False
        page.clean()
        page.bgcolor = SLATE_900
        page.add(build_landing(page, login_click, guest_login, show_register_page))
        page.update()

    def show_register_page():
        register_mode["v"] = True
        page.clean()
        page.bgcolor = SLATE_900
        page.add(build_register_form(page, None, show_landing))
        page.update()

    if page.auth and page.auth.user and page.current_user_data:
        await show_dashboard()
    else:
        page.current_user_data = {}
        show_landing()
    page.update()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)
