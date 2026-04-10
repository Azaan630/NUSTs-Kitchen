import httpx

# In Docker, we use the container service name 'backend'
BASE_URL = "http://backend:8000"

def get_status():
    """Checks if the backend is alive."""
    try:
        response = httpx.get(f"{BASE_URL}/health-check")
        return response.json()
    except Exception as e:
        return {"database": "Error", "details": str(e)}

def get_menu():
    """Fetches the food items."""
    try:
        response = httpx.get(f"{BASE_URL}/menu") # You will build this route in main.py
        return response.json()
    except:
        return []