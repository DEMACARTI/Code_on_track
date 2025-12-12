import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine
from app.models.item import Item
from app.schemas.items import ItemOut

async def test_serialization():
    async with engine.connect() as conn: # connection test
        pass
    
    # We need a session to load relations
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        query = select(Item).options(selectinload(Item.vendor)).limit(1)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if item:
            print(f"Found item: {item.uid}")
            if item.vendor:
                print(f"Vendor: {item.vendor.name}")
                # Try validation
                try:
                    schema_item = ItemOut.model_validate(item)
                    print("Serialization Success!")
                    print(schema_item.vendor)
                except Exception as e:
                    print(f"Serialization Failed: {e}")
        else:
            print("No items found to test.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_serialization())
