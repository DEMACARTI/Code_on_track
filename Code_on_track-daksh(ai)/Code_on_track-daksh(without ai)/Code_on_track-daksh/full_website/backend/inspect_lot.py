import asyncio
import sys
import os
from sqlalchemy import text
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def inspect_lot():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM items WHERE lot_no = 'LOT0019'"))
        rows = [dict(zip(res.keys(), row)) for row in res.fetchall()]
        print(json.dumps(rows, indent=2, default=str))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(inspect_lot())
