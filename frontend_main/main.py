import flet as ft
from api_client import get_all_users

def main(page: ft.Page):
    page.title = "RotiRouter User Test"
    user_list = ft.Column()

    def handle_test_click(e):
        users = get_all_users()
        user_list.controls.clear()
        if not users:
            user_list.controls.append(ft.Text("No users found or Backend offline.", color="red"))
        for u in users:
            user_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{u['First_Name']} {u['Last_Name']}"),
                    subtitle=ft.Text(u['Email'])
                )
            )
        page.update()

    page.add(
        ft.Text("RotiRouter Connection Test", size=30, weight="bold"),
        ft.ElevatedButton("Fetch Users from Backend", on_click=handle_test_click),
        ft.Divider(),
        user_list
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)