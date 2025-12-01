
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app import crud, models, schemas
from app.utils.security import get_password_hash
from tests.conftest import override_get_db, TestingSessionLocal

# Setup
app.dependency_overrides = {} # Reset
from app.database import get_db
app.dependency_overrides[get_db] = override_get_db

from tests.conftest import engine
from app.database import Base
Base.metadata.create_all(bind=engine)

def test_debug_login():
    db = TestingSessionLocal()
    # Create admin user if not exists
    hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
    admin = models.User(
        username="admin",
        email=settings.FIRST_SUPERUSER_EMAIL,
        hashed_password=hashed_password,
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        role=schemas.UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        print(f"\nAdmin user found: {admin}")
        if admin:
            print(f"Admin username: {admin.username}")
            print(f"Admin email: {admin.email}")
            print(f"Admin is_active: {admin.is_active}")
            
            # Verify password manually
            from app.utils.security import verify_password
            is_valid = verify_password(settings.FIRST_SUPERUSER_PASSWORD, admin.hashed_password)
            print(f"Password valid: {is_valid}")
        else:
            print("Admin user NOT found in DB!")

        client = TestClient(app)
        login_data = {
            "username": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        print(f"Attempting login with: {login_data}")
        
        r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
        print(f"Response status: {r.status_code}")
        print(f"Response body: {r.text}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_debug_login()
