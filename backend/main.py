import logging
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, UploadFile, File, Body
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import threading
from io import BytesIO, StringIO
import csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backend")
from email_utils import (
    registration_requested_email, registration_approved_email,
    account_deleted_email, bill_issued_email, feedback_email, send_email_sync,
)


def _fire_email(to_email, subject, html_body):
    """Fire-and-forget email sending in background thread."""
    import threading
    threading.Thread(target=send_email_sync, args=(to_email, subject, html_body), daemon=True).start()
from reportlab.lib.pagesizes import A4, landscape
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from database import get_db, run_db_seeder
from datetime import date
import models
import mysql.connector
from contextlib import asynccontextmanager
from dao import (
    BaseDAO, UserDAO, MenuDAO, BillDAO, FoodDAO,
    MessOffDAO, PollDAO, RegistrationDAO,
)
from auth import verify_api_key, get_user_email

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

UPLOAD_TOKENS: dict[str, str] = {}

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

def run_startup_tasks():
    """Idempotent startup routine: seed DB + pre-generate menu schedule."""
    try:
        run_db_seeder()
    except Exception as e:
        print(f"Startup seed error: {e}")
    try:
        from database import db_pool
        conn = db_pool.get_connection()
        try:
            MenuDAO(conn).maintain_menu_schedule()
        finally:
            conn.close()
    except Exception as e:
        print(f"Startup menu-schedule error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_tasks()
    yield

app = FastAPI(title="NUST's Kitchen API", lifespan=lifespan)

raw_origins = os.getenv("CORS_ORIGINS", "https://nusts-kitchen-production.up.railway.app")
origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
if not origins:
    origins = ["*"]
    print("WARNING: CORS_ORIGINS not set, allowing all origins")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def permission_checker(allowed_roles: list):
    def mapper(api_key=Depends(verify_api_key), request: Request = None, db=Depends(get_db)):
        email = request.headers.get("X-User-Email", "").strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Missing X-User-Email header")
        user_record = UserDAO(db).find_by_email(email)
        if not user_record:
            raise HTTPException(status_code=404, detail="User record not found")
        if user_record.get("Account_Type") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return user_record
    return mapper


@app.get("/")
def read_root():
    return {"status": "MEOWMEOW Backend is Online"}


@app.post("/auth/login")
@limiter.limit("20/minute")
def auth_login(request: Request, data: dict, db=Depends(get_db)):
    email = data.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")
    user_record = UserDAO(db).find_by_email(email)
    if not user_record:
        raise HTTPException(status_code=403, detail="Access Denied: email not registered.")
    return {"user_details": user_record}


@app.get("/users/verify")
@limiter.limit("20/minute")
def verify_registration(request: Request, email: str, db=Depends(get_db)):
    user_record = UserDAO(db).find_by_email(email.strip().lower())
    if not user_record:
        raise HTTPException(status_code=403, detail="Access Denied: email not registered.")
    return {"status": "authorized", "user_details": user_record}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), token: str = Query(default=None)):
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "png"
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    url = f"/uploads/{name}"
    if token:
        UPLOAD_TOKENS[token] = url
    return {"filename": name, "url": url}


@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/upload-ui")
async def upload_ui(token: str = Query(default="")):
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Upload File</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,sans-serif; background:#f5f5f5; display:flex; justify-content:center; align-items:center; min-height:100vh; }}
.card {{ background:white; border-radius:16px; padding:32px; width:400px; max-width:90vw; box-shadow:0 8px 32px #0000001a; }}
h2 {{ font-size:20px; margin-bottom:20px; color:#1a1a1a; }}
label {{ display:block; font-size:14px; color:#666; margin-bottom:6px; }}
input[type=file] {{ display:block; width:100%; margin-bottom:16px; padding:8px; border:2px dashed #ccc; border-radius:8px; }}
button {{ background:#6366f1; color:white; border:none; border-radius:8px; padding:10px 20px; font-size:14px; cursor:pointer; }}
button:hover {{ background:#4f46e5; }}
button:disabled {{ opacity:.6; cursor:default; }}
#msg {{ margin-top:12px; font-size:14px; }}
#url {{ word-break:break-all; color:#6366f1; }}
</style></head>
<body>
<div class="card">
<h2>Upload Image</h2>
<form id="form" enctype="multipart/form-data">
<label for="file">Choose an image</label>
<input type="file" id="file" name="file" accept="image/*" required>
<button type="submit" id="btn">Upload</button>
</form>
<div id="msg"></div>
</div>
<script>
document.getElementById('form').onsubmit = async function(e) {{
    e.preventDefault();
    const btn = document.getElementById('btn');
    btn.disabled = true; btn.textContent = 'Uploading...';
    const fd = new FormData();
    fd.append('file', document.getElementById('file').files[0]);
    const token = '{token}';
    if (token) fd.append('token', token);
    try {{
        const r = await fetch('/upload' + (token ? '?token='+token : ''), {{ method:'POST', body:fd }});
        const d = await r.json();
        if (r.ok) {{
            document.getElementById('msg').innerHTML = '<strong>Upload successful!</strong><br><br>URL:<br><code id="url">'+window.location.origin+d.url+'</code><br><br><button onclick="navigator.clipboard.writeText(window.location.origin+d.url)">Copy URL</button><br><br><small>You can close this tab now.</small>';
        }} else {{
            document.getElementById('msg').innerHTML = '<span style="color:red">Upload failed: '+d.detail+'</span>';
        }}
    }} catch(err) {{
        document.getElementById('msg').innerHTML = '<span style="color:red">Error: '+err.message+'</span>';
    }}
    btn.disabled = false; btn.textContent = 'Upload';
}};
</script>
</body>
</html>""", media_type="text/html")


@app.get("/upload-status/{token}")
async def upload_status(token: str):
    url = UPLOAD_TOKENS.get(token)
    if url:
        return {"status": "done", "url": url}
    return {"status": "pending", "url": None}


@app.patch("/users/{UserID}/picture")
def update_profile_picture(UserID: int, data: models.ProfilePictureUpdate, user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    if user.get("Account_Type") != "Admin" and user.get("UserID") != UserID:
        raise HTTPException(status_code=403, detail="Cannot update another user's picture")
    return BaseDAO(db).update_record("Users", data, "UserID", UserID)


@app.post("/drive-download")
async def download_from_drive(data: dict):
    drive_url = data.get("drive_url", "")
    token = data.get("token")
    import re
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/uc\?.*id=([a-zA-Z0-9_-]+)",
        r"^(1[0-9A-Za-z_-]{10,})$",
    ]
    fid = None
    for p in patterns:
        m = re.search(p, drive_url.strip())
        if m:
            fid = m.group(1)
            break
    if not fid:
        raise HTTPException(status_code=400, detail="Could not extract file ID from URL")
    url = f"https://lh3.googleusercontent.com/d/{fid}"
    if token:
        UPLOAD_TOKENS[token] = url
    return {"url": url}


@app.patch("/admin/food-items/{ItemID}/image")
def update_food_image(ItemID: int, data: models.ImagePathUpdate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Food_Items", data, "Item_ID", ItemID)


@app.patch("/admin/ingredients/{IngredientID}/image")
def update_ingredient_image(IngredientID: int, data: models.ImagePathUpdate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Ingredients", data, "IngredientID", IngredientID)


@app.get("/users/me")
def get_my_profile(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return UserDAO(db).get_my_profile(user.get("Email"))


@app.get("/menu/today")
def get_todays_menu(target_date: date = Query(default=date.today()), user_id: int = None, db=Depends(get_db)):
    menu_items = MenuDAO(db).get_todays_menu(target_date, user_id)
    return {"date": target_date.isoformat(), "item_count": len(menu_items), "menu": menu_items}


@app.get("/menu/weekly")
def get_weekly_menu(user_id: int = None, db=Depends(get_db)):
    return MenuDAO(db).get_weekly_menu(user_id=user_id)


@app.get("/admin/students/all")
def get_all_students(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return UserDAO(db).get_all_students_only()


@app.get("/admin/staff/all")
def get_all_staff(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return UserDAO(db).get_all_users()


@app.get("/admin/staff/details/{UserID}")
def get_staff_details(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return UserDAO(db).get_staff_details(UserID)


@app.get("/admin/students/details/{UserID}")
def get_student_details(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return UserDAO(db).get_student_details(UserID)


@app.get("/admin/food/costs")
def get_food_costs(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_all_food_costs()


@app.get("/admin/food/search")
def search_food_items(q: str = Query(min_length=1), limit: int = Query(default=20, le=100),
                      user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    try:
        return FoodDAO(db).search_food_items(q, limit)
    except Exception as e:
        logger.error("search_food_items q=%s: %s", q, e, exc_info=True)
        raise


@app.get("/admin/food/{ItemID}")
def get_food_by_id(ItemID: int, db=Depends(get_db), user=Depends(permission_checker(["Admin", "Staff"]))):
    return FoodDAO(db).get_food_by_id(ItemID)


@app.get("/admin/bills/all")
def get_all_individual_bills(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).get_all_bills()


@app.get("/admin/monthly-billing-summary")
def get_monthly_billing_summary(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).get_all_monthly_bills()


@app.get("/admin/{UserID}/bill-status")
def get_student_bill_status(UserID: int, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    return BillDAO(db).get_student_bill_details(UserID)


@app.get("/bills/my-history")
def get_my_bill_history(user=Depends(permission_checker(["Admin", "Student"])), db=Depends(get_db)):
    return BillDAO(db).get_my_bills(user.get("Email"))


@app.get("/analytics/ingredients")
def get_ingredients(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_ingredients()


@app.get("/recipes")
def get_recipes(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_recipes()


@app.get("/recipes/detailed")
def get_recipes_detailed(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_recipes_detailed()


@app.get("/recipes/steps/{item_id}")
def get_recipe_steps(item_id: int, user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_recipe_steps(item_id)


@app.get("/users/my-bills")
def get_my_bills(user=Depends(permission_checker(["Admin", "Student"])), db=Depends(get_db)):
    return BillDAO(db).get_my_bills(user.get("Email"))


@app.get("/students/bills/unseen-count")
def get_unseen_bills_count(user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    return {"count": BillDAO(db).get_unseen_count(user.get("Email"))}


# ── Registration Requests ──────────────────────────────────────

@app.post("/register/request")
def submit_registration_request(data: models.RegistrationRequestCreate, db=Depends(get_db)):
    result = RegistrationDAO(db).create_request(data)
    subject, body = registration_requested_email(data.First_Name, data.Email)
    _fire_email(data.Email, subject, body)
    return result


@app.post("/feedback/send")
def send_user_feedback(data: dict = Body(...), user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    subject = (data.get("subject") or "").strip()
    msg = (data.get("message") or "").strip()
    if not subject:
        raise HTTPException(400, "Subject is required")
    if not msg:
        raise HTTPException(400, "Message is required")
    name = data.get("name", user.get("Email", "User"))
    email = data.get("email", user.get("Email", ""))
    dao = BaseDAO(db)
    cursor = dao._execute("INSERT INTO Feedback (Name, Email, Subject, Message) VALUES (%s, %s, %s, %s)", (name, email, subject, msg))
    return {"message": "Feedback sent — thank you!", "id": cursor.lastrowid}


@app.get("/admin/feedback")
def get_feedback(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = BaseDAO(db)
    return dao._fetchall("SELECT Feedback_ID, Name, Email, Subject, Message, DATE_FORMAT(Created_At, '%Y-%m-%d %H:%i') AS Created_At FROM Feedback ORDER BY Created_At DESC")


@app.get("/admin/registration-requests")
def get_registration_requests(status: str = "Pending", user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return RegistrationDAO(db).get_requests(status)


@app.post("/admin/registration-requests/{RequestID}/approve")
def approve_registration(RequestID: int, data: models.RegistrationRequestUpdate = None, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    req = RegistrationDAO(db).get_request_by_id(RequestID)
    result = RegistrationDAO(db).approve_request(RequestID, data)
    if req:
        subject, body = registration_approved_email(req.get("First_Name", ""), req.get("Email", ""))
        _fire_email(req.get("Email", ""), subject, body)
    return result


@app.post("/admin/registration-requests/{RequestID}/reject")
def reject_registration(RequestID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return RegistrationDAO(db).reject_request(RequestID)


# ── Students ───────────────────────────────────────────────────

@app.post("/admin/students/register")
def register_student(data: models.StudentCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = UserDAO(db)
    user_cur = dao.register_user(data.First_Name, data.Last_Name, data.Email, "Student", data.Sex)
    new_user_id = user_cur.lastrowid
    dao.register_student(new_user_id, data.DoB, data.Department, data.Contact_Number,
                         data.Address, data.Father_Name, data.Hostel_Name, data.Room_Number)
    return {"message": "User and Student registered successfully", "UserID": new_user_id}


@app.patch("/admin/students/update/{UserID}")
def update_student_profile(data: models.StudentUpdate, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Student", data, "UserID", UserID)


@app.delete("/admin/students/delete/{UserID}")
def delete_student(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = UserDAO(db)
    u = dao._fetchone("SELECT First_Name, Email FROM Users WHERE UserID = %s", (UserID,))
    result = dao.cascade_delete_user(UserID)
    if u:
        subject, body = account_deleted_email(u.get("First_Name", ""), u.get("Email", ""))
        _fire_email(u.get("Email", ""), subject, body)
    return result


# ── Staff ──────────────────────────────────────────────────────

@app.post("/admin/staff/register")
def register_staff(data: models.Staff, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = UserDAO(db)
    user_cur = dao.register_user(data.First_Name, data.Last_Name, data.Email, "Staff", data.Sex)
    new_user_id = user_cur.lastrowid
    dao.register_staff(new_user_id, data.Category)
    return {"message": "User and Staff registered successfully", "UserID": new_user_id}


@app.patch("/admin/staff/update/{UserID}")
def update_staff_profile(data: models.Staff, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Staff", data, "UserID", UserID)


@app.delete("/admin/staff/delete/{UserID}")
def delete_staff(UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = UserDAO(db)
    u = dao._fetchone("SELECT First_Name, Email FROM Users WHERE UserID = %s", (UserID,))
    result = dao.cascade_delete_user(UserID)
    if u:
        subject, body = account_deleted_email(u.get("First_Name", ""), u.get("Email", ""))
        _fire_email(u.get("Email", ""), subject, body)
    return result


@app.post("/admin/staff/contact/{UserID}")
def add_staff_contact(data: models.StaffContactNumbers, UserID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = UserDAO(db).add_staff_contact(UserID, data.ContactNumber)
    return {"message": "Contact added", "id": cursor.lastrowid}


@app.post("/admin/staff/category")
def add_staff_category(data: models.StaffCategory, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    cursor = UserDAO(db).add_staff_category(data.Category, data.WorkingHours, data.Salary)
    return {"message": "Category created", "id": cursor.lastrowid}


@app.get("/admin/staff/category")
def list_staff_categories(db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    categories = UserDAO(db).get_all_staff_categories()
    return categories


@app.delete("/admin/staff/category/{category}")
def delete_staff_category(category: str, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    UserDAO(db).delete_staff_category(category)
    return {"message": "Category deleted"}


# ── Bills ──────────────────────────────────────────────────────

@app.post("/admin/bills/create")
def create_bill(data: models.BillCreate, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    dao = BillDAO(db)
    cursor = dao.create_bill(data.UserID, data.Issue_Date, data.Amount, data.Due_Date, data.Month, data.Status.value)
    u = UserDAO(db)._fetchone("SELECT First_Name, Email FROM Users WHERE UserID = %s", (data.UserID,))
    if u:
        subject, body = bill_issued_email(u.get("First_Name", ""), u.get("Email", ""),
                                          data.Amount, str(data.Month), str(data.Due_Date))
        _fire_email(u.get("Email", ""), subject, body)
    return {"message": "Bill created", "id": cursor.lastrowid}


@app.patch("/admin/bills/update/{BillID}")
def update_bill(data: models.BillUpdate, BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).update_record("Bills", data, "Billing_ID", BillID)


@app.delete("/admin/bills/delete/{BillID}")
def delete_bill(BillID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).delete_record("Bills", "Billing_ID", BillID)


def draw_challan_pdf(bill):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    col_width = width / 3

    def draw_section(x_offset, label):
        c.setDash(1, 2)
        c.line(x_offset + col_width - 5, 20, x_offset + col_width - 5, height - 20)
        c.setDash([])
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x_offset + (col_width / 2), height - 50, "NUST SEECS MESS")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x_offset + (col_width / 2), height - 65, label)
        c.setFont("Helvetica", 11)
        y = height - 120
        c.drawString(x_offset + 30, y, f"Bill ID:    {bill['Billing_ID']}")
        c.drawString(x_offset + 30, y - 20, f"Name:       {bill['First_Name']} {bill['Last_Name']}")
        c.drawString(x_offset + 30, y - 40, f"Month:      {bill['Month']}")
        c.drawString(x_offset + 30, y - 60, f"Due Date:   {bill['Due_Date']}")
        c.rect(x_offset + 25, y - 110, col_width - 60, 40)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_offset + 35, y - 100, f"Total Amount: Rs. {bill['Amount']}")
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(x_offset + 30, 60, "Bank Stamp / Signature")

    draw_section(0, "BANK COPY")
    draw_section(col_width, "OFFICE COPY")
    draw_section(col_width * 2, "STUDENT COPY")
    c.save()
    buffer.seek(0)
    return buffer


@app.get("/student/bills/download/{BillingID}")
def generate_pdf(BillingID: int, db=Depends(get_db), user=Depends(permission_checker(["Student"]))):
    bill_record = BillDAO(db).get_bill_pdf(BillingID, user.get("Email"))
    if not bill_record:
        raise HTTPException(status_code=404, detail="Bill not found")
    pdf_buffer = draw_challan_pdf(bill_record)
    filename = f"MessBill_{bill_record['Month']}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ── Food Items ─────────────────────────────────────────────────

@app.get("/admin/food-items/all")
def get_all_food_items(user=Depends(permission_checker(["Admin", "Staff", "Student"])), db=Depends(get_db)):
    return FoodDAO(db).get_all_food_items()


@app.post("/admin/food-items/create")
def create_food(data: models.Food, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = FoodDAO(db).create_food(data.Name, data.Quantity, data.Price)
    return {"message": "Food item created", "id": cursor.lastrowid}


@app.patch("/admin/food-items/update/{ItemID}")
def update_food(data: models.Food, ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Food_Items", data, "Item_ID", ItemID)


@app.delete("/admin/food-items/delete/{ItemID}")
def delete_food(ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).delete_record("Food_Items", "Item_ID", ItemID)


# ── Ingredients ────────────────────────────────────────────────

@app.post("/admin/ingredients/create")
def create_ingredient(data: models.Ingredient, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = FoodDAO(db).create_ingredient(data.Name, data.Total_Quantity, data.Unit, data.Unit_cost)
    return {"message": "Ingredient created", "id": cursor.lastrowid}


@app.patch("/admin/ingredients/update/{IngredientID}")
def update_ingredient(data: models.Ingredient, IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).update_record("Ingredients", data, "IngredientID", IngredientID)


@app.delete("/admin/ingredients/delete/{IngredientID}")
def delete_ingredient(IngredientID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BaseDAO(db).delete_record("Ingredients", "IngredientID", IngredientID)


# ── Recipes ────────────────────────────────────────────────────

@app.post("/admin/add-recipe/{ItemID}/{IngredientID}/{IngredientQuantity}")
def add_recipe(IngredientQuantity: float, ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    cursor = FoodDAO(db).add_recipe(ItemID, IngredientID, IngredientQuantity)
    return {"message": "Recipe added", "id": cursor.lastrowid}


@app.patch("/admin/recipe/update/{ItemID}/{IngredientID}")
def update_recipe(data: models.FoodItemIngredient, ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    return FoodDAO(db).update_recipe_ingredient(ItemID, IngredientID, data)


@app.delete("/admin/recipe/{ItemID}/{IngredientID}")
def delete_recipe(ItemID: int, IngredientID: int, user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    return FoodDAO(db).delete_recipe(ItemID, IngredientID)


# ── Voting ─────────────────────────────────────────────────────

@app.post("/admin/poll/start")
def start_poll(poll: models.PollRequest, db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    return PollDAO(db).start_poll(poll.item_ids, poll.meal_type)


@app.get("/poll/active")
def get_active_poll(db=Depends(get_db), user=Depends(permission_checker(["Admin", "Student"]))):
    return PollDAO(db).get_active_poll()


@app.post("/poll/vote/{ItemID}/{UserID}")
def cast_vote(UserID: int, ItemID: int, db=Depends(get_db), user=Depends(permission_checker(["Student"]))):
    dao = PollDAO(db)
    active_poll = dao.get_active_poll()
    if not active_poll.get("active"):
        raise HTTPException(status_code=404, detail="No active poll")
    active_ids = [str(item["Item_ID"]) for item in active_poll.get("items", [])]
    if str(ItemID) not in active_ids:
        raise HTTPException(status_code=400, detail="This item is not part of the active poll")
    return dao.cast_vote(UserID, ItemID)


@app.get("/admin/poll/results")
def get_poll_results(db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    return PollDAO(db).get_poll_results()


@app.post("/admin/poll/end")
def end_poll(db=Depends(get_db), user=Depends(permission_checker(["Admin"]))):
    return PollDAO(db).end_poll()


# ── Menu ───────────────────────────────────────────────────────

@app.post("/admin/menu-schedule/{ItemID}/{menu_date}/{meal_type}")
def add_menu(meal_type: str, menu_date: date, ItemID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    menu_dao = MenuDAO(db)
    schedule = menu_dao.get_current_schedule_id(menu_date, meal_type)
    if not schedule:
        raise HTTPException(status_code=400, detail="No schedule found")
    menu_dao.add_menu_item(schedule['Schedule_ID'], ItemID)
    return {"message": "Item added to menu"}


@app.patch("/admin/menu-schedule/{ItemID}/{ScheduleID}")
def update_menu(data: models.MenuFoodItem, ItemID: int, ScheduleID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return {"message": "No changes detected"}
    return BaseDAO(db).update_record("Menu_Food_Items", data, "ScheduleID", ScheduleID)


@app.delete("/admin/menu-schedule/{ItemID}/{ScheduleID}")
def delete_menu(ItemID: int, ScheduleID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return MenuDAO(db).delete_menu_item(ItemID, ScheduleID)


# ── Ratings ────────────────────────────────────────────────────

@app.post("/student/rating/{UserID}/{ItemID}/{Date}/{meal_type}/{score}")
def rate_food(score: int, Date: date, meal_type: str, UserID: int, ItemID: int, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    menu_dao = MenuDAO(db)
    food_dao = FoodDAO(db)
    schedule = menu_dao.get_current_schedule_id(Date, meal_type)
    if not schedule:
        raise HTTPException(status_code=400, detail="No schedule found")
    food_dao.rate_food_item(UserID, ItemID, schedule['Schedule_ID'], score)
    return {"message": "Food Rated successfully"}


@app.get("/food-rating/{ItemID}/{Date}/{meal_type}")
def get_food_rating(Date: date, meal_type: str, ItemID: int, db=Depends(get_db)):
    menu_dao = MenuDAO(db)
    food_dao = FoodDAO(db)
    schedule = menu_dao.get_current_schedule_id(Date, meal_type)
    if not schedule:
        raise HTTPException(status_code=400, detail="No schedule found")
    rating = food_dao.get_food_rating(schedule['Schedule_ID'], ItemID)
    if not rating:
        rating = "NULL"
    return {"rating": rating}


# ── Payment ────────────────────────────────────────────────────

@app.post("/admin/bills/pay/{BillingID}")
def record_payment(BillingID: int, amount: float, method: str, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.callproc('sp_RecordPayment', [BillingID, amount, method])
        db.commit()
        return {"message": "Payment recorded and bill status updated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@app.post("/admin/bills/undo-pay/{BillingID}")
def undo_payment(BillingID: int, user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Transactions WHERE Transaction_ID = ("
            "SELECT Transaction_ID FROM ("
            "SELECT Transaction_ID FROM Transactions "
            "WHERE Billing_ID = %s AND Transaction_Status = 'Success' "
            "ORDER BY Transaction_ID DESC LIMIT 1"
            ") AS t)",
            (BillingID,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No successful payment found to undo")
        cursor.execute("SELECT COALESCE(SUM(Amount_Paid), 0) AS total FROM Transactions WHERE Billing_ID = %s AND Transaction_Status = 'Success'", (BillingID,))
        total_paid = cursor.fetchone()[0]
        cursor.execute("SELECT Amount FROM Bills WHERE Billing_ID = %s", (BillingID,))
        bill_amount = cursor.fetchone()[0]
        if total_paid < bill_amount:
            cursor.execute("UPDATE Bills SET Status = 'Unpaid' WHERE Billing_ID = %s", (BillingID,))
        db.commit()
        return {"message": "Last payment undone", "total_paid": total_paid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# ── Mess Off ───────────────────────────────────────────────────

@app.post("/student/mess-off/request/{UserID}/{StartDate}/{EndDate}")
def request_mess_off(UserID: int, StartDate: date, EndDate: date, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    MessOffDAO(db).request_mess_off(UserID, StartDate, EndDate)
    return {"message": "Mess off requested successfully"}


@app.post("/student/mess-off/cancel/{MessOffID}")
def cancel_mess_off_request(MessOffID: int, user=Depends(permission_checker(["Student"])), db=Depends(get_db)):
    MessOffDAO(db).cancel_mess_off(MessOffID)
    return {"message": "Mess off request cancelled successfully"}


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
def get_mess_off_history(user=Depends(permission_checker(["Admin", "Student"])), db=Depends(get_db)):
    user_id = user.get("UserID")
    return {"status": MessOffDAO(db).get_my_mess_off_this_month(user_id)}


@app.get("/student/mess-off/{MessOffID}")
def get_mess_off(MessOffID: int, user=Depends(permission_checker(["Student", "Admin"])), db=Depends(get_db)):
    return MessOffDAO(db).get_mess_off_status(MessOffID)


# ══════════════════════════════════════════════════════════════════
#  QUALITY-OF-LIFE ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@app.get("/admin/dashboard/stats")
def get_dashboard_stats(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).get_dashboard_stats()


@app.get("/admin/users/search")
def search_users(q: str = Query(min_length=1), limit: int = Query(default=20, le=100),
                 user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return UserDAO(db).search_users(q, limit)


@app.get("/analytics/ingredients/low-stock")
def get_low_stock_ingredients(threshold: float = Query(default=10, ge=0),
                              user=Depends(permission_checker(["Admin", "Staff"])), db=Depends(get_db)):
    return FoodDAO(db).get_low_stock_ingredients(threshold)


@app.get("/admin/bills/export-csv")
def export_bills_csv(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    csv_data = BillDAO(db).export_bills_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bills_export.csv"}
    )


@app.get("/admin/students/export-csv")
def export_students_csv(user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    csv_data = UserDAO(db).export_students_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"}
    )


@app.get("/admin/activity/feed")
def get_activity_feed(limit: int = Query(default=10, le=50),
                      user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).get_recent_activity(limit)


@app.post("/admin/bills/generate-monthly")
def trigger_monthly_bills(amount: float = Query(default=5000),
                          user=Depends(permission_checker(["Admin"])), db=Depends(get_db)):
    return BillDAO(db).generate_monthly_bills(amount)


@app.get("/student/dashboard/stats")
def get_student_dashboard_stats(db=Depends(get_db),
                                user=Depends(permission_checker(["Student"]))):
    user_record = UserDAO(db).find_by_email(user.get("Email"))
    return UserDAO(db).get_student_dashboard_stats(user_record["UserID"])


@app.get("/menu/ratings-summary")
def get_ratings_summary(user=Depends(permission_checker(["Admin", "Staff", "Student"])),
                        db=Depends(get_db)):
    return MenuDAO(db).get_ratings_summary()
