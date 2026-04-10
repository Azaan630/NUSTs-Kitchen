import flet as ft


def main(page: ft.Page):
    page.title = "RotiRouter - Student Portal"
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Column([
            ft.Text("Welcome to RotiRouter", size=30, weight="bold"),
            ft.Text("The frontend container is running successfully!"),
            ft.ElevatedButton("Check Mess Menu", on_click=lambda _: print("Button Clicked"))
        ])
    )


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)