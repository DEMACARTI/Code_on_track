"""
Authentication routes for the IRF QR tracking system.
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_user_by_username,
)

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: Username for authentication
    - **password**: Password for authentication
    
    Returns an access token that can be used for subsequent requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me/", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Get the current user's profile.
    
    Returns the profile of the currently authenticated user.
    """
    return current_user

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    
    - **username**: Unique username
    - **email**: User's email address
    - **password**: Password (min 8 characters)
    - **full_name**: User's full name (optional)
    - **role**: User role (default: viewer)
    
    Returns the created user profile.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db=db, user=user)

@router.get("/verify-token")
async def verify_token(
    current_user: models.User = Depends(get_current_active_user)
) -> dict[str, str]:
    """
    Verify if the current access token is valid.
    
    Returns a success message if the token is valid.
    """
    return {"message": "Token is valid", "user": current_user.username}
