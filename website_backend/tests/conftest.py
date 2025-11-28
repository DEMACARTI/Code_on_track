"""
Test configuration and fixtures for the application.
"""
import os
import sys
import pytest
from datetime import datetime, timezone, UTC
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test environment variables before importing app
os.environ["TESTING"] = "true"
os.environ["ENGRAVE_API_KEY"] = "test-api-key-123"

# Now import the app and other modules
from app.main import app, get_db
from app.database import Base, engine, SessionLocal
from app import models, schemas, crud
from app.utils.security import get_password_hash

# Override the database dependency
def override_get_db():
    """Override the get_db dependency for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Fixtures
@pytest.fixture(scope="function")
def test_db():
    """Create a test database and yield a session."""
    # Clean up any existing data
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create a test user
        hashed_password = get_password_hash("testpassword")
        test_user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        yield db
        
    finally:
        # Clean up
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client():
    """Create a test client for the API."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def test_user(test_db):
    """Get the test user."""
    return test_db.query(models.User).filter(models.User.username == "testuser").first()

@pytest.fixture(scope="function")
def test_vendor(test_db):
    """Get or create a test vendor."""
    from datetime import datetime, timezone
    
    # Try to get existing test vendor
    test_vendor = test_db.query(models.Vendor).filter(models.Vendor.name == "Test Vendor").first()
    
    # If test vendor doesn't exist, create one
    if not test_vendor:
        test_vendor = models.Vendor(
            name="Test Vendor",
            contact_email="test@example.com",
            phone="+1234567890",
            address="123 Test St, Test City"
        )
        test_db.add(test_vendor)
        test_db.commit()
        test_db.refresh(test_vendor)
    
    return test_vendor

@pytest.fixture(scope="function")
def test_item(test_db, test_vendor):
    """Get or create a test item."""
    from datetime import datetime, timezone
    
    # Try to get existing test item
    test_item = test_db.query(models.Item).filter(models.Item.uid == "TEST123").first()
    
    # If test item doesn't exist, create one
    if not test_item and test_vendor:
        test_item = models.Item(
            uid="TEST123",
            name="Test Item",
            description="A test item for testing purposes",
            status="in_stock",
            vendor_id=test_vendor.id,
            location="Test Location"
        )
        test_db.add(test_item)
        test_db.commit()
        test_db.refresh(test_item)
    
    return test_item
