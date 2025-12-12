import asyncio
import sys
import os
import json
import urllib.request
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def verify_system():
    results = {
        "db_checks": {},
        "api_responses": {}
    }
    
    # 1. DB Checks
    print("Running DB Checks...")
    async with engine.connect() as conn:
        try:
            # Lots checks
            res_items = await conn.execute(text("SELECT COUNT(DISTINCT lot_no) FROM items"))
            items_lots = res_items.scalar()
            results["db_checks"]["items_distinct_lots"] = items_lots
            
            res_lq = await conn.execute(text("SELECT COUNT(*) FROM lot_quality"))
            lq_count = res_lq.scalar()
            results["db_checks"]["lot_quality_count"] = lq_count
            
            res_lh = await conn.execute(text("SELECT COUNT(*) FROM lot_health"))
            lh_count = res_lh.scalar()
            results["db_checks"]["lot_health_count"] = lh_count
            
        except Exception as e:
            results["db_checks"]["error"] = str(e)

    # 2. API Checks
    print("Running API Checks...")
    endpoints = [
        "/debug/status",
        "/analytics/weekly_defects",
        "/vendors/reliability",
        # "/lot_quality?limit=5", # These might need page/limit params
        # "/lot_health?limit=5"
    ]
    
    base_url = "http://localhost:8000"
    
    for ep in endpoints:
        try:
            with urllib.request.urlopen(f"{base_url}{ep}") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    results["api_responses"][ep] = "OK" # Summary
                    # Store snippet for report if needed
                else:
                    results["api_responses"][ep] = f"Error: {response.status}"
        except Exception as e:
            results["api_responses"][ep] = f"Exception: {e}"

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_system())
