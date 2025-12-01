from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
from typing import Optional

from app.database import get_db
from app.models import User

router = APIRouter()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    department: str
    role: str
    is_active: bool

# Hash password using SHA256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Simple token generation (in production, use JWT)
def generate_token(username: str) -> str:
    data = f"{username}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return token
    """
    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Verify password
    hashed_password = hash_password(request.password)
    if user.hashed_password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate token
    token = generate_token(user.username)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "department": user.department.value if user.department else "user",
            "role": user.department.value if user.department else "user",
            "is_active": user.is_active
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    Get current user info from token
    """
    # In production, validate JWT token properly
    # For now, just return basic validation
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # This is a simplified version - in production, decode JWT token
    # For now, return placeholder
    return {
        "id": 1,
        "username": "user",
        "email": "user@example.com",
        "full_name": "User Name",
        "department": "General",
        "role": "USER",
        "is_active": True
    }

@router.post("/logout")
async def logout():
    """
    Logout user (client should clear token)
    """
    return {"message": "Logged out successfully"}
