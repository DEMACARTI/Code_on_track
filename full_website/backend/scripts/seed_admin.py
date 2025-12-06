# backend/scripts/seed_admin.py
# Purpose: Seed database with initial users
# Author: Antigravity

import asyncio
import os
import sys
from passlib.context import CryptContext
from sqlalchemy import select

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    viewer_username = os.getenv("VIEWER_USERNAME", "viewer")
    viewer_password = os.getenv("VIEWER_PASSWORD", "viewer123")

    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == admin_username))
        if not result.scalar_one_or_none():
            admin = User(
                username=admin_username,
                password_hash=get_password_hash(admin_password),
                role=UserRole.ADMIN,
                email="admin@example.com"
            )
            session.add(admin)
            print(f"Created Admin: {admin_username} / {'*' * len(admin_password)}")
        else:
            print(f"Admin {admin_username} already exists")

        # Check if viewer exists
        result = await session.execute(select(User).where(User.username == viewer_username))
        if not result.scalar_one_or_none():
            viewer = User(
                username=viewer_username,
                password_hash=get_password_hash(viewer_password),
                role=UserRole.VIEWER,
                email="viewer@example.com"
            )
            session.add(viewer)
            print(f"Created Viewer: {viewer_username} / {'*' * len(viewer_password)}")
        else:
            print(f"Viewer {viewer_username} already exists")

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
