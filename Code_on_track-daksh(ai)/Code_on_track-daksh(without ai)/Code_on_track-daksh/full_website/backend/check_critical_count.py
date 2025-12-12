import asyncio
import logging
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

# Disable sqlalchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def check_critical_count():
    async with AsyncSessionLocal() as db:
        # Check specific count used in analytics
        query = text("SELECT count(DISTINCT lot_no) FROM lot_health WHERE risk_level = 'CRITICAL'")
        result = await db.execute(query)
        count = result.scalar()
        print(f"COUNT_RESULT: {count}")
        
        # Check raw rows
        query_all = text("SELECT lot_no FROM lot_health WHERE risk_level = 'CRITICAL'")
        result_all = await db.execute(query_all)
        rows = result_all.fetchall()
        unique_lots = set(r[0] for r in rows)
        print(f"UNIQUE_LOTS: {len(unique_lots)}")
        print(f"RAW_ROWS: {len(rows)}")

if __name__ == "__main__":
    asyncio.run(check_critical_count())
