import flet as ft
import os
import asyncio
from dotenv import load_dotenv
import requests
from pages.home_page import StudentHomePage
from pages.profile_page import StudentProfilePage
from pages.voting_page import StudentVotingPage
from pages.mess_off_page import StudentMessOffPage
from pages.admin_page import AdminPage
from pages.staff_page import StaffPage

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


# ─── Colour palette (cool modern) ─────────────────────────────────────────────

class Palette:
    SURFACE     = "#1C1D32"  # Glass card (dark)
    BG_DARK     = "#0B0C1A"  # Deep space
    BG_LIGHT    = "#F0F2F5"  # Clean off-white
    WHITE       = "#FFFFFF"
    TEXT_DARK   = "#0F172A"  # Slate-900
    TEXT_LIGHT  = "#E2E8F0"  # Slate-200
    MUTED       = "#64748B"  # Slate-500
    MUTED_LIGHT = "#94A3B8"

    PRIMARY     = "#7C3AED"  # Violet-600
    PRIMARY_LT  = "#A78BFA"  # Violet-400
    SECONDARY   = "#6366F1"  # Indigo-500
    ACCENT      = "#06B6D4"  # Cyan-500
    ACCENT2     = "#EC4899"  # Pink-500

    SUCCESS     = "#10B981"
    WARNING     = "#F59E0B"
    ERROR       = "#EF4444"


P = Palette


async def main(page: ft.Page):
    page.title = "RotiRouter | NUST SEECS"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.fonts = {
        "Playfair": "https://fonts.gstatic.com/s/playfairdisplay/v37/nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2",
        "DM Sans":  "https://fonts.gstatic.com/s/dmsans/v14/rP2Hp2ywxg089UriCZa4ET-DNl0.woff2",
    }

    is_dark = {"v": True}

    def bg():    return P.BG_DARK  if is_dark["v"] else P.BG_LIGHT
    def card():  return P.SURFACE  if is_dark["v"] else P.WHITE
    def txt():   return P.TEXT_LIGHT if is_dark["v"] else P.TEXT_DARK
    def muted(): return P.MUTED    if is_dark["v"] else P.MUTED_LIGHT

    provider = ft.auth.GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        redirect_url=os.getenv("OAUTH_REDIRECT_URL", "http://localhost:8550/oauth_callback"),
    )

    # ─── Theme helpers ──────────────────────────────────────────────────────

    def theme_dict():
        return {
            "is_dark": is_dark["v"],
            "bg": bg, "card": card, "txt": txt, "muted": muted,
            "P": P,
        }

    def glass(bgcolor=None, border_color=None):
        return ft.Container(
            bgcolor=bgcolor or ft.Colors.with_opacity(0.08, P.WHITE),
            border_radius=16,
            border=ft.Border.all(
                0.5,
                border_color or ft.Colors.with_opacity(0.12, P.WHITE),
            ),
        )

    # ─── Top bar ───────────────────────────────────────────────────────────

    def build_top_bar(role, on_logout, on_dark_toggle):
        first = page.current_user_data.get("First_Name", "U")
        last  = page.current_user_data.get("Last_Name", "")
        initials = (first[0] + (last[0] if last else "")).upper()

        avatar = ft.Container(
            content=ft.Text(initials, size=14, weight="bold", color=P.WHITE),
            width=38, height=38,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=[P.PRIMARY, P.ACCENT2],
            ),
            border_radius=19,
            alignment=ft.Alignment(0, 0),
            animate=ft.Animation(300, "easeOut"),
        )

        name_text = ft.Text(
            f"{first} {last}".strip(),
            size=13, weight="bold", color=txt(), font_family="DM Sans",
        )

        role_chip = ft.Container(
            content=ft.Text(role, size=9, weight="bold", color=P.WHITE),
            bgcolor=ft.Colors.with_opacity(0.2, P.ACCENT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
        )

        popup_menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE_ROUNDED, size=18, color=muted()),
                        ft.Text("Dark Mode", size=13, color=txt(), font_family="DM Sans"),
                    ], spacing=10),
                    on_click=on_dark_toggle,
                ),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=P.ERROR),
                        ft.Text("Logout", size=13, color=P.ERROR, font_family="DM Sans"),
                    ], spacing=10),
                    on_click=on_logout,
                ),
            ],
            menu_position=ft.PopupMenuPosition.UNDER,
        )

        popup_menu.content = ft.Container(
            content=ft.Row([
                avatar,
                ft.Column([name_text, role_chip], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=4, vertical=4),
        )

        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ROUTER_ROUNDED, size=24, color=P.PRIMARY_LT),
                        width=40, height=40,
                        bgcolor=ft.Colors.with_opacity(0.15, P.PRIMARY),
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("RotiRouter", size=20, weight="bold",
                                font_family="Playfair", color=P.WHITE if is_dark["v"] else P.TEXT_DARK),
                        ft.Text("NUST SEECS", size=10, color=muted(), font_family="DM Sans"),
                    ], spacing=0),
                ], spacing=12),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.DARK_MODE_OUTLINED if is_dark["v"] else ft.Icons.LIGHT_MODE_OUTLINED,
                        icon_color=P.WHITE if is_dark["v"] else P.TEXT_DARK,
                        icon_size=20,
                        tooltip="Toggle theme",
                        on_click=on_dark_toggle,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.08, P.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding.all(8),
                        ),
                    ),
                    popup_menu,
                ], spacing=8),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding.symmetric(horizontal=24, vertical=10),
            bgcolor=ft.Colors.with_opacity(0.6, P.SURFACE) if is_dark["v"] else P.WHITE,
            border_radius=0,
        )

    # ─── Tab bar for admin / staff ──────────────────────────────────────────

    def build_tab_bar(tabs, active_idx, on_select):
        items = []
        for i, (label, icon) in enumerate(tabs):
            selected = active_idx == i
            items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=16,
                                color=P.WHITE if selected else muted()),
                        ft.Text(label, size=12, font_family="DM Sans",
                                weight="bold" if selected else "normal",
                                color=P.WHITE if selected else muted()),
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                    bgcolor=(
                        ft.LinearGradient(
                            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                            colors=[P.PRIMARY, P.SECONDARY],
                        ) if selected else ft.Colors.TRANSPARENT
                    ),
                    border_radius=12,
                    on_click=lambda e, idx=i: on_select(idx),
                    animate=ft.Animation(200, "easeOut"),
                    ink=True,
                )
            )
        return ft.Container(
            content=ft.Row(items, spacing=4, scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding.symmetric(horizontal=24, vertical=8),
            bgcolor=None,
        )

    # ─── Student bottom dock ────────────────────────────────────────────────

    NAV_ITEMS = [
        {"icon": ft.Icons.RESTAURANT_MENU_ROUNDED, "label": "Menu",    "index": 0},
        {"icon": ft.Icons.HOW_TO_VOTE_ROUNDED,     "label": "Vote",    "index": 1},
        {"icon": ft.Icons.PERSON_ROUNDED,          "label": "Profile", "index": 2},
        {"icon": ft.Icons.CALENDAR_TODAY_ROUNDED,  "label": "Mess Off","index": 3},
    ]

    def build_student_dock(current_idx, on_select):
        items = []
        for item in NAV_ITEMS:
            sel = current_idx == item["index"]
            items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(
                                item["icon"],
                                size=22,
                                color=P.WHITE if sel else muted(),
                            ),
                            width=44, height=44,
                            bgcolor=(
                                ft.LinearGradient(
                                    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                                    colors=[P.PRIMARY, P.ACCENT],
                                ) if sel else ft.Colors.TRANSPARENT
                            ),
                            border_radius=14,
                            alignment=ft.Alignment(0, 0),
                            animate=ft.Animation(250, "easeOut"),
                        ),
                        ft.Text(
                            item["label"],
                            size=9, font_family="DM Sans",
                            weight="bold" if sel else "normal",
                            color=P.PRIMARY_LT if sel else muted(),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                    padding=ft.Padding.symmetric(horizontal=6, vertical=6),
                    on_click=lambda e, i=item["index"]: on_select(i),
                    animate=ft.Animation(200, "easeOut"),
                )
            )
        return ft.Container(
            content=ft.Row(items, alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
            margin=ft.Margin.only(bottom=16, left=40, right=40),
            bgcolor=ft.Colors.with_opacity(0.75, P.SURFACE) if is_dark["v"] else P.WHITE,
            border_radius=24,
            border=ft.Border.all(0.5, ft.Colors.with_opacity(0.15, P.WHITE)),
            shadow=ft.BoxShadow(
                blur_radius=40, spread_radius=0,
                color=ft.Colors.with_opacity(0.3, "#000000"),
                offset=ft.Offset(0, 8),
            ),
        )

    # ─── Dashboard ─────────────────────────────────────────────────────────

    async def show_dashboard():
        page.clean()
        page.bgcolor = bg()
        page.update()

        ud = page.current_user_data
        role = ud.get("Account_Type", "Student")

        current_tab = {"v": 0}
        content_area = ft.Container(expand=True, padding=0)

        def handle_logout(e):
            page.client_storage.remove("auth_email")
            page.clean()
            page.add(ft.Text("Logged out.", color=P.MUTED))
            page.update()
            import sys
            sys.exit(0)

        def toggle_theme(e):
            is_dark["v"] = not is_dark["v"]
            page.theme_mode = ft.ThemeMode.DARK if is_dark["v"] else ft.ThemeMode.LIGHT
            page.bgcolor = bg()
            rebuild()
            page.update()

        def rebuild():
            page.clean()
            page.bgcolor = bg()

            top = build_top_bar(role, handle_logout, toggle_theme)

            if role == "Admin":
                tabs = AdminPage.TABS
                bar = build_tab_bar(tabs, current_tab["v"], lambda idx: switch_admin(idx))

                def switch_admin(idx):
                    current_tab["v"] = idx
                    bar.content.controls = build_tab_bar(tabs, idx, lambda i: switch_admin(i)).content.controls
                    load_admin_content(idx)
                    page.update()

                def load_admin_content(idx):
                    ap = AdminPage(page, ud, theme_dict())
                    renderer = getattr(ap, ap.RENDERERS[idx])
                    asyncio.create_task(renderer(content_area))

                page.add(
                    ft.Column([
                        top,
                        bar,
                        ft.Container(content=content_area, expand=True, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    ], spacing=0, expand=True)
                )
                load_admin_content(0)
                page.update()
                return

            if role == "Staff":
                tabs = StaffPage.TABS
                bar = build_tab_bar(tabs, current_tab["v"], lambda idx: switch_staff(idx))

                def switch_staff(idx):
                    current_tab["v"] = idx
                    bar.content.controls = build_tab_bar(tabs, idx, lambda i: switch_staff(i)).content.controls
                    load_staff_content(idx)
                    page.update()

                def load_staff_content(idx):
                    sp = StaffPage(page, ud, theme_dict())
                    renderer = getattr(sp, sp.RENDERERS[idx])
                    asyncio.create_task(renderer(content_area))

                page.add(
                    ft.Column([
                        top,
                        bar,
                        ft.Container(content=content_area, expand=True, padding=ft.Padding.symmetric(horizontal=20, vertical=8)),
                    ], spacing=0, expand=True)
                )
                load_staff_content(0)
                page.update()
                return

            # ── Student ─────────────────────────────────────────────
            dock = build_student_dock(current_tab["v"], lambda idx: switch_student(idx))
            page_content = ft.Container(expand=True)

            def switch_student(idx):
                current_tab["v"] = idx
                new_dock = build_student_dock(idx, lambda i: switch_student(i))
                dock.content = new_dock.content
                load_student_content(idx)

            def load_student_content(idx):
                pages = [StudentHomePage, StudentVotingPage, StudentProfilePage, StudentMessOffPage]
                cls = pages[idx]
                instance = cls(page, ud, theme_dict())
                page_content.content = instance.build()
                page.update()

            page.add(
                ft.Column([
                    top,
                    ft.Container(content=page_content, expand=True),
                    dock,
                ], spacing=0, expand=True)
            )
            load_student_content(0)
            page.update()

        rebuild()

    # ─── Auth flow ─────────────────────────────────────────────────────────

    async def on_login(e: ft.LoginEvent):
        if e.error:
            page.add(ft.Text(f"Auth Error: {e.error}", color=P.ERROR))
            page.update()
            return

        while not (page.auth and page.auth.user):
            await asyncio.sleep(0.2)

        email = page.auth.user.get("email")

        try:
            response = requests.get(
                f"{BACKEND_URL}/users/verify",
                params={"email": email},
                timeout=5,
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
                page.add(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.GPP_BAD, color=P.ERROR, size=60),
                            ft.Text("Unauthorized NUST Entity", color=P.ERROR, font_family="DM Sans"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.Alignment(0, 0), expand=True,
                        bgcolor=P.BG_DARK,
                    )
                )
        except Exception as ex:
            page.add(ft.Text(f"System Crash: {str(ex)}", color=P.ERROR))

        page.update()

    page.on_login = on_login

    async def login_click(e):
        await page.login(provider, scope=["email", "profile"])

    # ── Landing page ───────────────────────────────────────────────────────

    if page.auth and page.auth.user and hasattr(page, "current_user_data"):
        await show_dashboard()
    else:
        page.bgcolor = P.BG_DARK
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Container(height=40),

                    # Logo glow
                    ft.Container(
                        content=ft.Container(
                            content=ft.Icon(ft.Icons.ROUTER_ROUNDED, size=56, color=P.WHITE),
                            width=100, height=100,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                                colors=[P.PRIMARY, P.ACCENT2],
                            ),
                            border_radius=30,
                            alignment=ft.Alignment(0, 0),
                            shadow=ft.BoxShadow(
                                blur_radius=60, spread_radius=10,
                                color=ft.Colors.with_opacity(0.35, P.PRIMARY),
                            ),
                        ),
                        padding=10,
                    ),

                    ft.Container(height=24),

                    ft.Text(
                        "RotiRouter",
                        size=48, weight="bold",
                        font_family="Playfair",
                        color=P.WHITE,
                    ),
                    ft.Text(
                        "NUST SEECS Mess Portal",
                        size=16, color=P.MUTED, font_family="DM Sans",
                    ),

                    ft.Container(height=48),

                    ft.Container(
                        content=ft.FilledButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LOGIN_ROUNDED, color=P.WHITE, size=18),
                                ft.Text(
                                    "Continue with Google",
                                    color=P.WHITE, weight="bold",
                                    font_family="DM Sans", size=15,
                                ),
                            ], spacing=10, tight=True),
                            on_click=login_click,
                            style=ft.ButtonStyle(
                                color=P.WHITE,
                                bgcolor=ft.Colors.TRANSPARENT,
                                padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                                shape=ft.RoundedRectangleBorder(radius=14),
                                elevation=0,
                                overlay_color=ft.Colors.with_opacity(0.1, P.WHITE),
                            ),
                        ),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                            colors=[P.PRIMARY, P.SECONDARY, P.ACCENT2],
                        ),
                        border_radius=14,
                        animate=ft.Animation(200, "easeOut"),
                        on_hover=lambda e: setattr(e.control, "scale", ft.transform.Scale(1.03) if e.data == "true" else ft.transform.Scale(1.0)),
                    ),

                    ft.Container(height=80),

                    ft.Row([
                        ft.Column([
                            ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=28, color=P.PRIMARY_LT),
                            ft.Text("Today's Menu", size=12, color=P.MUTED, font_family="DM Sans"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                        ft.Column([
                            ft.Icon(ft.Icons.HOW_TO_VOTE_ROUNDED, size=28, color=P.ACCENT),
                            ft.Text("Vote", size=12, color=P.MUTED, font_family="DM Sans"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                        ft.Column([
                            ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=28, color=P.ACCENT2),
                            ft.Text("Bills", size=12, color=P.MUTED, font_family="DM Sans"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),

                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0), expand=True,
            )
        )

    page.update()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)
