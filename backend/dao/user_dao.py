from io import StringIO
import csv
from fastapi import HTTPException
from dao.base import BaseDAO
from dao.queries import (
    findUserByEmail, registerUser, registerStudent,
    registerStaff, getStaffDetails, getStudentDetails,
    AddStaffContactNumber, addStaffCategory,
    getAllStaffCategories, deleteStaffCategory,
)


class UserDAO(BaseDAO):
    def find_by_email(self, email):
        return self._fetchone(findUserByEmail, (email,))

    def find_by_id(self, user_id):
        return self._fetchone("SELECT * FROM Users WHERE UserID = %s", (user_id,))

    def get_my_profile(self, email):
        return self._fetchone(findUserByEmail, (email,))

    def get_all_users(self):
        return self._fetchall("SELECT * FROM Users")

    def get_staff_details(self, user_id):
        return self._fetchall(getStaffDetails, (user_id,))

    def get_student_details(self, user_id):
        return self._fetchall(getStudentDetails, (user_id,))

    def register_user(self, first_name, last_name, email, account_type, sex=None, profile_picture=None):
        return self._execute(registerUser, (first_name, last_name, email, account_type, sex, profile_picture))

    def register_student(self, user_id, dob, department, contact, address, father, hostel, room):
        return self._execute(registerStudent, (user_id, dob, department, contact, address, father, hostel, room))

    def register_staff(self, user_id, category):
        return self._execute(registerStaff, (user_id, category))

    def add_staff_contact(self, user_id, contact_number):
        return self._execute(AddStaffContactNumber, (user_id, contact_number))

    def add_staff_category(self, category, working_hours, salary):
        return self._execute(addStaffCategory, (category, working_hours, salary))

    def get_all_staff_categories(self):
        return self._fetchall(getAllStaffCategories)

    def delete_staff_category(self, category):
        return self._execute(deleteStaffCategory, (category,))

    def search_users(self, query, limit=20):
        pattern = f"%{query}%"
        sql = """SELECT UserID, First_Name, Last_Name, Email, Account_Type
                 FROM Users
                 WHERE First_Name LIKE %s OR Last_Name LIKE %s OR Email LIKE %s
                 LIMIT %s"""
        return self._fetchall(sql, (pattern, pattern, pattern, limit))

    def export_students_csv(self):
        students = self._fetchall("""
            SELECT u.UserID, u.First_Name, u.Last_Name, u.Email,
                   s.DoB, s.Department, s.Contact_Number, s.Address,
                   s.Father_Name, s.Hostel_Name, s.Room_Number
            FROM Users u
            JOIN Student s ON u.UserID = s.UserID
            ORDER BY u.Last_Name, u.First_Name
        """)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["UserID", "First_Name", "Last_Name", "Email",
                         "DoB", "Department", "Contact", "Address",
                         "Father_Name", "Hostel", "Room"])
        for s in students:
            writer.writerow([
                s.get("UserID"), s.get("First_Name"), s.get("Last_Name"),
                s.get("Email"), s.get("DoB"), s.get("Department"),
                s.get("Contact_Number"), s.get("Address"),
                s.get("Father_Name"), s.get("Hostel_Name"), s.get("Room_Number"),
            ])
        return output.getvalue()

    def get_student_dashboard_stats(self, user_id):
        stats = {}
        stats["total_bills"] = self._fetchone(
            "SELECT COUNT(*) AS count FROM Bills WHERE User_ID = %s", (user_id,)
        )["count"]
        stats["unpaid_bills"] = self._fetchone(
            "SELECT COUNT(*) AS count FROM Bills WHERE User_ID = %s AND (Status = 'Unpaid' OR Status = 'Overdue')",
            (user_id,)
        )["count"]
        stats["mess_offs_this_month"] = self._fetchone(
            """SELECT COUNT(*) AS count FROM Mess_Off
               WHERE User_ID = %s
               AND DATE(Start_Date) >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01')""",
            (user_id,)
        )["count"]
        stats["pending_mess_offs"] = self._fetchone(
            "SELECT COUNT(*) AS count FROM Mess_Off WHERE User_ID = %s AND Status = 'Pending'",
            (user_id,)
        )["count"]
        stats["ratings_given"] = self._fetchone(
            "SELECT COUNT(*) AS count FROM Ratings WHERE User_ID = %s", (user_id,)
        )["count"]
        return stats

    def cascade_delete_user(self, user_id):
        """Delete a user and all dependent records. Fails if account_type can't be determined."""
        user = self._fetchone("SELECT Account_Type FROM Users WHERE UserID = %s", (user_id,))
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM Transactions WHERE Billing_ID IN (SELECT Billing_ID FROM Bills WHERE User_ID = %s)", (user_id,))
            tables = [
                ("Staff_Contact_Numbers", "UserID"),
                ("Ratings", "User_ID"),
                ("Votes", "User_ID"),
                ("Mess_Off", "User_ID"),
                ("Bills", "User_ID"),
                ("Student", "UserID"),
                ("Staff", "UserID"),
            ]
            for table, col in tables:
                cursor.execute(f"DELETE FROM {table} WHERE {col} = %s", (user_id,))
            cursor.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
        finally:
            cursor.close()
        return {"message": f"User {user_id} and all associated records deleted successfully"}
