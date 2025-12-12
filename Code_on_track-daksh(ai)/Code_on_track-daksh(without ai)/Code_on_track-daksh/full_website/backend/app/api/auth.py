# backend/app/api/auth.py
# Purpose: Authentication endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.auth.schemas import LoginRequest, Token
from app.auth.security import verify_password, create_access_token, create_refresh_token
from app.models.user import WebsiteUser

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Debug logging
    with open("debug_auth.log", "a") as f:
        f.write(f"\nLogin attempt for: '{login_data.username}' with pwd: '{login_data.password}'\n")

    # Find user by username
    result = await db.execute(select(WebsiteUser).where(WebsiteUser.username == login_data.username))
    user = result.scalar_one_or_none()
    
    with open("debug_auth.log", "a") as f:
        f.write(f"User found: {user}\n")

    if not user:
        with open("debug_auth.log", "a") as f:
            f.write("User NOT found in DB query.\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid = verify_password(login_data.password, user.password_hash)
    with open("debug_auth.log", "a") as f:
        f.write(f"Password verification result: {is_valid}\n")

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role
    }
