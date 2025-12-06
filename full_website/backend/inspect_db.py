import sqlite3

def inspect_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    # If users table exists, show columns
    if ('users',) in tables:
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("\nUsers table columns:")
        for col in columns:
            print(col)
            
    conn.close()

if __name__ == "__main__":
    inspect_db()
