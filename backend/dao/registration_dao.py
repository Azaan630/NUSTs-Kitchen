from fastapi import HTTPException
from dao.base import BaseDAO

REGISTRATION_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS Registration_Requests (
    RequestID      INT PRIMARY KEY AUTO_INCREMENT,
    First_Name     VARCHAR(50) NOT NULL,
    Last_Name      VARCHAR(50) NOT NULL,
    Email          VARCHAR(100) NOT NULL,
    Account_Type   ENUM('Student', 'Staff') NOT NULL,
    Sex            ENUM('Male', 'Female') DEFAULT NULL,
    DoB            DATE,
    Department     VARCHAR(100),
    Contact_Number VARCHAR(20),
    Address        TEXT,
    Father_Name    VARCHAR(100),
    Hostel_Name    VARCHAR(100),
    Room_Number    VARCHAR(20),
    Category       VARCHAR(30),
    Profile_Picture VARCHAR(500) DEFAULT NULL,
    Status         ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    Created_At     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


class RegistrationDAO(BaseDAO):
    def ensure_table_exists(self):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(REGISTRATION_TABLE_DDL)
            self.db.commit()
        finally:
            cursor.close()

    def create_request(self, data):
        self.ensure_table_exists()
        existing = self._fetchone(
            "SELECT Email FROM Users WHERE Email = %s", (data.Email,)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        self._execute(
            """INSERT INTO Registration_Requests
            (First_Name, Last_Name, Email, Account_Type, Sex, DoB, Department,
             Contact_Number, Address, Father_Name, Hostel_Name, Room_Number,
             Category, Profile_Picture, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')""",
            (
                data.First_Name, data.Last_Name, data.Email, data.Account_Type,
                data.Sex, data.DoB, data.Department, data.Contact_Number, data.Address,
                data.Father_Name, data.Hostel_Name, data.Room_Number, data.Category,
                data.Profile_Picture,
            )
        )
        return {"message": "Registration request submitted for admin approval"}

    def get_requests(self, status="Pending"):
        self.ensure_table_exists()
        return self._fetchall(
            "SELECT * FROM Registration_Requests WHERE Status = %s ORDER BY Created_At DESC",
            (status,)
        )

    def get_request_by_id(self, request_id):
        self.ensure_table_exists()
        return self._fetchone(
            "SELECT * FROM Registration_Requests WHERE RequestID = %s AND Status = 'Pending'",
            (request_id,)
        )

    def approve_request(self, request_id, data=None):
        self.ensure_table_exists()
        req = self._fetchone(
            "SELECT * FROM Registration_Requests WHERE RequestID = %s AND Status = 'Pending'",
            (request_id,)
        )
        if not req:
            raise HTTPException(status_code=404, detail="Pending request not found")

        from dao.queries import registerUser, registerStudent, registerStaff

        first = data.First_Name if data and data.First_Name else req["First_Name"]
        last  = data.Last_Name  if data and data.Last_Name  else req["Last_Name"]
        email = data.Email       if data and data.Email       else req["Email"]
        sex   = data.Sex         if data and data.Sex         else req.get("Sex")
        pp    = req.get("Profile_Picture") or (data.Profile_Picture if data else None)
        role  = req["Account_Type"]

        user_cur = self._execute(registerUser, (first, last, email, role, sex, pp))
        new_user_id = user_cur.lastrowid

        if role == "Student":
            self._execute(registerStudent, (
                new_user_id,
                data.DoB if data and data.DoB else req["DoB"],
                data.Department if data and data.Department else req["Department"],
                data.Contact_Number if data and data.Contact_Number else req["Contact_Number"],
                data.Address if data and data.Address else req["Address"],
                data.Father_Name if data and data.Father_Name else req["Father_Name"],
                data.Hostel_Name if data and data.Hostel_Name else req["Hostel_Name"],
                data.Room_Number if data and data.Room_Number else req["Room_Number"],
            ))
        elif role == "Staff":
            cat = data.Category if data and data.Category else req["Category"]
            self._execute(registerStaff, (new_user_id, cat))

        self._execute(
            "UPDATE Registration_Requests SET Status = 'Approved' WHERE RequestID = %s",
            (request_id,)
        )
        return {"message": f"{role} registered successfully", "UserID": new_user_id}

    def reject_request(self, request_id):
        self.ensure_table_exists()
        cursor = self._execute(
            "UPDATE Registration_Requests SET Status = 'Rejected' WHERE RequestID = %s AND Status = 'Pending'",
            (request_id,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pending request not found")
        return {"message": "Request rejected"}
