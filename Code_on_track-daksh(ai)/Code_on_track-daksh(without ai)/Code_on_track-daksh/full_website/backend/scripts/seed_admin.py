
import asyncio
import sys
import os
from sqlalchemy import select

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
print(f"DEBUG: Connecting to {engine.url}")
from app.models.user import WebsiteUser, UserRole
from app.auth.security import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_admin():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if admin exists
        stmt = select(WebsiteUser).where(WebsiteUser.username == "admin")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            print("Admin user already exists.")
            # Optional: reset password if needed
            # user.password_hash = get_password_hash("Admin@123")
            # await session.commit()
            # print("Admin password reset.")
        else:
            print("Creating admin user...")
            new_user = WebsiteUser(
                username="admin",
                email="admin@railchinh.com",
                password_hash=get_password_hash("Admin@123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            print("Admin user created successfully.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_admin())
