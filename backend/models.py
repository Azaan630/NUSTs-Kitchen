from datetime import date
from pydantic import BaseModel, Field

class UserPublic(BaseModel):
     UserID: int
     First_Name: str
     Last_Name: str
     Email: str
     Account_Type: str

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