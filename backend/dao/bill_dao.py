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
