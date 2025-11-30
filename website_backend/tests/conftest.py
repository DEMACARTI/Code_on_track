"""
Test configuration and fixtures for the application.
"""
import os
import sys
import pytest
from typing import Dict, List
from datetime import datetime, timezone, UTC
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test environment variables before importing app
os.environ["TESTING"] = "true"
os.environ["ENGRAVE_API_KEY"] = "test-api-key-123"

# Now import the app and other modules
from app.main import app, get_db
from app.config import settings
from app.database import Base
from app import models, schemas, crud
from app.utils.security import get_password_hash
from app.schemas import ItemCreate

# Set up test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Fixtures
@pytest.fixture(scope="function")
def db():
    """Create a test database and yield a session."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        # Create a test user
        hashed_password = get_password_hash("testpassword")
        test_user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            role=schemas.UserRole.VIEWER,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(test_user)
        
        # Create a test superuser
        hashed_password_admin = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        test_superuser = models.User(
            username="admin",
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=hashed_password_admin,
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            role=schemas.UserRole.ADMIN,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(test_superuser)
        
        db.commit()
        
        yield db
        
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Create a test client for the API."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def test_user(db):
    """Get the test user."""
    return db.query(models.User).filter(models.User.username == "testuser").first()

@pytest.fixture(scope="function")
def test_superuser(db):
    """Get the test superuser."""
    return db.query(models.User).filter(models.User.username == "admin").first()

@pytest.fixture(scope="function")
def superuser_token_headers(client, test_superuser):
    """Get a valid access token for a test superuser."""
    login_data = {
        "username": test_superuser.email,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    print(f"Fixture Login Response: {r.status_code} {r.text}")
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

@pytest.fixture(scope="function")
def test_vendor(db):
    """Get or create a test vendor."""
    # Try to get existing test vendor
    test_vendor = db.query(models.Vendor).filter(models.Vendor.name == "Test Vendor").first()
    
    # If test vendor doesn't exist, create one
    if not test_vendor:
        test_vendor = models.Vendor(
            name="Test Vendor",
            contact_email="test@example.com",
            phone="+1234567890",
            address="123 Test St, Test City"
        )
        db.add(test_vendor)
        db.commit()
        db.refresh(test_vendor)
    
    return test_vendor

@pytest.fixture(scope="function")
def inactive_user(db):
    """Create an inactive test user."""
    email = "inactive@example.com"
    hashed_password = get_password_hash("inactivepassword")
    user = models.User(
        username="inactiveuser",
        email=email,
        hashed_password=hashed_password,
        is_active=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def inactive_user_token_headers(inactive_user, client):
    """Get a token for the inactive test user."""
    login_data = {
        "username": inactive_user.email,
        "password": "inactivepassword"
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_t = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_t}"}
    return headers

@pytest.fixture(scope="function")
def test_item(db, test_vendor):
    """Get or create a test item."""
    # Try to get existing test item
    test_item = db.query(models.Item).filter(models.Item.uid == "TEST123").first()
    
    # If test item doesn't exist, create one
    if not test_item and test_vendor:
        # Get or create an owner
        owner = db.query(models.User).filter(models.User.username == "testuser").first()
            
        test_item = models.Item(
            uid="TEST123",
            name="Test Item",
            description="A test item for testing purposes",
            status="manufactured",
            vendor_id=test_vendor.id,
            owner_id=owner.id,
            item_metadata={
                "component_type": "Test Component",
                "lot_number": "LOT123",
                "warranty_years": 1,
                "manufacture_date": datetime.now(UTC).isoformat()
            },
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(test_item)
        db.commit()
        db.refresh(test_item)
    
    return test_item

@pytest.fixture(scope="function")
def test_items(db, test_user, test_vendor):
    """Create multiple test items."""
    items = []
    for i in range(3):
        item_data = {
            "component_type": f"component_{i+1}",
            "lot_number": f"LOT{i+1}",
            "vendor_id": test_vendor.id, # Use valid vendor ID
            "warranty_years": i+1,
            "manufacture_date": datetime.utcnow(),
            "item_metadata": {"test": f"data{i+1}", "type": "test"},
            "quantity": 1,
            "name": f"Test Item {i+1}",
            "description": f"Description for item {i+1}"
        }
        item_in = ItemCreate(**item_data)
        db_item = crud.create_item(db, item=item_in, owner_id=test_user.id)
        items.append(db_item)
    return items
