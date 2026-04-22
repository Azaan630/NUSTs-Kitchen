import httpx

# In Docker, we use the container service name 'backend'
BASE_URL = "http://backend:8000"

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