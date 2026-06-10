from dao.base import BaseDAO
from dao.queries import (
    findUserByEmail, registerUser, registerStudent,
    registerStaff, getStaffDetails, AddStaffContactNumber, addStaffCategory,
)


class UserDAO(BaseDAO):
    def find_by_email(self, email):
        return self._fetchone(findUserByEmail, (email,))

    def get_my_profile(self, email):
        return self._fetchone(findUserByEmail, (email,))

    def get_all_users(self):
        return self._fetchall("SELECT * FROM Users")

    def get_staff_details(self, user_id):
        return self._fetchall(getStaffDetails, (user_id,))

    def register_user(self, first_name, last_name, email, account_type):
        return self._execute(registerUser, (first_name, last_name, email, account_type))

    def register_student(self, user_id, dob, department, contact, address, father, hostel, room):
        return self._execute(registerStudent, (user_id, dob, department, contact, address, father, hostel, room))

    def register_staff(self, user_id, category):
        return self._execute(registerStaff, (user_id, category))

    def add_staff_contact(self, user_id, contact_number):
        return self._execute(AddStaffContactNumber, (user_id, contact_number))

    def add_staff_category(self, category, working_hours, salary):
        return self._execute(addStaffCategory, (category, working_hours, salary))
