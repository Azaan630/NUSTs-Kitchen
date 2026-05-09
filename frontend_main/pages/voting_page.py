import flet as ft
import asyncio
from pages.api_client import get_active_poll, cast_vote


class StudentVotingPage:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user_data = user_data
        self.user_id = int(user_data.get("UserID", 0))
        self.poll_container = ft.Container(
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
        )
        self.loading_text = ft.Text("Checking for active polls...", color=ft.Colors.GREY_600)

    async def load_poll(self):
        """Fetches active poll data and updates UI"""
        # Show loading
        self.poll_container.content = ft.Column([
            ft.Row([ft.ProgressRing(), self.loading_text], alignment=ft.MainAxisAlignment.CENTER)
        ])
        self.page.update()

        # Fetch poll
        poll_data = await get_active_poll()

        if "error" in poll_data:
            self.poll_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                ft.Text(f"Failed to load poll: {poll_data['error']}", color=ft.Colors.RED)
            ])
            self.page.update()
            return

        # If no active poll
        if not poll_data.get("active", False):
            self.poll_container.content = ft.Column([
                ft.Icon(ft.Icons.HOURGLASS_TOP, size=50, color=ft.Colors.GREY_400),
                ft.Text("No active poll right now.", size=16, color=ft.Colors.GREY),
                ft.Text("Check back later when the mess admin opens voting.", size=14, color=ft.Colors.GREY_500)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.page.update()
            return

        items = poll_data.get("items", [])
        if not items:
            self.poll_container.content = ft.Column([
                ft.Text("Active poll has no items yet.", size=16, color=ft.Colors.GREY)
            ])
            self.page.update()
            return

        # Build card for each food item
        poll_cards = []
        for item in items:
            # Placeholder for price - some items might not have price but usually work with menu UX
            card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(item.get("Name", "Unknown"), weight="bold", size=16),
                        ft.Text(f"PKR {item.get('Price', 0)}", size=14, color=ft.Colors.GREY_600)
                    ], expand=True),
                    ft.ElevatedButton(
                        content=ft.Text("Vote", weight="bold"),
                        icon=ft.Icons.THUMB_UP,
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.DEFAULT: ft.Colors.GREEN_700},
                            color={ft.ControlState.DEFAULT: ft.Colors.WHITE}
                        ),
                        data=item.get("Item_ID"),
                        on_click=self.handle_vote
                    )
                ]),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
                padding=15,
                margin=ft.margin.symmetric(vertical=5),
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300)
            )
            poll_cards.append(card)

        # Build Final UI
        self.poll_container.content = ft.Column(
            [
                ft.Text("🗳️ Vote for tomorrow's menu!", size=18, weight="bold", color=ft.Colors.BLUE_900),
                ft.Container(height=10),
                ft.Column(poll_cards, scroll=ft.ScrollMode.ADAPTIVE),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("Refresh Poll"),
                    icon=ft.Icons.REFRESH,
                    on_click=self.load_poll
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        self.page.update()

    async def handle_vote(self, e):
        item_id = e.control.data
        # Show loading state on the clicked button
        e.control.disabled = True
        self.page.update()

        # Cast vote
        result = await cast_vote(item_id, self.email)

        # Reset button
        e.control.disabled = False

        # Show result
        if result.get("success"):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Vote cast successfully!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            # Refresh poll data to update state if needed
            await self.load_poll()
        else:
            error_msg = result.get("error", "Failed to cast vote")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {error_msg}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700
            )
            self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        asyncio.create_task(self.load_poll())
        return ft.Container(
            content=ft.Column([
                ft.Text("Voting", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                self.poll_container
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            expand=True
        )