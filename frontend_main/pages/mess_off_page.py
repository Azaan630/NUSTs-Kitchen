import flet as ft
import asyncio
from datetime import date, datetime
import calendar
from pages.api_client import (
    request_mess_off,
    cancel_mess_off,
    get_mess_off_history
)


class StudentMessOffPage:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user_data = user_data
        self.user_id = int(user_data.get("UserID", 0))
        self.email = user_data.get("Email")
        self.first_name = user_data.get("First_Name", "")
        self.last_name = user_data.get("Last_Name", "")

        # Container for dynamic content
        self.content = ft.Container(
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
        )
        self.loading_text = ft.Text("Loading Mess Off data...", color=ft.Colors.GREY_600)
        self.history_table = None

    async def load_data(self):
        """Loads mess-off history and updates UI."""
        # Show loading
        self.content.content = ft.Column([
            ft.Row([ft.ProgressRing(), self.loading_text], alignment=ft.MainAxisAlignment.CENTER)
        ])
        self.page.update()

        # Fetch history
        result = await get_mess_off_history(self.email)

        requests = []
        if isinstance(result, dict) and "status" in result:
            requests = result["status"] if isinstance(result["status"], list) else []
        elif isinstance(result, list):
            requests = result

        # Calculate remaining days
        remaining_days = self.calculate_remaining_days(requests)

        # Build the UI
        await self.build_ui(requests, remaining_days)

    def calculate_remaining_days(self, requests):
        """Calculates approved mess-off days in the current month (max 12)."""
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        total_days = 0
        for req in requests:
            if req.get("Status") != "Approved":
                continue
            try:
                start = datetime.strptime(req["Start_Date"], "%Y-%m-%d").date()
                end = datetime.strptime(req["End_Date"], "%Y-%m-%d").date()
                if start > month_end or end < month_start:
                    continue
                overlap_start = max(start, month_start)
                overlap_end = min(end, month_end)
                days = (overlap_end - overlap_start).days + 1
                if days > 0:
                    total_days += days
            except:
                continue
        return max(12 - total_days, 0)

    async def build_ui(self, requests, remaining_days):
        """Constructs the UI with history table and request form."""
        # Build history table rows
        rows = []
        for req in requests:
            status = req.get("Status", "Pending")
            status_color = ft.Colors.BLUE
            if status == "Approved":
                status_color = ft.Colors.GREEN
            elif status == "Rejected":
                status_color = ft.Colors.RED
            elif status == "Cancelled":
                status_color = ft.Colors.GREY_600

            cancel_btn = None
            if status == "Pending":
                cancel_btn = ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    icon_color=ft.Colors.RED,
                    tooltip="Cancel request",
                    data=req.get("Mess_Off_ID"),
                    on_click=self.handle_cancel
                )

            row = ft.DataRow([
                ft.DataCell(ft.Text(str(req.get("Mess_Off_ID", "N/A")))),
                ft.DataCell(ft.Text(req.get("Start_Date", "N/A"))),
                ft.DataCell(ft.Text(req.get("End_Date", "N/A"))),
                ft.DataCell(ft.Text(req.get("Request_Date", "N/A"))),
                ft.DataCell(ft.Container(
                    content=ft.Text(status, color=ft.Colors.WHITE),
                    bgcolor=status_color,
                    padding=5,
                    border_radius=5
                )),
                ft.DataCell(cancel_btn if cancel_btn else ft.Text("—", color=ft.Colors.GREY_400))
            ])
            rows.append(row)

        # Create DataTable
        self.history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Start")),
                ft.DataColumn(ft.Text("End")),
                ft.DataColumn(ft.Text("Requested")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Action")),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
        )

        # Build final UI
        self.content.content = ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.BLUE_900, size=30),
                    ft.Text("Mess Off Management", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ]),
                padding=ft.padding.only(bottom=20)
            ),

            # Remaining days
            ft.Container(
                content=ft.Row([
                    ft.Text("📅 Remaining mess-off days this month:", weight="bold", size=16),
                    ft.Text(f"{remaining_days} / 12", size=18, weight="bold", color=ft.Colors.BLUE_700),
                ]),
                padding=10,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
                margin=ft.margin.only(bottom=15)
            ),

            # Section 1: History Table
            ft.Text("📋 Your Requests", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=5),
            ft.Container(
                content=ft.Column([self.history_table], scroll=ft.ScrollMode.ADAPTIVE),
                padding=10,
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                margin=ft.margin.only(bottom=15)
            ),

            # Section 2: Request Form
            self.build_request_form(),
        ], scroll=ft.ScrollMode.ADAPTIVE)
        self.page.update()

    def build_request_form(self):
        """Creates the form to request new mess off."""
        start_picker = ft.TextField(
            label="Start Date (YYYY-MM-DD)",
            hint_text="e.g. 2026-05-10",
            width=200,
        )
        end_picker = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            hint_text="e.g. 2026-05-12",
            width=200,
        )
        submit_btn = ft.ElevatedButton(
            content=ft.Text("Submit Request"),
            icon=ft.Icons.SEND,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_900},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE}
            )
        )

        async def submit(e):
            try:
                start = date.fromisoformat(start_picker.value)
                end = date.fromisoformat(end_picker.value)
                if start > end:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Start date must be before end date"),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                result = await request_mess_off(self.user_id, start, end,self.email)
                if result.get("success"):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(result.get("message", "Request submitted successfully")),
                        bgcolor=ft.Colors.GREEN
                    )
                    self.page.snack_bar.open = True
                    start_picker.value = ""
                    end_picker.value = ""
                    # Reload data
                    await self.load_data()
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(result.get("error", "Request failed")),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
            except ValueError:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Invalid date format. Use YYYY-MM-DD"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
            self.page.update()

        submit_btn.on_click = submit

        return ft.Container(
            content=ft.Column([
                ft.Text("📝 Request New Mess Off", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=5),
                ft.Row([
                    start_picker,
                    end_picker,
                    submit_btn
                ], wrap=True),
                ft.Container(height=10),
                ft.Text("Note: You can request up to 12 days per month.", size=14, color=ft.Colors.GREY_600),
            ]),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            margin=ft.margin.only(top=15)
        )

    async def handle_cancel(self, e):
        """Handles cancellation of a pending request."""
        mess_off_id = e.control.data
        result = await cancel_mess_off(mess_off_id, self.email)
        if result.get("success"):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(result.get("message", "Request cancelled successfully")),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            await self.load_data()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(result.get("error", "Failed to cancel request")),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        asyncio.create_task(self.load_data())
        return ft.Container(
            content=ft.Column([
                ft.Text("Mess Off", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                self.content
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            expand=True
        )