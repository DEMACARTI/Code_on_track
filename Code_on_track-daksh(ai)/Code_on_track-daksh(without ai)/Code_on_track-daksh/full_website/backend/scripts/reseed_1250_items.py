
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

async def reseed_items():
    print(f"DEBUG: Connecting to {engine.url}")
    async with AsyncSessionLocal() as db:
        try:
            # 1. Clear existing items
            print("Clearing existing items...")
            await db.execute(text("TRUNCATE TABLE items CASCADE"))
            await db.commit()
            print("Items cleared.")

            # 2. Get Vendors
            print("Fetching vendors...")
            result = await db.execute(select(Vendor))
            vendors = result.scalars().all()
            if not vendors:
                print("No vendors found! Cannot seed items.")
                return
            vendor_ids = [v.id for v in vendors]
            print(f"Found {len(vendors)} vendors.")

            # 3. Get Lots
            print("Fetching lots from lot_quality...")
            # Using raw SQL to be safe as we don't have LotQuality model loaded
            try:
                result = await db.execute(text("SELECT lot_no FROM lot_quality"))
                lots = [row[0] for row in result.fetchall()]
                print(f"Found {len(lots)} lots in lot_quality.")
            except Exception as e:
                print(f"Could not fetch lots: {e}")
                lots = []

            if not lots:
                print("Warning: No lots found. Generating dummy lots.")
                lots = [f"LOT-{i}" for i in range(100, 225)]

            # 4. Generate Items
            print("Generating 1250 items...")
            items = []
            component_types = ["Rail Clip", "Concrete Sleeper", "Fishplate", "Bolt", "Pad"]
            
            # Target ~1250 items.
            # If we have 125 lots, that's exactly 10 per lot.
            items_per_lot = 10
            
            count = 0
            for lot in lots:
                for _ in range(items_per_lot):
                    count += 1
                    uid = f"ITEM-{count:04d}-{random.randint(100,999)}"
                    
                    # Status distribution
                    r = random.random()
                    if r < 0.8: status = "active"
                    elif r < 0.9: status = "manufactured"
                    else: status = "rejected"

                    item = Item(
                        uid=uid,
                        lot_no=lot,
                        component_type=random.choice(component_types),
                        vendor_id=random.choice(vendor_ids),
                        status=status,
                        manufacture_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                        created_at=datetime.now()
                    )
                    
                    db.add(item)
                    
                    if len(db.new) >= 100:
                         await db.commit()
            
            await db.commit()
            print(f"Successfully seeded {count} items.")

            # 5. Verify
            count_result = await db.execute(text("SELECT COUNT(*) FROM items"))
            print(f"Final Item Count: {count_result.scalar()}")

        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reseed_items())
