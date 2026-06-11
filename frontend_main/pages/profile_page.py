import flet as ft
import asyncio
import os
from pages.api_client import get_my_bills
import mock_data


class StudentProfilePage:
    def __init__(self, page: ft.Page, user_data: dict, theme: dict):
        self.page = page
        self.user_data = user_data
        self.theme = theme
        self.email = user_data.get("Email", "")
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
        self.bills_data = []

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
                ft.Text("Loading your bills…", color=self.sub, font_family="DM Sans", size=14),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=60,
        )

    def _status_chip(self, status):
        colors = {
            "Paid":    ("#10B981", "#D1FAE5"),
            "Unpaid":  ("#F59E0B", "#FEF3C7"),
            "Overdue": ("#EF4444", "#FEE2E2"),
        }
        fg, bg = colors.get(status, (self.sub, self.card2))
        return ft.Container(
            content=ft.Text(status, size=11, color=fg, weight="bold", font_family="DM Sans"),
            bgcolor=bg,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

    def _bill_card(self, bill, on_download):
        status = bill.get("Status", "Unknown")
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        bill.get("Month", "N/A"),
                        size=15,
                        weight="bold",
                        color=self.txt,
                        font_family="DM Sans",
                    ),
                    ft.Text(
                        f"Due: {bill.get('Due_Date', 'N/A')}",
                        size=12,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                    ft.Text(
                        f"Bill #{bill.get('Billing_ID', '?')}",
                        size=11,
                        color=self.sub,
                        font_family="DM Sans",
                    ),
                ], expand=True, spacing=4),
                ft.Column([
                    ft.Text(
                        f"PKR {bill.get('Amount', 0):,.0f}",
                        size=18,
                        weight="bold",
                        color=self.amber,
                        font_family="DM Sans",
                    ),
                    self._status_chip(status),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF_ROUNDED, size=14, color=self.amber),
                            ft.Text("Download", size=12, color=self.amber, font_family="DM Sans"),
                        ], spacing=4, tight=True),
                        on_click=lambda e, b=bill: asyncio.create_task(on_download(b)),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4),
            ]),
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

    async def _download(self, bill):
        if self.is_guest:
            self._snack("PDF download not available in guest mode", ok=False)
            return
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
                bgcolor=self.amber
            )
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}", color="#FFF"),
                bgcolor="#EF4444"
            )

        self.page.snack_bar.open = True
        self.page.update()

    async def _render(self):
        self.main_container.content = self._loading()
        self.page.update()

        if self.is_guest:
            data = mock_data.get_my_bills()
        else:
            data = await get_my_bills(self.email)
        self.bills_data = data if isinstance(data, list) else []

        error = None
        if not self.is_guest and isinstance(data, dict) and "error" in data:
            error = data["error"]

        # ── Profile card ─────────────────────────────────────────
        first = self.user_data.get("First_Name", "")
        last  = self.user_data.get("Last_Name",  "")
        initials = (first[0] + (last[0] if last else "")).upper() if first else "U"

        profile_card = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(initials, size=28, weight="bold", color="#FFF"),
                    width=64, height=64,
                    bgcolor=self.amber,
                    border_radius=32,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(
                        f"{first} {last}".strip(),
                        size=20,
                        weight="bold",
                        color=self.txt,
                        font_family="DM Sans",
                    ),
                    ft.Text(self.email, size=13, color=self.sub, font_family="DM Sans"),
                    ft.Container(
                        content=ft.Text(
                            self.user_data.get("Account_Type", "Student"),
                            size=11,
                            color=self.amber,
                            weight="bold",
                            font_family="DM Sans",
                        ),
                        bgcolor=ft.Colors.with_opacity(0.12, self.amber),
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    ),
                ], spacing=4, expand=True),
            ], spacing=16),
            bgcolor=self.card,
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=ft.Colors.with_opacity(0.07, "#000"),
                offset=ft.Offset(0, 3),
            ),
            margin=ft.Margin.only(bottom=20),
        )

        # ── Bills section ────────────────────────────────────────
        if error:
            bills_section = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#EF4444", size=40),
                ft.Text(error, color="#EF4444", font_family="DM Sans"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        elif not self.bills_data:
            bills_section = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG_ROUNDED, size=48, color=self.sub),
                    ft.Text("No bills yet", color=self.sub, font_family="DM Sans"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.Alignment(0, 0),
                padding=40,
            )
        else:
            total_due = sum(
                b.get("Amount", 0) for b in self.bills_data
                if b.get("Status") in ("Unpaid", "Overdue")
            )
            summary = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Total Due", size=11, color=self.sub, font_family="DM Sans"),
                        ft.Text(
                            f"PKR {total_due:,.0f}",
                            size=20,
                            weight="bold",
                            color=self.amber,
                            font_family="DM Sans",
                        ),
                    ]),
                    ft.Column([
                        ft.Text("Bills", size=11, color=self.sub, font_family="DM Sans"),
                        ft.Text(
                            str(len(self.bills_data)),
                            size=20,
                            weight="bold",
                            color=self.txt,
                            font_family="DM Sans",
                        ),
                    ]),
                ], spacing=32),
                bgcolor=self.card2,
                border_radius=16,
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                margin=ft.Margin.only(bottom=16),
            )
            bill_cards = [self._bill_card(b, self._download) for b in self.bills_data]
            bills_section = ft.Column([summary] + bill_cards, spacing=0)

        self.main_container.content = ft.Column([
            self._guest_banner(),
            ft.Text("Profile", size=28, weight="bold", font_family="DM Sans", color=self.txt),
            ft.Container(height=12),
            profile_card,
            ft.Row([
                ft.Text("Billing History", size=18, weight="bold", color=self.txt, font_family="DM Sans"),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color=self.sub,
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
        m = (self.page.width or 1200) < 720
        return ft.Container(
            content=self.main_container,
            expand=True,
            padding=ft.Padding.symmetric(horizontal=12 if m else 24, vertical=20),
        )