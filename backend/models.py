from datetime import date, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

#User

class UserBase(BaseModel):
    First_Name: str
    Last_Name: str
    Email: str
    Account_Type: Optional[str] = None

#Student

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

#Staff

class Staff(UserBase):
    Category: str

class StaffUpdate(BaseModel):
    Category: str

class StaffCategory(BaseModel):
    Category: str
    WorkingHours: float
    Salary: float

class StaffContactNumbers(BaseModel):
    ContactID: int
    UserID: int
    ContactNumber: str

#Bill

class BillStatus(str, Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    OVERDUE = "Overdue"

def get_two_weeks_later():
    return date.today() + timedelta(weeks=2)

def get_current_month():
    return date.today().strftime("%B")

class BillCreate(BaseModel):
    UserID: int
    Issue_Date: date = Field(default_factory=date.today)
    Amount: Decimal = Field(max_digits=10, decimal_places=2)
    Due_Date: date = Field(default_factory=get_two_weeks_later)
    Month: str = Field(default_factory=get_current_month)
    Status: BillStatus = BillStatus.UNPAID

class BillUpdate(BaseModel):
    Issue_Date: date = Field(default_factory=date.today)
    Amount: Decimal = Field(max_digits=10, decimal_places=2)
    Due_Date: date = Field(default_factory=get_two_weeks_later)
    Month: str = Field(default_factory=get_current_month)
    Status: BillStatus = BillStatus.UNPAID

#Food

class Food(BaseModel):
    Name: str
    Quantity: Optional[float] = 0
    Price: float

#Ingredient

class Ingredient(BaseModel):
    Name: str
    Total_Quantity: float
    Unit_cost: float
    Unit: str


#Recipes

class FoodItemIngredient(BaseModel):
    Ingredient_Quantity: float


# Menu Schedule

class MenuFoodItem(BaseModel):
    ScheduleID: int
    ItemID: int

class PollRequest(BaseModel):
    meal_type: str
    item_ids: list[int]