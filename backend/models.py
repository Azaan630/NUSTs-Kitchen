from datetime import date
from pydantic import BaseModel, Field

class UserPublic(BaseModel):
     UserID: int = Field(alias="UserID")
     First_Name: str = Field(alias="First_Name")
     Last_Name: str = Field(alias="Last_Name")
     Email: str = Field(alias="Email")
     Account_Type: str = Field(alias="Account_Type")

     # This allows you to still use the camelCase names
     # when creating the model manually in Python
     model_config = {"populate_by_name": True}
"""
class User(BaseModel):
    userID: int
    firstName: str
    lastName: str
    email: str
    accountType: str
    password: str

class Student(UserPublic):
    dateOfBirth: date
    age: int = date.today().year - dateOfBirth.year
    fatherName: str
    address: str
    department: str
    hostelName: str
    roomNumber: int
    contactNumber: str

class Staff(UserPublic):
    contactNumber: str
    category: str
    salary: int
    workingHours: str """