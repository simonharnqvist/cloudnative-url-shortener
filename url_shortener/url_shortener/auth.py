from dotenv import load_dotenv
import os
from fastapi import Request, HTTPException, status, Depends
import secrets

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")


def verify_api_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing/invalid Auth header",
        )

    token = auth_header.split(" ")[1]
    if not secrets.compare_digest(token, API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
