import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def check():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT count(*) FROM notifications"))
            print(f"Notifications count: {result.scalar()}")
            
            result = await conn.execute(text("SELECT * FROM notifications LIMIT 1"))
            print("First notification:", result.mappings().first())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check())
