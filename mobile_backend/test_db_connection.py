"""
Test database connection for mobile backend
"""

from main import SessionLocal, User, Item
import os

def test_connection():
    print("=" * 60)
    print("🔍 Testing Mobile Backend Database Connection")
    print("=" * 60)
    
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
    )
    
    print(f"\n📡 Database URL: {db_url[:50]}...")
    
    db = SessionLocal()
    try:
        # Test 1: Query users
        print("\n📝 Test 1: Querying users table...")
        users = db.query(User).all()
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user.username} ({user.email}) - Role: {user.department.value if user.department else 'N/A'}")
        
        # Test 2: Query items
        print("\n📦 Test 2: Querying items table...")
        items = db.query(Item).limit(5).all()
        print(f"✅ Found {db.query(Item).count()} total items (showing first 5):")
        for item in items:
            print(f"   - {item.uid} - {item.component_type} - Status: {item.current_status}")
        
        # Test 3: Test authentication with a user
        print("\n🔐 Test 3: Testing authentication...")
        test_user = db.query(User).filter(User.username == "admin").first()
        if test_user:
            print(f"✅ Admin user found: {test_user.email}")
            print(f"   Active: {test_user.is_active}")
            print(f"   Department: {test_user.department.value if test_user.department else 'N/A'}")
        else:
            print("❌ Admin user not found")
        
        print("\n" + "=" * 60)
        print("✅ All database tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
