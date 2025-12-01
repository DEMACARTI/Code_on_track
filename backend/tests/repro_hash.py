from app.auth.security import get_password_hash, pwd_context
import bcrypt

try:
    print(f"Passlib schemes: {pwd_context.schemes()}")
    print("Hashing 'password123'...")
    print(f"Length: {len('password123')}")
    
    # Try raw bcrypt
    salt = bcrypt.gensalt()
    print(f"Raw bcrypt hash: {bcrypt.hashpw(b'password123', salt)}")

    hash = get_password_hash("password123")
    print(f"Hash: {hash}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
