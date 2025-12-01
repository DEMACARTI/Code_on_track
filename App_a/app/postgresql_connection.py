import psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    'dbname': 'irf_dev',
    'user': 'irf_user',
    'password': 'irf_pass',
    'host': 'localhost',
    'port': 5433
}

def test_postgresql_connection():
    try:
        # Establish connection
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Execute a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Database connection successful! PostgreSQL version: {db_version[0]}")

        # Close the cursor and connection
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_postgresql_connection()