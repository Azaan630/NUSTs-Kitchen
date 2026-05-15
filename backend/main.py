from fastapi import FastAPI, Depends, HTTPException, status, Query
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from dao.queries import findUserByEmail
from database import get_db
from datetime import date, timedelta
import models
import mysql.connector

from models import PollRequest

app = FastAPI(title="NUST's Kitchen API")

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
    return {"message": f"Update successful"}

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

def maintain_menu_schedule(db):
    today = date.today()
    next_week_check = today + timedelta(days=7)

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT 1 FROM Menu_Schedule WHERE Date = %s LIMIT 1",
            (next_week_check,)
        )
        exists = cursor.fetchone()
        if not exists:
            # Generate dates for today + 14 days
            for i in range(15):
                target_date = today + timedelta(days=i)
                for meal in ['Breakfast', 'Lunch', 'Dinner']:

                    # Using INSERT IGNORE to prevent duplication
                    cursor.execute(
                        """INSERT IGNORE INTO Menu_Schedule (Date, meal_type, status)
                        VALUES (%s, %s, 'active')""",
                        (target_date, meal)
                    )
            db.commit()

    except Exception as e:
        print(f"Maintenance Error: {e}")
        db.rollback()

    finally:
        cursor.close()


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

@app.get("/users/me") # ALSO FOR STAFF
def get_my_profile(email: str, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import findUserByEmail
    cursor.execute(findUserByEmail, (email,))
    user_record = cursor.fetchone()
    cursor.close()
    return user_record

@app.get("/menu/today") # ALSO FOR STAFF
def get_todays_menu(target_date: date = Query(default=date.today()), db=Depends(get_db)):
    maintain_menu_schedule(db)
    cursor = db.cursor(dictionary=True)
    from dao.queries import getMenuByDate
    cursor.execute(getMenuByDate, (target_date,))
    menu_items = cursor.fetchall()
    cursor.close()
    return {"date": target_date.isoformat(), "item_count": len(menu_items), "menu": menu_items}

@app.get("/menu/weekly") # ALSO FOR STAFF
def get_weekly_menu(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getWeeklyMenu
    cursor.execute(getWeeklyMenu)
    menu_items = cursor.fetchall()
    cursor.close()
    return menu_items

@app.get("/admin/students/all")
def get_all_students(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getAllUsers
    cursor.execute(getAllUsers)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/admin/staff/details/{UserID}")
def get_staff_details(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getStaffDetails
    cursor.execute(getStaffDetails, (UserID,))
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/admin/food/costs") # ALSO FOR STAFF
def get_food_costs(user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getAllFoodCosts
    cursor.execute(getAllFoodCosts)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/admin/food/{ItemID}") # ALSO FOR STAFF
def get_food_by_id(ItemID: int, db=Depends(get_db), user=Depends(permission_checker(["Admin", "Staff"]))):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getFoodByID
    cursor.execute(getFoodByID, (ItemID,))
    records = cursor.fetchall()
    cursor.close()
    return records



@app.get("/admin/monthly_billing_summary")
def get_monthly_billing_summary(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    from dao.queries import getMonthBills
    cursor.execute(getMonthBills)
    records = cursor.fetchall()
    cursor.close()
    return records

@app.get("/admin/{UserID}/bill_status")
def get_student_bill_status(UserID: int, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getStudentBillDetails
        cursor.execute(getStudentBillDetails, (UserID,))
        bills_record = cursor.fetchall()
        return bills_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.get("/bills/my_history")
def get_my_bill_history(email: str, db=Depends(get_db), user=Depends(permission_checker(["Admin", "Student"]))):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMyBills
        cursor.execute(getMyBills, (email,))
        bills_history = cursor.fetchall()
        return bills_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.get("/analytics/ingredients") # ALSO FOR STAFF
def get_ingredients(user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
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

@app.get("/recipes") # ALSO FOR STAFF
def get_recipes(user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    cursor = (db.cursor(dictionary=True))
    try:
        from dao.queries import getRecipes
        cursor.execute(getRecipes)
        recipes = cursor.fetchall()
        return recipes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cursor.close()

@app.get("/users/my_bills")
def get_my_bills(email: str, db=Depends(get_db), user=Depends(permission_checker(["Admin", "Student"]))):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMyBills
        cursor.execute(getMyBills, (email,))
        bills_record = cursor.fetchall()
        return bills_record

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    finally:
        cursor.close()


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
    delete_record(db, "Student", "UserID", UserID)
    return delete_record(db, "Users", "UserID" , UserID)


# Staff

@app.post("/admin/staff/register")
def register_staff(data: models.Staff, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import registerUser, registerStaff
        # Create User
        user_vals = (data.First_Name, data.Last_Name, data.Email, "Staff")
        cursor.execute(registerUser, (user_vals,))
        new_user_id = cursor.lastrowid

        # Create Staff using the new_user_id
        staff_vals = (new_user_id, data.Category)
        cursor.execute(registerStaff, (staff_vals,))

        db.commit()
        return {"message": "User and Staff registered successfully", "UserID": new_user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@app.post("/admin/staff/update")
def update_staff_profile(data: models.Staff, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Staff", data, "UserID", UserID)

@app.delete("/admin/staff/delete/{UserID}")
def delete_staff(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Staff", "UserID" , UserID)

@app.post("/admin/staff/contact/{UserID}")
def add_staff_contact(data: models.StaffContactNumbers, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
     from dao.queries import AddStaffContactNumber
     vals = (UserID, data.ContactID,)
     cursor = execute_transaction(db, AddStaffContactNumber, vals)
     return {"message": "Food item created", "id": cursor.lastrowid}

@app.post("/admin/staff/category")
def add_staff_category(data: models.StaffCategory, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    from dao.queries import addStaffCategory
    cursor = execute_transaction(db, addStaffCategory, data)
    return {"message": "Food item created", "id": cursor.lastrowid}


#Bills

@app.post("/admin/bills/create")
def create_bill(data: models.BillCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import createBill
    vals = (data.UserID, data.Issue_Date, data.Amount, data.Due_Date, data.Month, data.Status.value,)
    cursor = execute_transaction(db, createBill, vals)
    return {"message": "Bill created", "id": cursor.lastrowid}


@app.patch("/admin/bills/update/{BillID}")
def update_bill(data: models.BillUpdate, BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Bills", data, "BillingID", BillID)


@app.delete("/admin/bills/delete/{BillID}")
def delete_bill(BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Bills", "BillingID" , BillID)

# Bill PDF Generation

def draw_challan_pdf(bill):
    buffer = BytesIO()
    # Using landscape gives us width for 3 columns
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    col_width = width / 3

    def draw_section(x_offset, label):
        # 1. Vertical separator (Dashed line)
        c.setDash(1, 2)
        c.line(x_offset + col_width - 5, 20, x_offset + col_width - 5, height - 20)
        c.setDash([])  # Reset to solid lines

        # 2. Header
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x_offset + (col_width / 2), height - 50, "NUST SEECS MESS")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x_offset + (col_width / 2), height - 65, label)

        # 3. Bill Details
        c.setFont("Helvetica", 11)
        y = height - 120
        c.drawString(x_offset + 30, y, f"Bill ID:    {bill['Billing_ID']}")
        c.drawString(x_offset + 30, y - 20, f"Name:       {bill['First_Name']} {bill['Last_Name']}")
        c.drawString(x_offset + 30, y - 40, f"Month:      {bill['Month']}")
        c.drawString(x_offset + 30, y - 60, f"Due Date:   {bill['Due_Date']}")

        # 4. Amount Box
        c.rect(x_offset + 25, y - 110, col_width - 60, 40)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_offset + 35, y - 100, f"Total Amount: Rs. {bill['Amount']}")

        # 5. Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(x_offset + 30, 60, "Bank Stamp / Signature")

    # Draw the three copies
    draw_section(0, "BANK COPY")
    draw_section(col_width, "OFFICE COPY")
    draw_section(col_width * 2, "STUDENT COPY")

    c.save()
    buffer.seek(0)
    return buffer

@app.get("/student/bills/download/{BillingID}")
def generate_pdf(BillingID: int, email:str, db=Depends(get_db), user=Depends(permission_checker(["Student"]))):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getBillPDF
        cursor.execute(getBillPDF, (BillingID, email,))
        bill_record = cursor.fetchone()

        if not bill_record:
            raise HTTPException(status_code=404, detail="Bill not found")

        pdf_buffer = draw_challan_pdf(bill_record)

        filename = f"MessBill_{bill_record['Month']}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        cursor.close()


# Food Items

@app.post("/admin/food_items/create")
def create_food(data: models.Food, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import createFood
    vals = (data.Name, data.Quantity, data.Price,)
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
    vals = (data.Name, data.Total_Quantity, data.Pricing, data.Unit,)
    cursor = execute_transaction(db, createIngredient, vals)
    return {"message": "Ingredient created", "id": cursor.lastrowid}

@app.patch("/admin/ingredients/update/{IngredientID}")
def update_ingredient(data: models.Ingredient, IngredientID : int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return update_record(db, "Ingredients", data, "IngredientID", IngredientID)

@app.delete("/admin/ingredients/delete/{IngredientID}")
def delete_ingredient(IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return delete_record(db, "Ingredients", "IngredientID", IngredientID)


# Recipes

@app.post("/admin/add_recipe/{ItemID}/{IngredientID}/{Ingredient_Quantity}")
def add_recipe(Ingredient_Quantity: float, ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import addRecipe
    vals = (ItemID, IngredientID, Ingredient_Quantity)
    cursor = execute_transaction(db, addRecipe, vals)
    return {"message": "Recipe added", "id": cursor.lastrowid}

@app.patch("/admin/recipe/update/{ItemID}/{IngredientID}")
def update_recipe(data: models.FoodItemIngredient, ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"message": "No changes detected"}

    # To Build the dynamic SQL "SET column1 = %s, column2 = %s"
    column_placeholders = [f"{key} = %s" for key in update_data.keys()]
    set_clause = ", ".join(column_placeholders)
    query = f"UPDATE Food_Item_Ingredients SET {set_clause} WHERE Item_ID= %s AND Ingredient_ID = %s"
    parameters = list(update_data.values()) + [ItemID, IngredientID]
    execute_transaction(db, query, parameters)
    return {"message": "Recipe updated successfully"}

@app.delete("/admin/recipe/{ItemID}/{IngredientID}")
def delete_recipe(ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    query = f"DELETE FROM Food_Item_Ingredients WHERE Item_ID = %s AND Ingredient_ID = %s"
    cursor = execute_transaction(db, query, (ItemID, IngredientID))

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Record with ID {ItemID} + {IngredientID} not found in Food_Item_Ingredients."
        )

    return {"message": f"Record {ItemID} + {IngredientID} deleted successfully from Food_Item_Ingredients."}


# Voting

@app.post("/admin/poll/start")
def start_poll(poll: PollRequest, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    cursor = db.cursor(dictionary=True)

    try:
        # 1. Reset Vote_Count for all items
        cursor.execute("UPDATE Food_Items SET Vote_Count = 0")

        # 2. Clear all previous votes
        cursor.execute("DELETE FROM Votes")

        # 3. Join IDs into "1,2,3"
        poll_str = ",".join(map(str, poll.item_ids))

        query = "INSERT INTO System_Config (Config_Key, Value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE Value = %s"

        cursor.execute(query, ("active_poll_items", poll_str, poll_str))
        cursor.execute(query, ("active_poll_meal_type", poll.meal_type, poll.meal_type))

        db.commit()

        return {"status": "Poll Started"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()

@app.get("/poll/active")
def get_active_poll(db=Depends(get_db), user=Depends(permission_checker(["Admin", "Student"]))):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_items'")
        active_poll_items = cursor.fetchone()

        cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_meal_type'")
        active_meal_type = cursor.fetchone()

        if not active_poll_items or not active_poll_items['Value']:
            return {"active": False}

        id_list = active_poll_items['Value'].split(",")
        format_strings = ','.join(['%s'] * len(id_list))
        query = f"SELECT Item_ID, Name, Price FROM Food_Items WHERE Item_ID IN ({format_strings})"

        cursor.execute(query, tuple(id_list))
        items = cursor.fetchall()

        # Convert Decimal to float for JSON serialization
        for item in items:
            if 'Price' in item and item['Price'] is not None:
                item['Price'] = float(item['Price'])

        return {
            "active": True, 
            "meal_type": active_meal_type['Value'] if active_meal_type else "Poll",
            "items": items
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@app.post("/poll/vote/{ItemID}/{UserID}")
def cast_vote(UserID: int, ItemID: int, email: str, db=Depends(get_db), user=Depends(permission_checker(["Student"]))):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_items'")
    result = cursor.fetchone()
    cursor.close()

    if not result or not result['Value']:
        raise HTTPException(status_code=404, detail="No active poll")

    active_ids = result['Value'].split(",")
    if str(ItemID) not in [i.strip() for i in active_ids]:
        raise HTTPException(status_code=400, detail="This item is not part of the active poll")

    cursor2 = db.cursor()
    try:
        cursor2.callproc('sp_AddVote', [UserID, ItemID])
        db.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:  # MySQL Duplicate Entry Error
            raise HTTPException(status_code=400, detail="You already voted for this!")
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        cursor2.close()
    return {"status": "Voted successfully"}


@app.get("/admin/poll/results")
def get_poll_results(db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_items'")
        config = cursor.fetchone()

        if not config or not config['Value']:
            return {"results": [], "message": "No active poll items found"}

        item_ids = [i.strip() for i in config["Value"].split(",") if i.strip()]
        if not item_ids:
            return {"results": []}

        format_strings = ','.join(['%s'] * len(item_ids))

        query = f"""SELECT Item_ID, Name, Vote_Count
                    FROM Food_Items
                    WHERE Item_ID IN ({format_strings})
                    ORDER BY Vote_Count DESC"""
        cursor.execute(query, tuple(item_ids))
        results = cursor.fetchall()
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()


# Menu Food Items

@app.post("/admin/menu_schedule/{ItemID}/{menu_date}/{meal_type}")
def add_menu(meal_type: str, menu_date: date, ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    from dao.queries import addMenuItem

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"""SELECT Schedule_ID FROM Menu_Schedule WHERE Date = %s AND meal_type = %s""", (menu_date, meal_type,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=400, detail="No schedule found")

    schedule_id = result['Schedule_ID']
    execute_transaction(db, addMenuItem, (schedule_id, ItemID))
    return {"message": "Item added to menu"}

@app.patch("/admin/menu_schedule/{ItemID}/{ScheduleID}")
def update_menu(data: models.MenuFoodItem, ItemID: int, ScheduleID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"message": "No changes detected"}

    # To build the dynamic SQL "SET column1 = %s, column2 = %s"
    column_placeholders = [f"{key} = %s" for key in update_data.keys()]
    set_clause = ", ".join(column_placeholders)
    query = f"UPDATE Menu_Food_Items SET {set_clause} WHERE Item_ID = %s AND Schedule_ID = %s"
    parameters = list(update_data.values()) + [ItemID, ScheduleID]
    execute_transaction(db, query, parameters)
    return {"message": f"Recipe updated successfully"}

@app.delete("/admin/recipe/{ItemID}/{ScheduleID}")
def delete_menu(ItemID: int, ScheduleID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    query = f"DELETE FROM Menu_Food_Items WHERE Item_ID = %s AND Schedule_ID = %s"
    cursor = execute_transaction(db, query, (ItemID, ScheduleID,))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Record with ID {ItemID} + {ScheduleID} not found in Menu_Food_Items table."
        )

    return {"message": f"Record {ItemID} + {ScheduleID} deleted successfully from Menu_Food_Items table."}



# Ratings

@app.post("/student/rating/{UserID}/{ItemID}/{Date}/{meal_type}/{score}")
def rate_food(score: int, Date: date, meal_type: str, UserID: int, ItemID: int, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    from dao.queries import getCurrentScheduleID
    cursor = db.cursor(dictionary=True)
    cursor.execute(getCurrentScheduleID, (Date, meal_type,))
    current_schedule = cursor.fetchone()
    cursor.close()
    if not current_schedule:
        raise HTTPException(status_code=400, detail="No schedule found")

    current_schedule_id = current_schedule['Schedule_ID']
    from dao.queries import giveFoodRating
    execute_transaction(db, giveFoodRating, (UserID, ItemID, current_schedule_id, score,))
    return "Food Rated successfully"

@app.get("/getFoodRating/{ItemID}/{Date}/{meal_type}")
def get_food_rating(Date: date, meal_type: str, ItemID: int, db=Depends(get_db)):
    from dao.queries import getCurrentScheduleID
    cursor = db.cursor(dictionary=True)
    cursor.execute(getCurrentScheduleID, (Date, meal_type,))
    current_schedule = cursor.fetchone()
    cursor.close()
    if not current_schedule:
        raise HTTPException(status_code=400, detail="No schedule found")

    current_schedule_id = current_schedule['Schedule_ID']

    cursor2 = db.cursor(dictionary=True)
    from dao.queries import getFoodRating
    cursor2.execute(getFoodRating, (current_schedule_id, ItemID,))
    rating = cursor2.fetchone()
    cursor2.close()
    if not rating:
        rating = "NULL"
    return {"rating": rating}


# Payment Logging

@app.post("/admin/bills/pay/{BillingID}")
def record_payment(BillingID: int, amount: float, method: str, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        # Calls sp_RecordPayment(p_billing_id, p_amount, p_method)
        cursor.callproc('sp_RecordPayment', [BillingID, amount, method])
        db.commit()
        return {"message": "Payment recorded and bill status updated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# Mess Off

@app.post("/student/mess_off/request/{UserID}/{StartDate}/{EndDate}")
def request_mess_off(UserID: int, StartDate: date, EndDate: date, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        from dao.queries import requestMessOff
        cursor.execute(requestMessOff, (UserID, StartDate, EndDate,))
        db.commit()
        return {"message": "Mess off requested successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Database Error")
    finally:
        cursor.close()

@app.post("/student/mess_off/cancel/{MessOffID}")
def cancel_mess_off_request(MessOffID: int, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        from dao.queries import cancelMessOff
        cursor.execute(cancelMessOff, (MessOffID,))
        db.commit()
        return {"message": "Mess off request cancelled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Database Error")
    finally:
        cursor.close()

@app.post("/admin/mess-off/approve/{RequestID}")
def approve_mess_off(RequestID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.callproc('sp_ApproveMessOff', [RequestID])
        db.commit()
        return {"message": "Mess off approved successfully"}
    except mysql.connector.Error as err:
        if err.sqlstate == '45000':
            raise HTTPException(status_code=400, detail=err.msg)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Database Error")
    finally:
        cursor.close()

@app.get("/student/mess-off/history")
def get_mess_off_history(email: str, user=Depends(permission_checker(["Admin", "Student"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMessOffThisMonth
        cursor.execute(getMessOffThisMonth)
        result = cursor.fetchall()
        return {"status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Database Error")
    finally:
        cursor.close()

@app.get("/student/mess-off/{MessOffID}")
def get_mess_off(MessOffID: int, user=Depends(permission_checker(["Student", "Admin"])), db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        from dao.queries import getMessOffStatus
        cursor.execute(getMessOffStatus, (MessOffID,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Database Error")
    finally:
        cursor.close()