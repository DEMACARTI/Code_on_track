
import asyncio
import sys
import os
from sqlalchemy import select, func, text

# Add current dir to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.item import Item
from app.models.vendor import Vendor

import logging
# Disable sqlalchemy logs
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def check_data():
    output = []
    async with AsyncSessionLocal() as session:
        # Check items count
        output.append("Checking items count...")
        result = await session.execute(select(func.count(Item.uid)))
        count = result.scalar()
        output.append(f"Total Items: {count}")
        
        # Check sample items
        result = await session.execute(select(Item).limit(5))
        items = result.scalars().all()
        for item in items:
            output.append(f"Item {item.uid}: Vendor {item.vendor_id}, Type '{item.component_type}'")
            
        # Check aggregation
        output.append("\nTesting Query:")
        # Subqueries matching vendors.py
        items_count_subquery = (
            select(Item.vendor_id, func.count(Item.uid).label("count"))
            .group_by(Item.vendor_id)
            .subquery()
        )
        components_subquery = (
            select(Item.vendor_id, func.string_agg(Item.component_type.distinct(), ', ').label("components"))
            .group_by(Item.vendor_id)
            .subquery()
        )
        stmt = (
            select(
                                Vendor.name, 
                func.coalesce(items_count_subquery.c.count, 0).label("items_count"),
                components_subquery.c.components.label("components_str")
            )
            .outerjoin(items_count_subquery, Vendor.id == items_count_subquery.c.vendor_id)
            .outerjoin(components_subquery, Vendor.id == components_subquery.c.vendor_id)
        )
        try:
            result = await session.execute(stmt)
            for row in result:
                output.append(f"Vendor: {row.name}, Count: {row.items_count}, Components: {row.components_str}")
        except Exception as e:
            output.append(f"Query Error: {e}")
            
    with open("db_check.txt", "w") as f:
        f.write("\n".join(output))
    print("Check finished, written to db_check.txt")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_data())
