from fastapi import FastAPI
from database import get_db_connection

app = FastAPI(title="RotiRouter API")

@app.get("/")
def read_root():
    return {"status": "RotiRouter Backend is Online"}

@app.get("/health-check")
def db_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"database": "Connected"}
    except Exception as e:
        return {"database": "Error", "details": str(e)}