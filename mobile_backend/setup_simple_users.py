"""
Setup simple users for mobile app
Creates basic users with simple passwords for easy access
"""

import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, User, UserRole
import os

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_simple_users():
    """Create simple users for mobile app"""
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tables created/verified!")
        
        # Simple users with easy-to-remember credentials
        users = [
            {
                "username": "admin",
                "password": "admin123",
                "email": "admin@railchinh.com",
                "full_name": "Admin User",
                "department": UserRole.ADMIN
            },
            {
                "username": "inspection",
                "password": "inspect123",
                "email": "inspection@railchinh.com",
                "full_name": "Inspection Team",
                "department": UserRole.INSPECTION
            },
            {
                "username": "inventory",
                "password": "inventory123",
                "email": "inventory@railchinh.com",
                "full_name": "Inventory Manager",
                "department": UserRole.INVENTORY
            },
            {
                "username": "installation",
                "password": "install123",
                "email": "installation@railchinh.com",
                "full_name": "Installation Team",
                "department": UserRole.INSTALLATION
            },
            {
                "username": "management",
                "password": "manage123",
                "email": "management@railchinh.com",
                "full_name": "Management",
                "department": UserRole.MANAGEMENT
            }
        ]
        
        print("\n📝 Creating users...")
        print("=" * 60)
        
        for user_data in users:
            # Check if user already exists by username or email
            existing_user = db.query(User).filter(
                (User.username == user_data["username"]) | 
                (User.email == user_data["email"])
            ).first()
            
            if existing_user:
                # Update existing user
                existing_user.username = user_data["username"]
                existing_user.hashed_password = hash_password(user_data["password"])
                existing_user.email = user_data["email"]
                existing_user.full_name = user_data["full_name"]
                existing_user.department = user_data["department"]
                existing_user.is_active = True
                db.commit()
                print(f"✅ Updated user: {user_data['username']}")
            else:
                # Create new user
                new_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    department=user_data["department"],
                    is_active=True
                )
                db.add(new_user)
                db.commit()
                print(f"✅ Created user: {user_data['username']}")
        
        print("\n" + "=" * 60)
        print("✅ All users created/updated successfully!")
        print("\n📱 MOBILE APP LOGIN CREDENTIALS")
        print("=" * 60)
        
        for user_data in users:
            print(f"\n{user_data['full_name']}:")
            print(f"  Username: {user_data['username']}")
            print(f"  Password: {user_data['password']}")
            print(f"  Role: {user_data['department'].value}")
        
        print("\n" + "=" * 60)
        print("🔒 Security Note: These are simple credentials for development.")
        print("   Change them in production!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_users()
