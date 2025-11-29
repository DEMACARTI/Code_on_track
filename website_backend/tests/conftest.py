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
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test environment variables before importing app
os.environ["TESTING"] = "true"
os.environ["ENGRAVE_API_KEY"] = "test-api-key-123"

# Now import the app and other modules
from app.main import app, get_db
from app.database import Base
from app import models, schemas, crud
from app.utils.security import get_password_hash

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
def test_db():
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
        db.commit()
        db.refresh(test_user)
        
        yield db
        
    finally:
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
def inactive_user(test_db):
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
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def inactive_user_token_headers(inactive_user, client: TestClient):
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
def test_item(test_db, test_vendor):
    """Get or create a test item."""
    from datetime import datetime, timezone
    
    # Try to get existing test item
    test_item = test_db.query(models.Item).filter(models.Item.uid == "TEST123").first()
    
    # If test item doesn't exist, create one
    if not test_item and test_vendor:
        # Get or create an owner
        owner = test_db.query(models.User).filter(models.User.username == "testuser").first()
        if not owner:
            owner = models.User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
                is_active=True
            )
            test_db.add(owner)
            test_db.commit()
            test_db.refresh(owner)
            
        test_item = models.Item(
            uid="TEST123",
            name="Test Item",
            description="A test item for testing purposes",
            status="in_stock",
            vendor_id=test_vendor.id,
            owner_id=owner.id,
            location="Test Location",
            component_type="Test Component",
            lot_number="LOT123",
            warranty_years=1,
            manufacture_date=datetime.now(UTC),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        test_db.add(test_item)
        test_db.commit()
        test_db.refresh(test_item)
    
    return test_item
