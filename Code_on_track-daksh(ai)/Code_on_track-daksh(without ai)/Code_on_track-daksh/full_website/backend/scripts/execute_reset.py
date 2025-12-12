import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

SQL_RESET = """
TRUNCATE TABLE 
    item_events,
    engraving_history, 
    engraving_queue,
    lot_quality, 
    lot_health, 
    notifications,
    items,
    vendors,
    users,
    job_schedules 
    RESTART IDENTITY CASCADE;
"""

async def execute_reset():
    print("WARNING: EXECUTING FULL DB DATA PURGE...")
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text(SQL_RESET))
            await db.commit()
            print("DB Reset Complete (Cascade).")
        except Exception as e:
            print(f"Cascade truncate failed: {e}")
            print("Attempting individual truncates...")
            tables = ["item_events", "engraving_history", "engraving_queue", "lot_quality", "lot_health", "notifications", "items", "vendors", "users", "job_schedules"]
            for t in tables:
                try:
                    await db.execute(text(f"TRUNCATE TABLE {t} CASCADE"))
                    await db.commit()
                    print(f"Truncated {t}")
                except Exception as ex:
                    print(f"Failed to truncate {t}: {ex}")


if __name__ == "__main__":
    asyncio.run(execute_reset())
