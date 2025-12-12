import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def check_counts():
    async with engine.connect() as conn:
        r1 = await conn.execute(text("SELECT count(DISTINCT lot_no) FROM items"))
        items_count = r1.scalar()
        
        r2 = await conn.execute(text("SELECT count(*) FROM lot_quality"))
        quality_count = r2.scalar()
        
        r3 = await conn.execute(text("SELECT count(*) FROM lot_health"))
        health_count = r3.scalar()
        
        print(f"Items (Distinct Lots): {items_count}")
        print(f"Lot Quality Rows: {quality_count}")
        print(f"Lot Health Rows: {health_count}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_counts())
