from sqlalchemy import text
import sys
import os

# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def init_db():
    app = create_app()
    with app.app_context():
        print("Creating inspection_reports table...")
        sql = text("""
            CREATE TABLE IF NOT EXISTS inspection_reports (
                id SERIAL PRIMARY KEY,
                uid TEXT REFERENCES items(uid),
                lot_no TEXT,
                issue TEXT,
                confidence FLOAT,
                severity TEXT,
                recommended_action TEXT,
                image_base64 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        try:
            db.session.execute(sql)
            db.session.commit()
            print("Table created successfully.")
        except Exception as e:
            print(f"Error creating table: {e}")
            db.session.rollback()

if __name__ == "__main__":
    init_db()
