import asyncio
import sys
import os
from sqlalchemy import text
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

# Disable sqlalchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def check_schema():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM items LIMIT 1"))
        keys = res.keys()
        print(f"Items Columns: {list(keys)}")
        row = res.fetchone()
        print(f"Sample Row: {dict(zip(keys, row))}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_schema())
