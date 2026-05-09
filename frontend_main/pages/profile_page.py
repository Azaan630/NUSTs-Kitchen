import flet as ft
import asyncio
import webbrowser
from pages.api_client import get_my_bills, download_bill_pdf

class StudentProfilePage:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user_data = user_data
        self.email = user_data.get("Email")
        self.bill_container = ft.Container(padding=20, border_radius=15, bgcolor=ft.Colors.WHITE)
        self.loading_text = ft.Text("Loading your bills...", color=ft.Colors.GREY_600)
        self.bills_data = []  # Store bills for PDF download

    async def load_bills(self):
        self.bill_container.content = ft.Column([
            ft.Row([ft.ProgressRing(), self.loading_text], alignment=ft.MainAxisAlignment.CENTER)
        ])
        self.page.update()

        bills_data = await get_my_bills(self.email)
        self.bills_data = bills_data if isinstance(bills_data, list) else []

        if "error" in bills_data:
            self.bill_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED, size=50),
                ft.Text(f"Failed to load bills: {bills_data['error']}", color=ft.Colors.RED)
            ])
            self.page.update()
            return

        if not self.bills_data:
            self.bill_container.content = ft.Text("No bills found for your account.", color=ft.Colors.GREY)
            self.page.update()
            return

        bill_rows = []
        for bill in self.bills_data:
            status_color = ft.Colors.GREEN
            if bill.get("Status") == "Unpaid":
                status_color = ft.Colors.ORANGE
            elif bill.get("Status") == "Overdue":
                status_color = ft.Colors.RED

            bill_row = ft.DataRow([
                ft.DataCell(ft.Text(str(bill.get("Billing_ID", "N/A")))),
                ft.DataCell(ft.Text(bill.get("Month", "N/A"))),
                ft.DataCell(ft.Text(f"PKR {bill.get('Amount', 0.00)}")),
                ft.DataCell(ft.Text(bill.get("Due_Date", "N/A"))),
                ft.DataCell(ft.Container(
                    content=ft.Text(bill.get("Status", "Unknown"), color=ft.Colors.WHITE),
                    bgcolor=status_color,
                    padding=5,
                    border_radius=5
                )),
            ])
            bill_rows.append(bill_row)

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
            ft.Column([bill_table], scroll=ft.ScrollMode.ADAPTIVE),
        ])
        self.page.update()

    async def download_pdf(self, e):
        """Downloads the selected bill as PDF."""
        # You need to know which bill to download – let's use the first one
        if not self.bills_data:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No bills to download"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return

        # For now, download the first bill (you can add a selector later)
        billing_id = self.bills_data[0].get("Billing_ID")
        if not billing_id:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Invalid bill ID"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return

        pdf_bytes = await download_bill_pdf(billing_id, self.email)
        if pdf_bytes:
            # Option 1: Save file using FilePicker
            # Option 2: Open in browser (simpler for now)
            import base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            # Open PDF in a new browser tab (works in web mode)
            self.page.launch_url(f"data:application/pdf;base64,{pdf_base64}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text("PDF downloaded and opened!"), bgcolor=ft.Colors.GREEN)
        else:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Failed to download PDF"), bgcolor=ft.Colors.RED)
        self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        asyncio.create_task(self.load_bills())

        pdf_button = ft.ElevatedButton(
            content=ft.Text("📄 Download Bill PDF"),
            icon=ft.Icons.PICTURE_AS_PDF,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_900},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE}
            )
        )
        pdf_button.on_click = self.download_pdf  # ✅ Uses real download

        profile_details = ft.Container(
            content=ft.Column([
                ft.Text("🧑‍🎓 Student Profile", size=24, weight="bold", color=ft.Colors.BLUE_900),
                ft.Divider(height=10),
                ft.Row([ft.Text("Name:", weight="bold"), ft.Text(f"{self.user_data.get('First_Name', '')} {self.user_data.get('Last_Name', '')}")]),
                ft.Row([ft.Text("Email:", weight="bold"), ft.Text(self.user_data.get("Email", "N/A"))]),
                ft.Row([ft.Text("Account Type:", weight="bold"), ft.Text(self.user_data.get("Account_Type", "N/A"))]),
                ft.Container(height=20),
                pdf_button
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