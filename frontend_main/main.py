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
    if d:
        return {
            "is_dark":  True,
            "is_guest": False,
            "bg":      SLATE_900,
            "card":    SLATE_800,
            "card2":   SLATE_700,
            "text":    SLATE_100,
            "sub":     SLATE_500,
            "accent":  SKY_400,
            "accent2": VIOLET_400,
            "success": EMERALD_400,
            "danger":  ROSE_400,
            "warn":    AMBER_400,
            # backward-compat aliases
            "NAVY":       SLATE_900,
            "AMBER":      SKY_400,
            "CREAM":      SLATE_900,
            "WHITE":      WHITE,
            "GREY":       SLATE_500,
            "DARK_BG":    SLATE_900,
            "DARK_CARD":  SLATE_800,
            "DARK_CARD2": SLATE_700,
            "NAVY_LIGHT": SLATE_800,
            "AMBER_DIM":  SKY_600,
            "CREAM2":     SLATE_700,
            # gradients
            "bg_gradient": ft.LinearGradient(
                begin=ft.Alignment(-0.3, -0.3),
                end=ft.Alignment(0.7, 0.7),
                colors=["#0F172A", "#1a1f38"],
            ),
        }
    return {
        "is_dark":  False,
        "is_guest": False,
        "bg":      "#FAF8F5",
        "card":    "#FFFFFF",
        "card2":   "#F0EDEA",
        "text":    "#1C1C1E",
        "sub":     "#8E8E93",
        "accent":  "#007AFF",
        "accent2": "#AF52DE",
        "success": "#34C759",
        "danger":  "#FF3B30",
        "warn":    "#FF9F0A",
        # backward-compat aliases
        "NAVY":       "#1C1C1E",
        "AMBER":      "#007AFF",
        "CREAM":      "#FAF8F5",
        "WHITE":      "#FFFFFF",
        "GREY":       "#8E8E93",
        "DARK_BG":    "#FAF8F5",
        "DARK_CARD":  "#FFFFFF",
        "DARK_CARD2": "#F0EDEA",
        "NAVY_LIGHT": "#E8E8E8",
        "AMBER_DIM":  "#0056B3",
        "CREAM2":     "#F0EDEA",
        # gradients
        "bg_gradient": ft.LinearGradient(
            begin=ft.Alignment(-0.3, -0.3),
            end=ft.Alignment(0.7, 0.7),
            colors=["#FAF8F5", "#F5F0EB", "#FAF8F5"],
        ),
    }


FOOD_DECOS = [
    (ft.Icons.RICE_BOWL_ROUNDED,     180, 25,  60),
    (ft.Icons.COFFEE_ROUNDED,        110, None, None, 35, 40),
    (ft.Icons.SET_MEAL_ROUNDED,      140, 50,  None, None, 160),
    (ft.Icons.DINING_ROUNDED,         90, None, None, 30, 200),
    (ft.Icons.BAKERY_DINING_ROUNDED,  70, None, 120, None, None),
    (ft.Icons.EGG_ROUNDED,            55, 160, 70),
    (ft.Icons.LOCAL_PIZZA_ROUNDED,    80, None, None, 100, 300),
    (ft.Icons.RAMEN_DINING_ROUNDED,   65, 200, None, None, 100),
    (ft.Icons.SOUP_KITCHEN_ROUNDED,   50, None, 250, None, None),
    (ft.Icons.FASTFOOD_ROUNDED,       45, 280, 180),
]

def _food_decos(accent, opacity=0.05):
    icons = []
    for deco in FOOD_DECOS:
        icon_name, size, left, top, right, bottom = (deco + (None,)*6)[:6]
        kw = {}
        if left is not None: kw["left"] = left
        if top is not None: kw["top"] = top
        if right is not None: kw["right"] = right
        if bottom is not None: kw["bottom"] = bottom
        icons.append(ft.Container(
            content=ft.Icon(icon_name, size=size, opacity=opacity, color=accent),
            **kw,
        ))
    return icons

def build_landing(page, login_click, guest_login, show_register):
    t = make_theme()
    acc = t["accent"]
    sub = t["sub"]
    d = t["is_dark"]
    m = (page.width or 1200) < 720
    grad = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#0F172A", "#1a1f38", "#151B30"] if d else ["#FFF5E6", "#F8FAFC", "#FFF8E7"],
    )

    isize = 40 if m else 64
    ibox  = 72 if m else 104
    tsize = 28 if m else 52

    guest_btns = ft.Column([
        ft.OutlinedButton(text, on_click=lambda e, r=role: guest_login(r),
            style=ft.ButtonStyle(color=t["text"],
                side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, t["text"])),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10)))
        for text, role in [("Guest Student", "Student"), ("Guest Staff", "Staff"), ("Guest Admin", "Admin")]
    ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER) if m else ft.Row([
        ft.OutlinedButton(text, on_click=lambda e, r=role: guest_login(r),
            style=ft.ButtonStyle(color=t["text"],
                side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, t["text"])),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10)))
        for text, role in [("Guest Student", "Student"), ("Guest Staff", "Staff"), ("Guest Admin", "Admin")]
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    return ft.Container(
        gradient=grad,
        content=ft.Stack([
            ft.Container(expand=True),
            *_food_decos(acc),
            ft.Container(
                content=ft.Column([
                    ft.Container(height=60 if m else 80),
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=isize, color=acc),
                        bgcolor=ft.Colors.with_opacity(0.1, acc),
                        width=ibox, height=ibox, border_radius=ibox//2,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=16 if m else 20),
                    ft.Text("NUST's Kitchen", size=tsize, weight="bold",
                            font_family="Playfair", color=t["text"]),
                    ft.Text("Mess Portal \u2022 SEECS", size=14 if m else 17, color=sub,
                            font_family="DM Sans"),
                    ft.Container(height=36 if m else 48),
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGIN_ROUNDED, color=SLATE_900, size=18),
                            ft.Text("Continue with Google", color=SLATE_900,
                                    weight="bold", font_family="DM Sans", size=14),
                        ], spacing=10, tight=True),
                        on_click=login_click,
                        style=ft.ButtonStyle(
                            bgcolor=acc,
                            padding=ft.Padding.symmetric(horizontal=36, vertical=16),
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
                    guest_btns,
                    ft.Container(height=24),
                    ft.TextButton(
                        content=ft.Text("New here? Register as Student / Staff",
                                        color=acc, size=13, font_family="DM Sans"),
                        on_click=lambda e: show_register(),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                expand=True,
            ),
        ]),
        expand=True,
    )


def build_register_form(page, on_submit, on_back):
    t = make_theme()
    acc = t["accent"]
    sub = t["sub"]
    d = t["is_dark"]
    m = (page.width or 1200) < 720
    grad = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#0F172A", "#1a1f38"] if d else ["#F8FAFC", "#FFF8E7"],
    )

    fw = 320 if not m else None  # None = expand

    role_dd = ft.Dropdown(
        label="Role",
        options=[ft.dropdown.Option("Student"), ft.dropdown.Option("Staff")],
        value="Student", width=fw if not m else None, expand=m,
        color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
        border_color=ft.Colors.with_opacity(0.3, t["text"]),
    )

    fields = {}
    for key, label, hint in [
        ("first", "First Name", "e.g. Ali"),
        ("last", "Last Name", "e.g. Khan"),
        ("email", "Email", "you@seecs.edu.pk"),
        ("dept", "Department", "CS, SE, EE"),
        ("phone", "Contact", "03XX-XXXXXXX"),
        ("address", "Address", "H-12 NUST"),
        ("father", "Father's Name", ""),
        ("hostel", "Hostel", "Ghazali"),
        ("room", "Room No.", "101"),
    ]:
        fields[key] = ft.TextField(
            label=label, hint_text=hint, width=fw, expand=m,
            color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
            border_color=ft.Colors.with_opacity(0.3, t["text"]),
            cursor_color=acc, border_radius=10,
        )

    async def pick_date(e):
        dp = ft.DatePicker(
            on_change=lambda e: (
                setattr(fields["dob"], "value", e.control.value.strftime("%Y-%m-%d")),
                fields["dob"].update(),
            )[1],
        )
        page.show_dialog(dp)

    fields["dob"] = ft.TextField(
        label="Date of Birth", hint_text="YYYY-MM-DD", width=fw, expand=m,
        color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
        border_color=ft.Colors.with_opacity(0.3, t["text"]),
        cursor_color=acc, border_radius=10, read_only=True,
        suffix=ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=pick_date),
    )

    fields["category"] = ft.TextField(
        label="Staff Category", hint_text="Chef / Server", width=fw, expand=m,
        color=t["text"], label_style=ft.TextStyle(color=sub, size=13),
        border_color=ft.Colors.with_opacity(0.3, t["text"]),
        cursor_color=acc, border_radius=10,
    )
    category_row = ft.Container(content=fields["category"], visible=role_dd.value == "Staff")

    def on_role_change(e):
        category_row.visible = role_dd.value == "Staff"
        page.update()
    role_dd.on_change = on_role_change

    msg = ft.Text("", size=13, color=acc, font_family="DM Sans")

    async def submit(e):
        for f in fields.values():
            f.error_text = ""
            f.update()
        from pages.validation import (
            validate_name, validate_email, validate_phone, validate_date_str,
            validate_hostel, validate_room, validate_address,
            validate_department, validate_category,
        )
        v_first, err = validate_name(fields["first"].value, "First Name")
        fields["first"].error_text = err
        v_last, err = validate_name(fields["last"].value, "Last Name")
        fields["last"].error_text = err
        v_email, err = validate_email(fields["email"].value)
        fields["email"].error_text = err
        v_dob, err = validate_date_str(fields["dob"].value, "Date of Birth") if fields["dob"].value else (None, None)
        if err and fields["dob"].value:
            fields["dob"].error_text = err
        v_dept, err = validate_department(fields["dept"].value)
        if err: fields["dept"].error_text = err
        v_phone, err = validate_phone(fields["phone"].value)
        if err: fields["phone"].error_text = err
        v_addr, err = validate_address(fields["address"].value)
        if err: fields["address"].error_text = err
        v_father, err = validate_name(fields["father"].value, "Father's Name") if fields["father"].value else (None, None)
        if err: fields["father"].error_text = err
        v_hostel, err = validate_hostel(fields["hostel"].value)
        if err: fields["hostel"].error_text = err
        v_room, err = validate_room(fields["room"].value)
        if err: fields["room"].error_text = err
        if category_row.visible:
            v_cat, err = validate_category(fields["category"].value)
            if err: fields["category"].error_text = err
        else:
            v_cat = None

        first_err = None
        for f in fields.values():
            if f.error_text:
                f.update()
                if not first_err:
                    first_err = f.error_text
        if first_err:
            page.snack_bar = ft.SnackBar(content=ft.Text(first_err, color="#FFF"),
                bgcolor=t["danger"], duration=4000)
            page.snack_bar.open = True
            page.update()
            return
        payload = {
            "First_Name": v_first,
            "Last_Name": v_last,
            "Email": v_email,
            "Account_Type": role_dd.value,
            "DoB": str(v_dob) if v_dob else None,
            "Department": v_dept,
            "Contact_Number": v_phone,
            "Address": v_addr,
            "Father_Name": v_father,
            "Hostel_Name": v_hostel,
            "Room_Number": v_room,
            "Category": v_cat,
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
        gradient=grad,
        content=ft.Stack([
            ft.Container(expand=True),
            ft.Container(
                content=ft.Icon(ft.Icons.SET_MEAL_ROUNDED, size=120, opacity=0.045, color=acc),
                left=15, top=60,
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.RICE_BOWL_ROUNDED, size=100, opacity=0.04, color=acc),
                right=15, bottom=100,
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.COFFEE_ROUNDED, size=70, opacity=0.035, color=acc),
                left=140, bottom=60,
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.DINING_ROUNDED, size=60, opacity=0.03, color=acc),
                right=130, top=120,
            ),
            ft.Container(
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
                    category_row,
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
                alignment=ft.Alignment(0, 0),
                expand=True,
            ),
        ]),
        expand=True,
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
        _page_bg = ft.Container(expand=True, gradient=t["bg_gradient"])
        page_content_placeholder = ft.Container(expand=True,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_OUT))
        page_content = ft.Container(
            expand=True, padding=0,
            content=ft.Stack([
                _page_bg,
                ft.Container(
                    content=ft.Icon(ft.Icons.RICE_BOWL_ROUNDED, size=150, opacity=0.035, color=t["accent"]),
                    left=20, top=30,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.COFFEE_ROUNDED, size=90, opacity=0.03, color=t["accent"]),
                    right=30, top=50,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.SET_MEAL_ROUNDED, size=120, opacity=0.025, color=t["accent"]),
                    left=40, bottom=80,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.DINING_ROUNDED, size=70, opacity=0.03, color=t["accent"]),
                    right=25, bottom=90,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.BAKERY_DINING_ROUNDED, size=55, opacity=0.02, color=t["accent"]),
                    left=120, top=200,
                ),
                page_content_placeholder,
            ]),
        )

        def toggle_dark(e):
            is_dark["v"] = not is_dark["v"]
            t = make_theme()
            page.bgcolor = t["bg"]
            top_bar.bgcolor = t["card"]
            dock_container.bgcolor = t["card"]
            _page_bg.gradient = t["bg_gradient"]
            load_page(current_index["v"])
            page.update()

        dark_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED, icon_color=t["text"], icon_size=20,
            tooltip="Toggle theme", on_click=lambda e: toggle_dark(e),
        )

        # ── Overlay helpers (toggle-based, no stacking) ──
        _active_overlay = [None]

        async def _remove_overlay(fast=False):
            o = _active_overlay[0]
            if o and o in page.controls:
                o.opacity = 0
                page.update()
                await asyncio.sleep(0.08 if fast else 0.2)
                if o in page.controls:
                    page.remove(o)
            _active_overlay[0] = None
            page.update()

        def _show_overlay(content, open_ms=250):
            async def close_overlay(e):
                await _remove_overlay()
            o = ft.Container(
                content=content, bgcolor=ft.Colors.with_opacity(0.4, "#000"),
                alignment=ft.Alignment(0, 0), expand=True,
                on_click=close_overlay,
                animate_opacity=ft.Animation(open_ms, ft.AnimationCurve.EASE_OUT),
                opacity=0,
            )
            page.add(o)
            _active_overlay[0] = o
            page.update()
            o.opacity = 1
            page.update()

        def _confirm_dialog(title, msg, on_confirm):
            async def do_cancel(e):
                await _remove_overlay(fast=True)
            async def do_confirm(e):
                await _remove_overlay(fast=True)
                on_confirm()
            card = ft.Container(
                content=ft.Column([
                    ft.Text(title, weight="bold", size=17, color=t["text"],
                            font_family="DM Sans"),
                    ft.Container(height=6),
                    ft.Text(msg, size=13, color=t["sub"], font_family="DM Sans"),
                    ft.Container(height=16),
                    ft.Row([
                        ft.TextButton("Cancel", on_click=do_cancel,
                            style=ft.ButtonStyle(color=t["sub"])),
                        ft.FilledButton("Confirm",
                            style=ft.ButtonStyle(bgcolor=t["danger"]),
                            on_click=do_confirm),
                    ], alignment=ft.MainAxisAlignment.END, spacing=8),
                ], tight=True, spacing=4),
                bgcolor=t["card"], border_radius=18, padding=24, width=340,
                shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
            )
            _show_overlay(card)

        async def logout_click(e):
            is_dark["v"] = True
            page.current_user_data = {}
            page.clean()
            page.bgcolor = SLATE_900
            page.theme_mode = ft.ThemeMode.DARK
            page.add(build_landing(page, login_click, guest_login, show_register_page))
            page.update()

        async def show_profile_popup(e):
            await _remove_overlay()
            email = get_val("Email", "")
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                avatar,
                                ft.Column([
                                    ft.Text(f"{first} {last}".strip(), weight="bold", size=15,
                                            color=t["text"], font_family="DM Sans"),
                                    ft.Text(email, size=12, color=t["sub"], font_family="DM Sans"),
                                ], spacing=0, tight=True),
                            ], spacing=10),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.CLOSE_ROUNDED, size=18, color=t["sub"]),
                            on_click=lambda e: asyncio.create_task(_remove_overlay()),
                            padding=4, border_radius=8,
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=12, color=ft.Colors.with_opacity(0.1, t["text"])),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=16, color=t["danger"]),
                            ft.Text("Logout", size=13, weight="bold", color=t["danger"],
                                    font_family="DM Sans"),
                        ], spacing=8),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                        border_radius=10,
                        on_click=lambda e: asyncio.create_task(_do_logout()),
                    ),
                ], tight=True, spacing=4),
                bgcolor=t["card"], border_radius=18, padding=20, width=280,
                shadow=ft.BoxShadow(blur_radius=24, color="#00000055"),
            )
            _show_overlay(card, 380)

        async def _do_logout():
            await _remove_overlay()
            _confirm_dialog(
                "Logout", "Are you sure you want to log out?",
                lambda: asyncio.create_task(logout_click(None)),
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
            on_click=show_profile_popup,
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
                ft.Row([name_chip, dark_btn], spacing=2),
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
            page_content_placeholder.content = None
            page_content_placeholder.opacity = 0
            page.update()
            ud = page.current_user_data
            role = ud.get("Account_Type", "Student")
            theme = make_theme()
            theme["is_guest"] = ud.get("is_guest", False)

            if role == "Admin":
                page_content_placeholder.content = AdminPage(page, ud, theme).build()
                refresh_dock(); page.update(); dock_wrapper.visible = False
                page_content_placeholder.opacity = 1; page.update()
                return
            if role == "Staff":
                page_content_placeholder.content = StaffPage(page, ud, theme).build()
                refresh_dock(); page.update(); dock_wrapper.visible = False
                page_content_placeholder.opacity = 1; page.update()
                return

            dock_wrapper.visible = True
            pages = [StudentHomePage, StudentVotingPage, StudentProfilePage, StudentMessOffPage]
            if 0 <= index < len(pages):
                page_content_placeholder.content = pages[index](page, ud, theme).build()
            refresh_dock()
            page.update()
            page_content_placeholder.opacity = 1
            page.update()

        body = ft.Column([
            top_bar,
            ft.Container(content=page_content, expand=True),
            dock_wrapper,
        ], spacing=0, expand=True)

        page.on_resized = lambda e: load_page(current_index["v"])
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
        landing = build_landing(page, login_click, guest_login, show_register_page)
        landing.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_OUT)
        landing.opacity = 0
        landing.scale = 0.92
        landing.animate_scale = ft.Animation(600, ft.AnimationCurve.EASE_OUT)
        page.add(landing)
        page.update()
        landing.opacity = 1
        landing.scale = 1.0
        page.update()

    def show_register_page():
        register_mode["v"] = True
        page.clean()
        page.bgcolor = SLATE_900
        reg = build_register_form(page, None, show_landing)
        reg.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_OUT)
        reg.animate_scale = ft.Animation(500, ft.AnimationCurve.EASE_OUT)
        reg.opacity = 0
        reg.scale = 0.95
        page.add(reg)
        page.update()
        reg.opacity = 1
        reg.scale = 1.0
        page.update()

    if page.auth and page.auth.user and page.current_user_data:
        await show_dashboard()
    else:
        page.current_user_data = {}
        show_landing()
    page.update()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)
