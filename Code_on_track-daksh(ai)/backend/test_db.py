import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Define the connection string (matching what the backend should use)
DB_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:0001@127.0.0.1:5432/qrtrack')

def test_connection():
    print(f"Testing connection to: {DB_URI}")
    
    try:
        # Create engine
        engine = create_engine(DB_URI)
        
        # Try to connect
        with engine.connect() as connection:
            print("Successfully connected to the database!")
            
            # Run a simple query
            result = connection.execute(text("SELECT 1;"))
            print(f"Query result: {result.scalar()}")
            
            # Check for tables
            result = connection.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"))
            table_count = result.scalar()
            print(f"Found {table_count} tables in public schema.")
            
            if table_count > 0:
                print("Tables found. Database seems populated.")
            else:
                print("WARNING: No tables found in public schema!")

    except OperationalError as e:
        print("\nCRITICAL ERROR: Could not connect to the database.")
        print(f"Error details: {e}")
        print("\nPossible causes:")
        print("1. PostgreSQL service is not running.")
        print("2. Wrong credentials (username/password).")
        print("3. Database 'qrtrack' does not exist.")
        print("4. Firewall blocking port 5432.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    test_connection()
