import sys
import os
from sqlalchemy import text
from app import create_app
from services.db import db
import time

def setup_notifications():
    app = create_app()
    with app.app_context():
        print("Checking 'notifications' table...")
        
        try:
            # 1. Check if exists
            check_sql = text("SELECT to_regclass('public.notifications')")
            exists = db.session.execute(check_sql).scalar()
            
            if not exists:
                print("Table 'notifications' NOT FOUND. Creating...")
                create_sql = text("""
                    CREATE TABLE notifications (
                        id SERIAL PRIMARY KEY,
                        type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        severity TEXT DEFAULT 'info',
                        read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                db.session.execute(create_sql)
                print("Table created.")
            else:
                print("Table 'notifications' exists.")
                
            # 2. Check for columns
            required_cols = ['type', 'title', 'message', 'severity', 'read', 'created_at']
            get_cols_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='notifications'")
            existing_cols = {row[0] for row in db.session.execute(get_cols_sql).fetchall()}
            
            for col in required_cols:
                if col not in existing_cols:
                    print(f"Missing column '{col}'. Adding...")
                    db.session.execute(text(f"ALTER TABLE notifications ADD COLUMN {col} TEXT")) # Simplified TEXT for patch
            
            db.session.commit()
            
            # 3. Seed if empty
            count_sql = text("SELECT COUNT(*) FROM notifications")
            count = db.session.execute(count_sql).scalar()
            if count == 0:
                print("Table empty. Seeding sample data...")
                seed_sql = text("""
                    INSERT INTO notifications (type, title, message, severity, read)
                    VALUES
                    ('system', 'System Ready', 'QR Track System successfully initialized', 'info', FALSE),
                    ('analysis', 'Analysis Completed', 'Lot quality & health analysis finished', 'info', FALSE),
                    ('vendor', 'Vendor Alert', 'Vendor RailFast shows high failure rate trend', 'warning', FALSE),
                    ('anomaly', 'Anomaly Detected', 'Lot LOT00022 shows abnormal quality deviation', 'danger', FALSE);
                """)
                db.session.execute(seed_sql)
                db.session.commit()
                print("Seeded.")
            else:
                print(f"Table has {count} notifications.")
                
            print("DONE. Verification complete.")
            
        except Exception as e:
            print(f"ERROR: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_notifications()
