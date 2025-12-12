import sys
import os

# Add parent directory to path to allow importing from backend
# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print(f"Added to path: {backend_dir}")
try:
    from app import app
    from services.db import db
except ImportError as e:
    # Try importing with package prefix if running as module
    from backend.app import app
    from backend.services.db import db
from sqlalchemy import text

def fix_notifications_db():
    print("Checking 'notifications' table...")
    
    with app.app_context():
        # Check if table exists
        check_table_sql = text("SELECT to_regclass('public.notifications')")
        table_exists = db.session.execute(check_table_sql).scalar()
        
        if not table_exists:
            print("Table 'notifications' does not exist. Creating...")
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
            db.session.commit()
            print("Table created successfully.")
            
            # Seed initial data
            print("Seeding initial data...")
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
            print("Seeded successfully.")
            
        else:
            print("Table 'notifications' exists. Checking columns...")
            # Check for 'read' column (common missing column in migrations)
            check_col_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='notifications' AND column_name='read'")
            col_exists = db.session.execute(check_col_sql).scalar()
            
            if not col_exists:
                print("Adding missing column 'read'...")
                db.session.execute(text("ALTER TABLE notifications ADD COLUMN read BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                print("Column added.")
            else:
                print("Schema looks correct.")

if __name__ == "__main__":
    fix_notifications_db()
