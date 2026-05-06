import flet as ft
import asyncio
from api_client import get_todays_menu


class StudentHomePage:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user_data = user_data
        self.email = user_data.get("Email")
        self.menu_container = ft.Container(
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
        )
        self.loading_text = ft.Text("Fetching Today's Menu...", color=ft.Colors.GREY_600)

    async def load_menu(self):
        """Fetches menu data and updates UI"""
        # Show Loading
        self.menu_container.content = ft.Column([
            ft.Row([ft.ProgressRing(), self.loading_text], alignment=ft.MainAxisAlignment.CENTER)
        ])
        self.page.update()

        # Fetch Data
        menu_data = await get_todays_menu(self.email)

        if "error" in menu_data:
            self.menu_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                ft.Text(f"Failed to load menu: {menu_data['error']}", color=ft.Colors.RED)
            ])
            self.page.update()
            return

        # Build Menu UI
        menu_items = menu_data.get("menu", [])
        date_str = menu_data.get("date", "Today")

        if not menu_items:
            self.menu_container.content = ft.Column([
                ft.Text("No menu items available for today.", size=16, color=ft.Colors.GREY)
            ])
            self.page.update()
            return

        # Create Cards for each Food Item
        menu_cards = []
        for item in menu_items:
            # Pick random icons based on name for visual fun
            icon_name = ft.Icons.RICE_BOWL
            if "biryani" in item["Name"].lower():
                icon_name = ft.Icons.LOCAL_DINING
            elif "daal" in item["Name"].lower():
                icon_name = ft.Icons.GRAIN
            elif "tea" in item["Name"].lower():
                icon_name = ft.Icons.COFFEE
            elif "chicken" in item["Name"].lower():
                icon_name = ft.Icons.CHICKEN
            elif "paratha" in item["Name"].lower():
                icon_name = ft.Icons.CROISSANT

            card = ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(icon_name, color=ft.Colors.BLUE_700, size=35),
                    title=ft.Text(item["Name"], weight="bold", size=16),
                    subtitle=ft.Text(f"⭐ Rating: {item.get('Rating', 'N/A')} / 5.0"),
                    trailing=ft.Container(
                        content=ft.Text(f"ID: #{item['Item_ID']}", size=12, color=ft.Colors.GREY_500),
                        bgcolor=ft.Colors.GREY_200,
                        padding=5,
                        border_radius=5
                    )
                ),
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                margin=ft.margin.symmetric(vertical=5),
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300)
            )
            menu_cards.append(card)

        # Build Final UI
        self.menu_container.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.BLUE_900),
                ft.Text(f"Menu for: {date_str}", size=20, weight="bold")
            ]),
            ft.Container(height=10),
            ft.Column(menu_cards, scroll=ft.ScrollMode.ADAPTIVE),
            ft.Container(height=20),
            ft.ElevatedButton(
                text="Refresh Menu",
                icon=ft.Icons.REFRESH,
                on_click=self.refresh_menu
            )
        ], scroll=ft.ScrollMode.ADAPTIVE)
        self.page.update()

    async def refresh_menu(self, e):
        await self.load_menu()

    def build(self):
        """Constructs the page UI"""
        asyncio.create_task(self.load_menu())

        return ft.Container(
            content=ft.Column([
                ft.Text("Today's Menu", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                self.menu_container
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            expand=True
        )