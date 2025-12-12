
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import text
from app.db.session import engine

async def check_item():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT * FROM items LIMIT 1"))
            # result.keys() returns columns
            print(f"Columns: {result.keys()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_item())
