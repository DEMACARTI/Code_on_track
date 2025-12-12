import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add current dir to path
sys.path.append(os.getcwd())

from app.db.session import engine, AsyncSessionLocal
from app.models.vendor import Vendor
from app.models.item import Item
from sqlalchemy import select, text

import traceback

async def seed():
    try:
        print("Starting seed...")
        async with AsyncSessionLocal() as session:
            # Clear existing items to ensure clean state matching requirements
            await session.execute(text("DELETE FROM items"))
            await session.commit()
            print("Cleared existing items.")

            # Create Vendors
            vendors_data = [
                {"name": "Acme Supply Co", "code": "ACME-01", "contact": "Alice Smith", "email": "alice@acme.com", "items": 60, "types": ["ERC", "Rail Pads"]},
                {"name": "Rapid Parts Inc", "code": "RPI-99", "contact": "Bob Jones", "email": "bob@rapidparts.com", "items": 40, "types": ["Sleepers"]},
                {"name": "Global Components", "code": "GLB-X", "contact": "Charlie Day", "email": "charlie@global.com", "items": 50, "types": ["ERC", "Liners", "Rail Pads"]},
            ]
            
            created_vendors = []
            for v_data in vendors_data:
                result = await session.execute(select(Vendor).where(Vendor.name == v_data["name"]))
                existing = result.scalar_one_or_none()
                if not existing:
                    vendor = Vendor(
                        name=v_data["name"],
                        contact_info={"name": v_data["contact"], "email": v_data["email"], "phone": "555-0123", "address": "123 Tech Park"},
                        metadata_={"vendor_code": v_data["code"], "warranty_months": 12, "notes": "Premium supplier"}
                    )
                    session.add(vendor)
                    await session.flush() # to get ID
                    created_vendors.append((vendor, v_data))
                    print(f"Created vendor: {vendor.name}")
                else:
                    created_vendors.append((existing, v_data))
                    print(f"Vendor exists: {existing.name} (ID: {existing.id})")

            # Create Items
            count = 0
            for vendor, v_data in created_vendors:
                print(f"Creating items for vendor {vendor.name} (ID: {vendor.id})", flush=True)
                import json
                
                types = v_data["types"]
                for i in range(v_data["items"]):
                    # Cycle through types to ensure all are represented if possible
                    comp_type = types[i % len(types)]
                    
                    uid = f"TEST-{vendor.id}-{random.randint(10000,99999)}"
                    await session.execute(text("""
                        INSERT INTO items (uid, component_type, lot_number, vendor_id, quantity, current_status, warranty_years, manufacture_date, qr_image_url, metadata, created_at, updated_at)
                        VALUES (:uid, :type, :lot, :vid, :qty, :status, :warranty, :mfg, :qr, :meta, :created, :updated)
                    """), {
                        "uid": uid,
                        "type": comp_type,
                        "lot": f"LOT-{random.randint(10, 99)}",
                        "vid": vendor.id,
                        "qty": random.randint(1, 100),
                        "status": random.choice(["manufactured", "installed", "rejected"]),
                        "warranty": 1,
                        "mfg": datetime.now() - timedelta(days=random.randint(1, 365)),
                        "qr": None,
                        "meta": json.dumps({"description": "Seeded item"}), 
                        "created": datetime.now(),
                        "updated": datetime.now()
                    })
                    count += 1
            
            await session.commit()
            print(f"Seeding complete. Added {count} items.", flush=True)
    except Exception as e:
        print("Error seeding data:")
        with open("error.log", "w") as f:
            f.write(str(e))
            traceback.print_exc(file=f)


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
