import re
from datetime import date, datetime

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")
DATE_RE  = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NAME_RE  = re.compile(r"^[a-zA-ZÀ-ÿ'\- ]+$")


def sanitize(value):
    if value is None:
        return ""
    return str(value).strip()


def validate_required(value, field_name):
    cleaned = sanitize(value)
    if not cleaned:
        return None, f"{field_name} is required"
    return cleaned, None


def validate_name(value, field_name):
    cleaned = sanitize(value)
    if not cleaned:
        return None, f"{field_name} is required"
    if not NAME_RE.match(cleaned):
        return None, f"{field_name} can only contain letters, hyphens, and apostrophes"
    if len(cleaned) > 100:
        return None, f"{field_name} is too long (max 100 chars)"
    return cleaned, None


def validate_email(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, "Email is required"
    if not EMAIL_RE.match(cleaned):
        return None, "Enter a valid email (e.g. name@domain.com)"
    if len(cleaned) > 254:
        return None, "Email is too long"
    return cleaned.lower(), None


def validate_phone(value):
    if not value or not sanitize(value):
        return None, None  # phone is optional
    cleaned = sanitize(value)
    digits_only = re.sub(r"[\s\-()+]", "", cleaned)
    if not digits_only.isdigit():
        return None, "Phone number can only contain digits, spaces, hyphens, and parentheses"
    if len(digits_only) < 9 or len(digits_only) > 13:
        return None, "Phone number must be 9-13 digits"
    return cleaned, None


def validate_date_str(value, field_name="Date"):
    cleaned = sanitize(value)
    if not cleaned:
        return None, f"{field_name} is required"
    if not DATE_RE.match(cleaned):
        return None, f"{field_name} must be in YYYY-MM-DD format"
    try:
        dt = datetime.strptime(cleaned, "%Y-%m-%d").date()
        if dt > date.today():
            return None, f"{field_name} cannot be in the future"
        if dt.year < 1900:
            return None, f"{field_name} year seems invalid"
        return dt, None
    except ValueError:
        return None, f"{field_name} is not a valid calendar date"


def validate_positive_number(value, field_name):
    if not value or not sanitize(value):
        return None, f"{field_name} is required"
    cleaned = sanitize(value)
    try:
        num = float(cleaned)
        if num < 0:
            return None, f"{field_name} cannot be negative"
        if num > 1_000_000_000:
            return None, f"{field_name} is unreasonably large"
        return num, None
    except ValueError:
        return None, f"{field_name} must be a valid number"


def validate_non_negative_int(value, field_name):
    cleaned = sanitize(value)
    if not cleaned:
        return None, f"{field_name} is required"
    try:
        num = int(cleaned)
        if num < 0:
            return None, f"{field_name} cannot be negative"
        if num > 1_000_000:
            return None, f"{field_name} is unreasonably large"
        return num, None
    except ValueError:
        return None, f"{field_name} must be a whole number"


def validate_hostel(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, None
    if len(cleaned) > 100:
        return None, "Hostel name is too long (max 100 chars)"
    return cleaned, None


def validate_room(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, None
    if len(cleaned) > 20:
        return None, "Room number is too long (max 20 chars)"
    return cleaned, None


def validate_address(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, None
    if len(cleaned) > 500:
        return None, "Address is too long (max 500 chars)"
    return cleaned, None


def validate_department(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, None
    if len(cleaned) > 100:
        return None, "Department is too long (max 100 chars)"
    return cleaned, None


def validate_category(value):
    cleaned = sanitize(value)
    if not cleaned:
        return None, None
    if len(cleaned) > 100:
        return None, "Category is too long (max 100 chars)"
    return cleaned, None
