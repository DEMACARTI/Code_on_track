from app import create_app
from services.db import db
from sqlalchemy import text

def inspect():
    app = create_app()
    with app.app_context():
        # List tables
        print("--- Tables ---")
        tables = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        for t in tables:
            print(f"- {t[0]}")
            # List columns for each table
            cols = db.session.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{t[0]}'")).fetchall()
            for c in cols:
                print(f"  - {c[0]} ({c[1]})")

if __name__ == "__main__":
    inspect()
