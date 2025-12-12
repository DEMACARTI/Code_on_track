import os
import sqlalchemy
from sqlalchemy import text
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def apply_sql_file(conn, filepath):
    print(f"Applying {os.path.basename(filepath)}...")
    with open(filepath, 'r') as f:
        sql_commands = f.read()
    try:
        conn.execute(text(sql_commands))
        print("Success.")
    except Exception as e:
        print(f"Error: {e}")
        # Don't exit, try next

def run_migration():
    print(f"Connecting to {config.SQLALCHEMY_DATABASE_URI}...")
    engine = sqlalchemy.create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    # List of migrations to run
    migrations = [
        'create_lot_health.sql',
        'add_reason_to_lot_quality.sql',
        'add_last_updated_to_lot_quality.sql'
    ]
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for m in migrations:
                fpath = os.path.join(os.path.dirname(__file__), 'db', 'migrations', m)
                if os.path.exists(fpath):
                    apply_sql_file(conn, fpath)
            trans.commit()
            print("All migrations applied.")
        except Exception as e:
            trans.rollback()
            print(f"Migration transaction failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_migration()
