"""
Tests for authentication endpoints.
"""
import json
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.main import app
from tests.test_utils import random_email, random_lower_string

client = TestClient(app)


def test_get_access_token(client: TestClient) -> None:
    """Test successful login and token retrieval."""
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
    assert tokens["token_type"] == "bearer"


def test_use_access_token(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    """Test accessing a protected endpoint with a valid token."""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_login_incorrect_password(client: TestClient) -> None:
    """Test login with incorrect password."""
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": "wrongpassword",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 400
    assert "Incorrect email or password" in r.json()["detail"]


def test_login_incorrect_email(client: TestClient) -> None:
    """Test login with non-existent email."""
    login_data = {"username": "nonexistent@example.com", "password": "testpass"}
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 400
    assert "Incorrect email or password" in r.json()["detail"]


def test_get_current_user(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    """Test retrieving current user with valid token."""
    r = client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["email"] == settings.FIRST_SUPERUSER_EMAIL
    assert "hashed_password" not in current_user


def test_get_current_user_inactive(
    client: TestClient, inactive_user_token_headers: Dict[str, str]
) -> None:
    """Test retrieving current user with inactive user token."""
    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=inactive_user_token_headers,
    )
    assert r.status_code == 400
    assert "Inactive user" in r.json()["detail"]


def test_get_current_user_invalid_token(client: TestClient) -> None:
    """Test retrieving current user with invalid token."""
    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert r.status_code == 401
    assert "Could not validate credentials" in r.json()["detail"]


def test_get_current_user_no_token(client: TestClient) -> None:
    """Test retrieving current user without token."""
    r = client.get(f"{settings.API_V1_STR}/users/me")
    assert r.status_code == 401
    assert "Not authenticated" in r.json()["detail"]


def test_password_recovery(client: TestClient, db: Session) -> None:
    """Test password recovery flow."""
    email = random_email()
    password = random_lower_string()
    
    # Create a test user
    user_in = schemas.UserCreate(
        username=email.split('@')[0],
        email=email,
        password=password,
        full_name="Test User",
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Request password recovery
    r = client.post(
        f"{settings.API_V1_STR}/auth/password-recovery/{email}"
    )
    assert r.status_code == 200
    assert "msg" in r.json()
    
    # TODO: Test reset password with token
    # This would require mocking the email sending and token verification

def test_reset_password(client: TestClient, db: Session) -> None:
    """Test password reset with valid token."""
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()
    
    # Create a test user
    user_in = schemas.UserCreate(
        username=email.split('@')[0],
        email=email,
        password=password,
        full_name="Test User",
    )
    user = crud.user.create(db, obj_in=user_in)
    
    # Generate a password reset token
    from app.core.security import generate_password_reset_token
    token = generate_password_reset_token(email=email)
    
    # Reset password
    data = {"token": token, "new_password": new_password}
    r = client.post(
        f"{settings.API_V1_STR}/auth/reset-password/",
        json=data,
    )
    assert r.status_code == 200
    assert "msg" in r.json()
    
    # Verify new password works
    login_data = {
        "username": email,
        "password": new_password,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_reset_password_invalid_token(client: TestClient) -> None:
    """Test password reset with invalid token."""
    data = {
        "token": "invalidtoken",
        "new_password": "newpassword",
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/reset-password/",
        json=data,
    )
    assert r.status_code == 400
    assert "Invalid token" in r.json()["detail"]
