from io import StringIO
import csv
from dao.base import BaseDAO
from dao.queries import getStudentBillDetails, getMyBills, createBill, getBillPDF, getMonthBills


class BillDAO(BaseDAO):
    def get_student_bill_details(self, user_id):
        return self._fetchall(getStudentBillDetails, (user_id,))

    def get_my_bills(self, email):
        return self._fetchall(getMyBills, (email,))

    def create_bill(self, user_id, issue_date, amount, due_date, month, status):
        return self._execute(createBill, (user_id, issue_date, amount, due_date, month, status))

    def get_bill_pdf(self, billing_id, email):
        return self._fetchone(getBillPDF, (billing_id, email))

    def get_all_monthly_bills(self):
        return self._fetchall(getMonthBills)

    def export_bills_csv(self):
        bills = self._fetchall("""
            SELECT b.Billing_ID, u.First_Name, u.Last_Name, u.Email,
                   b.Month, b.Amount, b.Due_Date, b.Status
            FROM Bills b JOIN Users u ON b.User_ID = u.UserID
            ORDER BY b.Issue_Date DESC
        """)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Billing_ID", "First_Name", "Last_Name", "Email",
                         "Month", "Amount", "Due_Date", "Status"])
        for b in bills:
            writer.writerow([
                b.get("Billing_ID"), b.get("First_Name"), b.get("Last_Name"),
                b.get("Email"), b.get("Month"), b.get("Amount"),
                b.get("Due_Date"), b.get("Status"),
            ])
        return output.getvalue()

    def generate_monthly_bills(self, amount=5000, due_days=14):
        """Generate bills for all students who don't already have one for the current month."""
        from datetime import date, timedelta
        today = date.today()
        month_str = today.strftime("%Y-%m-01")
        due_date = today + timedelta(days=due_days)

        students = self._fetchall(
            "SELECT UserID FROM Student WHERE UserID NOT IN ("
            "SELECT User_ID FROM Bills WHERE Month = %s)", (month_str,)
        )
        generated = 0
        for s in students:
            self._execute(
                "INSERT INTO Bills (User_ID, Issue_Date, Amount, Due_Date, Month, Status) "
                "VALUES (%s, %s, %s, %s, %s, 'Unpaid')",
                (s["UserID"], today, amount, due_date, month_str)
            )
            generated += 1
        return {"message": f"Generated {generated} bills for {month_str}", "count": generated}

    def get_recent_activity(self, limit=10):
        """Unify recent bill payments, mess-off approvals, and new registrations."""
        from datetime import datetime
        bills = self._fetchall(
            """SELECT CONCAT('Bill paid: ', u.First_Name, ' ', u.Last_Name) AS description,
                      b.Status AS detail, b.Issue_Date AS event_date
               FROM Bills b JOIN Users u ON b.User_ID = u.UserID
               WHERE b.Status = 'Paid'
               ORDER BY b.Issue_Date DESC LIMIT %s""", (limit,)
        )
        mess_offs = self._fetchall(
            """SELECT CONCAT('Mess-off ', LOWER(mo.Status), ': ', u.First_Name, ' ', u.Last_Name) AS description,
                      mo.Status AS detail, COALESCE(mo.Request_Date, mo.Start_Date) AS event_date
               FROM Mess_Off mo JOIN Users u ON mo.User_ID = u.UserID
               WHERE mo.Status IN ('Approved', 'Rejected')
               ORDER BY event_date DESC LIMIT %s""", (limit,)
        )
        regs = self._fetchall(
            """SELECT CONCAT('Registration ', LOWER(Status), ': ', First_Name, ' ', Last_Name) AS description,
                      Status AS detail, Created_At AS event_date
               FROM Registration_Requests
               WHERE Status IN ('Approved', 'Rejected')
               ORDER BY Created_At DESC LIMIT %s""", (limit,)
        )
        def _key(x):
            v = x.get("event_date")
            if isinstance(v, datetime):
                return v
            if hasattr(v, "isoformat"):
                return datetime.combine(v, datetime.min.time())
            return datetime.min
        items = sorted(bills + mess_offs + regs, key=_key, reverse=True)[:limit]
        return items

    def get_dashboard_stats(self):
        total_students = self._fetchone(
            "SELECT COUNT(*) AS count FROM Users WHERE Account_Type = 'Student'"
        )["count"]
        total_staff = self._fetchone(
            "SELECT COUNT(*) AS count FROM Users WHERE Account_Type = 'Staff'"
        )["count"]
        total_food_items = self._fetchone(
            "SELECT COUNT(*) AS count FROM Food_Items"
        )["count"]
        active_mess_offs = self._fetchone(
            "SELECT COUNT(*) AS count FROM Mess_Off WHERE Status = 'Pending'"
        )["count"]
        unpaid_bills = self._fetchone(
            "SELECT COUNT(*) AS count FROM Bills WHERE Status = 'Unpaid' OR Status = 'Overdue'"
        )["count"]
        pending_registrations = self._fetchone(
            "SELECT COUNT(*) AS count FROM Registration_Requests WHERE Status = 'Pending'"
        )["count"]
        total_ingredients = self._fetchone(
            "SELECT COUNT(*) AS count FROM Ingredients"
        )["count"]

        return {
            "total_students": total_students,
            "total_staff": total_staff,
            "total_food_items": total_food_items,
            "total_ingredients": total_ingredients,
            "active_mess_offs": active_mess_offs,
            "unpaid_bills": unpaid_bills,
            "pending_registration_requests": pending_registrations,
        }
