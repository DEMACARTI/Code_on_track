
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import text
from app.db.session import engine

async def check_schema():
    print("Checking schema...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'items'"))
            columns = [row[0] for row in result.fetchall()]
            print("Columns found:")
            for c in columns:
                print(f"- {c}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
