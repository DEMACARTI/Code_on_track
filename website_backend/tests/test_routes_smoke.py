"""
Smoke tests for API routes.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Test data
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_EMAIL = "test@example.com"
TEST_API_KEY = "test-api-key"  # This should match the one in your test environment

def test_auth_login(test_client, test_db):
    """Test login endpoint with valid and invalid credentials."""
    # Test successful login
    response = test_client.post(
        "/api/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test invalid credentials
    response = test_client.post(
        "/api/auth/login",
        data={"username": TEST_USERNAME, "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

def test_items_list(test_client, test_db, test_user):
    """Test items list endpoint."""
    # Log in to get the access token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = test_client.post(
        "/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    
    # Now use the token to access the items list
    response = test_client.get(
        "/api/items/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("items"), list)
    assert "total" in data
    
    # If there are items, verify they have the required fields
    if data.get("items"):
        item = data["items"][0]
        # Only check for fields that are guaranteed to exist
        assert "id" in item
        assert "name" in item
        assert "status" in item

def test_engrave_callback(test_client, test_db, test_item):
    """Test engrave callback endpoint with API key."""
    test_api_key = os.getenv("ENGRAVE_API_KEY")
    
    # Test with valid API key
    response = test_client.post(
        "/api/engrave/callback",
        json={
            "item_id": test_item.id,
            "status": "completed",
            "message": "Test engraving"
        },
        headers={"X-API-KEY": test_api_key}
    )
    
    # Debug output
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # If we get an error, print the traceback for debugging
    if response.status_code >= 400:
        print(f"Error ({response.status_code}): {response.text}")
    
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
