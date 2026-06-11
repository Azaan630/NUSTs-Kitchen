import flet as ft
import asyncio
from pages.api_client import get_active_poll, cast_vote
import mock_data


class StudentVotingPage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email   = user_data.get("Email", "")
        self.user_id = int(user_data.get("UserID", 0))
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.bg    = t["DARK_BG"]    if t["is_dark"] else t["CREAM"]
        self.card  = t["DARK_CARD"]  if t["is_dark"] else t["WHITE"]
        self.card2 = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt   = t["WHITE"]      if t["is_dark"] else t["NAVY"]
        self.sub   = t["GREY"]
        self.amber = t["AMBER"]
        self.navy  = t["NAVY"]

        self.main_container = ft.Container(expand=True)
        self._voted = set()

    def _guest_banner(self):
        if not self.is_guest:
            return ft.Container()
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18, color=self.navy),
                ft.Text(
                    "Guest Mode \u2014 Changes are temporary and reset on logout. "
                    "This is a demo sandbox, not real data.",
                    size=12, color=self.navy, font_family="DM Sans", expand=True,
                ),
            ], spacing=10),
            bgcolor="#FEF3C7", border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=12),
        )

    def _loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.amber, width=40, height=40, stroke_width=3),
                ft.Text("Checking for active polls…", color=self.sub, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=60,
        )

    def _poll_card(self, item):
        item_id  = item.get("Item_ID")
        voted    = item_id in self._voted
        btn_refs = {}

        async def handle_vote(e):
            if voted:
                return
            btn_refs["btn"].disabled = True
            btn_refs["btn"].content.controls[0].name = ft.Icons.HOURGLASS_TOP_ROUNDED
            self.page.update()

            if self.is_guest:
                mock_data.cast_vote(item_id, self.user_id)
                result = {"message": "Vote cast"}
            else:
                result = await cast_vote(item_id, self.user_id, self.email)

            if result and "error" not in result:
                self._voted.add(item_id)
                btn_refs["btn"].disabled = True
                btn_refs["btn"].content.controls[0].name  = ft.Icons.CHECK_CIRCLE_ROUNDED
                btn_refs["btn"].content.controls[0].color = "#10B981"
                btn_refs["btn"].content.controls[1].value = "Voted!"
                btn_refs["btn"].content.controls[1].color = "#10B981"
                btn_refs["btn"].style.bgcolor = ft.Colors.with_opacity(0.1, "#10B981")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("🗳️ Vote cast!", color="#FFF"), bgcolor="#10B981"
                )
                self.page.snack_bar.open = True
            else:
                err = result.get("error", "Already voted") if result else "Already voted"
                btn_refs["btn"].disabled = False
                btn_refs["btn"].content.controls[0].name = ft.Icons.HOW_TO_VOTE_ROUNDED
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"⚠️ {err}", color="#FFF"), bgcolor="#F59E0B"
                )
                self.page.snack_bar.open = True
            self.page.update()

        vote_btn = ft.FilledButton(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE_ROUNDED if voted else ft.Icons.HOW_TO_VOTE_ROUNDED,
                    size=18,
                    color="#10B981" if voted else self.amber,
                ),
                ft.Text(
                    "Voted!" if voted else "Vote",
                    size=13,
                    weight="bold",
                    font_family="DM Sans",
                    color="#10B981" if voted else self.amber,
                ),
            ], spacing=6, tight=True),
            disabled=voted,
            on_click=handle_vote,
            style=ft.ButtonStyle(
                bgcolor=(
                    ft.Colors.with_opacity(0.1, "#10B981") if voted
                    else ft.Colors.with_opacity(0.12, self.amber)
                ),
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=10),
            ),
        )
        btn_refs["btn"] = vote_btn

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.SET_MEAL_ROUNDED, size=22, color=self.amber),
                    width=48, height=48,
                    bgcolor=ft.Colors.with_opacity(0.12, self.amber),
                    border_radius=14,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(
                        item.get("Name", "Item"),
                        size=15,
                        weight="bold",
                        color=self.txt,
                        font_family="DM Sans",
                    ),
                    ft.Text(
                        f"PKR {item.get('Price', '—')}",
                        size=12,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], expand=True, spacing=4),
                vote_btn,
            ], spacing=14),
            bgcolor=self.card,
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.with_opacity(0.06, "#000"),
                offset=ft.Offset(0, 2),
            ),
            border=ft.Border.all(
                1,
                ft.Colors.with_opacity(0.2, "#10B981") if voted
                else ft.Colors.with_opacity(0.06, "#000"),
            ),
            animate=ft.Animation(200, "easeOut"),
        )

    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        if self.is_guest:
            poll_data = mock_data.get_active_poll()
        else:
            poll_data = await get_active_poll(self.email)

        if not self.is_guest and isinstance(poll_data, dict) and "error" in poll_data:
            body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#EF4444", size=40),
                    ft.Text(poll_data["error"], color="#EF4444", font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0),
                padding=60,
            )
        elif not poll_data.get("active", False):
            body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HOURGLASS_EMPTY_ROUNDED, size=64, color=self.sub),
                    ft.Text(
                        "No active poll right now",
                        size=18,
                        weight="bold",
                        color=self.txt,
                        font_family="DM Sans",
                    ),
                    ft.Text(
                        "Check back when the mess admin opens voting",
                        size=14,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0),
                padding=60,
            )
        else:
            items = poll_data.get("items", [])
            cards = [self._poll_card(item) for item in items]

            info_strip = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=self.amber),
                    ft.Text(
                        "Vote for what you want in tomorrow's menu. One vote per item.",
                        size=12,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.with_opacity(0.08, self.amber),
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                margin=ft.Margin.only(bottom=16),
            )
            body = ft.Column([info_strip] + cards, spacing=0)

        self.main_container.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Column([
                    ft.Text("Vote", size=28, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text("Help shape tomorrow's menu", size=13, color=self.sub, font_family="DM Sans"),
                ]),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color=self.sub,
                    tooltip="Refresh",
                    on_click=lambda e: asyncio.create_task(self._render()),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            body,
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()

    def build(self):
        asyncio.create_task(self._render())
        return ft.Container(
            content=self.main_container,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
        )