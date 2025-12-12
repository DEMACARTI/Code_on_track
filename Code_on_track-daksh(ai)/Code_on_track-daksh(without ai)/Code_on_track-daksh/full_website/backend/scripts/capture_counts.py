import asyncio
import json
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def get_counts():
    tables = [
        'items', 'notifications', 'job_schedules', 'item_events', 
        'lot_health', 'users', 'engraving_queue', 
        'engraving_history', 'vendors', 'lot_quality'
    ]
    counts = {}
    async with AsyncSessionLocal() as db:
        for t in tables:
            try:
                result = await db.execute(text(f"SELECT count(*) FROM {t}"))
                counts[t] = result.scalar()
            except Exception as e:
                counts[t] = str(e)
    
    with open("../artifacts/after_reset_counts.json", "w") as f:
        json.dump(counts, f, indent=2)
    print("Snapshot saved to artifacts/after_reset_counts.json")
    print(counts)

if __name__ == "__main__":
    asyncio.run(get_counts())
