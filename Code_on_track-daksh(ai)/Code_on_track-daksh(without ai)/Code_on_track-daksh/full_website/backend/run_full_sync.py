import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def run_sync():
    print("Running Full Sync...")
    async with engine.connect() as conn:
        # 1. Run Quality Job Logic
        print("Executing Quality Job...")
        sql_quality = """
        INSERT INTO lot_quality (lot_no, vendor_id, component_type, total_items, failed_items, failure_rate, anomaly_score)
        SELECT 
            lot_no, 
            MAX(vendor_id) as vendor_id,
            STRING_AGG(DISTINCT component_type, ', ') as component_type,
            COUNT(*) AS total_items,
            SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_items,
            ROUND(SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END)::numeric / COUNT(*)::numeric, 4) AS failure_rate,
            ROUND(AVG(0.1 + (CASE WHEN status='failed' THEN 1 ELSE 0 END)*0.2), 3) as anomaly_score
        FROM items 
        GROUP BY lot_no
        ON CONFLICT (lot_no) 
        DO UPDATE SET
            vendor_id = EXCLUDED.vendor_id,
            component_type = EXCLUDED.component_type,
            total_items = EXCLUDED.total_items,
            failed_items = EXCLUDED.failed_items,
            failure_rate = EXCLUDED.failure_rate,
            anomaly_score = EXCLUDED.anomaly_score;
        """
        await conn.execute(text(sql_quality))
        await conn.commit()
        
        # 2. Run Health Job Logic (Assuming manual_run_job.py logic)
        print("Executing Health Job...")
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
                ROUND(GREATEST(0, LEAST(100, 
                    100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0) + (random() * 3)
                ))::numeric, 2) AS health_score,
                CASE 
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 40 THEN 'CRITICAL' 
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 70 THEN 'HIGH'
                    WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 85 THEN 'MEDIUM'
                    ELSE 'LOW' 
                END AS risk_level,
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
        print("Sync Complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_sync())
