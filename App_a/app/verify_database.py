import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import Item, EngravingQueue, EngravingHistory
from sqlalchemy import inspect

def verify_database():
    """Verify database tables and their structure."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("✓ Database connection successful!\n")
        print(f"Found {len(tables)} tables:\n")
        
        for table in tables:
            print(f"Table: {table}")
            columns = inspector.get_columns(table)
            print("  Columns:")
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"    - {col['name']}: {col_type} {nullable}")
            print()
        
        # Test a simple query
        db = SessionLocal()
        item_count = db.query(Item).count()
        engraving_count = db.query(EngravingQueue).count()
        history_count = db.query(EngravingHistory).count()
        db.close()
        
        print("Current data counts:")
        print(f"  Items: {item_count}")
        print(f"  Engraving Queue: {engraving_count}")
        print(f"  Engraving History: {history_count}")
        
    except Exception as e:
        print(f"Error verifying database: {e}")

if __name__ == "__main__":
    verify_database()
