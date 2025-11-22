import os
from typing import Optional
from fastapi import HTTPException, Request, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import verify_token_with_user_service

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme)) -> dict:
    if os.getenv("AUTH_DISABLED", "false").lower() == "true":
        return {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}

    user: Optional[dict] = getattr(request.state, "user", None)
    if user:
        return user

    token = None
    if credentials:
        if credentials.scheme and credentials.scheme.lower() == 'bearer':
            token = credentials.credentials
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")

    if not token:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
        token = parts[1]

    user = verify_token_with_user_service(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def require_auth_security(credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))) -> dict:
    if os.getenv("AUTH_DISABLED", "false").lower() == "true":
        return {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}

    if not credentials or not credentials.scheme or credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing credentials")

    token = credentials.credentials
    user = verify_token_with_user_service(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user
