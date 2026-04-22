import flet as ft
import os
import asyncio
from dotenv import load_dotenv
import requests

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


async def main(page: ft.Page):
    page.title = "RotiRouter | NUST"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    provider = ft.auth.GoogleOAuthProvider(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_url="http://localhost:8550/oauth_callback",
    )

    async def show_authenticated_ui(user_name):
        page.clean()

        # 1. Try to grab the data we supposedly saved
        # We use getattr as a safety net
        saved_user = getattr(page, "current_user_data", "NOT FOUND")

        # 2. Display it directly on the screen
        page.add(
            ft.Text(f"Welcome, {user_name}!", size=30, weight="bold"),
            ft.Divider(),
            ft.Text("SESSION DATA CHECK:", color="blue", weight="bold"),

            # If this shows the full dictionary, your 'Direct Attribute' trick is 100% working
            ft.Text(f"{saved_user}", color="green" if saved_user != "NOT FOUND" else "red"),

            ft.ElevatedButton("Logout", on_click=lambda _: page.logout())
        )
        page.update()

    async def on_login(e: ft.LoginEvent):
        if e.error:
            page.add(ft.Text(f"Login error: {e.error}", color="red"))
            page.update()
            return

        # Wait for user object to populate
        for _ in range(10):
            if page.auth and page.auth.user:
                break
            await asyncio.sleep(0.5)

        if page.auth and page.auth.user:
            user_email = page.auth.user.get("email")

            # Use a simple HTTP GET request with the email as a query param
            # This matches the new backend signature: /users/verify?email=...
            try:
                # We use the BACKEND_URL from your env
                backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
                response = requests.get(f"{backend_url}/users/verify", params={"email": user_email})

                if response.status_code == 200:
                    data = response.json()

                    # --- ADD THE LOGIC HERE ---
                    user_data = data["user_details"]

                    # page.session is like a private locker for this specific user tab
                    page.current_user_data = user_data
                    page.is_authenticated = True

                    # Now use the data we just stored to greet them
                    first = user_data.get("First_Name", "Student")
                    last = user_data.get("Last_Name", "")
                    full_name = f"{first} {last}".strip()

                    await show_authenticated_ui(full_name)
                elif response.status_code == 403:
                    page.clean()
                    page.add(ft.Icon(ft.Icons.BLOCK, color="red"), ft.Text("Not Registered in NUST Mess System"))
                else:
                    page.add(ft.Text(f"Error: {response.status_code}", color="orange"))
            except Exception as ex:
                page.add(ft.Text(f"Connection Failed: {ex}", color="red"))

        page.update()

    page.on_login = on_login

    async def login_click(e):
        await page.login(provider, scope=["email", "profile"])

    # Initial UI Logic
    if page.auth and page.auth.user:
        await show_authenticated_ui(page.auth.user.get("name", "Student"))
    else:
        page.add(
            ft.Text("RotiRouter", size=45, weight="bold", color="blue800"),
            ft.Text("NUST Mess Management", size=16),
            ft.Container(height=20),
            ft.FilledButton("Sign in with Google", icon=ft.Icons.LOGIN, on_click=login_click)
        )
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)