import httpx
import os
from datetime import date
from typing import Optional, Dict, Any

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")


async def _make_request(
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Internal helper to make HTTP requests to the backend.
    Returns a dict with either data or an error key.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method.upper() == "GET":
                response = await client.get(url, params=params, timeout=10.0)
            elif method.upper() == "POST":
                response = await client.post(url, params=params, json=json_data, timeout=10.0)
            else:
                return {"error": f"Unsupported method: {method}"}

            response.raise_for_status()
            # If response is empty (e.g., 204), return empty dict
            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Backend Connection Error: {str(e)}"}
        except httpx.HTTPStatusError as e:
            # Try to parse error detail from response
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except:
                error_detail = e.response.text
            return {"error": f"Backend Error ({e.response.status_code}): {error_detail}"}


# ------------------------------------------------------------------
# Authentication & User
# ------------------------------------------------------------------
async def verify_user(email: str) -> Dict[str, Any]:
    """
    Verifies if a user is registered in the system.
    Returns: {"status": "authorized", "user_details": {...}} or error.
    """
    return await _make_request("GET", "/users/verify", params={"email": email})


async def get_my_profile(email: str) -> Dict[str, Any]:
    """
    Fetches the authenticated user's profile details.
    """
    return await _make_request("GET", "/users/me", params={"email": email})


# ------------------------------------------------------------------
# Menu
# ------------------------------------------------------------------
async def get_todays_menu(email: str, target_date: date = date.today()) -> Dict[str, Any]:
    """
    Fetches the menu for a specific date.
    Returns: {"date": "...", "item_count": ..., "menu": [...]}
    """
    return await _make_request(
        "GET", "/menu/today", params={"email": email, "target_date": target_date.isoformat()}
    )


async def get_weekly_menu() -> Dict[str, Any]:
    """
    Fetches the full weekly menu.
    """
    return await _make_request("GET", "/menu/weekly")


# ------------------------------------------------------------------
# Bills (Profile)
# ------------------------------------------------------------------
async def get_my_bills(email: str) -> Dict[str, Any]:
    """
    Fetches bill history for the logged-in student.
    """
    return await _make_request("GET", "/users/my_bills", params={"email": email})


async def download_bill_pdf(billing_id: int, email: str) -> Optional[bytes]:
    """
    Downloads a bill PDF as bytes.
    Returns bytes (PDF content) or None if error.
    """
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}/student/bills/download/{billing_id}"
            response = await client.get(url, params={"email": email}, timeout=15.0)
            response.raise_for_status()
            return response.content  # Returns binary PDF data
        except Exception as e:
            print(f"PDF Download Error: {e}")
            return None


# ------------------------------------------------------------------
# Voting
# ------------------------------------------------------------------
async def get_active_poll(email: str) -> Dict[str, Any]:
    """
    Fetches the currently active poll items.
    """
    return await _make_request("GET", "/poll/active", params={"email": email})



async def cast_vote(item_id: int, user_id: int, email: str) -> Dict[str, Any]:
    """
    Casts a vote for a specific food item.
    """
    return await _make_request(
        "POST", f"/poll/vote/{item_id}/{user_id}", params={"email": email}
    )


# ------------------------------------------------------------------
# Mess Off
# ------------------------------------------------------------------
async def request_mess_off(user_id: int, start_date: date, end_date: date, email: str) -> Dict[str, Any]:
    """
    Submits a new mess-off request.
    """
    endpoint = f"/student/mess_off/request/{user_id}/{start_date.isoformat()}/{end_date.isoformat()}"
    return await _make_request("POST", endpoint , params={"email": email})


async def cancel_mess_off(mess_off_id: int, email: str) -> Dict[str, Any]:
    """
    Cancels a pending mess-off request.
    """
    return await _make_request("POST", f"/student/mess_off/cancel/{mess_off_id}", params={"email": email})


async def get_mess_off_status(mess_off_id: int, email: str) -> Dict[str, Any]:
    """
    Fetches the status of a specific mess-off request.
    """
    return await _make_request("GET", f"/student/mess-off/{mess_off_id}", params={"email": email})


async def get_mess_off_history(email: str) -> Dict[str, Any]:
    """
    Fetches the mess-off history for the logged-in student.
    Returns: {"status": [...]} or error.
    """
    return await _make_request("GET", "/student/mess-off/history", params={"email": email})
