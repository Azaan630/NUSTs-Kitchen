import flet as ft
import asyncio
import os
from pages.api_client import get_my_bills, download_bill_pdf


class StudentProfilePage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
        self.P = theme["P"]
        is_dark = theme["is_dark"]
        self.bg      = self.P.BG_DARK if is_dark else self.P.BG_LIGHT
        self.card_bg = self.P.SURFACE if is_dark else self.P.WHITE
        self.txt_c   = self.P.TEXT_LIGHT if is_dark else self.P.TEXT_DARK
        self.sub_c   = self.P.MUTED if is_dark else self.P.MUTED_LIGHT

        self.main_container = ft.Container(expand=True)
        self.bills_data = []

    def _loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=self.P.PRIMARY, width=40, height=40, stroke_width=3),
                ft.Text("Loading your bills...", color=self.sub_c, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0), expand=True, padding=60,
        )

    def _status_chip(self, status):
        colors = {
            "Paid":    (self.P.SUCCESS, ft.Colors.with_opacity(0.12, self.P.SUCCESS)),
            "Unpaid":  (self.P.WARNING, ft.Colors.with_opacity(0.12, self.P.WARNING)),
            "Overdue": (self.P.ERROR, ft.Colors.with_opacity(0.12, self.P.ERROR)),
        }
        fg, bg = colors.get(status, (self.sub_c, ft.Colors.with_opacity(0.05, self.P.WHITE)))
        return ft.Container(
            content=ft.Text(status, size=11, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg, border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

    def _bill_card(self, bill, on_download):
        status = bill.get("Status", "Unknown")
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(bill.get("Month", "N/A"), size=15, weight="bold",
                            color=self.txt_c, font_family="DM Sans"),
                    ft.Text(f"Due: {bill.get('Due_Date', 'N/A')}", size=12,
                            color=self.sub_c, font_family="DM Sans"),
                    ft.Text(f"Bill #{bill.get('Billing_ID', '?')}", size=11,
                            color=self.sub_c, font_family="DM Sans"),
                ], expand=True, spacing=4),
                ft.Column([
                    ft.Text(f"PKR {bill.get('Amount', 0):,.0f}", size=18, weight="bold",
                            color=self.P.PRIMARY_LT, font_family="DM Sans"),
                    self._status_chip(status),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF_ROUNDED, size=14, color=self.P.PRIMARY_LT),
                            ft.Text("Download", size=12, color=self.P.PRIMARY_LT, font_family="DM Sans"),
                        ], spacing=4, tight=True),
                        on_click=lambda e, b=bill: asyncio.create_task(on_download(b)),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
            ]),
            bgcolor=self.card_bg, border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            margin=ft.Margin.only(bottom=10),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, "#000"), offset=ft.Offset(0, 2)),
            border=ft.Border.all(0.5, ft.Colors.with_opacity(0.1, self.P.WHITE)),
        )

    def _snack(self, msg, ok=True):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#FFF"),
            bgcolor=self.P.SUCCESS if ok else self.P.ERROR,
        )
        self.page.snack_bar.open = True
        self.page.update()

    async def _download(self, bill):
        billing_id = bill.get("Billing_ID")
        if not billing_id:
            self._snack("Invalid Bill ID", ok=False)
            return

        public_backend_url = os.getenv("PUBLIC_BACKEND_URL", "http://localhost:8000")
        actual_url = f"{public_backend_url}/student/bills/download/{billing_id}"
        params = f"?email={self.email}"
        full_path = f"{actual_url}{params}"

        try:
            await self.page.launch_url(full_path)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Attempting to download PDF...", color="#FFF"),
                bgcolor=self.P.PRIMARY,
            )
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}", color="#FFF"),
                bgcolor=self.P.ERROR,
            )

        self.page.snack_bar.open = True
        self.page.update()

    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        data = await get_my_bills(self.email)
        self.bills_data = data if isinstance(data, list) else []

        error = None
        if isinstance(data, dict) and "error" in data:
            error = data["error"]

        first = self.user_data.get("First_Name", "")
        last  = self.user_data.get("Last_Name", "")
        initials = (first[0] + (last[0] if last else "")).upper() if first else "U"

        profile_card = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(initials, size=28, weight="bold", color=self.P.WHITE),
                    width=64, height=64,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                        colors=[self.P.PRIMARY, self.P.ACCENT2],
                    ),
                    border_radius=32, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(f"{first} {last}".strip(), size=20, weight="bold",
                            color=self.txt_c, font_family="DM Sans"),
                    ft.Text(self.email, size=13, color=self.sub_c, font_family="DM Sans"),
                    ft.Container(
                        content=ft.Text(self.user_data.get("Account_Type", "Student"),
                                        size=11, color=self.P.PRIMARY_LT, weight="bold",
                                        font_family="DM Sans"),
                        bgcolor=ft.Colors.with_opacity(0.12, self.P.PRIMARY_LT),
                        border_radius=8, padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    ),
                ], spacing=4, expand=True),
            ], spacing=16),
            bgcolor=self.card_bg, border_radius=20,
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.07, "#000"), offset=ft.Offset(0, 3)),
            margin=ft.Margin.only(bottom=20),
        )

        if error:
            bills_section = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=self.P.ERROR, size=40),
                ft.Text(error, color=self.P.ERROR, font_family="DM Sans"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        elif not self.bills_data:
            bills_section = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=48, color=self.sub_c),
                    ft.Text("No bills yet", color=self.sub_c, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0), padding=40,
            )
        else:
            total_due = sum(
                b.get("Amount", 0) for b in self.bills_data
                if b.get("Status") in ("Unpaid", "Overdue")
            )
            summary = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Total Due", size=11, color=self.sub_c, font_family="DM Sans"),
                        ft.Text(f"PKR {total_due:,.0f}", size=20, weight="bold",
                                color=self.P.PRIMARY_LT, font_family="DM Sans"),
                    ]),
                    ft.Column([
                        ft.Text("Bills", size=11, color=self.sub_c, font_family="DM Sans"),
                        ft.Text(str(len(self.bills_data)), size=20, weight="bold",
                                color=self.txt_c, font_family="DM Sans"),
                    ]),
                ], spacing=32),
                bgcolor=ft.Colors.with_opacity(0.05, self.P.WHITE),
                border_radius=16, padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                margin=ft.Margin.only(bottom=16),
            )
            bill_cards = [self._bill_card(b, self._download) for b in self.bills_data]
            bills_section = ft.Column([summary] + bill_cards, spacing=0)

        self.main_container.content = ft.Column([
            ft.Text("Profile", size=28, weight="bold", font_family="DM Sans", color=self.txt_c),
            ft.Container(height=12),
            profile_card,
            ft.Row([
                ft.Text("Billing History", size=18, weight="bold",
                        color=self.txt_c, font_family="DM Sans"),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED, icon_color=self.sub_c,
                    tooltip="Refresh",
                    on_click=lambda e: asyncio.create_task(self._render()),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=8),
            bills_section,
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self.page.update()

    def build(self):
        asyncio.create_task(self._render())
        return ft.Container(
            content=self.main_container, bgcolor=self.bg, expand=True,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
        )
