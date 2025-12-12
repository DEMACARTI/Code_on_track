from app import create_app
from services.db import db
from sqlalchemy import text
import json

def seed():
    app = create_app()
    with app.app_context():
        # Check if empty
        if db.session.execute(text("SELECT COUNT(*) FROM notifications")).scalar() == 0:
            print("Seeding notifications...")
            data = [
                ('system', 'System Ready', 'QR Track system initialized', 'info'),
                ('analysis', 'Analysis Completed', 'Lot quality & health analysis finished', 'info'),
                ('vendor', 'Vendor Alert', 'Vendor RailFast shows high failure rate', 'warning'),
                ('anomaly', 'Anomaly Detected', 'Lot LOT00022 shows abnormal quality deviation', 'danger')
            ]
            
            for type_, title, msg, sev in data:
                # Use simple formatting for the query to ensure no bind param issues with the driver
                # (Safety note: standard app logic uses bind params, this is a controlled seed script)
                metadata_json = json.dumps({"seeded": True})
                sql = text(f"INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at) VALUES ('{type_}', '{title}', '{msg}', '{sev}', FALSE, '{metadata_json}', NOW())")
                db.session.execute(sql)
            
            db.session.commit()
            print("Seeding complete.")
        else:
            print("Table not empty, skipping seed.")

if __name__ == "__main__":
    seed()
