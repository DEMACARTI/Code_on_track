import asyncio
import sys
import os
import json
from datetime import datetime
from sqlalchemy import text
import urllib.request
import urllib.error

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
    
    # 1. DB Checks
    try:
        async with engine.connect() as conn:
            # Counts
            counts = {}
            for query, label in [
                ("SELECT COUNT(*) FROM items", "items_total"),
                ("SELECT COUNT(*) FROM vendors", "vendors_total"),
                ("SELECT COUNT(*) FROM lot_quality", "lot_quality_total"),
                ("SELECT COUNT(*) FROM lot_health", "lot_health_total")
            ]:
                try:
                    res = await conn.execute(text(query))
                    counts[label] = res.scalar()
                except Exception as e:
                    counts[label] = f"Error: {e}"
            results['counts'] = counts

            # Schema
            schemas = {}
            for table in ['items', 'vendors']:
                try:
                    res = await conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """))
                    schemas[table] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
                except Exception as e:
                    schemas[table] = f"Error: {e}"
            results['schemas'] = schemas

            # Sample Rows
            samples = {}
            for table in ['items', 'vendors']:
                try:
                    res = await conn.execute(text(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 10"))
                    samples[table] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
                except Exception as e:
                    samples[table] = f"Error: {e}"
            results['samples'] = samples

            # Null Checks
            null_checks = {}
            try:
                res = await conn.execute(text("SELECT * FROM items WHERE uid IS NULL OR lot_no IS NULL LIMIT 20"))
                null_checks['items_nulls'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                null_checks['items_nulls_error'] = str(e)
            
            try:
                res = await conn.execute(text("SELECT * FROM vendors WHERE name IS NULL LIMIT 20"))
                null_checks['vendors_nulls'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                null_checks['vendors_nulls_error'] = str(e)
            results['null_checks'] = null_checks

    except Exception as e:
        results['db_connection_error'] = str(e)

    # 2. Endpoint Checks (Port 8000 based on previous knowledge, trying 5000 as backup if user insisted)
    endpoints = [
        "http://localhost:8000/items", 
        "http://localhost:8000/items/", 
        "http://localhost:8000/vendors",
        "http://localhost:8000/vendors/"
    ]
    
    api_results = {}
    for url in endpoints:
        try:
             # Set a timeout
            with urllib.request.urlopen(url, timeout=2) as response:
                api_results[url] = {
                    "status": response.status,
                    "preview": str(response.read()[:200])
                }
        except urllib.error.HTTPError as e:
            api_results[url] = f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            api_results[url] = f"Error: {e}"
            
    results['api_checks'] = api_results

    print(json.dumps(results, indent=2, cls=DateTimeEncoder))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostics())
