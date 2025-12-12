import os
import sys
from sqlalchemy import text
from app import create_app
from services.db import db

def run_migration():
    app = create_app()
    with app.app_context():
        try:
            print("Checking 'notifications' table schema...")
            
            # 1. Create table if not exists (User's Schema)
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata JSONB,
                    severity TEXT DEFAULT 'info',
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
                )
            """)
            db.session.execute(create_sql)
            
            # 2. Alter table to ensure columns exist (Idempotent)
            # We check for missing columns and add them.
            required_columns = {
                "metadata": "JSONB",
                "is_read": "BOOLEAN DEFAULT FALSE",
                "severity": "TEXT DEFAULT 'info'"
            }
            
            for col, dtype in required_columns.items():
                check_col = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='notifications' AND column_name='{col}'")
                if not db.session.execute(check_col).scalar():
                    print(f"Adding missing column: {col}")
                    db.session.execute(text(f"ALTER TABLE notifications ADD COLUMN {col} {dtype}"))
            
            # 3. Handle 'read' vs 'is_read' legacy
            # If 'read' exists but 'is_read' was just added, copy data
            check_read = text("SELECT column_name FROM information_schema.columns WHERE table_name='notifications' AND column_name='read'")
            if db.session.execute(check_read).scalar():
                print("Migrating 'read' data to 'is_read'...")
                db.session.execute(text("UPDATE notifications SET is_read = read WHERE is_read IS FALSE AND read IS NOT NULL"))
            
            db.session.commit()
            
            # 4. Report Final Structure
            final_cols_sql = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications'")
            cols = db.session.execute(final_cols_sql).fetchall()
            print("\nFinal Schema:")
            for c in cols:
                print(f" - {c[0]} ({c[1]})")
                
            # 5. Report Row Count
            count = db.session.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
            print(f"\nTotal Notifications: {count}")
            
        except Exception as e:
            print(f"Migration Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
