import asyncio
import sys
import os
from sqlalchemy.schema import CreateTable

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.db.base_class import Base
# Make sure to import all models so they are registered in Base
from app.models import user, item, vendor, notification, inspection, engraving

async def create_tables():
    print("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_tables())
