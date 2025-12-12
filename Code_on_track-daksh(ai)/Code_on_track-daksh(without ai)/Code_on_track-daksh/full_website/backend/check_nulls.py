import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def check_nulls():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT COUNT(*) FROM items WHERE lot_no IS NULL OR uid IS NULL OR vendor_id IS NULL"))
        count = res.scalar()
        print(f"Nulls Count: {count}")
        
        if count > 0:
            res_rows = await conn.execute(text("SELECT id, uid, lot_no, vendor_id FROM items WHERE lot_no IS NULL OR uid IS NULL OR vendor_id IS NULL LIMIT 5"))
            for row in res_rows:
                print(row)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_nulls())
