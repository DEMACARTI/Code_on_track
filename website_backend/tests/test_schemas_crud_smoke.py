"""
Smoke tests for schemas and CRUD functions.
These tests don't require a database connection.
"""
import pytest
from datetime import datetime, timedelta, UTC
from pydantic import ValidationError

from app import schemas, crud

def test_item_schema_validation():
    """Test that ItemCreate schema validates correctly."""
    # Valid data
    valid_data = {
        "component_type": "Bearing",
        "lot_number": "LOT123",
        "vendor_id": 1,
        "warranty_years": 2,
        "manufacture_date": "2023-01-15T00:00:00",
        "metadata": {"color": "blue"},
        "quantity": 5
    }
    
    # Should not raise
    item = schemas.ItemCreate(**valid_data)
    assert item.quantity == 5
    assert item.component_type == "Bearing"
    
    # Test validation for required fields
    with pytest.raises(ValidationError):
        schemas.ItemCreate(**{"component_type": "Bearing"})  # Missing required fields
    
    # Test quantity validation
    with pytest.raises(ValidationError):
        schemas.ItemCreate(**{
            **valid_data,
            "quantity": 0  # Must be > 0
        })

def test_user_schema_validation():
    """Test that UserCreate schema validates correctly."""
    # Valid data
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    # Should not raise
    user = schemas.UserCreate(**user_data)
    assert user.username == "testuser"
    
    # Test validation for required fields
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="test")  # Missing email and password
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="test", password="pass")  # Missing email

def test_crud_functions_importable():
    """Test that all CRUD functions can be imported and have the right signature."""
    # User functions
    assert callable(crud.get_user_by_username)
    assert callable(crud.create_user)
    
    # Vendor functions
    assert callable(crud.create_vendor)
    assert callable(crud.get_vendor)
    assert callable(crud.list_vendors)
    
    # Item functions
    assert callable(crud.create_item)
    assert callable(crud.get_item_by_uid)
    assert callable(crud.get_items)  # Changed from list_items to get_items
    assert callable(crud.update_item_status)
    
    # Event functions
    assert callable(crud.create_event)
    assert callable(crud.get_events)
    
    # Engrave job functions
    assert callable(crud.upsert_engrave_job)
    assert callable(crud.get_engrave_job)
    assert callable(crud.get_engrave_jobs)
    
    # Inspection functions - not implemented yet
    # assert callable(crud.create_inspection)
    # assert callable(crud.list_inspections_for_item)

def test_orm_mode():
    """Test that ORM mode is enabled on read schemas."""
    # Create an ORM-style object
    class ORMItem:
        def __init__(self):
            self.id = 1
            self.uid = "test-uid-123"
            self.component_type = "Bearing"
            self.lot_number = "LOT123"
            self.vendor_id = 1
            self.warranty_years = 2
            self.manufacture_date = datetime.now()
            self.current_status = schemas.ItemStatus.MANUFACTURED
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
    
    orm_item = ORMItem()
    
    # This should work with model_validate
    item_read = schemas.ItemRead.model_validate(orm_item)
    assert item_read.id == 1
    assert item_read.uid == "test-uid-123"
    
    # Test with a dictionary (should also work with from_attributes=True)
    item_dict = {
        "id": 2,
        "uid": "test-uid-456",
        "component_type": "Gear",
        "lot_number": "LOT456",
        "vendor_id": 2,
        "warranty_years": 3,
        "manufacture_date": datetime.now(UTC),
        "current_status": schemas.ItemStatus.SUPPLIED,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    
    item_read = schemas.ItemRead.model_validate(item_dict)
    assert item_read.id == 2
    assert item_read.uid == "test-uid-456"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
