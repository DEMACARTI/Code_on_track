from sqlalchemy import create_engine, inspect
import os
from config import Config

# Assuming Config has SQLALCHEMY_DATABASE_URI
# Or we can just build it: postgresql://postgres:0001@127.0.0.1/qrtrack

try:
    db_url = Config.SQLALCHEMY_DATABASE_URI
except:
    db_url = "postgresql://postgres:0001@127.0.0.1/qrtrack"

print(f"Connecting to {db_url}...")
engine = create_engine(db_url)
inspector = inspect(engine)
columns = inspector.get_columns('vendors')

print("--- Vendors Table Columns ---")
for col in columns:
    print(f"{col['name']} ({col['type']})")
print("-----------------------------")
