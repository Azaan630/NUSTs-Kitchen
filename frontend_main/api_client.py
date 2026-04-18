import httpx

# In Docker, we use the container service name 'backend'
BASE_URL = "http://backend:8000"

def get_all_users():
    try:
        with httpx.Client() as client:
            response = client.get(f"{BASE_URL}/users")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Frontend API Error: {e}")
        return []