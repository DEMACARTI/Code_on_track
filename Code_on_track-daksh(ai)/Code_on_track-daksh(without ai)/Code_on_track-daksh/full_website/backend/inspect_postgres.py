import asyncio
import sys
import os
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Add the parent directory to sys.path to make app module importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

async def inspect_db():
    print(f"Connecting to: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    try:
        async with engine.connect() as conn:
            # Postgres specific query to list tables
            result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            print("\nFound Tables:")
            if not tables:
                print("No tables found.")
            for table in tables:
                print(f"- {table[0]}")
            
            # Check row count for 'items' if it exists
            table_names = [t[0] for t in tables]
            if 'items' in table_names:
                 res = await conn.execute(text("SELECT count(*) FROM items"))
                 print(f"\nItems count: {res.scalar()}")
            else:
                 print("\n'items' table NOT found!")

    except Exception as e:
        print("Connection failed!")
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(inspect_db())
