
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine, AsyncSessionLocal
from app.models.item import Item
from app.models.vendor import Vendor
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError

async def seed_items():
    print(f"DEBUG: Connecting to {engine.url}")
    async with AsyncSessionLocal() as db:
        try:
            # 1. Check Vendors
            print("Checking vendors...")
            result = await db.execute(select(Vendor))
            vendors = result.scalars().all()
            if not vendors:
                print("No vendors found! Cannot seed items.")
                return
            
            print(f"Found {len(vendors)} vendors.")
            vendor_ids = [v.id for v in vendors]

            # 2. Create Items
            print("Creating items...")
            items = []
            component_types = ["Rail Clip", "Concrete Sleeper", "Fishplate", "Bolt", "Pad"]
            
            for i in range(1, 11):
                uid = f"ITEM-{i:03d}"
                # Check if exists
                existing = await db.execute(select(Item).where(Item.uid == uid))
                if existing.scalar_one_or_none():
                    print(f"Item {uid} already exists.")
                    continue

                item = Item(
                    uid=uid,
                    lot_no=f"LOT-{random.randint(100, 999)}",
                    component_type=random.choice(component_types),
                    vendor_id=random.choice(vendor_ids),
                    status="manufactured",
                    manufacture_date=datetime.now() - timedelta(days=random.randint(1, 100)),
                    created_at=datetime.now()
                )
                db.add(item)
                items.append(item)
            
            if items:
                print(f"Adding {len(items)} items...")
                await db.commit()
                print("Items seeded successfully.")
            else:
                print("No new items to add.")

            # 3. Verify
            count = await db.execute(text("SELECT COUNT(*) FROM items"))
            print(f"Total items in DB: {count.scalar()}")

        except ProgrammingError as e:
            print(f"SCHEMA MISMATCH ERROR: {e}")
            print("ORIGINAL EXCEPTION:", e.orig)
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_items())
