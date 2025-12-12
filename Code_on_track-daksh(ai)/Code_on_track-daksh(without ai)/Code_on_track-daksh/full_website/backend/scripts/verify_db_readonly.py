
import asyncio
import sys
import os
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def verify_db():
    results = {
        "database_url": settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, "***") if settings.POSTGRES_PASSWORD else settings.DATABASE_URL,
        "counts": {},
        "samples": {},
        "errors": []
    }

    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            # Counts
            tables = ["items", "vendors", "lot_quality", "lot_health"]
            for table in tables:
                try:
                    res = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    results["counts"][f"{table}_count"] = res.scalar()
                except Exception as e:
                    results["errors"].append(f"Error counting {table}: {str(e)}")

            # Samples
            queries = {
                "items": "SELECT id, uid, status, lot_no, type FROM items ORDER BY id ASC LIMIT 5",
                "vendors": "SELECT id, name, vendor_code FROM vendors ORDER BY id ASC LIMIT 5",
                "lot_quality": "SELECT id, lot_no, vendor_id, total_items, failed_items, failure_rate FROM lot_quality ORDER BY id ASC LIMIT 5"
            }

            for name, query in queries.items():
                try:
                    res = await conn.execute(text(query))
                    rows = [dict(row._mapping) for row in res]
                    # Convert UUIDs/dates to strings for JSON serialization
                    for row in rows:
                        for k, v in row.items():
                            if not isinstance(v, (str, int, float, bool, type(None))):
                                row[k] = str(v)
                    results["samples"][name] = rows
                except Exception as e:
                     results["errors"].append(f"Error sampling {name}: {str(e)}")

    except Exception as e:
        results["errors"].append(f"Connection error: {str(e)}")

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_db())
