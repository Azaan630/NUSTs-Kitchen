import os
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials

    client_id = os.getenv("GOOGLE_CLIENT_ID")

    if not client_id:
        raise HTTPException(status_code=500, detail="Server misconfigured: Missing Google Client ID")

    try:
        # Cryptographic Verification
        # This talks to Google's public keys to ensure the token hasn't been faked.
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            client_id
        )


        if "nust.edu.pk" not in idinfo.get("email", ""):
            raise HTTPException(status_code=403, detail="Only NUST emails allowed")

        # Returns a dict containing 'sub' (Google ID), 'email', and 'name'
        return idinfo

    except ValueError:
        # This happens if the token is forged, expired, or for a different app
        raise HTTPException(status_code=401, detail="Invalid Google Token")

