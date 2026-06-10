import flet as ft
import asyncio
import calendar
from datetime import date, datetime
from pages.api_client import request_mess_off, cancel_mess_off, get_mess_off_history


class StudentMessOffPage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.user_id = int(user_data.get("UserID", 0))
        self.email   = user_data.get("Email", "")
        self.P = theme["P"]
        is_dark = theme["is_dark"]
        self.bg      = self.P.BG_DARK if is_dark else self.P.BG_LIGHT
        self.card_bg = self.P.SURFACE if is_dark else self.P.WHITE
        self.card2_bg = ft.Colors.with_opacity(0.05, self.P.WHITE)
        self.txt_c   = self.P.TEXT_LIGHT if is_dark else self.P.TEXT_DARK
        self.sub_c   = self.P.MUTED if is_dark else self.P.MUTED_LIGHT

        self.main_container = ft.Container(expand=True)

    def _loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.P.PRIMARY, width=40, height=40, stroke_width=3),
                ft.Text("Loading mess off data...", color=self.sub_c, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0), expand=True, padding=60,
        )

    def _calc_remaining(self, requests):
        today       = date.today()
        month_start = date(today.year, today.month, 1)
        month_end   = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        total = 0
        for req in requests:
            if req.get("Status") != "Approved":
                continue
            try:
                start = datetime.strptime(req["Start_Date"], "%Y-%m-%d").date()
                end   = datetime.strptime(req["End_Date"],   "%Y-%m-%d").date()
                if start > month_end or end < month_start:
                    continue
                os_ = max(start, month_start)
                oe_ = min(end, month_end)
                d   = (oe_ - os_).days + 1
                if d > 0:
                    total += d
            except:
                continue
        return max(12 - total, 0)

    def _status_chip(self, status):
        colours = {
            "Approved":  (self.P.SUCCESS, ft.Colors.with_opacity(0.12, self.P.SUCCESS)),
            "Pending":   (self.P.WARNING, ft.Colors.with_opacity(0.12, self.P.WARNING)),
            "Rejected":  (self.P.ERROR, ft.Colors.with_opacity(0.12, self.P.ERROR)),
            "Cancelled": (self.sub_c, ft.Colors.with_opacity(0.05, self.P.WHITE)),
        }
        fg, bg = colours.get(status, (self.sub_c, ft.Colors.with_opacity(0.05, self.P.WHITE)))
        return ft.Container(
            content=ft.Text(status, size=11, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

    def _request_card(self, req, on_cancel):
        status      = req.get("Status", "Pending")
        mess_off_id = req.get("Mess_Off_ID")

        cancel_btn = ft.Container()
        if status == "Pending":
            cancel_btn = ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL_ROUNDED, size=14, color=self.P.ERROR),
                    ft.Text("Cancel", size=12, color=self.P.ERROR, font_family="DM Sans"),
                ], spacing=4, tight=True),
                on_click=lambda e, mid=mess_off_id: asyncio.create_task(on_cancel(mid)),
                style=ft.ButtonStyle(padding=ft.Padding.all(4)),
            )

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=20, color=self.P.PRIMARY_LT),
                    width=44, height=44,
                    bgcolor=ft.Colors.with_opacity(0.12, self.P.PRIMARY),
                    border_radius=12, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(f"{req.get('Start_Date','?')} \u2192 {req.get('End_Date','?')}",
                                size=14, weight="bold", color=self.txt_c, font_family="DM Sans"),
                        self._status_chip(status),
                    ], spacing=8),
                    ft.Text(
                        f"Requested: {req.get('Request_Date', req.get('Start_Date','?'))}  \u2022  ID #{mess_off_id}",
                        size=11, color=self.sub_c, font_family="DM Sans",
                    ),
                ], expand=True, spacing=4),
                cancel_btn,
            ], spacing=12),
            bgcolor=self.card_bg, border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, "#000"), offset=ft.Offset(0, 2)),
            border=ft.Border.all(0.5, ft.Colors.with_opacity(0.1, self.P.WHITE)),
        )

    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        result = await get_mess_off_history(self.email)
        requests = []
        if isinstance(result, dict) and "status" in result:
            requests = result["status"] if isinstance(result["status"], list) else []
        elif isinstance(result, list):
            requests = result

        remaining = self._calc_remaining(requests)

        used     = 12 - remaining
        fraction = used / 12
        quota_card = ft.Container(
            content=ft.Row([
                ft.Stack([
                    ft.Container(
                        content=ft.ProgressRing(
                            value=fraction, color=self.P.PRIMARY,
                            bgcolor=ft.Colors.with_opacity(0.15, self.P.PRIMARY),
                            width=64, height=64, stroke_width=6,
                        ),
                    ),
                    ft.Container(
                        content=ft.Text(str(remaining), size=18, weight="bold",
                                        color=self.P.PRIMARY_LT, font_family="DM Sans"),
                        width=64, height=64, alignment=ft.Alignment(0, 0),
                    ),
                ]),
                ft.Column([
                    ft.Text("Days remaining this month", size=14, weight="bold",
                            color=self.txt_c, font_family="DM Sans"),
                    ft.Text(f"{used} used of 12 allowed", size=12,
                            color=self.sub_c, font_family="DM Sans"),
                ], spacing=4, expand=True),
            ], spacing=16),
            bgcolor=ft.Colors.with_opacity(0.05, self.P.WHITE),
            border_radius=18, padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            margin=ft.Margin.only(bottom=20),
        )

        start_field = ft.TextField(
            label="Start Date", hint_text="YYYY-MM-DD", expand=True,
            border_color=self.P.PRIMARY, focused_border_color=self.P.PRIMARY_LT,
            label_style=ft.TextStyle(color=self.sub_c, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self.txt_c, font_family="DM Sans"),
            border_radius=12, filled=True, fill_color=self.card_bg,
        )
        end_field = ft.TextField(
            label="End Date", hint_text="YYYY-MM-DD", expand=True,
            border_color=self.P.PRIMARY, focused_border_color=self.P.PRIMARY_LT,
            label_style=ft.TextStyle(color=self.sub_c, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self.txt_c, font_family="DM Sans"),
            border_radius=12, filled=True, fill_color=self.card_bg,
        )

        async def submit(e):
            try:
                start = date.fromisoformat(start_field.value.strip())
                end   = date.fromisoformat(end_field.value.strip())
            except:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Invalid date format - use YYYY-MM-DD", color="#FFF"),
                    bgcolor=self.P.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            if start > end:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Start date must be before end date", color="#FFF"),
                    bgcolor=self.P.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            result = await request_mess_off(self.user_id, start, end, self.email)

            if isinstance(result, dict) and "error" in result:
                msg, colour = result["error"], self.P.ERROR
            else:
                msg = result.get("message", "Request submitted!") if isinstance(result, dict) else "Submitted!"
                colour = self.P.SUCCESS
                start_field.value = ""
                end_field.value   = ""
                asyncio.create_task(self._render())

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="#FFF"), bgcolor=colour,
            )
            self.page.snack_bar.open = True
            self.page.update()

        submit_btn = ft.Container(
            content=ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.SEND_ROUNDED, size=16, color=self.P.WHITE),
                    ft.Text("Submit", size=13, weight="bold", color=self.P.WHITE, font_family="DM Sans"),
                ], spacing=8, tight=True),
                on_click=submit,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TRANSPARENT, elevation=0,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                ),
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=[self.P.PRIMARY, self.P.SECONDARY],
            ),
            border_radius=12,
        )

        form_card = ft.Container(
            content=ft.Column([
                ft.Text("New Request", size=15, weight="bold",
                        color=self.txt_c, font_family="DM Sans"),
                ft.Container(height=8),
                ft.Row([start_field, end_field], spacing=10),
                ft.Container(height=10),
                ft.Row([submit_btn], alignment=ft.MainAxisAlignment.END),
                ft.Text(
                    "Max 12 days per month. Approved requests will deduct from your quota.",
                    size=11, color=self.sub_c, font_family="DM Sans",
                ),
            ], spacing=0),
            bgcolor=self.card_bg, border_radius=18,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            margin=ft.Margin.only(bottom=20),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, "#000"), offset=ft.Offset(0, 2)),
        )

        async def handle_cancel(mid):
            result = await cancel_mess_off(mid, self.email)
            if isinstance(result, dict) and "error" in result:
                msg, colour = result["error"], self.P.ERROR
            else:
                msg = result.get("message", "Cancelled") if isinstance(result, dict) else "Cancelled"
                colour = self.P.SUCCESS
                asyncio.create_task(self._render())
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="#FFF"), bgcolor=colour,
            )
            self.page.snack_bar.open = True
            self.page.update()

        if not requests:
            history_body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX_ROUNDED, size=40, color=self.sub_c),
                    ft.Text("No requests this month", color=self.sub_c, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.Alignment(0, 0), padding=40,
            )
        else:
            history_body = ft.Column(
                [self._request_card(r, handle_cancel) for r in requests], spacing=0
            )

        self.main_container.content = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Mess Off", size=28, weight="bold", color=self.txt_c, font_family="DM Sans"),
                    ft.Text("Manage your meal absences", size=13, color=self.sub_c, font_family="DM Sans"),
                ]),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED, icon_color=self.sub_c,
                    tooltip="Refresh",
                    on_click=lambda e: asyncio.create_task(self._render()),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            quota_card,
            form_card,
            ft.Text("Your Requests", size=16, weight="bold",
                    color=self.txt_c, font_family="DM Sans"),
            ft.Container(height=8),
            history_body,
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()

    def build(self):
        asyncio.create_task(self._render())
        return ft.Container(
            content=self.main_container, bgcolor=self.bg, expand=True,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
        )
