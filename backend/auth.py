import os
import logging
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

API_KEY = os.getenv("BACKEND_API_KEY")
if not API_KEY:
    raise RuntimeError("BACKEND_API_KEY environment variable is not set")


def verify_api_key(request: Request):
    key = request.headers.get("X-Api-Key") or request.query_params.get("api_key")
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


def get_user_email(request: Request) -> str:
    email = request.headers.get("X-User-Email", "").strip().lower()
    if not email:
        email = request.query_params.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Missing email (X-User-Email header or email query param)")
    return email
