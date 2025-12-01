import sys
import os
import psycopg2

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration
DB_CONFIG = {
    'dbname': 'irf_dev',
    'user': 'irf_user',
    'password': 'irf_pass',
    'host': 'localhost',
    'port': 5433
}

def check_enum_values():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Query to get enum type values
        cursor.execute("""
            SELECT e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname = 'engravingstatus'
            ORDER BY e.enumsortorder;
        """)
        
        enum_values = cursor.fetchall()
        print("Enum values for 'engravingstatus':")
        for value in enum_values:
            print(f"  - {value[0]}")

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_enum_values()
