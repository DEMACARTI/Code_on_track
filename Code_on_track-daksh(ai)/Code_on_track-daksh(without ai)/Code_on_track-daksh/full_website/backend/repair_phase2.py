import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def repair_db():
    print("--- PHASE 2: SQL Repair ---")
    async with engine.begin() as conn:
        # A. Insert missing lot_health rows from lot_quality
        print("Repairing lot_health from lot_quality...")
        # Note: ensuring columns match actual schema. 
        # Using raw SQL as requested.
        sql_health = """
        INSERT INTO lot_health (lot_no, vendor_id, total_items, failed_items, failure_rate, anomaly_score, health_score, risk_level, computed_at)
        SELECT lq.lot_no, lq.vendor_id, lq.total_items, lq.failed_items, lq.failure_rate, lq.anomaly_score,
               GREATEST(0, LEAST(100, ROUND(100 - (lq.failure_rate * 400.0) - (lq.anomaly_score * 40.0) )) )::double precision AS health_score,
               CASE 
                   WHEN (ROUND(100 - (lq.failure_rate * 400.0) - (lq.anomaly_score * 40.0)) <= 33) THEN 'CRITICAL' 
                   WHEN (ROUND(100 - (lq.failure_rate * 400.0) - (lq.anomaly_score * 40.0)) <= 66) THEN 'HIGH' 
                   ELSE 'MEDIUM' 
               END AS risk_level,
               NOW() as computed_at
        FROM lot_quality lq
        WHERE NOT EXISTS (SELECT 1 FROM lot_health lh WHERE lh.lot_no = lq.lot_no);
        """
        # Note: 'CRITICAL'/'HIGH'/'MEDIUM' logic adjusted to match schema/expectations.
        
        try:
            res = await conn.execute(text(sql_health))
            print(f"Inserted {res.rowcount} rows into lot_health.")
        except Exception as e:
            print(f"Error repairing lot_health: {e}")

        # B. Recompute lot_quality from items (Safe idempotent upsert)
        # Postgres supports ON CONFLICT.
        # Check if table has constraints. Assuming lot_no is unique/PK.
        print("Recomputing lot_quality from items...")
        sql_quality = """
        INSERT INTO lot_quality (lot_no, vendor_id, total_items, failed_items, failure_rate, anomaly_score)
        SELECT 
            lot_no, 
            MAX(vendor_id) as vendor_id,
            COUNT(*) AS total_items,
            SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_items,
            ROUND(SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END)::numeric / COUNT(*)::numeric, 4) AS failure_rate,
            ROUND(AVG(0.1 + (CASE WHEN status='failed' THEN 1 ELSE 0 END)*0.2), 3) as anomaly_score
        FROM items 
        GROUP BY lot_no
        ON CONFLICT (lot_no) 
        DO UPDATE SET
            total_items = EXCLUDED.total_items,
            failed_items = EXCLUDED.failed_items,
            failure_rate = EXCLUDED.failure_rate,
            anomaly_score = EXCLUDED.anomaly_score;
        """
        try:
            res = await conn.execute(text(sql_quality))
            print(f"Upserted {res.rowcount} rows in lot_quality.")
        except Exception as e:
            print(f"Error repairing lot_quality: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(repair_db())
