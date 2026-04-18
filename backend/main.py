from fastapi import FastAPI, Depends
import os
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from dao.queries import GET_ALL_USERS
from models import UserPublic
from database import get_db
from dao import queries

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

@app.get("/users", response_model=list[UserPublic])
def get_users(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute(GET_ALL_USERS)
    data = cursor.fetchall()
    cursor.close()
    return [UserPublic(**row) for row in data]