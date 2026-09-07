from fastapi import APIRouter, Depends, HTTPException, status

from auth import create_admin_access_token, get_current_admin, verify_admin_password
import schemas

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
    summary="Admin Login (Get JWT Token)",
)
def admin_login(login_data: schemas.AdminLoginRequest):
    """Authenticates the admin using the configured server-side password/hash

    and returns a signed cryptographic JWT access token.
    """
    if not login_data.password or not verify_admin_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expire_minutes = create_admin_access_token()
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": expire_minutes,
    }


@router.get(
    "/verify",
    summary="Verify Admin Token",
)
def verify_admin_token(admin: dict = Depends(get_current_admin)):
    """Verifies that the provided JWT token is valid, active, and authenticated."""
    return {
        "status": "authenticated",
        "sub": admin["sub"],
        "role": admin["role"],
    }
