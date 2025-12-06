# backend/app/auth/schemas.py
# Purpose: Auth Pydantic models
# Author: Antigravity

from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    role: UserRole

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: Optional[EmailStr] = None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
