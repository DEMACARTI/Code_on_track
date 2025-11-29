"""
Tests for item management endpoints.
"""
import json
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.main import app
from tests.test_utils import random_lower_string, random_uid

client = TestClient(app)


def test_create_item(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test creating a new item."""
    item_data = {
        "uid": random_uid(),
        "name": "Test Item",
        "description": "Test description",
        "status": "manufactured",
        "metadata": {"lot": "LOT123", "type": "bearing"}
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=item_data,
    )
    assert r.status_code == 201
    created_item = r.json()
    assert created_item["uid"] == item_data["uid"]
    assert created_item["name"] == item_data["name"]
    assert created_item["status"] == item_data["status"]
    assert "id" in created_item


def test_create_duplicate_uid(
    client: TestClient, superuser_token_headers: Dict[str, str], test_item: models.Item
) -> None:
    """Test creating an item with a duplicate UID."""
    item_data = {
        "uid": test_item.uid,
        "name": "Duplicate Item",
        "description": "This should fail",
        "status": "manufactured"
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=item_data,
    )
    assert r.status_code == 409
    assert f"Item with UID {test_item.uid} already exists" in r.json()["detail"]


def test_read_item(
    client: TestClient, test_item: models.Item
) -> None:
    """Test retrieving an item by UID."""
    r = client.get(f"{settings.API_V1_STR}/items/{test_item.uid}")
    assert r.status_code == 200
    item = r.json()
    assert item["uid"] == test_item.uid
    assert item["name"] == test_item.name
    assert "created_at" in item


def test_read_nonexistent_item(
    client: TestClient
) -> None:
    """Test retrieving a non-existent item."""
    non_existent_uid = "NONEXISTENT123"
    r = client.get(f"{settings.API_V1_STR}/items/{non_existent_uid}")
    assert r.status_code == 404
    assert f"Item with UID {non_existent_uid} not found" in r.json()["detail"]


def test_list_items(
    client: TestClient, test_items: List[models.Item]
) -> None:
    """Test listing items with pagination."""
    r = client.get(f"{settings.API_V1_STR}/items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == len(test_items)
    
    # Test pagination
    r = client.get(f"{settings.API_V1_STR}/items/?skip=1&limit=1")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_filter_items(
    client: TestClient, test_item: models.Item
) -> None:
    """Test filtering items by various criteria."""
    # Filter by status
    r = client.get(f"{settings.API_V1_STR}/items/?status={test_item.status}")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert all(item["status"] == test_item.status for item in items)
    
    # Filter by type (from metadata)
    r = client.get(f"{settings.API_V1_STR}/items/?type=test")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_item_status(
    client: TestClient, test_item: models.Item, superuser_token_headers: Dict[str, str]
) -> None:
    """Test updating an item's status."""
    new_status = "installed"
    update_data = {"status": new_status, "notes": "Installed in engine bay 1"}
    
    r = client.patch(
        f"{settings.API_V1_STR}/items/{test_item.uid}/status",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert r.status_code == 200
    updated_item = r.json()
    assert updated_item["status"] == new_status
    
    # Verify the status was updated in the database
    r = client.get(f"{settings.API_V1_STR}/items/{test_item.uid}")
    assert r.status_code == 200
    assert r.json()["status"] == new_status


def test_update_nonexistent_item_status(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    """Test updating status of a non-existent item."""
    non_existent_uid = "NONEXISTENT123"
    update_data = {"status": "installed", "notes": "Test update"}
    
    r = client.patch(
        f"{settings.API_V1_STR}/items/{non_existent_uid}/status",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert r.status_code == 404
    assert f"Item with UID {non_existent_uid} not found" in r.json()["detail"]


def test_create_multiple_items(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    """Test creating multiple items in a single request."""
    item_data = [
        {
            "uid": random_uid(),
            "name": "Bulk Item 1",
            "description": "First bulk item",
            "status": "manufactured"
        },
        {
            "uid": random_uid(),
            "name": "Bulk Item 2",
            "description": "Second bulk item",
            "status": "manufactured"
        }
    ]
    
    r = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=item_data,
    )
    assert r.status_code == 201
    created_items = r.json()
    assert len(created_items) == 2
    assert all("id" in item for item in created_items)
    assert {item["name"] for item in created_items} == {"Bulk Item 1", "Bulk Item 2"}
