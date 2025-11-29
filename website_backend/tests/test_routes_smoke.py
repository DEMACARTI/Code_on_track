"""
Smoke tests for API routes.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Test data
TEST_PASSWORD = "testpassword"

def test_auth_login(test_client, test_db, test_user):
    """Test login endpoint with valid and invalid credentials."""
    # Test successful login with email
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Login failed with email: {response.text}"
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test successful login with username
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": test_user.username, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Login failed with username: {response.text}"
    
    # Test invalid credentials
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USERNAME, "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

def test_items_list(test_client, test_db, test_user):
    """Test items list endpoint."""
    # Log in to get the access token
    login_data = {
        "username": test_user.email,
        "password": "testpassword"
    }
    response = test_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    access_token = response.json()["access_token"]
    
    # Get items list with the access token
    response = test_client.get(
        "/api/v1/items/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert isinstance(data, list)
    assert "total" in data
    
    # If there are items, verify they have the required fields
    if data:
        item = data[0]
        # Only check for fields that are guaranteed to exist
        assert "id" in item
        assert "name" in item
        assert "status" in item

def test_engrave_callback(test_client, test_db, test_item):
    """Test engrave callback endpoint with API key."""
    # Use the test API key from settings
    api_key = "test-api-key"  # This should match the one in your test environment
    
    # Prepare the request data without the 'location' field
    data = {
        "item_id": test_item.id,
        "engrave_job_id": "JOB12345",
        "status": "completed",
        "metadata": {"notes": "Test engraving completed"}
    }
    
    # Make the request with the API key
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json()["status"] == "completed"
    
    # Test with invalid API key
    response = test_client.post(
        "/api/engrave/callback",
        json={
            "item_id": test_item.id,
            "status": "completed"
        },
        headers={"X-API-KEY": "wrong-key"}
    )
    assert response.status_code == 401
