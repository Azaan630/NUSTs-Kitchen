from datetime import date, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class UserBase(BaseModel):
    UserID: int
    First_Name: str
    Last_Name: str
    Email: str
    Account_Type: str

class StudentBase(UserBase):
    Department: str
    Contact_Number: str
    Address: str
    Hostel_Name: str
    Room_Number: str

class StudentCreate(StudentBase):
    DoB: date
    Father_Name: str

class StudentUpdate(BaseModel):
    Department: Optional[str] = None
    Contact_Number: Optional[str] = None
    Address: Optional[str] = None
    Hostel_Name: Optional[str] = None
    Room_Number: Optional[str] = None
    Father_Name: Optional[str] = None

class BillStatus(str, Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    OVERDUE = "Overdue"

def get_two_weeks_later():
    return date.today() + timedelta(weeks=2)

def get_current_month():
    return date.today().strftime("%B")

class BillCreate(BaseModel):
    Billing_ID: int
    UserID: int
    Issue_Date: date = Field(default_factory=date.today)
    Amount: Decimal = Field(max_digits=10, decimal_places=2)
    Extra_Fee: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    Due_Date: date = Field(default_factory=get_two_weeks_later)
    Month: str = Field(default_factory=get_current_month)
    Status: BillStatus = BillStatus.UNPAID