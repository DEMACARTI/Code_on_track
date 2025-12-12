
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

async def clean_reseed():
    print(f"DEBUG: Connecting to {engine.url}")
    async with AsyncSessionLocal() as db:
        try:
            # 1. Verification of Clean State (Optional, script assumes deletes happened)
            # We won't truncate here to respect "Delete invalid types" instruction if user kept some valid ones.
            # But likely all were deleted.
            
            # 2. Get Vendors
            print("Fetching vendors...")
            result = await db.execute(select(Vendor))
            vendors = result.scalars().all()
            if not vendors:
                print("No vendors found! Cannot seed items.")
                return
            vendor_ids = [v.id for v in vendors]

            # 3. Get Lots
            print("Fetching lots...")
            try:
                result = await db.execute(text("SELECT lot_no FROM lot_quality"))
                lots = [row[0] for row in result.fetchall()]
            except Exception:
                lots = []
            
            if not lots:
                # Fallback if table empty
                lots = [f"LOT-{i}" for i in range(100, 225)]
            
            print(f"distributing items across {len(lots)} lots.")

            # 4. Generate Items
            # ALLOWED TYPES ONLY
            allowed_types = ["ERC", "Rail Pad", "Liner", "Sleeper"]
            
            # Target 1250 total
            items_needed = 1250
            
            # Check current count
            curr = await db.execute(text("SELECT COUNT(*) FROM items"))
            current_count = curr.scalar()
            
            to_add = max(0, items_needed - current_count)
            print(f"Current items: {current_count}. Generating {to_add} new items...")
            
            if to_add == 0:
                print("Target count already met.")
                return

            items_per_lot = (to_add // len(lots)) + 1
            
            count = 0
            for lot in lots:
                for _ in range(items_per_lot):
                    if count >= to_add: break
                    
                    count += 1
                    uid = f"ITEM-{random.randint(1000,9999)}-{random.randint(10,99)}"
                    
                    # Weighted status
                    r = random.random()
                    if r < 0.7: status = "manufactured"
                    elif r < 0.9: status = "installed"
                    else: status = "rejected" # or failed, keeping simple

                    item = Item(
                        uid=uid,
                        lot_no=lot,
                        component_type=random.choice(allowed_types),
                        vendor_id=random.choice(vendor_ids),
                        status=status,
                        manufacture_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                        created_at=datetime.now()
                    )
                    
                    db.add(item)
                    if len(db.new) >= 200:
                        await db.commit()
                        
            await db.commit()
            print(f"Successfully added {count} clean items.")

            # 5. Final Summary
            final_count = await db.execute(text("SELECT COUNT(*) FROM items"))
            print(f"Total Items: {final_count.scalar()}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(clean_reseed())
