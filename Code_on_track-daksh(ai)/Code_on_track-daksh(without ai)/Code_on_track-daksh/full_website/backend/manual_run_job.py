import asyncio
import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
# Import the function references or just logic
# We will just run the SQL logic directly to be sure, or import the router function if feasible.
# Importing router function requires dependency injection mock. simpler to run SQL.

async def run_manual_job():
    print("Running manual health job...")
    try:
        async with engine.connect() as conn:  # Helper script, using connect + execute/commit
             # Copying the SQL from lot_health.py
            sql_health = """
            INSERT INTO lot_health (
                lot_no, component_type, vendor_id, 
                total_items, failed_items, failure_rate, 
                anomaly_score, health_score, risk_level, 
                recommended_action, next_suggested_inspection_date,
                computed_at
            )
            SELECT 
                lq.lot_no, 
                lq.component_type, 
                lq.vendor_id, 
                lq.total_items, 
                lq.failed_items, 
                lq.failure_rate, 
                lq.anomaly_score,
                -- Correct Formula
                ROUND(GREATEST(0, LEAST(100, 
                    100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0) + (random() * 3)
                ))::numeric, 2) AS health_score,
                -- Risk Level
                CASE 
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 40 THEN 'CRITICAL' 
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 70 THEN 'HIGH'
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 85 THEN 'MEDIUM'
                    ELSE 'LOW' 
                END AS risk_level,
                -- Recommended Action
                CASE
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 40 THEN 'Inspect immediately'
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 70 THEN 'Schedule maintenance'
                    ELSE 'Routine check'
                END AS recommended_action,
                (NOW() + INTERVAL '7 days') as next_suggested_inspection_date,
                NOW() as computed_at
            FROM lot_quality lq
            ON CONFLICT (lot_no) 
            DO UPDATE SET
                component_type = EXCLUDED.component_type,
                vendor_id = EXCLUDED.vendor_id,
                total_items = EXCLUDED.total_items,
                failed_items = EXCLUDED.failed_items,
                failure_rate = EXCLUDED.failure_rate,
                anomaly_score = EXCLUDED.anomaly_score,
                health_score = EXCLUDED.health_score,
                risk_level = EXCLUDED.risk_level,
                recommended_action = EXCLUDED.recommended_action,
                next_suggested_inspection_date = EXCLUDED.next_suggested_inspection_date,
                computed_at = EXCLUDED.computed_at;
            """
            await conn.execute(text(sql_health))
            await conn.commit()
            print("Job executed successfully.")
            
            # Verify
            res = await conn.execute(text("SELECT count(*), count(component_type) FROM lot_health"))
            row = res.fetchone()
            print(f"Total Rows: {row[0]}, Rows with Component Type: {row[1]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_manual_job())
