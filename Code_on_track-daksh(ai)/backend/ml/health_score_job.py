import logging
from sqlalchemy import create_engine, text
import pandas as pd
import datetime
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job():
    """
    Computes health scores for all lots in the database and upserts them into lot_health.
    """
    logger.info("Starting Health Score Job...")
    
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    stats = {
        "processed": 0,
        "upserted": 0,
        "skipped": []
    }

    try:
        with engine.connect() as conn:
            # 1. Fetch all unique lots from items table (and optionally lot_quality for edge cases)
            # For simplicity and correctness, we primarily look at items as the source of truth for lot content.
            # We also join with lot_quality to get anomaly scores.
            
            logger.info("Fetching lot data...")
            
            # This query aggregates data per lot
            query = text("""
                SELECT 
                    i.lot_no,
                    i.component_type,
                    i.vendor_id,
                    COUNT(i.id) as total_items,
                    SUM(CASE WHEN i.status IN ('failed', 'scrapped', 'rejected') THEN 1 ELSE 0 END) as failed_items,
                    AVG(EXTRACT(DAY FROM (NOW() - i.manufacture_date))) as age_days,
                    MAX(lq.anomaly_score) as max_anomaly_score
                FROM items i
                LEFT JOIN lot_quality lq ON i.lot_no = lq.lot_no
                WHERE i.lot_no IS NOT NULL
                GROUP BY i.lot_no, i.component_type, i.vendor_id
            """)
            
            df = pd.read_sql(query, conn)
            
            if df.empty:
                logger.info("No lots found in items table. Nothing to compute.")
                return {"success": True, "message": "No lots found", "stats": stats}

            # 2. Compute Health Scores
            for _, row in df.iterrows():
                lot_no = row['lot_no']
                processed = True
                
                try:
                    total = row['total_items'] or 0
                    failed = row['failed_items'] or 0
                    age = row['age_days'] or 0
                    anomaly_score = row['max_anomaly_score'] or 0.0 # -1 to 1 typically from IsolationForest, assume normalized 0-1 for penalty
                    
                    # Normalize Anomaly Score if it's from IF which is roughly -0.5 to 0.5 centered. 
                    # Let's assume the previous job stored it. If unknown, 0 penalty.
                    # Basic logic:
                    
                    failure_rate = (failed / total) if total > 0 else 0.0
                    
                    # Score Calculation
                    base_score = 100.0
                    
                    # Penalty for failure rate (heavy penalty)
                    # e.g. 10% failure -> -5 points
                    failure_penalty = (failure_rate * 100) * 0.5
                    
                    # Penalty for age (1 year = -10 points)
                    age_penalty = (age / 365.0) * 10.0
                    
                    # Penalty for anomalies (if score > 0.5, mild penalty)
                    # Assuming anomaly_score is 0-1 where 1 is highly anomalous
                    anomaly_penalty = max(0, anomaly_score * 20.0)
                    
                    health_score = base_score - failure_penalty - age_penalty - anomaly_penalty
                    health_score = max(0.0, min(100.0, health_score))
                    
                    # 3. Determine Risk & Action
                    if health_score < 25:
                        risk_level = "CRITICAL"
                        action = "Urgent replacement"
                    elif health_score < 50:
                        risk_level = "HIGH"
                        action = "Inspect soon / schedule"
                    elif health_score < 75:
                        risk_level = "MEDIUM"
                        action = "Monitor"
                    else:
                        risk_level = "LOW"
                        action = "No immediate action"
                    
                    # 4. Upsert
                    upsert_sql = text("""
                        INSERT INTO lot_health (
                            lot_no, component_type, vendor_id, 
                            total_items, failed_items, failure_rate, 
                            health_score, risk_level, recommended_action, 
                            computed_at
                        ) VALUES (
                            :lot_no, :ctype, :vid,
                            :total, :failed, :frate,
                            :score, :risk, :action,
                            NOW()
                        )
                        ON CONFLICT (lot_no) DO UPDATE SET
                            component_type = EXCLUDED.component_type,
                            vendor_id = EXCLUDED.vendor_id,
                            total_items = EXCLUDED.total_items,
                            failed_items = EXCLUDED.failed_items,
                            failure_rate = EXCLUDED.failure_rate,
                            health_score = EXCLUDED.health_score,
                            risk_level = EXCLUDED.risk_level,
                            recommended_action = EXCLUDED.recommended_action,
                            computed_at = NOW();
                    """)
                    
                    conn.execute(upsert_sql, {
                        "lot_no": lot_no,
                        "ctype": row['component_type'],
                        "vid": row['vendor_id'],
                        "total": total,
                        "failed": failed,
                        "frate": failure_rate,
                        "score": health_score,
                        "risk": risk_level,
                        "action": action
                    })
                    
                    stats["processed"] += 1
                    stats["upserted"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing lot {lot_no}: {e}")
                    stats["skipped"].append({"lot_no": lot_no, "reason": str(e)})

            conn.commit()
            logger.info(f"Health Job Completed. Stats: {stats}")
            
    except Exception as e:
        logger.error(f"Critical Job Error: {e}")
        return {"success": False, "message": str(e), "stats": stats}

    return {"success": True, "message": "Job completed successfully", "stats": stats}

if __name__ == "__main__":
    run_job()
