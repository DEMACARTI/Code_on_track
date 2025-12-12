import asyncio
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

from app.db.session import engine, AsyncSessionLocal
from app.db.base_class import Base
from app.models.user import WebsiteUser, UserRole
from app.models.vendor import Vendor
from app.models.item import Item
from app.models.notification import Notification
from app.auth.security import get_password_hash

async def init_db():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    async with AsyncSessionLocal() as session:
        print("Creating admin user...")
        admin = WebsiteUser(
            email="admin@example.com",
            username="admin",
            password_hash=get_password_hash("admin"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("Admin user created (admin/admin).")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_db())
