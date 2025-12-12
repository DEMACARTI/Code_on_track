import asyncio
import sys
import os
import json
from datetime import datetime
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def run_diagnostics():
    results = {}
    try:
        async with engine.connect() as conn:
            # 1. Row counts
            counts = {}
            for table in ['lot_quality', 'lot_health', 'items']:
                try:
                    query = f"SELECT count(*) FROM {table}"
                    if table == 'items':
                        query = "SELECT count(DISTINCT lot_no) FROM items"
                    res = await conn.execute(text(query))
                    counts[table] = res.scalar()
                except Exception as e:
                    counts[table] = f"Error: {e}"
            results['row_counts'] = counts

            # 2. Schema
            schemas = {}
            for table in ['lot_quality', 'lot_health']:
                try:
                    res = await conn.execute(text(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND table_schema = 'public'
                    """))
                    schemas[table] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
                except Exception as e:
                    schemas[table] = f"Error: {e}"
            results['schemas'] = schemas

            # 3. Samples
            samples = {}
            for table in ['lot_quality', 'lot_health']:
                try:
                    res = await conn.execute(text(f"SELECT * FROM {table} LIMIT 10"))
                    samples[table] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
                except Exception as e:
                    samples[table] = f"Error: {e}"
            results['samples'] = samples

    except Exception as e:
        results['connection_error'] = str(e)

    print(json.dumps(results, indent=2, cls=DateTimeEncoder))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostics())
