"""
Smoke tests for schemas and CRUD functions.
These tests don't require a database connection.
"""
import pytest
from datetime import datetime, timedelta
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
        "password": "securepassword123"
    }
    
    # Should not raise
    user = schemas.UserCreate(**user_data)
    assert user.username == "testuser"
    
    # Test validation for required fields
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="test")  # Missing password

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
    assert callable(crud.list_items)
    assert callable(crud.update_item_status)
    
    # Event functions
    assert callable(crud.create_event)
    assert callable(crud.list_events_for_item)
    
    # Engrave job functions
    assert callable(crud.upsert_engrave_job)
    assert callable(crud.get_engrave_job_by_jobid)
    assert callable(crud.list_recent_engrave_jobs)
    
    # Inspection functions
    assert callable(crud.create_inspection)
    assert callable(crud.list_inspections_for_item)

def test_orm_mode():
    """Test that ORM mode is enabled on read schemas."""
    # Create a dummy ORM object with the expected attributes
    class DummyModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    # Test ItemRead with ORM object
    orm_item = DummyModel(
        id=1,
        uid="TEST123",
        component_type="Bearing",
        lot_number="LOT123",
        vendor_id=1,
        warranty_years=2,
        manufacture_date=datetime.utcnow(),
        current_status=schemas.ItemStatus.MANUFACTURED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # This should work because of orm_mode = True
    item_read = schemas.ItemRead.from_orm(orm_item)
    assert item_read.id == 1
    assert item_read.uid == "TEST123"
    
    # Test VendorRead with ORM object
    orm_vendor = DummyModel(
        id=1,
        name="Test Vendor",
        created_at=datetime.utcnow()
    )
    vendor_read = schemas.VendorRead.from_orm(orm_vendor)
    assert vendor_read.id == 1
    assert vendor_read.name == "Test Vendor"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
