from fastapi import FastAPI, Depends, HTTPException, status
import os
from starlette.middleware.cors import CORSMiddleware
from auth import get_current_user
from dao.queries import findUserByEmail
from models import UserPublic
from database import get_db
from auth import get_current_user

app = FastAPI(title="RotiRouter API")

raw_origins = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def permission_checker(allowed_roles: list):
    def mapper(email: str, db = Depends(get_db)):
        cursor = db.cursor(dictionary=True)
        cursor.execute(findUserByEmail, (email,))
        user_record = cursor.fetchone()
        cursor.close()

        if not user_record:
            raise HTTPException(status_code=404, detail="User record not found in database")

        user_account_status = user_record.get("Account_Type")

        if user_account_status not in allowed_roles:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return user_record
    return mapper

@app.get("/")
def read_root():
    return {"status": "MEOWMEOW Backend is Online"}

@app.get("/users/me")
def read_user_me(current_user: dict = Depends(get_current_user)):
    # current_user now contains verified info like:
    # current_user['email'], current_user['name'], current_user['sub']
    return {"message": f"Hello {current_user['name']}", "id": current_user['sub']}


@app.get("/users/verify")
def verify_registration(email: str, db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute(findUserByEmail, (email,))
    user_record = cursor.fetchone()
    cursor.close()

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Your NUST email is not registered in the RotiRouter system. Please contact the Mess Admin."
        )

    return {"status": "authorized", "user_details": user_record}

# Route 1: The VIP Lounge (Admin Only)
@app.get("/test/admin-only")
def test_admin(user=Depends(permission_checker(["Admin"]))):
    return {
        "message": "Success! You are a certified Admin.",
        "user_email": user["Email"]
    }

# Route 2: The General Area (Student or Admin)
@app.get("/test/any-authorized")
def test_student(user=Depends(permission_checker(["Student", "Admin"]))):
    return {
        "message": "Access Granted: Student/Admin level reached.",
        "user_role": user["Account_Type"]
    }