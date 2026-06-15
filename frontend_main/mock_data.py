from datetime import date, datetime, timedelta
import copy

_db = {}

MOCK_EMAIL = "guest@demo.app"


def init_session():
    global _db
    today = date.today()
    _db = {
        "food_items": [
            {"Item_ID": 1,  "Name": "Chicken Biryani",  "Price": 250.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/biryani/400/300",  "Ratings_Average": 4.5, "Vote_Count": 12},
            {"Item_ID": 2,  "Name": "Daal Mash",        "Price": 150.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/daalmash/400/300","Ratings_Average": 3.8, "Vote_Count": 8},
            {"Item_ID": 3,  "Name": "Special Tea",       "Price": 50.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/tea/400/300",      "Ratings_Average": 4.2, "Vote_Count": 15},
            {"Item_ID": 4,  "Name": "Aloo Paratha",      "Price": 80.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/paratha/400/300",  "Ratings_Average": 4.0, "Vote_Count": 9},
            {"Item_ID": 5,  "Name": "Chicken Karahi",    "Price": 450.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/karahi/400/300",   "Ratings_Average": 4.7, "Vote_Count": 20},
            {"Item_ID": 6,  "Name": "Mixed Vegetable",   "Price": 120.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/veg/400/300",       "Ratings_Average": 3.5, "Vote_Count": 5},
            {"Item_ID": 7,  "Name": "Roti",              "Price": 15.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/roti/400/300",     "Ratings_Average": 4.1, "Vote_Count": 3},
            {"Item_ID": 8,  "Name": "Nihari",            "Price": 380.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/nihari/400/300",    "Ratings_Average": 4.8, "Vote_Count": 25},
            {"Item_ID": 9,  "Name": "Chicken Pulao",     "Price": 200.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/pulao/400/300",     "Ratings_Average": 4.3, "Vote_Count": 10},
            {"Item_ID": 10, "Name": "Omelette",          "Price": 60.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/omelette/400/300", "Ratings_Average": 3.9, "Vote_Count": 7},
            {"Item_ID": 11, "Name": "Haleem",            "Price": 300.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/haleem/400/300",    "Ratings_Average": 4.6, "Vote_Count": 18},
            {"Item_ID": 12, "Name": "Chicken Tikka",     "Price": 350.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/tikka/400/300",    "Ratings_Average": 4.4, "Vote_Count": 14},
            {"Item_ID": 13, "Name": "Fruit Chaat",       "Price": 70.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/chaat/400/300",    "Ratings_Average": 4.0, "Vote_Count": 6},
            {"Item_ID": 14, "Name": "Keema Naan",        "Price": 120.0, "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/keema/400/300",    "Ratings_Average": 4.2, "Vote_Count": 11},
            {"Item_ID": 15, "Name": "Gulab Jamun",       "Price": 50.0,  "Quantity": 1.0, "Image_Path": "https://picsum.photos/seed/gulab/400/300",   "Ratings_Average": 4.9, "Vote_Count": 22},
        ],
        "students": [
            {"UserID": 2,  "First_Name": "Muhammad", "Last_Name": "Azaan",  "Email": "mazaan.bscs25seecs@seecs.edu.pk", "Account_Type": "Student", "Contact_Number": "0300-1234567", "Department": "Computer Science",      "Hostel_Name": "Ghazali", "Room_Number": "101", "DoB": "2004-05-15", "Sex": "Male",   "Profile_Picture": "https://picsum.photos/seed/student1/200/200", "Address": "H-12 NUST Islamabad", "Father_Name": "John Azaan"},
            {"UserID": 4,  "First_Name": "Aisha",    "Last_Name": "Khan",   "Email": "aisha.student@seecs.edu.pk",      "Account_Type": "Student", "Contact_Number": "0300-2345678", "Department": "Software Engineering",   "Hostel_Name": "Rumi",    "Room_Number": "205", "DoB": "2003-08-22", "Sex": "Female", "Profile_Picture": "https://picsum.photos/seed/aisha/200/200",    "Address": "H-12 NUST Islamabad", "Father_Name": "Imran Khan"},
            {"UserID": 5,  "First_Name": "Bilal",    "Last_Name": "Ahmed",  "Email": "bilal.student@seecs.edu.pk",      "Account_Type": "Student", "Contact_Number": "0300-3456789", "Department": "Electrical Engineering", "Hostel_Name": "Attar",   "Room_Number": "310", "DoB": "2004-01-10", "Sex": "Male",   "Profile_Picture": "https://picsum.photos/seed/bilal/200/200",    "Address": "H-12 NUST Islamabad", "Father_Name": "Ahmed Bilal"},
            {"UserID": 7,  "First_Name": "Zara",     "Last_Name": "Malik",  "Email": "zara.student@seecs.edu.pk",       "Account_Type": "Student", "Contact_Number": "0300-4567890", "Department": "Mechanical Engineering", "Hostel_Name": "Ghazali", "Room_Number": "115", "DoB": "2005-03-14", "Sex": "Female", "Profile_Picture": "https://picsum.photos/seed/zara/200/200",     "Address": "H-12 NUST Islamabad", "Father_Name": "Tariq Malik"},
            {"UserID": 8,  "First_Name": "Hassan",   "Last_Name": "Raza",   "Email": "hassan.student@seecs.edu.pk",     "Account_Type": "Student", "Contact_Number": "0300-5678901", "Department": "Computer Science",      "Hostel_Name": "Rumi",    "Room_Number": "220", "DoB": "2003-11-30", "Sex": "Male",   "Profile_Picture": "https://picsum.photos/seed/hassan/200/200",   "Address": "H-12 NUST Islamabad", "Father_Name": "Raza Shah"},
            {"UserID": 9,  "First_Name": "Sara",     "Last_Name": "Javed",  "Email": "sara.student@seecs.edu.pk",       "Account_Type": "Student", "Contact_Number": "0300-6789012", "Department": "Biotechnology",          "Hostel_Name": "Attar",   "Room_Number": "405", "DoB": "2004-07-05", "Sex": "Female", "Profile_Picture": "https://picsum.photos/seed/sara/200/200",     "Address": "H-12 NUST Islamabad", "Father_Name": "Javed Iqbal"},
            {"UserID": 11, "First_Name": "Usman",    "Last_Name": "Dar",    "Email": "usman.dar@seecs.edu.pk",          "Account_Type": "Student", "Contact_Number": "0300-7890123", "Department": "Civil Engineering",      "Hostel_Name": "Iqbal",   "Room_Number": "118", "DoB": "2005-02-18", "Sex": "Male",   "Profile_Picture": "https://picsum.photos/seed/usman/200/200",    "Address": "H-12 NUST Islamabad", "Father_Name": "Usman Dar"},
        ],
        "staff": [
            {"UserID": 3,  "First_Name": "Muhammad", "Last_Name": "Azaan", "Email": "zainif630@gmail.com",  "Account_Type": "Staff", "Category": "Server",    "Salary": 30000.00, "Working_hours": 6.0, "Profile_Picture": "https://picsum.photos/seed/staff1/200/200",  "Sex": "Male"},
            {"UserID": 6,  "First_Name": "Fatima",   "Last_Name": "Ali",   "Email": "fatima.staff@seecs.edu.pk",  "Account_Type": "Staff", "Category": "Head Chef", "Salary": 85000.00, "Working_hours": 9.0, "Profile_Picture": "https://picsum.photos/seed/fatima/200/200",   "Sex": "Female"},
            {"UserID": 10, "First_Name": "Omar",     "Last_Name": "Sheikh","Email": "omar.staff@seecs.edu.pk",    "Account_Type": "Staff", "Category": "Chef",      "Salary": 50000.00, "Working_hours": 8.0, "Profile_Picture": "https://picsum.photos/seed/omar/200/200",     "Sex": "Male"},
        ],
        "staff_categories": [
            {"Category": "Head Chef", "Working_hours": 9.0, "Salary": 85000.00},
            {"Category": "Chef",      "Working_hours": 8.0, "Salary": 50000.00},
            {"Category": "Server",    "Working_hours": 6.0, "Salary": 30000.00},
            {"Category": "Cleaner",   "Working_hours": 8.0, "Salary": 28000.00},
        ],
        "menu_schedule": _build_menu(today),
        "ingredients": [
            {"Ingredient_ID": 1,  "Name": "Basmati Rice",     "Unit": "kg",     "Unit_cost": 350.0,  "Total_Quantity": 500.0,  "Image_Path": "https://picsum.photos/seed/rice/400/300"},
            {"Ingredient_ID": 2,  "Name": "Chicken Breast",   "Unit": "kg",     "Unit_cost": 600.0,  "Total_Quantity": 200.0,  "Image_Path": "https://picsum.photos/seed/chicken/400/300"},
            {"Ingredient_ID": 3,  "Name": "Cooking Oil",      "Unit": "Litre",  "Unit_cost": 450.0,  "Total_Quantity": 100.0,  "Image_Path": "https://picsum.photos/seed/oil/400/300"},
            {"Ingredient_ID": 4,  "Name": "Salt",             "Unit": "kg",     "Unit_cost": 50.0,   "Total_Quantity": 50.0,   "Image_Path": "https://picsum.photos/seed/salt/400/300"},
            {"Ingredient_ID": 5,  "Name": "Lentils (Daal)",   "Unit": "kg",     "Unit_cost": 280.0,  "Total_Quantity": 150.0,  "Image_Path": "https://picsum.photos/seed/daal/400/300"},
            {"Ingredient_ID": 6,  "Name": "Onion",            "Unit": "kg",     "Unit_cost": 150.0,  "Total_Quantity": 100.0,  "Image_Path": "https://picsum.photos/seed/onion/400/300"},
            {"Ingredient_ID": 7,  "Name": "Tomato",           "Unit": "kg",     "Unit_cost": 100.0,  "Total_Quantity": 80.0,   "Image_Path": "https://picsum.photos/seed/tomato/400/300"},
            {"Ingredient_ID": 8,  "Name": "Garlic",           "Unit": "kg",     "Unit_cost": 400.0,  "Total_Quantity": 20.0,   "Image_Path": "https://picsum.photos/seed/garlic/400/300"},
            {"Ingredient_ID": 9,  "Name": "Ginger",           "Unit": "kg",     "Unit_cost": 350.0,  "Total_Quantity": 20.0,   "Image_Path": "https://picsum.photos/seed/ginger/400/300"},
            {"Ingredient_ID": 10, "Name": "Wheat Flour",      "Unit": "kg",     "Unit_cost": 120.0,  "Total_Quantity": 1000.0, "Image_Path": "https://picsum.photos/seed/flour/400/300"},
            {"Ingredient_ID": 11, "Name": "Butter",           "Unit": "kg",     "Unit_cost": 800.0,  "Total_Quantity": 30.0,   "Image_Path": "https://picsum.photos/seed/butter/400/300"},
            {"Ingredient_ID": 12, "Name": "Yogurt",           "Unit": "kg",     "Unit_cost": 200.0,  "Total_Quantity": 60.0,   "Image_Path": "https://picsum.photos/seed/yogurt/400/300"},
            {"Ingredient_ID": 13, "Name": "Red Chili Powder", "Unit": "kg",     "Unit_cost": 450.0,  "Total_Quantity": 15.0,   "Image_Path": "https://picsum.photos/seed/chili/400/300"},
            {"Ingredient_ID": 14, "Name": "Turmeric Powder",  "Unit": "kg",     "Unit_cost": 350.0,  "Total_Quantity": 12.0,   "Image_Path": "https://picsum.photos/seed/turmeric/400/300"},
            {"Ingredient_ID": 15, "Name": "Cumin Seeds",      "Unit": "kg",     "Unit_cost": 600.0,  "Total_Quantity": 10.0,   "Image_Path": "https://picsum.photos/seed/cumin/400/300"},
            {"Ingredient_ID": 16, "Name": "Milk",             "Unit": "Litre",  "Unit_cost": 180.0,  "Total_Quantity": 80.0,   "Image_Path": "https://picsum.photos/seed/milk/400/300"},
            {"Ingredient_ID": 17, "Name": "Eggs",             "Unit": "dozen",  "Unit_cost": 240.0,  "Total_Quantity": 50.0,   "Image_Path": "https://picsum.photos/seed/eggs/400/300"},
            {"Ingredient_ID": 18, "Name": "Potato",           "Unit": "kg",     "Unit_cost": 80.0,   "Total_Quantity": 200.0,  "Image_Path": "https://picsum.photos/seed/potato/400/300"},
            {"Ingredient_ID": 19, "Name": "Green Chili",      "Unit": "kg",     "Unit_cost": 200.0,  "Total_Quantity": 15.0,   "Image_Path": "https://picsum.photos/seed/greenchili/400/300"},
            {"Ingredient_ID": 20, "Name": "Coriander Leaves", "Unit": "bunch",  "Unit_cost": 30.0,   "Total_Quantity": 50.0,   "Image_Path": "https://picsum.photos/seed/coriander/400/300"},
        ],
        "recipes": [
            {"Item_ID": 1,  "Name": "Basmati Rice",     "Ingredient_Quantity": 0.50, "Unit": "kg", "Ingredient_ID": 1},
            {"Item_ID": 1,  "Name": "Chicken Breast",   "Ingredient_Quantity": 0.30, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 1,  "Name": "Cooking Oil",      "Ingredient_Quantity": 0.10, "Unit": "Litre","Ingredient_ID": 3},
            {"Item_ID": 1,  "Name": "Onion",            "Ingredient_Quantity": 0.15, "Unit": "kg", "Ingredient_ID": 6},
            {"Item_ID": 1,  "Name": "Tomato",           "Ingredient_Quantity": 0.10, "Unit": "kg", "Ingredient_ID": 7},
            {"Item_ID": 2,  "Name": "Lentils (Daal)",   "Ingredient_Quantity": 0.40, "Unit": "kg", "Ingredient_ID": 5},
            {"Item_ID": 2,  "Name": "Cooking Oil",      "Ingredient_Quantity": 0.05, "Unit": "Litre","Ingredient_ID": 3},
            {"Item_ID": 3,  "Name": "Milk",             "Ingredient_Quantity": 0.20, "Unit": "Litre","Ingredient_ID": 16},
            {"Item_ID": 3,  "Name": "Ginger",           "Ingredient_Quantity": 0.01, "Unit": "kg", "Ingredient_ID": 9},
            {"Item_ID": 4,  "Name": "Wheat Flour",      "Ingredient_Quantity": 0.20, "Unit": "kg", "Ingredient_ID": 10},
            {"Item_ID": 4,  "Name": "Potato",           "Ingredient_Quantity": 0.15, "Unit": "kg", "Ingredient_ID": 18},
            {"Item_ID": 5,  "Name": "Chicken Breast",   "Ingredient_Quantity": 0.50, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 5,  "Name": "Tomato",           "Ingredient_Quantity": 0.20, "Unit": "kg", "Ingredient_ID": 7},
            {"Item_ID": 5,  "Name": "Onion",            "Ingredient_Quantity": 0.10, "Unit": "kg", "Ingredient_ID": 6},
            {"Item_ID": 6,  "Name": "Potato",           "Ingredient_Quantity": 0.20, "Unit": "kg", "Ingredient_ID": 18},
            {"Item_ID": 6,  "Name": "Onion",            "Ingredient_Quantity": 0.15, "Unit": "kg", "Ingredient_ID": 6},
            {"Item_ID": 7,  "Name": "Wheat Flour",      "Ingredient_Quantity": 0.15, "Unit": "kg", "Ingredient_ID": 10},
            {"Item_ID": 8,  "Name": "Chicken Breast",   "Ingredient_Quantity": 0.40, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 9,  "Name": "Basmati Rice",     "Ingredient_Quantity": 0.40, "Unit": "kg", "Ingredient_ID": 1},
            {"Item_ID": 9,  "Name": "Chicken Breast",   "Ingredient_Quantity": 0.25, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 10, "Name": "Eggs",             "Ingredient_Quantity": 0.13, "Unit": "dozen","Ingredient_ID": 17},
            {"Item_ID": 11, "Name": "Lentils (Daal)",   "Ingredient_Quantity": 0.30, "Unit": "kg", "Ingredient_ID": 5},
            {"Item_ID": 11, "Name": "Chicken Breast",   "Ingredient_Quantity": 0.20, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 12, "Name": "Chicken Breast",   "Ingredient_Quantity": 0.40, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 12, "Name": "Yogurt",           "Ingredient_Quantity": 0.15, "Unit": "kg", "Ingredient_ID": 12},
            {"Item_ID": 13, "Name": "Potato",           "Ingredient_Quantity": 0.10, "Unit": "kg", "Ingredient_ID": 18},
            {"Item_ID": 14, "Name": "Wheat Flour",      "Ingredient_Quantity": 0.25, "Unit": "kg", "Ingredient_ID": 10},
            {"Item_ID": 14, "Name": "Chicken Breast",   "Ingredient_Quantity": 0.30, "Unit": "kg", "Ingredient_ID": 2},
            {"Item_ID": 15, "Name": "Milk",             "Ingredient_Quantity": 0.15, "Unit": "Litre","Ingredient_ID": 16},
        ],
        "bills": [
            {"Billing_ID": 1,  "User_ID": 2,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 4500.0, "Total_Collected": 3500.0, "Outstanding": 1000.0, "Status": "Unpaid",  "Month": today.strftime("%Y-%m"), "Amount": 4500.0, "Due_Date": (today + timedelta(days=10)).isoformat()},
            {"Billing_ID": 2,  "User_ID": 2,  "Billing_Month": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m"), "Total_Amount": 4200.0, "Total_Collected": 4200.0, "Outstanding": 0.0,    "Status": "Paid",    "Month": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m"), "Amount": 4200.0, "Due_Date": (today - timedelta(days=30)).isoformat()},
            {"Billing_ID": 3,  "User_ID": 4,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 3800.0, "Total_Collected": 0.0, "Outstanding": 3800.0, "Status": "Overdue", "Month": today.strftime("%Y-%m"), "Amount": 3800.0, "Due_Date": (today - timedelta(days=2)).isoformat()},
            {"Billing_ID": 4,  "User_ID": 4,  "Billing_Month": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m"), "Total_Amount": 4000.0, "Total_Collected": 4000.0, "Outstanding": 0.0,    "Status": "Paid",    "Month": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m"), "Amount": 4000.0, "Due_Date": (today - timedelta(days=40)).isoformat()},
            {"Billing_ID": 5,  "User_ID": 5,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 4500.0, "Total_Collected": 0.0, "Outstanding": 4500.0, "Status": "Unpaid",  "Month": today.strftime("%Y-%m"), "Amount": 4500.0, "Due_Date": (today + timedelta(days=10)).isoformat()},
            {"Billing_ID": 6,  "User_ID": 7,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 4000.0, "Total_Collected": 0.0, "Outstanding": 4000.0, "Status": "Unpaid",  "Month": today.strftime("%Y-%m"), "Amount": 4000.0, "Due_Date": (today + timedelta(days=15)).isoformat()},
            {"Billing_ID": 7,  "User_ID": 8,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 5000.0, "Total_Collected": 0.0, "Outstanding": 5000.0, "Status": "Unpaid",  "Month": today.strftime("%Y-%m"), "Amount": 5000.0, "Due_Date": (today + timedelta(days=8)).isoformat()},
            {"Billing_ID": 8,  "User_ID": 9,  "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 4100.0, "Total_Collected": 4100.0, "Outstanding": 0.0,    "Status": "Paid",    "Month": today.strftime("%Y-%m"), "Amount": 4100.0, "Due_Date": (today + timedelta(days=12)).isoformat()},
            {"Billing_ID": 9,  "User_ID": 11, "Billing_Month": today.strftime("%Y-%m"), "Total_Amount": 4400.0, "Total_Collected": 4400.0, "Outstanding": 0.0,    "Status": "Paid",    "Month": today.strftime("%Y-%m"), "Amount": 4400.0, "Due_Date": (today + timedelta(days=20)).isoformat()},
        ],
        "mess_off_requests": [
            {"Mess_Off_ID": 1, "User_ID": 2,  "Start_Date": (today + timedelta(days=5)).isoformat(),  "End_Date": (today + timedelta(days=10)).isoformat(), "Request_Date": today.isoformat(), "Status": "Pending"},
            {"Mess_Off_ID": 2, "User_ID": 4,  "Start_Date": (today + timedelta(days=1)).isoformat(),  "End_Date": (today + timedelta(days=3)).isoformat(),  "Request_Date": today.isoformat(), "Status": "Approved"},
            {"Mess_Off_ID": 3, "User_ID": 5,  "Start_Date": (today + timedelta(days=8)).isoformat(),  "End_Date": (today + timedelta(days=12)).isoformat(), "Request_Date": today.isoformat(), "Status": "Pending"},
            {"Mess_Off_ID": 4, "User_ID": 7,  "Start_Date": (today + timedelta(days=2)).isoformat(),  "End_Date": (today + timedelta(days=4)).isoformat(),  "Request_Date": today.isoformat(), "Status": "Pending"},
            {"Mess_Off_ID": 5, "User_ID": 8,  "Start_Date": (today - timedelta(days=2)).isoformat(),  "End_Date": (today + timedelta(days=1)).isoformat(),  "Request_Date": (today - timedelta(days=3)).isoformat(), "Status": "Approved"},
            {"Mess_Off_ID": 6, "User_ID": 2,  "Start_Date": (today - timedelta(days=5)).isoformat(),  "End_Date": (today - timedelta(days=2)).isoformat(),  "Request_Date": (today - timedelta(days=6)).isoformat(), "Status": "Rejected"},
        ],
        "next_schedule_id": 22,
        "next_mess_off_id": 7,
        "next_billing_id": 10,
        "next_food_id": 16,
        "poll_active": True,
        "poll_meal_type": "Lunch",
        "poll_items": [
            {"Item_ID": 5,  "Name": "Chicken Karahi",  "Price": 450.0},
            {"Item_ID": 9,  "Name": "Chicken Pulao",   "Price": 200.0},
            {"Item_ID": 12, "Name": "Chicken Tikka",   "Price": 350.0},
        ],
        "poll_votes": {},
        "registration_requests": [
            {"RequestID": 1, "First_Name": "Usman",  "Last_Name": "Dar",     "Email": "usman.dar@seecs.edu.pk",    "Account_Type": "Student", "Department": "Civil Engineering",       "Contact_Number": "0300-7890123", "DoB": "2005-02-18", "Address": "H-12 NUST", "Father_Name": "Mr. Dar",    "Hostel_Name": "Iqbal",   "Room_Number": "118", "Status": "Pending", "Profile_Picture": "https://picsum.photos/seed/usman/200/200",  "Created_At": today.isoformat()},
            {"RequestID": 2, "First_Name": "Nadia",  "Last_Name": "Hussain", "Email": "nadia.hussain@seecs.edu.pk", "Account_Type": "Student", "Department": "Business Administration",  "Contact_Number": "0300-8901234", "DoB": "2004-09-12", "Address": "H-12 NUST", "Father_Name": "Mr. Hussain","Hostel_Name": "Ghazali", "Room_Number": "210", "Status": "Pending", "Profile_Picture": "https://picsum.photos/seed/nadia/200/200", "Created_At": today.isoformat()},
            {"RequestID": 3, "First_Name": "Kamran", "Last_Name": "Tariq",   "Email": "kamran.tariq@gmail.com",     "Account_Type": "Staff",   "Category":    "Server",                                            "Contact_Number": "0300-9012345", "DoB": "1990-03-05", "Address": "H-12 NUST", "Father_Name": "Mr. Tariq",  "Hostel_Name": None,     "Room_Number": None,   "Status": "Pending", "Profile_Picture": "https://picsum.photos/seed/kamran/200/200","Created_At": today.isoformat()},
        ],
        "votes": [
            {"User_ID": 2, "Food_ID": 1}, {"User_ID": 2, "Food_ID": 5}, {"User_ID": 2, "Food_ID": 8},
            {"User_ID": 4, "Food_ID": 5}, {"User_ID": 4, "Food_ID": 12}, {"User_ID": 4, "Food_ID": 15},
            {"User_ID": 5, "Food_ID": 1}, {"User_ID": 5, "Food_ID": 9},
        ],
        "ratings": [
            {"User_ID": 2, "Item_ID": 1, "Schedule_ID": 2, "Score": 5},
            {"User_ID": 2, "Item_ID": 3, "Schedule_ID": 1, "Score": 3},
            {"User_ID": 4, "Item_ID": 1, "Schedule_ID": 2, "Score": 4},
            {"User_ID": 5, "Item_ID": 8, "Schedule_ID": 6, "Score": 5},
        ],
    }


def _build_menu(today):
    menu = []
    # 7 days × 3 meals
    days = [today + timedelta(days=i) for i in range(7)]
    meals = ["Breakfast", "Lunch", "Dinner"]
    # Map: (day_idx, meal_idx) → list of (Item_ID, Name)
    plan = {
        (0,0): [(3, "Special Tea"), (10, "Omelette"), (4, "Aloo Paratha")],
        (0,1): [(1, "Chicken Biryani"), (5, "Chicken Karahi"), (7, "Roti")],
        (0,2): [(2, "Daal Mash"), (6, "Mixed Vegetable"), (7, "Roti")],
        (1,0): [(4, "Aloo Paratha"), (3, "Special Tea"), (10, "Omelette")],
        (1,1): [(9, "Chicken Pulao"), (12, "Chicken Tikka"), (7, "Roti")],
        (1,2): [(8, "Nihari"), (14, "Keema Naan"), (7, "Roti")],
        (2,0): [(10, "Omelette"), (4, "Aloo Paratha"), (3, "Special Tea")],
        (2,1): [(1, "Chicken Biryani"), (6, "Mixed Vegetable")],
        (2,2): [(2, "Daal Mash"), (14, "Keema Naan")],
        (3,0): [(3, "Special Tea"), (10, "Omelette"), (13, "Fruit Chaat")],
        (3,1): [(5, "Chicken Karahi"), (7, "Roti")],
        (3,2): [(11, "Haleem"), (7, "Roti")],
        (4,0): [(4, "Aloo Paratha"), (3, "Special Tea")],
        (4,1): [(8, "Nihari"), (7, "Roti")],
        (4,2): [(9, "Chicken Pulao"), (6, "Mixed Vegetable"), (7, "Roti")],
        (5,0): [(10, "Omelette"), (4, "Aloo Paratha"), (15, "Gulab Jamun")],
        (5,1): [(12, "Chicken Tikka"), (1, "Chicken Biryani")],
        (5,2): [(2, "Daal Mash"), (7, "Roti"), (15, "Gulab Jamun")],
        (6,0): [(13, "Fruit Chaat"), (3, "Special Tea")],
        (6,1): [(5, "Chicken Karahi"), (9, "Chicken Pulao"), (7, "Roti")],
        (6,2): [(11, "Haleem"), (14, "Keema Naan"), (7, "Roti")],
    }
    sid = 0
    for di, d in enumerate(days):
        for mi, meal in enumerate(meals):
            items = plan.get((di, mi), [])
            for item_id, item_name in items:
                sid += 1
                rating = 4.0
                if item_id in (1,5,8,11,12,15): rating = 4.5
                elif item_id in (6,): rating = 3.5
                elif item_id in (3,4,9,14): rating = 4.2
                menu.append({
                    "Schedule_ID": sid, "Item_ID": item_id,
                    "Date": d.isoformat(), "meal_type": meal,
                    "Food_Item_Name": item_name,
                    "Ratings_Average": rating,
                })
    return menu


# ── Query helpers ─────────────────────────────────────────────────

def get_students():
    return copy.deepcopy(_db.get("students", []))


def register_student(data):
    sid = max((s.get("UserID", 0) for s in _db["students"]), default=10) + 1
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


def get_staff_categories():
    return copy.deepcopy(_db.get("staff_categories", []))


def register_staff(data):
    sid = max((s.get("UserID", 0) for s in _db["staff"]), default=10) + 1
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
    entry = {"Item_ID": fid, "Ratings_Average": 0, "Vote_Count": 0, **data}
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
    entry = {"Schedule_ID": sid, "Item_ID": int(item_id), "Date": menu_date, "meal_type": meal_type, "Food_Item_Name": name, "Ratings_Average": 4.0}
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
    return {"active": True, "items": copy.deepcopy(_db["poll_items"]), "meal_type": _db.get("poll_meal_type", "Poll")}


def end_poll():
    _db["poll_active"] = False
    _db["poll_meal_type"] = ""
    _db["poll_items"] = []
    _db["poll_votes"] = {}
    return {"message": "Poll ended"}


def search_food(q, limit=20):
    q = q.lower()
    return [f for f in _db["food_items"] if q in f.get("Name", "").lower()][:limit]


def cast_vote(item_id, user_id):
    _db["poll_votes"][user_id] = item_id
    return {"message": "Vote cast"}


def rate_food_item(user_id, item_id, meal_date, meal_type, score):
    for m in _db["menu_schedule"]:
        if m.get("Item_ID") == item_id and m.get("meal_type") == meal_type:
            m["user_rating"] = score
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


def get_low_stock_ingredients(threshold=10):
    return [i for i in _db.get("ingredients", []) if i.get("Total_Quantity", 0) < threshold]


def get_food_ratings():
    ratings_map = {}
    for f in _db.get("food_items", []):
        fid = f.get("Item_ID")
        avg = f.get("Ratings_Average", 3.0)
        vc = f.get("Vote_Count", 0)
        ratings_map[fid] = {"avg_rating": avg, "rating_count": max(vc, 1)}
    result = []
    for f in _db.get("food_items", []):
        fid = f.get("Item_ID")
        r = ratings_map.get(fid, {"avg_rating": 3.0, "rating_count": 0})
        result.append({**f, "avg_rating": r["avg_rating"], "rating_count": r["rating_count"]})
    return result


def get_monthly_billing_summary():
    return copy.deepcopy(_db.get("bills", []))


def create_ingredient(data):
    existing = _db.setdefault("ingredients", [])
    iid = max((i.get("Ingredient_ID", 0) for i in existing), default=0) + 1
    entry = {"Ingredient_ID": iid, **data}
    existing.append(entry)
    return entry


def update_ingredient(iid, data):
    for i in _db.get("ingredients", []):
        if i.get("Ingredient_ID") == iid:
            i.update(data)
    return {}


def delete_ingredient(iid):
    _db["ingredients"] = [i for i in _db.get("ingredients", []) if i.get("Ingredient_ID") != iid]
    return {}


def get_recipes():
    return copy.deepcopy(_db.get("recipes", []))


def get_recipes_detailed():
    food_items = {f["Item_ID"]: f for f in _db.get("food_items", [])}
    ingredients = {i["Ingredient_ID"]: i for i in _db.get("ingredients", [])}
    result = []
    for r in _db.get("recipes", []):
        iid = r.get("Ingredient_ID")
        fi = food_items.get(r["Item_ID"], {})
        ing = ingredients.get(iid, {})
        result.append({
            "Item_ID": r["Item_ID"],
            "Item_Name": fi.get("Name", f"Item #{r['Item_ID']}"),
            "Item_Image": fi.get("Image_Path", ""),
            "Price": fi.get("Price", 0),
            "Ratings_Average": fi.get("Ratings_Average", 0),
            "Ingredient_ID": iid if iid else 0,
            "Ingredient_Name": r.get("Name", ""),
            "Ingredient_Image": ing.get("Image_Path", ""),
            "Unit": r.get("Unit", ""),
            "Ingredient_Quantity": r.get("Ingredient_Quantity", 0),
            "Ingredient_Stock": ing.get("Total_Quantity", 0),
        })
    return copy.deepcopy(result)


def get_todays_menu():
    today = date.today().isoformat()
    menu = [m for m in _db["menu_schedule"] if m.get("Date") == today]
    return {"menu": copy.deepcopy(menu), "date": today}


def get_registration_requests(status="Pending"):
    return [r for r in _db.get("registration_requests", []) if r.get("Status") == status]


def submit_registration_request(data):
    rid = len(_db.get("registration_requests", [])) + 1
    entry = {"RequestID": rid, **data, "Status": "Pending", "Profile_Picture": data.get("Profile_Picture"), "Created_At": date.today().isoformat()}
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
                sid = max((s.get("UserID", 0) for s in _db["students"]), default=10) + 1
                _db["students"].append({
                    "UserID": sid, "First_Name": r["First_Name"], "Last_Name": r["Last_Name"],
                    "Email": r["Email"], "Account_Type": "Student", "Profile_Picture": r.get("Profile_Picture"),
                    "Department": r.get("Department", ""), "Contact_Number": r.get("Contact_Number", ""),
                    "Hostel_Name": r.get("Hostel_Name", ""), "Room_Number": r.get("Room_Number", ""),
                    "DoB": r.get("DoB", ""), "Sex": r.get("Sex", ""),
                })
            elif role == "Staff":
                sid = max((s.get("UserID", 0) for s in _db["staff"]), default=10) + 1
                _db["staff"].append({
                    "UserID": sid, "First_Name": r["First_Name"], "Last_Name": r["Last_Name"],
                    "Email": r["Email"], "Account_Type": "Staff", "Profile_Picture": r.get("Profile_Picture"),
                    "Category": r.get("Category", ""), "Sex": r.get("Sex", ""),
                })
    return {"message": "Approved"}


def reject_registration(rid):
    for r in _db.get("registration_requests", []):
        if r.get("RequestID") == rid:
            r["Status"] = "Rejected"
    return {"message": "Rejected"}
