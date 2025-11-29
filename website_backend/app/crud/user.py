"""
CRUD operations for User model.
"""
from typing import Optional, List, Any, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status

from .. import models, schemas
from ..utils.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.User]:
    """Get a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        user: UserCreate schema with user data
        
    Returns:
        models.User: The created user
        
    Raises:
        HTTPException: If user creation fails due to duplicate username/email or other errors
    """
    # Check if username already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Check if email already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_superuser=user.is_superuser if hasattr(user, 'is_superuser') else False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e).lower():
            if "users_username_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            elif "users_email_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error creating user: {str(e)}"
        )


def update_user(
    db: Session, db_user: models.User, user_update: Union[schemas.UserUpdate, Dict[str, Any]]
) -> models.User:
    """
    Update a user's information.
    
    Args:
        db: Database session
        db_user: The user model instance to update
        user_update: UserUpdate schema or dict with updated fields
        
    Returns:
        models.User: The updated user
        
    Raises:
        HTTPException: If update fails due to validation or database errors
    """
    if isinstance(user_update, dict):
        update_data = user_update
    else:
        update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle password hashing if password is being updated
    if 'password' in update_data and update_data['password']:
        hashed_password = get_password_hash(update_data['password'])
        update_data['hashed_password'] = hashed_password
        del update_data['password']
    
    # Check for duplicate username/email
    if 'username' in update_data and update_data['username'] != db_user.username:
        if get_user_by_username(db, update_data['username']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use"
            )
    
    if 'email' in update_data and update_data['email'] != db_user.email:
        if get_user_by_email(db, update_data['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Update user attributes
    for field, value in update_data.items():
        if hasattr(db_user, field) and value is not None:
            setattr(db_user, field, value)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e).lower():
            if "users_username_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already in use"
                )
            elif "users_email_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error updating user: {str(e)}"
        )


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user by ID.
    
    Args:
        db: Database session
        user_id: ID of the user to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        HTTPException: If user not found or deletion fails
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        db.delete(db_user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


def authenticate_user(
    db: Session, 
    username: str, 
    password: str
) -> Optional[models.User]:
    """
    Authenticate a user with username and password.
    
    Args:
        db: Database session
        username: Username to authenticate
        password: Plain text password to verify
        
    Returns:
        Optional[models.User]: The authenticated user if successful, None otherwise
    """
    if not username or not password:
        return None
        
    user = get_user_by_username(db, username=username)
    if not user:
        # Try with email as fallback
        user = get_user_by_email(db, email=username)
        if not user:
            return None
    
    if not user.is_active:
        return None
        
    if not verify_password(password, user.hashed_password):
        return None
        
    return user
