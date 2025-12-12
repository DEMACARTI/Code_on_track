from services.db import db
from sqlalchemy import text
import threading
import time
import atexit
import json
from datetime import datetime

# Lock to ensure only one scheduler thread runs
_scheduler_lock = threading.Lock()
_scheduler_thread = None
_running = False

def check_and_create_notifications(app):
    """Job to check conditions and insert notifications."""
    with app.app_context():
        try:
            # 1. High Risk Lots
            # We fetch candidates first to avoid complex SQL binding issues
            high_risk_lots = db.session.execute(text("SELECT lot_no FROM lot_health WHERE risk_level = 'HIGH'")).fetchall()
            
            for row in high_risk_lots:
                lot_no = row[0]
                # Check if notification already exists for today
                check_sql = text(f"SELECT 1 FROM notifications WHERE type='high_risk' AND metadata->>'lot_no' = '{lot_no}' AND created_at > NOW() - INTERVAL '1 day'")
                if not db.session.execute(check_sql).scalar():
                    meta = json.dumps({"event": "lot_high", "lot_no": lot_no})
                    ins_sql = text(f"INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at) VALUES ('high_risk', 'High-Risk Lot Detected', 'Lot {lot_no} is now HIGH risk.', 'danger', FALSE, '{meta}', NOW())")
                    db.session.execute(ins_sql)

            # 2. Anomalies > 0.20
            anomalies = db.session.execute(text("SELECT lot_no, anomaly_score FROM lot_quality WHERE anomaly_score > 0.20")).fetchall()
            for row in anomalies:
                lot_no = row[0]
                score = round(float(row[1]), 2)
                check_sql = text(f"SELECT 1 FROM notifications WHERE type='anomaly' AND metadata->>'lot_no' = '{lot_no}' AND created_at > NOW() - INTERVAL '1 day'")
                if not db.session.execute(check_sql).scalar():
                    meta = json.dumps({"event": "anomaly", "lot_no": lot_no, "score": score})
                    ins_sql = text(f"INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at) VALUES ('anomaly', 'Anomaly Detected', 'Lot {lot_no} shows anomaly score: {score}', 'warning', FALSE, '{meta}', NOW())")
                    db.session.execute(ins_sql)

            # 3. Item Failures (Limit to recent 50 to avoid massive loops if many failures)
            failures = db.session.execute(text("SELECT uid FROM items WHERE status = 'failed' LIMIT 50")).fetchall()
            for row in failures:
                uid = row[0]
                check_sql = text(f"SELECT 1 FROM notifications WHERE type='failure' AND metadata->>'uid' = '{uid}'")
                if not db.session.execute(check_sql).scalar():
                    meta = json.dumps({"event": "failure", "uid": uid})
                    # Use unique ID check to avoid spam
                    ins_sql = text(f"INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at) VALUES ('failure', 'Item Failure Detected', 'Item {uid} failed inspection.', 'danger', FALSE, '{meta}', NOW())")
                    db.session.execute(ins_sql)

            # 4. Daily Summmary
            check_daily = text("SELECT 1 FROM notifications WHERE type='system' AND title='System Health Check' AND created_at::date = NOW()::date")
            if not db.session.execute(check_daily).scalar():
                meta = json.dumps({"event": "daily_summary"})
                start_msg = "Daily system health check complete. All services running."
                ins_sql = text(f"INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at) VALUES ('system', 'System Health Check', '{start_msg}', 'info', FALSE, '{meta}', NOW())")
                db.session.execute(ins_sql)

            db.session.commit()
        except Exception as e:
            print(f"Scheduler Error: {e}")
            db.session.rollback()

def run_scheduler(app):
    global _running
    _running = True
    print("Scheduler started.")
    while _running:
        check_and_create_notifications(app)
        time.sleep(60)

def start_scheduler(app):
    global _scheduler_thread
    with _scheduler_lock:
        if _scheduler_thread is None:
            _scheduler_thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
            _scheduler_thread.start()
            
            def stop_scheduler():
                global _running
                _running = False
            
            atexit.register(stop_scheduler)


