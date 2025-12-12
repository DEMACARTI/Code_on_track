import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def add_constraint():
    print("Adding unique constraint to lot_health(lot_no)...")
    async with engine.begin() as conn:
        try:
            # First, check for duplicates and handle them? 
            # Assuming cleanup was done, or taking distinct.
            # But let's just try adding it.
            # Using raw SQL
            await conn.execute(text("ALTER TABLE lot_health ADD CONSTRAINT uq_lot_health_lot_no UNIQUE(lot_no);"))
            print("Constraint added.")
        except Exception as e:
            print(f"Error adding constraint (might exist or dupes): {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_constraint())
