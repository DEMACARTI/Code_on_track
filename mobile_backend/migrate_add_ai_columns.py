"""
Database migration to add AI classification columns to inspections table
Run this script to update the database schema
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def add_ai_columns():
    """Add ai_classification and ai_confidence columns if they don't exist"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking inspections table...")
        
        # Check if columns exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='inspections' 
            AND column_name IN ('ai_classification', 'ai_confidence');
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        # Add ai_classification if missing
        if 'ai_classification' not in existing_columns:
            print("Adding ai_classification column...")
            cur.execute("""
                ALTER TABLE inspections 
                ADD COLUMN ai_classification VARCHAR(50);
            """)
            print("✅ Added ai_classification column")
        else:
            print("✓ ai_classification column already exists")
        
        # Add ai_confidence if missing
        if 'ai_confidence' not in existing_columns:
            print("Adding ai_confidence column...")
            cur.execute("""
                ALTER TABLE inspections 
                ADD COLUMN ai_confidence FLOAT;
            """)
            print("✅ Added ai_confidence column")
        else:
            print("✓ ai_confidence column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add AI Classification Columns")
    print("=" * 60)
    add_ai_columns()
