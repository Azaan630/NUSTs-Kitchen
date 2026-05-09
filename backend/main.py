from fastapi import FastAPI, Depends, HTTPException, status, Query
import os
from starlette.middleware.cors import CORSMiddleware
from dao.queries import findUserByEmail
from database import get_db
from datetime import date
import models
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

@app.get("/analytics/ingredients")
def get_ingredients(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getIngredients
        cursor.execute(getIngredients)
        ingredients = cursor.fetchall()
        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.post("/admin/students/register")
def register_student(data:models.StudentCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import registerStudent
        values = (
            data.First_Name, data.Last_Name, data.Email, data.Account_Type,
            data.DoB, data.Department,
            data.Contact_Number, data.Address, data.Father_Name,
            data.Hostel_Name, data.Room_Number
        )
        cursor.execute(registerStudent, values)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.patch("/admin/students/update/{UserID}")
def update_student_profile(data: models.StudentUpdate, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return {"message": "No changes detected"}

        column_placeholders = [f"{key} = %s" for key in update_data.keys()]
        set_clause = ", ".join(column_placeholders)
        update_query = f"""UPDATE Student 
                           SET {set_clause} 
                           WHERE UserID = %s"""

        parameters = list(update_data.values()) + [UserID]
        cursor.execute(update_query, parameters)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.post("/admin/bills/create")
def create_bill(data: models.BillCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import createBill
        values = (
            data.UserID, data.Issue_Date, data.Amount, data.Extra_Fee, data.Due_Date, data.Month, data.Status.value
        )
        cursor.execute(createBill, values)
        db.commit()
        return {"message": "Bill created successfully", "id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()