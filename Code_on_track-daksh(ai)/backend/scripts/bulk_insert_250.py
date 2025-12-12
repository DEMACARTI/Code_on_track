import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# Add backend directory to path so we can import if needed, though we'll use raw SQL mainly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

def get_db_url():
    return os.environ.get('DATABASE_URL', 'postgresql://postgres:0001@localhost:5432/qrtrack')

def run_backup(engine, timestamp):
    print(f"--- Creating Backups (Timestamp: {timestamp}) ---")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Backup items
            conn.execute(text(f"CREATE TABLE backup_items_{timestamp} AS TABLE items"))
            print(f"Created backup_items_{timestamp}")
            
            # Backup lot_quality
            conn.execute(text(f"CREATE TABLE backup_lot_quality_{timestamp} AS TABLE lot_quality"))
            print(f"Created backup_lot_quality_{timestamp}")
            
            # Backup lot_health
            conn.execute(text(f"CREATE TABLE backup_lot_health_{timestamp} AS TABLE lot_health"))
            print(f"Created backup_lot_health_{timestamp}")
            
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"Error creating backups: {e}")
            sys.exit(1)

def fetch_vendor_ids(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM vendors"))
        rows = result.fetchall()
        return [row[0] for row in rows]

def generate_items(vendor_ids, count=250):
    items = []
    component_types = [
        ('ERC', 'ERC'), 
        ('Rail Pads', 'RP'), 
        ('Sleepers', 'SL'), 
        ('Liners', 'LN')
    ]
    statuses = ['manufactured', 'installed', 'inspected', 'failed']
    status_weights = [0.4, 0.3, 0.2, 0.1]
    
    # Starting from 1 for SYN sequence
    # To avoid collision, we might strictly stick to SYN-0001 to SYN-0250. 
    # If SYN items already exist, this might duplicate UIDs if we are not careful about unique constraints.
    # However, user instructions say "Use UID prefix SYN- for all inserted rows: SYN-0001 .. SYN-0250."
    # I will assume these are new.
    
    for i in range(1, count + 1):
        uid = f"SYN-{i:04d}"
        comp_name, comp_code = random.choice(component_types)
        lot_suffix = random.randint(100, 150)
        lot_no = f"LOT-{comp_code}-{lot_suffix}"
        
        vendor_id = random.choice(vendor_ids) if vendor_ids else None
        
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        
        # Date within last 720 days
        days_ago = random.randint(0, 720)
        manufacture_date = datetime.now() - timedelta(days=days_ago)
        
        warranty_months = random.choice([18, 24, 36, 48])
        
        items.append({
            'uid': uid,
            'lot_no': lot_no,
            'component_type': comp_name,
            'vendor_id': vendor_id,
            'status': status,
            'manufacture_date': manufacture_date,
            'warranty_months': warranty_months
        })
    return items

def insert_items(engine, items):
    print(f"--- Inserting {len(items)} Items ---")
    insert_sql = text("""
        INSERT INTO items (uid, lot_no, component_type, vendor_id, status, manufacture_date, warranty_months)
        VALUES (:uid, :lot_no, :component_type, :vendor_id, :status, :manufacture_date, :warranty_months)
        ON CONFLICT (uid) DO NOTHING
    """)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for item in items:
                conn.execute(insert_sql, item)
            trans.commit()
            print("Successfully inserted items.")
        except Exception as e:
            trans.rollback()
            print(f"Error inserting items: {e}")
            sys.exit(1)

def main():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    db_url = get_db_url()
    engine = create_engine(db_url)
    
    print(f"Connecting to database...")
    
    # 1. Backup
    run_backup(engine, timestamp)
    
    # 2. Fetch Vendors
    vendor_ids = fetch_vendor_ids(engine)
    if not vendor_ids:
        print("No vendors found! Cannot assign vendor_id.")
        # We'll proceed with None or exit? Instructions say "Use existing vendor IDs".
        # If none, we might just use NULL.
    
    # 3. Generate Data
    new_items = generate_items(vendor_ids, 250)
    
    # 4. Insert
    insert_items(engine, new_items)
    
    print("--- Done ---")

if __name__ == "__main__":
    main()
