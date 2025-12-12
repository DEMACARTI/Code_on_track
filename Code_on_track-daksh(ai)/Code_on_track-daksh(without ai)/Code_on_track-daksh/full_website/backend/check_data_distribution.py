import asyncio
import logging
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

# Disable all logging
logging.disable(logging.CRITICAL)

async def check_data_distribution():
    async with AsyncSessionLocal() as db:
        print("--- LOT HEALTH RISK DISTRIBUTION ---")
        query = text("SELECT risk_level, count(*) as count, count(DISTINCT lot_no) as unique_lots FROM lot_health GROUP BY risk_level")
        result = await db.execute(query)
        for row in result:
            print(f"Risk: {row.risk_level}, Count: {row.count}, Unique: {row.unique_lots}")

        print("\n--- ITEM STATUS DISTRIBUTION ---")
        query_items = text("SELECT status, count(*) FROM items GROUP BY status")
        result_items = await db.execute(query_items)
        for row in result_items:
            print(f"Status: {row.status}, Count: {row.count}")

if __name__ == "__main__":
    asyncio.run(check_data_distribution())
