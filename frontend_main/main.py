import flet as ft
import os
import asyncio
from dotenv import load_dotenv
import requests

load_dotenv()

# --- CONFIGURATION ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


async def main(page: ft.Page):
    # Initial Page Setup
    page.title = "RotiRouter | NUST SEECS"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    # Provider setup
    provider = ft.auth.GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_url="http://localhost:8550/oauth_callback",
    )

    # --- DEFENSIVE DATA RETRIEVAL ---
    def get_user_data():
        return getattr(page, "current_user_data", {})

    def get_val(key, default="N/A"):
        return get_user_data().get(key, default)

    # --- PERSISTENT UI ELEMENT: THE STATUS BAR ---
    # We define this globally so the tester can reach it
    status_icon = ft.Icon(ft.Icons.SHIELD_OUTLINED, color=ft.Colors.GREY_400)
    status_text = ft.Text("System Standby: Awaiting Bouncer Check", weight="bold")

    status_bar = ft.Container(
        content=ft.Row([status_icon, status_text], alignment=ft.MainAxisAlignment.CENTER),
        padding=15,
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        animate=ft.Animation(400, "decelerate")
    )

    # --- CORE LOGIC: BACKEND TESTER ---
    async def run_rbac_test(e):
        route = e.control.data
        email = get_val("Email", None)

        if not email:
            status_text.value = "ERROR: Email missing from session"
            status_bar.bgcolor = ft.Colors.RED_100
            page.update()
            return

        # 1. Loading State
        e.control.disabled = True
        status_text.value = f"Contacting Bouncer for {route}..."
        status_bar.bgcolor = ft.Colors.BLUE_50
        status_icon.name = ft.Icons.SYNC
        status_icon.color = ft.Colors.BLUE_400
        page.update()

        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(
                None,
                lambda: requests.get(f"{BACKEND_URL}/test/{route}", params={"email": email}, timeout=5)
            )

            # 2. Update UI based on Response
            if res.status_code == 200:
                status_text.value = f"PERMITTED: Access granted to {route}!"
                status_bar.bgcolor = ft.Colors.GREEN_100
                status_icon.name = ft.Icons.VERIFIED_USER
                status_icon.color = ft.Colors.GREEN_700
            elif res.status_code == 403:
                status_text.value = "BANNED: Bouncer says your role is insufficient."
                status_bar.bgcolor = ft.Colors.RED_100
                status_icon.name = ft.Icons.GPP_BAD
                status_icon.color = ft.Colors.RED_700
            else:
                status_text.value = f"SERVER ERROR: Status Code {res.status_code}"
                status_bar.bgcolor = ft.Colors.ORANGE_100
                status_icon.name = ft.Icons.WARNING_AMBER
                status_icon.color = ft.Colors.ORANGE_700

        except Exception as ex:
            status_text.value = f"CONNECTION FAILED: {str(ex)}"
            status_bar.bgcolor = ft.Colors.RED_100
            status_icon.name = ft.Icons.DANGEROUS

        # 3. Restore Button
        e.control.disabled = False
        page.update()

    # --- UI COMPONENT: DASHBOARD ---
    async def show_dashboard():
        page.clean()

        user_role = str(get_val("Account_Type", "Student")).upper()
        full_name = f"{get_val('First_Name', 'User')} {get_val('Last_Name', '')}".strip()

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label="Home"),
                ft.NavigationRailDestination(icon=ft.Icons.RESTAURANT_MENU_ROUNDED, label="Menu"),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_SUGGEST_ROUNDED,
                    label="Admin"
                ) if user_role == "ADMIN" else ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Profile"),
            ],
            bgcolor=ft.Colors.GREY_50,
        )

        content_view = ft.Container(
            content=ft.Column([
                ft.Text(f"Welcome, {full_name}", size=32, weight="bold", color=ft.Colors.BLUE_900),
                ft.Text(f"Identity Verified | Role: {user_role}", color=ft.Colors.GREY_600),
                ft.Divider(height=30),

                # The Status Banner is now at the top of the action area
                status_bar,

                ft.Container(height=20),
                ft.Text("Security Bouncer Verification", size=20, weight="w600"),
                ft.Row([
                    ft.FilledButton(
                        content=ft.Text("Test Admin Gate"),
                        icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                        data="admin-only",
                        on_click=run_rbac_test,
                        style=ft.ButtonStyle(bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_900})
                    ),
                    ft.OutlinedButton(
                        content=ft.Text("Test Any Authorized"),
                        icon=ft.Icons.LOCK_OPEN_ROUNDED,
                        data="any-authorized",
                        on_click=run_rbac_test,
                    ),
                ], spacing=15),

                ft.Container(height=30),
                ft.Text("Session Meta (Read-Only)", size=14, weight="bold", color=ft.Colors.GREY_500),
                ft.Container(
                    content=ft.Text(f"{get_user_data()}", size=12, font_family="monospace"),
                    padding=15,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                )
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            expand=True
        )

        page.add(
            ft.Row([rail, ft.VerticalDivider(width=1), content_view], expand=True)
        )
        page.update()

    # --- AUTHENTICATION HANDLERS ---
    async def on_login(e: ft.LoginEvent):
        if e.error:
            page.add(ft.Text(f"Auth Error: {e.error}", color="red"))
            page.update()
            return

        while not (page.auth and page.auth.user):
            await asyncio.sleep(0.2)

        email = page.auth.user.get("email")

        try:
            response = requests.get(f"{BACKEND_URL}/users/verify", params={"email": email}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "user_details" in data:
                    page.current_user_data = data["user_details"]
                    await show_dashboard()
                else:
                    raise KeyError("user_details missing")
            else:
                page.clean()
                page.add(ft.Icon(ft.Icons.GPP_BAD, color="red", size=50), ft.Text("Unauthorized NUST Entity"))
        except Exception as ex:
            page.add(ft.Text(f"System Crash: {str(ex)}", color="red"))

        page.update()

    page.on_login = on_login

    async def login_click(e):
        await page.login(provider, scope=["email", "profile"])

    # --- INITIAL VIEW ---
    if page.auth and page.auth.user and hasattr(page, "current_user_data"):
        await show_dashboard()
    else:
        page.add(
            ft.Column([
                ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=100, color=ft.Colors.BLUE_900),
                ft.Text("RotiRouter", size=50, weight="bold", color=ft.Colors.BLUE_900),
                ft.Container(height=20),
                ft.FilledButton(
                    content=ft.Text("Login with Google"),
                    icon=ft.Icons.LOGIN,
                    on_click=login_click,
                    width=300,
                    height=50
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)