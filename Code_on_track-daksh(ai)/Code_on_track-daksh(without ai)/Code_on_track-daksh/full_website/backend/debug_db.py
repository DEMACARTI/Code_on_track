import sqlite3

def debug():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    print("--- SCHEMA ---")
    for row in cursor.execute("PRAGMA table_info(items)"):
        print(row)
    
    print("\n--- RAW INSERT ---")
    try:
        # Assuming vendor_id 1 exists from previous successful seed run
        cursor.execute("""
            INSERT INTO items (uid, component_type, lot_number, vendor_id, quantity, current_status)
            VALUES ('TEST-RAW', 'RAW', 'LOT00', 1, 5, 'manufactured')
        """)
        conn.commit()
        print("Raw insert successful")
    except Exception as e:
        print(f"Raw insert failed: {e}")

    conn.close()

if __name__ == "__main__":
    debug()
