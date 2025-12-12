
import asyncio
import sys
import os

# Add parent path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, func
from app.db.session import engine
from app.models.item import Item
from typing import List, Dict, Any

async def test_analytics():
    print("Testing analytics...")
    try:
        async with engine.connect() as conn:
            # We need a session, not just connection, for ORM select(Item) query usually? 
            # Actually engine.connect() gives connection. select(Item) needs Session for scalars() usually or execute() returns rows.
            # But let's try to replicate logic from analytics.py which accepts 'db: AsyncSession'.
            # So we should use AsyncSessionLocal logic.
            from app.db.session import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                print("Checking items count...")
                result_items = await db.execute(select(func.count(Item.id)))
                total_items = result_items.scalar()
                print(f"Total Items: {total_items}")

                print("Checking critical...")
                result_critical = await db.execute(select(func.count(Item.id)).where(Item.current_status == 'failed'))
                critical = result_critical.scalar()
                print(f"Critical: {critical}")

                print("Checking active...")
                result_health = await db.execute(select(func.count(Item.id)).where(Item.current_status == 'active'))
                active = result_health.scalar()
                print(f"Active: {active}")

                print("Checking vendors...")
                # Check if this syntax is valid for the dialect
                result_vendors = await db.execute(select(func.count(func.distinct(Item.vendor_id))))
                vendors = result_vendors.scalar()
                print(f"Vendors: {vendors}")

                print("Checking system activity...")
                result = await db.execute(select(Item).order_by(Item.created_at.desc()).limit(5))
                items = result.scalars().all()
                print(f"Activity items: {len(items)}")
                for i in items:
                    print(f" - {i.uid}")
        
    except Exception as e:
        print("âŒ Error occurred!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_analytics())
