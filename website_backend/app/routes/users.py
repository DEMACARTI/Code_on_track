"""
User management routes for the IRF QR tracking system.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user, get_current_active_superuser

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post(
    "",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)]
)
async def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only).
    
    - **email**: User's email (must be unique)
    - **password**: User's password (will be hashed)
    - **full_name**: User's full name
    - **is_active**: Whether the user is active (default: True)
    - **is_superuser**: Whether the user is a superuser (default: False)
    
    Returns the created user (without password hash).
    """
    # Check if user with this email already exists
    db_user = crud.user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create the user
    return crud.user.create(db, obj_in=user_in)

@router.get(
    "",
    response_model=List[schemas.UserRead],
    dependencies=[Depends(get_current_active_superuser)]
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve users (admin only).
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return (max 100)
    
    Returns a list of users (without password hashes).
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get(
    "/me",
    response_model=schemas.UserRead
)
async def read_user_me(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    
    Returns the profile of the currently authenticated user.
    """
    return current_user

@router.put(
    "/me",
    response_model=schemas.UserRead
)
async def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update current user's profile.
    
    - **full_name**: New full name (optional)
    - **email**: New email (optional, must be unique)
    - **password**: New password (optional)
    
    Returns the updated user profile.
    """
    # Don't allow updating to an existing email
    if user_in.email and user_in.email != current_user.email:
        db_user = crud.user.get_by_email(db, email=user_in.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    return crud.user.update(db, db_obj=current_user, obj_in=user_in)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_superuser)]
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).
    
    - **user_id**: ID of the user to delete
    
    Returns 204 No Content on success.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    crud.user.remove(db, id=user_id)
    return None
