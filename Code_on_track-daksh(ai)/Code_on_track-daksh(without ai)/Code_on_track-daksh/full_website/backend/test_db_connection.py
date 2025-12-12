
import asyncio
import sys
import os

# Add the parent directory to sys.path to make app module importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

async def test_connection():
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("âœ… Connection successful!")
            print(f"Result: {result.scalar()}")
    except Exception as e:
        print("âŒ Connection failed!")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_connection())
