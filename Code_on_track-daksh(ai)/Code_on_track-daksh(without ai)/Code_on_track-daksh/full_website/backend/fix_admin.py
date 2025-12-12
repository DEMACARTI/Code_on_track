
import asyncio
import sys
import os
from passlib.context import CryptContext

# Add current dir to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.user import WebsiteUser, UserRole
from sqlalchemy import select, delete

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def fix_admin():
    async with AsyncSessionLocal() as session:
        # Check existing admin
        result = await session.execute(select(WebsiteUser).where(WebsiteUser.username == "admin"))
        user = result.scalar_one_or_none()
        
        if user:
            print("Admin exists. Updating password...")
            user.password_hash = pwd_context.hash("admin")
            user.role = UserRole.ADMIN
        else:
            print("Admin missing. Creating...")
            user = WebsiteUser(
                username="admin",
                password_hash=pwd_context.hash("admin"),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(user)
        
        await session.commit()
        print("Admin user fixed: admin/admin")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_admin())
