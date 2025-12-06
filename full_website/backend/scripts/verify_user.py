import asyncio
import os
import sys
from sqlalchemy import select
from passlib.context import CryptContext

import logging
logging.basicConfig(level=logging.ERROR)

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def verify_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"Total users found: {len(users)}")
        for user in users:
            print(f"User: {user.username}, Role: {user.role}, Hash: {user.password_hash}")
            
            if user.username == "admin":
                 if pwd_context.verify("admin123", user.password_hash):
                    print("Password 'admin123' matches!")
                 else:
                    print("Password 'admin123' DOES NOT match!")

if __name__ == "__main__":
    asyncio.run(verify_user())
