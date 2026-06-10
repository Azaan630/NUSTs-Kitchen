from datetime import date, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    First_Name: str
    Last_Name: str
    Email: str
    Account_Type: Optional[str] = None


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


class Staff(UserBase):
    Category: str


class StaffUpdate(BaseModel):
    Category: str


class StaffCategory(BaseModel):
    Category: str
    WorkingHours: float
    Salary: float


class StaffContactNumbers(BaseModel):
    UserID: int
    ContactNumber: str


class BillStatus(str, Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    OVERDUE = "Overdue"


class BillCreate(BaseModel):
    UserID: int
    Issue_Date: date = Field(default_factory=date.today)
    Amount: float = Field(gt=0)
    Due_Date: date = Field(default_factory=lambda: date.today() + timedelta(weeks=2))
    Month: str = Field(default_factory=lambda: date.today().strftime("%Y-%m-01"))
    Status: BillStatus = BillStatus.UNPAID


class BillUpdate(BaseModel):
    Issue_Date: Optional[date] = None
    Amount: Optional[float] = None
    Due_Date: Optional[date] = None
    Month: Optional[str] = None
    Status: Optional[BillStatus] = None


class Food(BaseModel):
    Name: str = Field(min_length=1)
    Quantity: Optional[float] = 0
    Price: float = Field(gt=0)


class Ingredient(BaseModel):
    Name: str = Field(min_length=1)
    Total_Quantity: float = Field(gt=0)
    Unit_cost: float = Field(gt=0)
    Unit: str = Field(min_length=1)


class FoodItemIngredient(BaseModel):
    Ingredient_Quantity: float = Field(gt=0)


class MenuFoodItem(BaseModel):
    ScheduleID: int
    ItemID: int


class PollRequest(BaseModel):
    meal_type: str
    item_ids: list[int]


class RegistrationRequestCreate(BaseModel):
    First_Name: str = Field(min_length=1)
    Last_Name: str = Field(min_length=1)
    Email: str = Field(min_length=5)
    Account_Type: str
    DoB: Optional[date] = None
    Department: Optional[str] = None
    Contact_Number: Optional[str] = None
    Address: Optional[str] = None
    Father_Name: Optional[str] = None
    Hostel_Name: Optional[str] = None
    Room_Number: Optional[str] = None
    Category: Optional[str] = None


class RegistrationRequestUpdate(BaseModel):
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None
    Email: Optional[str] = None
    DoB: Optional[date] = None
    Department: Optional[str] = None
    Contact_Number: Optional[str] = None
    Address: Optional[str] = None
    Father_Name: Optional[str] = None
    Hostel_Name: Optional[str] = None
    Room_Number: Optional[str] = None
    Category: Optional[str] = None
