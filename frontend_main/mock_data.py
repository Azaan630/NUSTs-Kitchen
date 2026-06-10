from datetime import date, datetime, timedelta
import copy

_db = {}

MOCK_EMAIL = "guest@demo.app"


def init_session():
    global _db
    today = date.today()
    _db = {
        "food_items": [
            {"Item_ID": 1, "Name": "Chicken Biryani", "Price": 150.0, "Quantity": 1.0, "Estimated_Cost": 120.0},
            {"Item_ID": 2, "Name": "Daal Chawal", "Price": 80.0, "Quantity": 1.0, "Estimated_Cost": 45.0},
            {"Item_ID": 3, "Name": "Chicken Karahi", "Price": 200.0, "Quantity": 1.0, "Estimated_Cost": 160.0},
            {"Item_ID": 4, "Name": "Nihari", "Price": 180.0, "Quantity": 1.0, "Estimated_Cost": 140.0},
            {"Item_ID": 5, "Name": "Chicken Pulao", "Price": 130.0, "Quantity": 1.0, "Estimated_Cost": 100.0},
            {"Item_ID": 6, "Name": "Anda Paratha", "Price": 60.0, "Quantity": 1.0, "Estimated_Cost": 35.0},
        ],
        "students": [
            {"UserID": 101, "First_Name": "Alice", "Last_Name": "Khan", "Email": "alice@seecs.edu.pk", "Account_Type": "Student", "Contact_Number": "03001234567", "Department": "CS", "Hostel_Name": "A1", "Room_Number": "101"},
            {"UserID": 102, "First_Name": "Bob", "Last_Name": "Ahmed", "Email": "bob@seecs.edu.pk", "Account_Type": "Student", "Contact_Number": "03007654321", "Department": "EE", "Hostel_Name": "B2", "Room_Number": "205"},
            {"UserID": 103, "First_Name": "Charlie", "Last_Name": "Ali", "Email": "charlie@seecs.edu.pk", "Account_Type": "Student", "Contact_Number": "03001112233", "Department": "MS", "Hostel_Name": "C3", "Room_Number": "312"},
        ],
        "staff": [
            {"UserID": 201, "First_Name": "Chef", "Last_Name": "Rashid", "Email": "chef@kitchen.pk", "Account_Type": "Staff", "Category": "Head Chef"},
            {"UserID": 202, "First_Name": "Ali", "Last_Name": "Raza", "Email": "ali@kitchen.pk", "Account_Type": "Staff", "Category": "Cook"},
        ],
        "menu_schedule": [
            {"Schedule_ID": 1, "Item_ID": 1, "Date": today.isoformat(), "meal_type": "Lunch", "Food_Item_Name": "Chicken Biryani", "Ratings_Average": 4.2},
            {"Schedule_ID": 2, "Item_ID": 6, "Date": today.isoformat(), "meal_type": "Breakfast", "Food_Item_Name": "Anda Paratha", "Ratings_Average": 3.8},
            {"Schedule_ID": 3, "Item_ID": 4, "Date": today.isoformat(), "meal_type": "Dinner", "Food_Item_Name": "Nihari", "Ratings_Average": 4.5},
            {"Schedule_ID": 4, "Item_ID": 2, "Date": (today + timedelta(days=1)).isoformat(), "meal_type": "Lunch", "Food_Item_Name": "Daal Chawal", "Ratings_Average": 3.5},
            {"Schedule_ID": 5, "Item_ID": 3, "Date": (today + timedelta(days=1)).isoformat(), "meal_type": "Dinner", "Food_Item_Name": "Chicken Karahi", "Ratings_Average": 4.7},
        ],
        "ingredients": [
            {"Ingredient_ID": 1, "Name": "Rice", "Unit": "kg", "Unit_cost": 150.0, "Total_Quantity": 50.0},
            {"Ingredient_ID": 2, "Name": "Chicken", "Unit": "kg", "Unit_cost": 400.0, "Total_Quantity": 30.0},
            {"Ingredient_ID": 3, "Name": "Daal", "Unit": "kg", "Unit_cost": 200.0, "Total_Quantity": 25.0},
            {"Ingredient_ID": 4, "Name": "Onions", "Unit": "kg", "Unit_cost": 80.0, "Total_Quantity": 40.0},
            {"Ingredient_ID": 5, "Name": "Tomatoes", "Unit": "kg", "Unit_cost": 100.0, "Total_Quantity": 35.0},
            {"Ingredient_ID": 6, "Name": "Oil", "Unit": "L", "Unit_cost": 350.0, "Total_Quantity": 20.0},
        ],
        "recipes": [
            {"Item_ID": 1, "Name": "Rice", "Ingredient_Quantity": 0.5, "Unit": "kg"},
            {"Item_ID": 1, "Name": "Chicken", "Ingredient_Quantity": 0.3, "Unit": "kg"},
            {"Item_ID": 1, "Name": "Onions", "Ingredient_Quantity": 0.2, "Unit": "kg"},
            {"Item_ID": 2, "Name": "Daal", "Ingredient_Quantity": 0.4, "Unit": "kg"},
            {"Item_ID": 2, "Name": "Tomatoes", "Ingredient_Quantity": 0.2, "Unit": "kg"},
            {"Item_ID": 3, "Name": "Chicken", "Ingredient_Quantity": 0.5, "Unit": "kg"},
            {"Item_ID": 3, "Name": "Oil", "Ingredient_Quantity": 0.1, "Unit": "kg"},
        ],
        "bills": [
            {"Billing_ID": 1, "User_ID": 101, "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 2500.0, "Total_Collected": 2500.0, "Outstanding": 0.0, "Status": "Paid", "Month": today.strftime("%Y-%m"), "Amount": 2500.0, "Due_Date": (today + timedelta(days=15)).isoformat()},
            {"Billing_ID": 2, "User_ID": 102, "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 2500.0, "Total_Collected": 1500.0, "Outstanding": 1000.0, "Status": "Unpaid", "Month": today.strftime("%Y-%m"), "Amount": 2500.0, "Due_Date": (today + timedelta(days=15)).isoformat()},
        ],
        "mess_off_requests": [
            {"Mess_Off_ID": 1, "User_ID": 101, "Start_Date": (today - timedelta(days=2)).isoformat(), "End_Date": today.isoformat(), "Request_Date": (today - timedelta(days=3)).isoformat(), "Status": "Approved"},
            {"Mess_Off_ID": 2, "User_ID": 102, "Start_Date": (today + timedelta(days=5)).isoformat(), "End_Date": (today + timedelta(days=7)).isoformat(), "Request_Date": today.isoformat(), "Status": "Pending"},
        ],
        "next_schedule_id": 6,
        "next_mess_off_id": 3,
        "next_billing_id": 3,
        "next_food_id": 7,
        "poll_active": False,
        "poll_meal_type": "",
        "poll_items": [],
        "poll_votes": {},
        "registration_requests": [
            {"RequestID": 1, "First_Name": "New", "Last_Name": "Student", "Email": "new.student@seecs.edu.pk",
             "Account_Type": "Student", "Department": "CS", "Contact_Number": "03001112233",
             "DoB": "2004-01-15", "Address": "H-12 NUST", "Father_Name": "Mr. Student",
             "Hostel_Name": "Ghazali", "Room_Number": "105", "Status": "Pending",
             "Created_At": date.today().isoformat()},
        ],
    }


def get_students():
    return copy.deepcopy(_db.get("students", []))


def register_student(data):
    sid = len(_db["students"]) + 101
    entry = {"UserID": sid, "Account_Type": "Student", **(data.copy())}
    _db["students"].append(entry)
    return entry


def delete_student(uid):
    _db["students"] = [s for s in _db["students"] if s.get("UserID") != uid]
    return {}


def update_student(uid, data):
    for s in _db["students"]:
        if s.get("UserID") == uid:
            s.update(data)
    return {}


def get_staff():
    return copy.deepcopy(_db.get("staff", []))


def register_staff(data):
    sid = len(_db["staff"]) + 201
    entry = {"UserID": sid, "Account_Type": "Staff", **(data.copy())}
    _db["staff"].append(entry)
    return entry


def delete_staff(uid):
    _db["staff"] = [s for s in _db["staff"] if s.get("UserID") != uid]
    return {}


def update_staff(uid, data):
    for s in _db["staff"]:
        if s.get("UserID") == uid:
            s.update(data)
    return {}


def get_food_costs():
    return copy.deepcopy(_db.get("food_items", []))


def create_food(data):
    fid = _db["next_food_id"]
    _db["next_food_id"] += 1
    entry = {"Item_ID": fid, "Estimated_Cost": data.get("Price", 0) * 0.8, **data}
    _db["food_items"].append(entry)
    return entry


def update_food(iid, data):
    for f in _db["food_items"]:
        if f.get("Item_ID") == iid:
            f.update(data)
    return {}


def delete_food(iid):
    _db["food_items"] = [f for f in _db["food_items"] if f.get("Item_ID") != iid]
    return {}


def get_mess_off_requests():
    return copy.deepcopy(_db.get("mess_off_requests", []))


def approve_mess_off(rid):
    for r in _db["mess_off_requests"]:
        if r.get("Mess_Off_ID") == rid:
            r["Status"] = "Approved"


def reject_mess_off(rid):
    for r in _db["mess_off_requests"]:
        if r.get("Mess_Off_ID") == rid:
            r["Status"] = "Cancelled"


def get_monthly_bills():
    return copy.deepcopy(_db.get("bills", []))


def create_bill(data):
    bid = _db["next_billing_id"]
    _db["next_billing_id"] += 1
    entry = {"Billing_ID": bid, **data}
    _db["bills"].append(entry)
    return entry


def update_bill(bid, data):
    for b in _db["bills"]:
        if b.get("Billing_ID") == bid:
            b.update(data)
            b["Outstanding"] = b.get("Total_Amount", 0) - b.get("Total_Collected", 0)
    return {}


def delete_bill(bid):
    _db["bills"] = [b for b in _db["bills"] if b.get("Billing_ID") != bid]
    return {}


def pay_bill(bid, amount):
    for b in _db["bills"]:
        if b.get("Billing_ID") == bid:
            b["Total_Collected"] = b.get("Total_Collected", 0) + amount
            b["Outstanding"] = b.get("Total_Amount", 0) - b["Total_Collected"]
            if b["Outstanding"] <= 0:
                b["Status"] = "Paid"
    return {}


def get_weekly_menu():
    return copy.deepcopy(_db.get("menu_schedule", []))


def add_menu_item(item_id, menu_date, meal_type):
    sid = _db["next_schedule_id"]
    _db["next_schedule_id"] += 1
    name = "Item"
    for f in _db["food_items"]:
        if f.get("Item_ID") == int(item_id):
            name = f.get("Name", "Item")
    entry = {"Schedule_ID": sid, "Item_ID": int(item_id), "Date": menu_date, "meal_type": meal_type, "Food_Item_Name": name}
    _db["menu_schedule"].append(entry)
    return entry


def delete_menu_item(item_id, schedule_id):
    _db["menu_schedule"] = [
        m for m in _db["menu_schedule"]
        if not (m.get("Item_ID") == int(item_id) and m.get("Schedule_ID") == int(schedule_id))
    ]
    return {}


def start_poll(data):
    _db["poll_active"] = True
    _db["poll_meal_type"] = data.get("meal_type", "")
    _db["poll_items"] = []
    _db["poll_votes"] = {}
    for pid in data.get("item_ids", []):
        name = "Item"
        price = 0
        for f in _db["food_items"]:
            if f.get("Item_ID") == pid:
                name = f.get("Name", "Item")
                price = f.get("Price", 0)
        _db["poll_items"].append({"Item_ID": pid, "Name": name, "Price": price})
    return {"message": "Poll started"}


def get_poll_results():
    results = []
    for item in _db["poll_items"]:
        iid = item["Item_ID"]
        count = len([v for v in _db["poll_votes"].values() if v == iid])
        results.append({"Name": item["Name"], "Vote_Count": count, "Item_ID": iid})
    return {"results": results}


def get_active_poll():
    if not _db["poll_active"]:
        return {"active": False, "items": []}
    return {"active": True, "items": copy.deepcopy(_db["poll_items"])}


def cast_vote(item_id, user_id):
    _db["poll_votes"][user_id] = item_id
    return {"message": "Vote cast"}


def rate_food_item(user_id, item_id, meal_date, meal_type, score):
    for m in _db["menu_schedule"]:
        if m.get("Item_ID") == item_id and m.get("meal_type") == meal_type:
            m["user_rating"] = score
            m["Ratings_Average"] = score
    return {"message": "Rating saved"}


def get_my_bills():
    return copy.deepcopy(_db.get("bills", []))


def request_mess_off(user_id, start_date, end_date):
    mid = _db["next_mess_off_id"]
    _db["next_mess_off_id"] += 1
    entry = {
        "Mess_Off_ID": mid, "User_ID": user_id,
        "Start_Date": start_date.isoformat(), "End_Date": end_date.isoformat(),
        "Request_Date": date.today().isoformat(), "Status": "Pending",
    }
    _db["mess_off_requests"].append(entry)
    return {"message": "Request submitted!"}


def cancel_mess_off(mid):
    for r in _db["mess_off_requests"]:
        if r.get("Mess_Off_ID") == mid:
            r["Status"] = "Cancelled"
    return {"message": "Cancelled"}


def get_mess_off_history():
    return {"status": copy.deepcopy(_db.get("mess_off_requests", []))}


def get_ingredients():
    return copy.deepcopy(_db.get("ingredients", []))


def get_recipes():
    return copy.deepcopy(_db.get("recipes", []))


def get_todays_menu():
    today = date.today().isoformat()
    menu = [m for m in _db["menu_schedule"] if m.get("Date") == today]
    return {"menu": copy.deepcopy(menu), "date": today}


def get_registration_requests(status="Pending"):
    return copy.deepcopy(_db.get("registration_requests", []))


def submit_registration_request(data):
    rid = len(_db.get("registration_requests", [])) + 1
    entry = {"RequestID": rid, **data, "Status": "Pending", "Created_At": date.today().isoformat()}
    _db.setdefault("registration_requests", []).append(entry)
    return {"message": "Request submitted"}


def approve_registration(rid, data=None):
    for r in _db.get("registration_requests", []):
        if r.get("RequestID") == rid:
            r["Status"] = "Approved"
            if data:
                r.update(data)
            role = r.get("Account_Type", "Student")
            if role == "Student":
                sid = len(_db["students"]) + 101
                _db["students"].append({
                    "UserID": sid, "First_Name": r["First_Name"], "Last_Name": r["Last_Name"],
                    "Email": r["Email"], "Account_Type": "Student",
                    "Department": r.get("Department", ""), "Contact_Number": r.get("Contact_Number", ""),
                    "Hostel_Name": r.get("Hostel_Name", ""), "Room_Number": r.get("Room_Number", ""),
                })
            elif role == "Staff":
                sid = len(_db["staff"]) + 201
                _db["staff"].append({
                    "UserID": sid, "First_Name": r["First_Name"], "Last_Name": r["Last_Name"],
                    "Email": r["Email"], "Account_Type": "Staff",
                    "Category": r.get("Category", ""),
                })
    return {"message": "Approved"}


def reject_registration(rid):
    for r in _db.get("registration_requests", []):
        if r.get("RequestID") == rid:
            r["Status"] = "Rejected"
    return {"message": "Rejected"}
