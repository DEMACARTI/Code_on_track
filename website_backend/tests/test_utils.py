"""
Test utilities for the IRF QR tracking system.
"""
import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app import crud, models, schemas
from app.config import settings
from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.schemas import ItemCreate, ItemStatus, UserCreate
from app.utils.security import get_password_hash

# Create test database session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test client
def get_test_db() -> Generator[Session, None, None]:
    """
    Create a test database session that rolls back after each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# Override the get_db dependency in the app
app.dependency_overrides[get_db] = get_test_db

# Test client with overridden db
def get_test_client() -> TestClient:
    """Create a test client with overridden dependencies."""
    return TestClient(app)

# Fixtures
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db() -> Generator[Session, None, None]:
    """
    Create a test database session.
    """
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# User fixtures
@pytest.fixture(scope="function")
def test_user(db: Session) -> models.User:
    """Get or create a test user."""
    # Delete any existing test users to avoid conflicts
    db.query(models.User).filter(
        models.User.username.in_(["testuser", "test@example.com"])
    ).delete(synchronize_session=False)
    db.commit()
    
    # Create a new test user
    hashed_password = get_password_hash("testpassword")
    user = models.User(
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
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_superuser(db: Session) -> models.User:
    """Get or create a test superuser."""
    # Delete any existing admin user to avoid conflicts
    db.query(models.User).filter(
        models.User.username == "admin"
    ).delete(synchronize_session=False)
    db.commit()
    
    # Create a new test superuser
    hashed_password = get_password_hash("adminpassword")
    user = models.User(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed_password,
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        role=schemas.UserRole.ADMIN,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Authentication fixtures
@pytest.fixture(scope="module")
def user_token_headers(client: TestClient, test_user: models.User) -> Dict[str, str]:
    """Get a valid access token for a test user."""
    login_data = {
        "username": test_user.email,
        "password": "testpassword",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient, test_superuser: models.User) -> Dict[str, str]:
    """Get a valid access token for a test superuser."""
    login_data = {
        "username": test_superuser.email,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

# Item fixtures
@pytest.fixture(scope="function")
def test_item(db: Session, test_user: models.User) -> models.Item:
    """Create a test item."""
    uid = random_uid()
    item_data = {
        "component_type": "bearing",
        "lot_number": "LOT123",
        "vendor_id": 1,
        "warranty_years": 2,
        "manufacture_date": datetime.utcnow(),
        "item_metadata": {"test": "data"},
        "quantity": 1
    }
    item_in = ItemCreate(**item_data)
    
    # Create item using the CRUD function
    db_item = crud.create_item(db, item=item_in, owner_id=test_user.id)
    return db_item

@pytest.fixture(scope="function")
def test_items(db: Session, test_user: models.User) -> List[models.Item]:
    """Create multiple test items."""
    items = []
    for i in range(3):
        item_data = {
            "component_type": f"component_{i+1}",
            "lot_number": f"LOT{i+1}",
            "vendor_id": i+1,
            "warranty_years": i+1,
            "manufacture_date": datetime.utcnow(),
            "item_metadata": {"test": f"data{i+1}", "type": "test"},
            "quantity": 1
        }
        item_in = ItemCreate(**item_data)
        db_item = crud.create_item(db, item=item_in, owner_id=test_user.id)
        items.append(db_item)
    return items

# Utility functions
def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string."""
    return "".join(random.choices(string.ascii_lowercase, k=length))

def random_email() -> str:
    """Generate a random email."""
    return f"{random_lower_string()}@{random_lower_string()}.com"

def random_uid(prefix: str = "TEST", length: int = 8) -> str:
    """Generate a random UID with optional prefix."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}_{suffix}"

def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    """Get a valid access token for a superuser."""
    login_data = {
        "username": settings.FIRST_SUPERUSER_EMAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
