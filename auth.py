import os
import secrets
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

ADMIN_API_PASSWORD = os.getenv("ADMIN_API_PASSWORD", "change-me-in-production")

# Support both Bearer token header and X-Admin-Password header
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-Admin-Password", auto_error=False)


def require_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
) -> bool:
    """Verifies that the incoming request contains the correct admin password

    Accepts credentials via either:
    1. Authorization: Bearer <ADMIN_API_PASSWORD>
    2. X-Admin-Password: <ADMIN_API_PASSWORD>
    """
    provided_password = None

    if credentials and credentials.credentials:
        provided_password = credentials.credentials
    elif api_key:
        provided_password = api_key

    if not provided_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Please provide a valid admin password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(provided_password, ADMIN_API_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin credentials.",
        )

    return True
