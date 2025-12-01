# tests/test_auth_hashing.py
import pytest
from app.utils.security import get_password_hash, verify_password

def test_password_hashing():
    # Test that hashing works and is not plaintext
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert password != hashed
    assert len(hashed) > len(password)
    
    # Test verification works with correct password
    assert verify_password(password, hashed) is True
    
    # Test verification fails with wrong password
    assert verify_password("wrongpassword", hashed) is False

# tests/test_uid_unique.py
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal

@pytest.mark.usefixtures("test_db")
def test_duplicate_uid(test_db, test_user):
    # Use the test_user fixture to get a test user
    user = test_user
    
    # Create first item with owner_id
    item1 = models.Item(
        uid="TEST123",
        name="Test Item",
        status="in_stock",
        owner_id=user.id
    )
    test_db.add(item1)
    test_db.commit()
    
    # Try to create second item with same UID but same owner
    item2 = models.Item(
        uid="TEST123",
        name="Duplicate Item",
        status="in_stock",
        owner_id=user.id
    )
    test_db.add(item2)
    
    # Should raise IntegrityError due to duplicate UID
    with pytest.raises(IntegrityError):
        test_db.commit()
    
    # Rollback to clean up
    test_db.rollback()

# tests/test_engrave_idempotency.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, UTC, timezone, timedelta

from app.main import app
from app import models, crud
from app.database import SessionLocal

client = TestClient(app)

# Temporarily skipping this test as it requires more setup
@pytest.mark.skip(reason="Requires additional setup for API testing")
def test_engrave_job_idempotency(test_db, test_user, test_client):
    # This test requires more setup and mocking
    pass