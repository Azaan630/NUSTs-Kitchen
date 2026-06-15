import httpx
import os
from datetime import date
from typing import Optional, Dict, Any

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_KEY = os.getenv("BACKEND_API_KEY", "")

_email: str | None = None


def set_user_email(email: str | None):
    global _email
    _email = email


def get_headers() -> dict:
    headers = {"X-Api-Key": API_KEY}
    if _email:
        headers["X-User-Email"] = _email
    return headers


async def _make_request(
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}{endpoint}"
            headers = get_headers()
            if method.upper() == "GET":
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
            elif method.upper() == "POST":
                response = await client.post(url, params=params, json=json_data, headers=headers, timeout=10.0)
            else:
                return {"error": f"Unsupported method: {method}"}

            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Backend Connection Error: {str(e)}"}
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("detail", e.response.text)
            except Exception:
                error_detail = e.response.text
            return {"error": f"Backend Error ({e.response.status_code}): {error_detail}"}


# ── Auth & User ────────────────────────────────────────────────────
async def verify_user(email: str) -> Dict[str, Any]:
    return await _make_request("GET", "/users/verify", params={"email": email})


async def login(email: str) -> Dict[str, Any]:
    return await _make_request("POST", "/auth/login", json_data={"email": email})


async def get_my_profile() -> Dict[str, Any]:
    return await _make_request("GET", "/users/me")


# ── Menu ───────────────────────────────────────────────────────────
async def get_todays_menu(target_date: date = None, user_id: int = None) -> Dict[str, Any]:
    if target_date is None:
        target_date = date.today()
    params = {"target_date": target_date.isoformat()}
    if user_id is not None:
        params["user_id"] = user_id
    return await _make_request("GET", "/menu/today", params=params)


async def get_weekly_menu(user_id: int = None) -> Any:
    params = {}
    if user_id is not None:
        params["user_id"] = user_id
    return await _make_request("GET", "/menu/weekly", params=params)


# ── Ratings ────────────────────────────────────────────────────────
async def rate_food_item(
    user_id: int,
    item_id: int,
    meal_date: date,
    meal_type: str,
    score: int,
) -> Dict[str, Any]:
    endpoint = (
        f"/student/rating/{user_id}/{item_id}/{meal_date.isoformat()}/{meal_type}/{score}"
    )
    return await _make_request("POST", endpoint)


# ── Bills ──────────────────────────────────────────────────────────
async def get_my_bills() -> Any:
    return await _make_request("GET", "/users/my-bills")


async def download_bill_pdf(billing_id: int) -> Optional[bytes]:
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BASE_URL}/student/bills/download/{billing_id}"
            response = await client.get(url, headers=get_headers(), timeout=15.0)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"PDF Download Error: {e}")
            return None


# ── Voting ─────────────────────────────────────────────────────────
async def get_active_poll() -> Dict[str, Any]:
    return await _make_request("GET", "/poll/active")


async def cast_vote(item_id: int, user_id: int) -> Dict[str, Any]:
    return await _make_request("POST", f"/poll/vote/{item_id}/{user_id}")


# ── Mess Off ───────────────────────────────────────────────────────
async def request_mess_off(user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    endpoint = f"/student/mess-off/request/{user_id}/{start_date.isoformat()}/{end_date.isoformat()}"
    return await _make_request("POST", endpoint)


async def cancel_mess_off(mess_off_id: int) -> Dict[str, Any]:
    return await _make_request("POST", f"/student/mess-off/cancel/{mess_off_id}")


async def get_mess_off_status(mess_off_id: int) -> Dict[str, Any]:
    return await _make_request("GET", f"/student/mess-off/{mess_off_id}")


async def get_mess_off_history() -> Dict[str, Any]:
    return await _make_request("GET", "/student/mess-off/history")


# ── Recipes ────────────────────────────────────────────────────────
async def get_recipes_detailed() -> Any:
    return await _make_request("GET", "/recipes/detailed")
