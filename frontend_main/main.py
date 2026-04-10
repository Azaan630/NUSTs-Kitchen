import flet as ft
# Import your client to prove the button can talk to the backend
from api_client import get_status


def main(page: ft.Page):
    # This text will update when you click the button
    status_text = ft.Text("Status: Waiting...")

    def button_clicked(e):
        # 1. Call the API
        data = get_status()
        # 2. Update the UI
        status_text.value = f"Backend says: {data.get('database')}"
        # 3. CRITICAL: Tell Flet the UI changed!
        page.update()

    page.add(
        ft.Text("RotiRouter Control", size=20),
        ft.ElevatedButton("Check Connection", on_click=button_clicked),
        status_text
    )


ft.app(target=main, port=8080, view=ft.AppView.WEB_BROWSER)