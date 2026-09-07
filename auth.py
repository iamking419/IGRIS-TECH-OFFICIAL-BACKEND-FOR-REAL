import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from passlib.context import CryptContext

load_dotenv()

# Password hashing context for bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Single standard HTTP Bearer scheme for Swagger UI & API documentation
jwt_bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="JWTBearer",
    description="Enter the JWT access token received from /api/v1/auth/login",
)


def get_admin_password() -> Optional[str]:
    """Retrieve plain admin password from environment if configured."""
    pw = os.getenv("ADMIN_API_PASSWORD")
    return pw.strip("\"'") if pw else None


def get_admin_password_hash() -> Optional[str]:
    """Retrieve pre-hashed bcrypt password from environment if configured."""
    h = os.getenv("ADMIN_PASSWORD_HASH")
    return h.strip("\"'") if h else None


def get_jwt_secret_key() -> str:
    """Retrieve JWT secret key from environment."""
    key = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
    if not key:
        # Fallback to avoid complete crash if not configured, but log clearly
        fallback = get_admin_password() or "default_insecure_jwt_secret_change_me"
        key = f"{fallback}_igris_secret_jwt_key_2026"
    return key.strip("\"'")


def get_jwt_algorithm() -> str:
    """Retrieve configured JWT algorithm (default: HS256)."""
    return os.getenv("JWT_ALGORITHM", "HS256").strip("\"'")


def get_jwt_expire_minutes() -> int:
    """Retrieve JWT expiration lifetime in minutes (default: 60 minutes)."""
    val = os.getenv("JWT_EXPIRE_MINUTES") or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    try:
        return int(val) if val else 60
    except ValueError:
        return 60


def verify_admin_password(plain_password: str) -> bool:
    """Securely verifies the plain password against the server configuration

    Checks:
    1. Bcrypt hash if ADMIN_PASSWORD_HASH is set.
    2. Constant-time string comparison if ADMIN_API_PASSWORD is set.
    """
    if not plain_password:
        return False

    password_hash = get_admin_password_hash()
    if password_hash:
        try:
            return pwd_context.verify(plain_password, password_hash)
        except Exception:
            return False

    expected_plain = get_admin_password()
    if expected_plain:
        return secrets.compare_digest(plain_password.strip(), expected_plain)

    return False


def create_admin_access_token(expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    """Generates a cryptographically signed JWT access token for the admin.

    Returns:
        tuple[str, int]: (token_string, expires_in_minutes)
    """
    expire_minutes = get_jwt_expire_minutes()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire_time = now + expires_delta
        expire_minutes = max(1, int(expires_delta.total_seconds() // 60))
    else:
        expire_time = now + timedelta(minutes=expire_minutes)

    payload = {
        "sub": "admin",
        "role": "admin",
        "iat": now,
        "exp": expire_time,
    }

    token = jwt.encode(
        payload,
        get_jwt_secret_key(),
        algorithm=get_jwt_algorithm(),
    )
    return token, expire_minutes


def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(jwt_bearer_scheme),
) -> Dict[str, Any]:
    """Centralized authentication dependency for all protected admin routes.

    1. Reads Bearer token from the Authorization header.
    2. Rejects missing credentials with 401 Unauthorized.
    3. Cryptographically decodes and verifies the JWT signature.
    4. Validates token expiration.
    5. Validates subject identity ('sub' == 'admin').
    6. Rejects invalid, malformed, expired, or tampered tokens with 401 Unauthorized.
    7. Returns authenticated claims payload.
    """
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    try:
        payload = jwt.decode(
            token,
            get_jwt_secret_key(),
            algorithms=[get_jwt_algorithm()],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="The token has expired"'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        )

    # Validate required claims
    subject = payload.get("sub")
    role = payload.get("role")
    if subject != "admin" or role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims. Admin access required.",
            headers={"WWW-Authenticate": 'Bearer error="insufficient_scope"'},
        )

    return {"sub": subject, "role": role}


# Reusable alias for backwards compatibility
require_admin = get_current_admin
