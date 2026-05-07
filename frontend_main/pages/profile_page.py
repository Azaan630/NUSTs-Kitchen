import flet as ft
import asyncio
from api_client import get_my_bills

class StudentProfilePage:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user_data = user_data
        self.email = user_data.get("Email")
        self.bill_container = ft.Container(padding=20, border_radius=15, bgcolor=ft.Colors.WHITE)
        self.loading_text = ft.Text("Loading your bills...", color=ft.Colors.GREY_600)

    async def load_bills(self):
        # Show loading
        self.bill_container.content = ft.Column([
            ft.Row([ft.ProgressRing(), self.loading_text], alignment=ft.MainAxisAlignment.CENTER)
        ])
        self.page.update()

        # Fetch bills from backend
        bills_data = await get_my_bills(self.email)

        if "error" in bills_data:
            self.bill_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                ft.Text(f"Failed to load bills: {bills_data['error']}", color=ft.Colors.RED)
            ])
            self.page.update()
            return

        if not bills_data or len(bills_data) == 0:
            self.bill_container.content = ft.Text("No bills found for your account.", color=ft.Colors.GREY)
            self.page.update()
            return

        # Build bill table
        bill_rows = []
        for bill in bills_data:
            # Determine status color
            status_color = ft.Colors.GREEN
            if bill.get("Status") == "Unpaid":
                status_color = ft.Colors.ORANGE
            elif bill.get("Status") == "Overdue":
                status_color = ft.Colors.RED

            bill_row = ft.DataRow([
                ft.DataCell(ft.Text(bill.get("Billing_ID", "N/A"))),
                ft.DataCell(ft.Text(bill.get("Month", "N/A"))),
                ft.DataCell(ft.Text(f"PKR {bill.get('Amount', 0.00)}")),
                ft.DataCell(ft.Text(bill.get("Due_Date", "N/A"))),
                ft.DataCell(ft.Container(
                    content=ft.Text(bill.get("Status", "Unknown")),
                    bgcolor=status_color,
                    padding=5,
                    border_radius=5,
                    color=ft.Colors.WHITE
                )),
            ])
            bill_rows.append(bill_row)

        # Create DataTable
        bill_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Bill ID")),
                ft.DataColumn(ft.Text("Month")),
                ft.DataColumn(ft.Text("Amount")),
                ft.DataColumn(ft.Text("Due Date")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=bill_rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=50,
        )

        self.bill_container.content = ft.Column([
            ft.Text("📄 Your Bill History", size=18, weight="bold"),
            ft.Container(height=10),
            ft.Container(bill_table, scroll=ft.ScrollMode.ADAPTIVE),
        ])
        self.page.update()

    async def generate_pdf(self, e):
        # Placeholder for PDF generation
        # You can integrate reportlab or any PDF library here later
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("PDF Generation coming soon! 🚀"), bgcolor=ft.Colors.BLUE))
        self.page.update()

    def build(self):
        asyncio.create_task(self.load_bills())

        # Profile details section
        profile_details = ft.Container(
            content=ft.Column([
                ft.Text("🧑‍🎓 Student Profile", size=24, weight="bold", color=ft.Colors.BLUE_900),
                ft.Divider(height=10),
                ft.Row([ft.Text("Name:", weight="bold"), ft.Text(f"{self.user_data.get('First_Name', '')} {self.user_data.get('Last_Name', '')}")]),
                ft.Row([ft.Text("Email:", weight="bold"), ft.Text(self.user_data.get("Email", "N/A"))]),
                ft.Row([ft.Text("Account Type:", weight="bold"), ft.Text(self.user_data.get("Account_Type", "N/A"))]),
                # You can add more fields like Room Number, Hostel, etc. if available in user_data
                ft.Container(height=20),
                ft.ElevatedButton(
                    text="📄 Generate Bill PDF",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    on_click=self.generate_pdf,
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_900},
                        color={ft.ControlState.DEFAULT: ft.Colors.WHITE}
                    )
                )
            ]),
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10
        )

        return ft.Container(
            content=ft.Column([
                profile_details,
                ft.Container(height=20),
                self.bill_container
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            expand=True
        )