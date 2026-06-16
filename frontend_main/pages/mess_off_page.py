import flet as ft
import asyncio
import calendar
from datetime import date, datetime
from pages.api_client import request_mess_off, cancel_mess_off, get_mess_off_history
import mock_data


class StudentMessOffPage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.user_id = int(user_data.get("UserID", 0))
        self.email   = user_data.get("Email", "")
        self.is_guest = theme.get("is_guest", False)

        t = theme
        self.bg    = t["DARK_BG"]    if t["is_dark"] else t["CREAM"]
        self.card  = t["DARK_CARD"]  if t["is_dark"] else t["WHITE"]
        self.card2 = t["DARK_CARD2"] if t["is_dark"] else t["CREAM2"]
        self.txt   = t["WHITE"]      if t["is_dark"] else t["NAVY"]
        self.sub   = t["GREY"]
        self.amber = t["AMBER"]
        self.navy  = t["NAVY"]

        self.main_container = ft.Container(expand=True,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_OUT))

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
                ft.Text("Loading mess off data…", color=self.sub, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=60,
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
            except (ValueError, TypeError):
                continue
        return max(12 - total, 0)

    def _status_chip(self, status):
        colours = {
            "Approved":  ("#10B981", "#D1FAE5"),
            "Pending":   ("#F59E0B", "#FEF3C7"),
            "Rejected":  ("#EF4444", "#FEE2E2"),
            "Cancelled": (self.sub, self.card2),
        }
        fg, bg = colours.get(status, (self.sub, self.card2))
        return ft.Container(
            content=ft.Text(status, size=11, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

    def _request_card(self, req, on_cancel):
        status      = req.get("Status", "Pending")
        mess_off_id = req.get("Mess_Off_ID")

        cancel_btn = ft.Container()
        if status == "Pending":
            cancel_btn = ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL_ROUNDED, size=14, color="#EF4444"),
                    ft.Text("Cancel", size=12, color="#EF4444", font_family="DM Sans"),
                ], spacing=4, tight=True),
                on_click=lambda e, mid=mess_off_id: asyncio.create_task(on_cancel(mid)),
                style=ft.ButtonStyle(padding=ft.Padding.all(4)),
            )

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=20, color=self.amber),
                    width=44, height=44,
                    bgcolor=ft.Colors.with_opacity(0.12, self.amber),
                    border_radius=12,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(
                            f"{req.get('Start_Date','?')} → {req.get('End_Date','?')}",
                            size=14,
                            weight="bold",
                            color=self.txt,
                            font_family="DM Sans",
                        ),
                        self._status_chip(status),
                    ], spacing=8),
                    ft.Text(
                        f"Requested: {req.get('Request_Date', req.get('Start_Date','?'))}  •  ID #{mess_off_id}",
                        size=11,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], expand=True, spacing=4),
                cancel_btn,
            ], spacing=12),
            bgcolor=self.card,
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.06, "#000"),
                offset=ft.Offset(0, 2),
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, "#000")),
        )

    async def _render(self):
        self.main_container.content = self._loading()
        self.main_container.opacity = 0
        self.page.update()

        if self.is_guest:
            result = mock_data.get_mess_off_history()
        else:
            result = await get_mess_off_history()
        requests = []
        if isinstance(result, dict) and "status" in result:
            requests = result["status"] if isinstance(result["status"], list) else []
        elif isinstance(result, list):
            requests = result

        remaining = self._calc_remaining(requests)

        # ── Quota ring ───────────────────────────────────────────
        used     = 12 - remaining
        fraction = used / 12
        quota_card = ft.Container(
            content=ft.Row([
                ft.Stack([
                    ft.Container(
                        content=ft.ProgressRing(
                            value=fraction,
                            color=self.amber,
                            bgcolor=ft.Colors.with_opacity(0.15, self.amber),
                            width=64, height=64,
                            stroke_width=6,
                        ),
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(remaining),
                            size=18,
                            weight="bold",
                            color=self.amber,
                            font_family="DM Sans",
                        ),
                        width=64, height=64,
                        alignment=ft.Alignment(0, 0),
                    ),
                ]),
                ft.Column([
                    ft.Text(
                        "Days remaining this month",
                        size=14,
                        weight="bold",
                        color=self.txt,
                        font_family="DM Sans",
                    ),
                    ft.Text(
                        f"{used} used of 12 allowed",
                        size=12,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], spacing=4, expand=True),
            ], spacing=16),
            bgcolor=self.card2,
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            margin=ft.Margin.only(bottom=20),
        )

        # ── Request form ─────────────────────────────────────────
        start_field = ft.TextField(
            label="Start Date",
            hint_text="YYYY-MM-DD",
            expand=True,
            border_color=self.amber,
            focused_border_color=self.amber,
            label_style=ft.TextStyle(color=self.sub, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self.txt, font_family="DM Sans"),
            border_radius=12,
            filled=True,
            fill_color=self.card,
        )
        end_field = ft.TextField(
            label="End Date",
            hint_text="YYYY-MM-DD",
            expand=True,
            border_color=self.amber,
            focused_border_color=self.amber,
            label_style=ft.TextStyle(color=self.sub, font_family="DM Sans"),
            text_style=ft.TextStyle(color=self.txt, font_family="DM Sans"),
            border_radius=12,
            filled=True,
            fill_color=self.card,
        )

        async def submit(e):
            from pages.validation import validate_date_str
            start_dt, err = validate_date_str(start_field.value, "Start Date")
            if err:
                start_field.error = err; start_field.update()
                return
            start_field.error = ""
            end_dt, err = validate_date_str(end_field.value, "End Date")
            if err:
                end_field.error = err; end_field.update()
                return
            end_field.error = ""
            start = start_dt
            end   = end_dt
            if start > end:
                start_field.error = "Start date must be before end date"
                end_field.error = "End date must be after start date"
                start_field.update(); end_field.update()
                return

            if self.is_guest:
                mock_data.request_mess_off(self.user_id, start, end)
                result = {"message": "Request submitted!"}
            else:
                result = await request_mess_off(self.user_id, start, end)

            if isinstance(result, dict) and "error" in result:
                msg = result["error"]
                colour = "#EF4444"
            else:
                msg    = result.get("message", "Request submitted!") if isinstance(result, dict) else "Submitted!"
                colour = "#10B981"
                start_field.value = ""
                end_field.value   = ""
                asyncio.create_task(self._render())

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="#FFF"), bgcolor=colour
            )
            self.page.snack_bar.open = True
            self.page.update()

        submit_btn = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SEND_ROUNDED, size=16, color=self.card),
                ft.Text("Submit", size=13, weight="bold", color=self.card, font_family="DM Sans"),
            ], spacing=8, tight=True),
            on_click=submit,
            style=ft.ButtonStyle(
                bgcolor=self.amber,
                elevation=0,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            ),
        )

        form_card = ft.Container(
            content=ft.Column([
                ft.Text(
                    "New Request",
                    size=15,
                    weight="bold",
                    color=self.txt,
                    font_family="DM Sans",
                ),
                ft.Container(height=8),
                ft.Row([start_field, end_field], spacing=10),
                ft.Container(height=10),
                ft.Row([submit_btn], alignment=ft.MainAxisAlignment.END),
                ft.Text(
                    "Max 12 days per month. Approved requests will deduct from your quota.",
                    size=11,
                    color=self.sub,
                    font_family="DM Sans",
                ),
            ], spacing=0),
            bgcolor=self.card,
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            margin=ft.Margin.only(bottom=20),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.06, "#000"),
                offset=ft.Offset(0, 2),
            ),
        )

        # ── Cancel handler ───────────────────────────────────────
        async def handle_cancel(mid):
            if self.is_guest:
                mock_data.cancel_mess_off(mid)
                result = {"message": "Cancelled"}
            else:
                result = await cancel_mess_off(mid)
            if isinstance(result, dict) and "error" in result:
                msg, colour = result["error"], "#EF4444"
            else:
                msg    = result.get("message", "Cancelled") if isinstance(result, dict) else "Cancelled"
                colour = "#10B981"
                asyncio.create_task(self._render())
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color="#FFF"), bgcolor=colour
            )
            self.page.snack_bar.open = True
            self.page.update()

        # ── History list ─────────────────────────────────────────
        if not requests:
            history_body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX_ROUNDED, size=40, color=self.sub),
                    ft.Text("No requests this month", color=self.sub, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.Alignment(0, 0),
                padding=40,
            )
        else:
            history_body = ft.Column(
                [self._request_card(r, handle_cancel) for r in requests], spacing=0
            )

        self.main_container.content = ft.Column([
            self._guest_banner(),
            ft.Row([
                ft.Column([
                    ft.Text("Mess Off", size=28, weight="bold", color=self.txt, font_family="DM Sans"),
                    ft.Text("Manage your meal absences", size=13, color=self.sub, font_family="DM Sans"),
                ]),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color=self.sub,
                    tooltip="Refresh",
                    on_click=lambda e: asyncio.create_task(self._render()),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            quota_card,
            form_card,
            ft.Text(
                "Your Requests",
                size=16,
                weight="bold",
                color=self.txt,
                font_family="DM Sans",
            ),
            ft.Container(height=8),
            history_body,
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()
        self.main_container.opacity = 1
        self.page.update()

    def build(self):
        self.main_container.content = self._loading()
        asyncio.create_task(self._render())
        m = (self.page.width or 1200) < 720
        return ft.Container(
            content=self.main_container,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=12 if m else 24, vertical=20),
        )