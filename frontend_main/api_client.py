import httpx
import os
from datetime import date

BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def verify_user_in_db(id_token: str):
    """
    Sends the Google ID Token to the backend to check registration status.
    """
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/users/verify", headers=headers)
            if response.status_code == 403:
                return {"error": "unregistered"}
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Verification Error: {e}")
        return {"error": "server_error"}

async def get_todays_menu(email: str, target_date: date = date.today()):
    """
    Fetches today's menu from the backend.
    """
    async with httpx.AsyncClient() as client:
        try:
            params = {"email": email, "target_date": target_date.isoformat()}
            response = await client.get(f"{BASE_URL}/menu/today", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Backend Connection Error: {str(e)}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"Backend Error: {e.response.status_code}"}


async def get_my_bills(email: str):
    """
    Fetches bill history for the logged-in student.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/users/my_bills", params={"email": email}, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Backend Connection Error: {str(e)}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"Backend Error: {e.response.status_code}"}