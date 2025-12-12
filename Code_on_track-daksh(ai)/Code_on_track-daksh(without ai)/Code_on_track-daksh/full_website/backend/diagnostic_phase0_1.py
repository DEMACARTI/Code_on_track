import asyncio
import sys
import os
import json
import datetime
from sqlalchemy import text, inspect

sys.path.append(os.getcwd())
from app.db.session import engine, AsyncSessionLocal

async def run_diagnostics():
    timestamp = datetime.datetime.now().isoformat().replace(":", "-")
    snapshot_path = f"diagnostic_db_snapshot_{timestamp}.json"
    
    diagnostic_data = {
        "snapshot_path": snapshot_path,
        "timestamp": timestamp,
        "db_schema": {},
        "counts": {},
        "missing_mappings": {},
        "backend_routes": [],
        "scheduler_jobs": [],
        "frontend_components": [],
        "diagnostic_summary": ""
    }

    # PHASE 0: Sanity & Backup
    print("--- PHASE 0: DB Snapshot ---")
    try:
        async with engine.connect() as conn:
            # List tables and row counts
            tables = ['items', 'lot_quality', 'lot_health', 'vendors', 'notifications', 'history']
            for table in tables:
                try:
                    # Check if table exists
                    exists = await conn.execute(text(f"SELECT to_regclass('public.{table}')"))
                    if exists.scalar():
                        # Row count
                        rc = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = rc.scalar()
                        diagnostic_data["counts"][f"{table}_count"] = count
                        
                        # Schema
                        # In async sqlalchemy, reflection is tricky. Using information_schema check.
                        cols = await conn.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'"))
                        diagnostic_data["db_schema"][table] = [dict(row._mapping) for row in cols]
                    else:
                        diagnostic_data["counts"][f"{table}_count"] = "MISSING"
                except Exception as e:
                    print(f"Error checking table {table}: {e}")

            # Safe DB backup command (just recording it)
            # Assuming connection string is available in environment or config
            print("To backup run: pg_dump -U postgres -h localhost -p 5432 qrtrack > qrtrack_backup.sql")

    except Exception as e:
        print(f"DB Connection Error: {e}")
        diagnostic_data["diagnostic_summary"] = f"DB Connection Failed: {e}"
        print(json.dumps(diagnostic_data, indent=2))
        return

    # PHASE 1: Diagnostic Checks
    print("--- PHASE 1: Diagnostic Queries ---")
    async with engine.connect() as conn:
        try:
            # 1. DB Checks
            if diagnostic_data["counts"].get("items_count") != "MISSING":
                # Distinct Lots
                res = await conn.execute(text("SELECT COUNT(DISTINCT lot_no) FROM items"))
                diagnostic_data["counts"]["items_lots"] = res.scalar()
                
                # Check mapping gaps
                # Missing in lot_quality
                missing_lq = await conn.execute(text("""
                    SELECT DISTINCT i.lot_no FROM items i
                    LEFT JOIN lot_quality lq ON i.lot_no = lq.lot_no
                    WHERE lq.lot_no IS NULL LIMIT 20
                """))
                diagnostic_data["missing_mappings"]["items_without_lot_quality"] = missing_lq.scalars().all()
                
                # Missing in lot_health using items as base (or lot_quality as base per prompt inverse)
                # "Do the inverse: lot_quality rows missing in lot_health"
                missing_lh = await conn.execute(text("""
                    SELECT lq.lot_no FROM lot_quality lq
                    LEFT JOIN lot_health lh ON lq.lot_no = lh.lot_no
                    WHERE lh.lot_no IS NULL LIMIT 20
                """))
                diagnostic_data["missing_mappings"]["lot_quality_without_lot_health"] = missing_lh.scalars().all()

            # 2. Backend Code Search (Simulated for this script, I will do it via tools separately mostly, 
            # but can try to walk directory here if I want. I will leave it empty in script and fill via agent inspection)
            
            # 3. Scheduler & ML Jobs
            # (Agent will inspect files)

            # 4. Frontend 
            # (Agent will inspect files)
            
        except Exception as e:
            print(f"Error running diagnostic queries: {e}")

    # Save Snapshot
    with open(snapshot_path, "w") as f:
        json.dump(diagnostic_data, f, indent=2, default=str)
    
    print(f"Snapshot saved to {snapshot_path}")
    print("Diagnostic Data Summary:")
    print(json.dumps(diagnostic_data, indent=2, default=str))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostics())
