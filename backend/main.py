from fastapi import FastAPI, Depends, HTTPException, status, Query
import os
from starlette.middleware.cors import CORSMiddleware
from dao.queries import findUserByEmail, registerUser
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
            raise HTTPException(status_code=404, detail="User record not found")

        user_account_status = user_record.get("Account_Type")

        if user_account_status not in allowed_roles:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return user_record
    return mapper


# Standardized helper for write operations (POST, PATCH, DELETE)
def execute_transaction(db, query, params=None):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        db.commit()
        return cursor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

# Helper function for updating data (PATCH)
def update_record(db, table_name, data_model, id_column, id_value):
    # To Extract only the fields the user actually sent
    update_data = data_model.model_dump(exclude_unset=True)

    if not update_data:
        return {"message": "No changes detected"}

    # To Build the dynamic SQL "SET column1 = %s, column2 = %s"
    column_placeholders = [f"{key} = %s" for key in update_data.keys()]
    set_clause = ", ".join(column_placeholders)
    query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
    parameters = list(update_data.values()) + [id_value]
    execute_transaction(db, query, parameters)
    return {"message": f"{table_name} updated successfully"}

# Helper function for deleting data (DELETE)
def delete_record(db, table_name, id_column, id_value):
    # 1. Create the query
    query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
    cursor = execute_transaction(db, query, (id_value,))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Record with ID {id_value} not found in {table_name}."
        )

    return {"message": f"Record {id_value} deleted successfully from {table_name}"}

# READ OPERATIONS (GET)

@app.get("/")
def read_root():
    return {"status": "MEOWMEOW Backend is Online"}

@app.get("/users/verify")
def verify_registration(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import findUserByEmail
    cursor.execute(findUserByEmail, (email,))
    user_record = cursor.fetchone()
    cursor.close()
    if not user_record:
        raise HTTPException(status_code=403, detail="Access Denied: NUST email not registered.")
    return {"status": "authorized", "user_details": user_record}

@app.get("/test/admin-only")
def test_admin(user=Depends(permission_checker(["Admin"]))):
    return {
        "message": "Success! You are a certified Admin.",
        "user_email": user["Email"]
    }

@app.get("/test/any-authorized")
def test_student(user=Depends(permission_checker(["Student", "Admin"]))):
    return {
        "message": "Access Granted: Student/Admin level reached.",
        "user_role": user["Account_Type"]
    }

@app.get("/users/me")
def get_my_profile(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import findUserByEmail
    cursor.execute(findUserByEmail, (email,))
    user_record = cursor.fetchone()
    cursor.close()
    return user_record


@app.get("/menu/today")
def get_todays_menu(target_date: date = Query(default=date.today()), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getMenuByDate
    cursor.execute(getMenuByDate, (target_date,))
    menu_items = cursor.fetchall()
    cursor.close()
    return {"date": target_date.isoformat(), "item_count": len(menu_items), "menu": menu_items}


@app.get("/admin/students/all")
def get_all_students(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getAllUsers
    cursor.execute(getAllUsers)
    records = cursor.fetchall()
    cursor.close()
    return records


# WRITE OPERATIONS (POST, PATCH, DELETE)

# Students

@app.post("/admin/students/register")
def register_student(data: models.StudentCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import registerUser, registerStudent
        # Create User
        user_vals = (data.First_Name, data.Last_Name, data.Email, "Student")
        cursor.execute(registerUser, user_vals)
        new_user_id = cursor.lastrowid

        # Create Student using the new_user_id
        student_vals = (new_user_id, data.DoB, data.Department, data.Contact_Number,
                        data.Address, data.Father_Name, data.Hostel_Name, data.Room_Number)
        cursor.execute(registerStudent, student_vals)

        db.commit()
        return {"message": "User and Student registered successfully", "UserID": new_user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.patch("/admin/students/update/{UserID}")
def update_student_profile(data: models.StudentUpdate, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Student", data, "UserID", UserID)


@app.delete("/admin/students/delete/{UserID}")
def delete_student(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Student", "UserID" , UserID)


#Bills

@app.post("/admin/bills/create")
def create_bill(data: models.BillCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import createBill
    vals = (data.UserID, data.Issue_Date, data.Amount, data.Due_Date, data.Month, data.Status.value)
    cursor = execute_transaction(db, createBill, vals)
    return {"message": "Bill created", "id": cursor.lastrowid}


@app.patch("/admin/bills/update/{BillID}")
def update_bill(data: models.BillUpdate, BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Bills", data, "BillingID", BillID)


@app.delete("/admin/bills/delete/{BillID}")
def delete_bill(BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Bills", "BillingID" , BillID)


# Food Items

@app.post("/admin/food_items/create")
def create_food(data: models.Food, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import createFood
    vals = (data.Name, data.Quantity, data.Item_Expenditure)
    cursor = execute_transaction(db, createFood, vals)
    return {"message": "Food item created", "id": cursor.lastrowid}

@app.patch("/admin/food_items/update/{ItemID}")
def update_food(data: models.Food, ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Food_Items", data, "ItemID", ItemID)

@app.delete("/admin/food_items/delete/{ItemID}")
def delete_food(ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Food_Items", "ItemID" , ItemID)


# Ingredients

@app.post("/admin/ingredients/create")
def create_ingredient(data: models.Ingredient, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import createIngredient
    vals = (data.Name, data.Total_Quantity, data.Pricing)
    cursor = execute_transaction(db, createIngredient, vals)
    return {"message": "Ingredient created", "id": cursor.lastrowid}

@app.patch("/admin/ingredients/update/{IngredientID}")
def update_ingredient(data: models.Ingredient, IngredientID : int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Ingredients", data, "IngredientID", IngredientID)

@app.delete("/admin/ingredients/delete/{IngredientID}")
def delete_ingredient(IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Ingredients", "IngredientID", IngredientID)


# Staff

@app.post("/admin/staff/register")
def register_staff(data: models.Staff, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import registerUser, registerStaff
        # Create User
        user_vals = (data.First_Name, data.Last_Name, data.Email, "Staff")
        cursor.execute(registerUser, user_vals)
        new_user_id = cursor.lastrowid

        # Create Staff using the new_user_id
        staff_vals = (new_user_id, data.Category)
        cursor.execute(registerStaff, staff_vals)

        db.commit()
        return {"message": "User and Staff registered successfully", "UserID": new_user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.post("/admin/staff/update")
def update_student_profile(data: models.Staff, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Staff", data, "UserID", UserID)