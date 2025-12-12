from sqlalchemy import text
from services.db import db
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, date

def run_anomaly_job():
    """
    Analyzes item data to detect anomalous lots and updates the lot_quality table.
    """
    print(f"[{datetime.now()}] Starting ML Anomaly Job...")
    
    # 1. Fetch data aggregated by lot
    sql = text("""
        SELECT 
            lot_no,
            vendor_id,
            COUNT(*) as total_items,
            SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed_items,
            MIN(manufacture_date) as oldest_date,
            MAX(manufacture_date) as newest_date,
            string_agg(DISTINCT component_type, ', ') as component_types
        FROM items
        WHERE lot_no IS NOT NULL
        GROUP BY lot_no, vendor_id
    """)
    
    try:
        # Use pandas to read SQL directly
        # Note: db.session.connection() is needed for pandas read_sql
        conn = db.session.connection()
        df = pd.read_sql(sql, conn)
        
        if df.empty:
            print("No data found for anomaly detection.")
            return {"status": "skipped", "reason": "no data"}
            
        print(f"Loaded {len(df)} lots for analysis.")
        
        # 2. Feature Engineering
        # failure_rate
        df['failure_rate'] = df['failed_items'] / df['total_items']
        
        # age & recency
        today = pd.to_datetime(date.today())
        
        # Convert date columns to datetime
        df['oldest_date'] = pd.to_datetime(df['oldest_date'])
        df['newest_date'] = pd.to_datetime(df['newest_date'])
        
        df['age_days'] = (today - df['oldest_date']).dt.days
        df['recency_days'] = (today - df['newest_date']).dt.days
        
        # Fill NaNs if any (e.g. if dates are missing, though query filters null lots)
        df.fillna(0, inplace=True)
        
        # Select Features for Model
        features = ['total_items', 'failed_items', 'failure_rate', 'age_days', 'recency_days']
        X = df[features]
        
        # 3. Train Model (Isolation Forest)
        # contamination=0.05 means we expect roughly 5% anomalies
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X)
        
        # Predict: -1 for outliers, 1 for inliers
        df['anomaly_pred'] = model.predict(X)
        # Decision function: lower scores are more anomalous (negative)
        df['anomaly_score'] = model.decision_function(X)
        
        # 4. Generate Reasons & Flags
        # Standardize score: The prompt says "is_anomalous = anomaly_score < threshold (-0.1)"
        # IsolationForest decision_function returns negative for anomalies depending on threshold offset
        # But 'predict' already uses the threshold.
        # Let's trust 'predict' == -1 is anomalous, or refine with score.
        # We will follow the prompt logic: use score directly.
        
        THRESHOLD = -0.1
        df['is_anomalous'] = df['anomaly_score'] < THRESHOLD
        
        def generate_reason(row):
            reasons = []
            if row['failure_rate'] > 0.10:
                reasons.append("High failure rate")
            if row['age_days'] < 30 and row['total_items'] > 0:
                reasons.append("Very new lot")
            if row['total_items'] < 5:
                reasons.append("Low sample size")
            if row['is_anomalous']:
                reasons.append("Statistical anomaly detected")
                
            return "; ".join(reasons) if reasons else None

        df['reason'] = df.apply(generate_reason, axis=1)
        
        # 5. UPSERT into lot_quality
        # We iterate and insert. For bulk upsert efficient logic is needed but loop is fine for <1000 lots.
        
        updated_count = 0
        for _, row in df.iterrows():
            # SQL for UPSERT
            upsert_sql = text("""
                INSERT INTO lot_quality (
                    lot_no, component_type, vendor_id, 
                    total_items, failed_items, failure_rate,
                    anomaly_score, is_anomalous, reason, 
                    last_updated
                ) VALUES (
                    :lot_no, :comp_type, :vendor_id,
                    :total, :failed, :rate,
                    :score, :is_anom, :reason,
                    NOW()
                )
                ON CONFLICT (lot_no) DO UPDATE SET
                    component_type = EXCLUDED.component_type,
                    vendor_id = EXCLUDED.vendor_id,
                    total_items = EXCLUDED.total_items,
                    failed_items = EXCLUDED.failed_items,
                    failure_rate = EXCLUDED.failure_rate,
                    anomaly_score = EXCLUDED.anomaly_score,
                    is_anomalous = EXCLUDED.is_anomalous,
                    reason = EXCLUDED.reason,
                    last_updated = EXCLUDED.last_updated
            """)
            
            db.session.execute(upsert_sql, {
                "lot_no": row['lot_no'],
                "comp_type": row['component_types'], # Taking aggregated string
                "vendor_id": row['vendor_id'],
                "total": int(row['total_items']),
                "failed": int(row['failed_items']),
                "rate": float(row['failure_rate']),
                "score": float(row['anomaly_score']),
                "is_anom": bool(row['is_anomalous']),
                "reason": row['reason']
            })
            updated_count += 1
            
        db.session.commit()
        print(f"Successfully updated {updated_count} lots.")
        return {"status": "success", "updated_rows": updated_count}
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in anomaly job: {e}")
        return {"status": "error", "message": str(e)}
