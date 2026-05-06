from fastapi import FastAPI, Depends, HTTPException, status, Query
import os
from starlette.middleware.cors import CORSMiddleware
from dao.queries import findUserByEmail
from database import get_db
from datetime import date

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


@app.get("/users/me")
def get_my_profile(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute(findUserByEmail, (email,))
    user_record = cursor.fetchone()
    cursor.close()

    return user_record
@app.get("/menu/today")
def get_todays_menu(
        target_date: date = Query(default=date.today()),
        db = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMenuByDate
        cursor.execute(getMenuByDate, (target_date,))
        menu_items = cursor.fetchall()

        return {
            "date": target_date.isoformat(),
            "item_count": len(menu_items),
            "menu": menu_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.get("/menu/weekly")
def get_this_week_menu(
        target_date: date = Query(default=date.today()),
        db = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getWeeklyMenu
        cursor.execute(getWeeklyMenu, (target_date, target_date))
        weekly_menu = cursor.fetchall()

        grouped_menu = {}
        for item in weekly_menu:
            date_key = item["Date"].isoformat()

            if date_key not in grouped_menu:
                grouped_menu[date_key] = []

            grouped_menu[date_key].append({
                "Item_ID": item["Item_ID"],
                "Name": item["Name"],
                "Rating": float(item["Ratings_Average"])
            })

        return {
            "start_date": target_date.isoformat(),
            "day_count": len(grouped_menu),
            "weekly_schedule": grouped_menu
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()


@app.get("/admin/students/all")
def get_all_students(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getAllUsers
        cursor.execute(getAllUsers)
        user_record = cursor.fetchall()
        return user_record

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    finally:
        cursor.close()


@app.get("/users/my_bills")
def get_my_bills(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMyBills
        cursor.execute(getMyBills, (email, ))
        bills_record = cursor.fetchall()
        return bills_record

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    finally:
        cursor.close()


@app.get("/admin/{UserID}/bill_status")
def get_student_bill_status(UserID: int, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getStudentBillDetails
        cursor.execute(getStudentBillDetails, (UserID, ))
        bills_record = cursor.fetchall()
        return bills_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.get("/bills/my_history")
def get_my_bill_history(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMyBills
        cursor.execute(getMyBills, (email, ))
        bills_history = cursor.fetchall()
        return bills_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()