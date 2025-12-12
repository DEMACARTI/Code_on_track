from sqlalchemy import create_engine, inspect

# Hardcoded for reliability
db_url = "postgresql://postgres:0001@127.0.0.1/qrtrack"

print(f"Connecting to {db_url}...")
try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    columns = inspector.get_columns('lot_quality')

    print("--- Lot Quality Table Columns ---")
    for col in columns:
        print(f"{col['name']} ({col['type']})")
    print("---------------------------------")
except Exception as e:
    print(f"Error: {e}")
