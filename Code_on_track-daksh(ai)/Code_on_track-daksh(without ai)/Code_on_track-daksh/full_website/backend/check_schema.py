import sqlite3

def check_schema():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(items)")
    columns = cursor.fetchall()
    print("Schema for items table:")
    print("cid, name, type, notnull, dflt_value, pk")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
