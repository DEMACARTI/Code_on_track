
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import text
from app.db.session import engine

async def check_status():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT distinct status FROM items"))
            statuses = [row[0] for row in result.fetchall()]
            print(f"Statuses: {statuses}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_status())
