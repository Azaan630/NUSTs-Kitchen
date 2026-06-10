import flet as ft
import asyncio
from pages.api_client import get_active_poll, cast_vote


class StudentVotingPage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email   = user_data.get("Email", "")
        self.user_id = int(user_data.get("UserID", 0))
        self.P = theme["P"]
        is_dark = theme["is_dark"]
        self.bg      = self.P.BG_DARK if is_dark else self.P.BG_LIGHT
        self.card_bg = self.P.SURFACE if is_dark else self.P.WHITE
        self.txt_c   = self.P.TEXT_LIGHT if is_dark else self.P.TEXT_DARK
        self.sub_c   = self.P.MUTED if is_dark else self.P.MUTED_LIGHT

        self.main_container = ft.Container(expand=True)
        self._voted = set()

    def _loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.P.PRIMARY, width=40, height=40, stroke_width=3),
                ft.Text("Checking for active polls...", color=self.sub_c, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0), expand=True, padding=60,
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

            result = await cast_vote(item_id, self.user_id, self.email)

            if result and "error" not in result:
                self._voted.add(item_id)
                btn_refs["btn"].disabled = True
                btn_refs["btn"].content.controls[0].name  = ft.Icons.CHECK_CIRCLE_ROUNDED
                btn_refs["btn"].content.controls[0].color = self.P.SUCCESS
                btn_refs["btn"].content.controls[1].value = "Voted!"
                btn_refs["btn"].content.controls[1].color = self.P.SUCCESS
                btn_refs["btn"].style.bgcolor = ft.Colors.with_opacity(0.1, self.P.SUCCESS)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Vote cast!", color="#FFF"), bgcolor=self.P.SUCCESS,
                )
                self.page.snack_bar.open = True
            else:
                err = result.get("error", "Already voted") if result else "Already voted"
                btn_refs["btn"].disabled = False
                btn_refs["btn"].content.controls[0].name = ft.Icons.HOW_TO_VOTE_ROUNDED
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(err, color="#FFF"), bgcolor=self.P.WARNING,
                )
                self.page.snack_bar.open = True
            self.page.update()

        vote_btn = ft.FilledButton(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE_ROUNDED if voted else ft.Icons.HOW_TO_VOTE_ROUNDED,
                    size=18, color=self.P.SUCCESS if voted else self.P.PRIMARY_LT,
                ),
                ft.Text(
                    "Voted!" if voted else "Vote", size=13, weight="bold",
                    font_family="DM Sans", color=self.P.SUCCESS if voted else self.P.PRIMARY_LT,
                ),
            ], spacing=6, tight=True),
            disabled=voted,
            on_click=handle_vote,
            style=ft.ButtonStyle(
                bgcolor=(
                    ft.Colors.with_opacity(0.1, self.P.SUCCESS) if voted
                    else ft.Colors.with_opacity(0.12, self.P.PRIMARY)
                ),
                elevation=0, shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=10),
            ),
        )
        btn_refs["btn"] = vote_btn

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.SET_MEAL_ROUNDED, size=22, color=self.P.PRIMARY_LT),
                    width=48, height=48,
                    bgcolor=ft.Colors.with_opacity(0.12, self.P.PRIMARY),
                    border_radius=14, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(item.get("Name", "Item"), size=15, weight="bold",
                            color=self.txt_c, font_family="DM Sans"),
                    ft.Text(f"PKR {item.get('Price', '—')}", size=12,
                            color=self.sub_c, font_family="DM Sans"),
                ], expand=True, spacing=4),
                vote_btn,
            ], spacing=14),
            bgcolor=self.card_bg, border_radius=18,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.06, "#000"), offset=ft.Offset(0, 2)),
            border=ft.Border.all(1, (
                ft.Colors.with_opacity(0.2, self.P.SUCCESS) if voted
                else ft.Colors.with_opacity(0.08, self.P.WHITE)
            )),
            animate=ft.Animation(200, "easeOut"),
        )

    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        poll_data = await get_active_poll(self.email)

        if isinstance(poll_data, dict) and "error" in poll_data:
            body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=self.P.ERROR, size=40),
                    ft.Text(poll_data["error"], color=self.P.ERROR, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0), padding=60,
            )
        elif not poll_data.get("active", False):
            body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HOURGLASS_EMPTY_ROUNDED, size=64, color=self.sub_c),
                    ft.Text("No active poll right now", size=18, weight="bold",
                            color=self.txt_c, font_family="DM Sans"),
                    ft.Text("Check back when the mess admin opens voting", size=14,
                            color=self.sub_c, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0), padding=60,
            )
        else:
            items = poll_data.get("items", [])
            cards = [self._poll_card(item) for item in items]

            info_strip = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=self.P.PRIMARY_LT),
                    ft.Text(
                        "Vote for what you want in tomorrow's menu. One vote per item.",
                        size=12, color=self.sub_c, font_family="DM Sans",
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.with_opacity(0.08, self.P.PRIMARY),
                border_radius=10, padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                margin=ft.Margin.only(bottom=16),
            )
            body = ft.Column([info_strip] + cards, spacing=0)

        self.main_container.content = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Vote", size=28, weight="bold", color=self.txt_c, font_family="DM Sans"),
                    ft.Text("Help shape tomorrow's menu", size=13, color=self.sub_c, font_family="DM Sans"),
                ]),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED, icon_color=self.sub_c,
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
            content=self.main_container, bgcolor=self.bg, expand=True,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
        )
