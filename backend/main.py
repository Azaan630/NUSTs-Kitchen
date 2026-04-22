from fastapi import FastAPI, Depends, HTTPException, status
import os
from starlette.middleware.cors import CORSMiddleware
from auth import get_current_user
from dao.queries import findUserByEmail
from models import UserPublic
from database import get_db

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