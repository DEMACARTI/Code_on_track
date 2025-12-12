import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def fix_schema():
    print("Fixing schema for lot_health...")
    async with engine.begin() as conn:
        try:
            # Check if column exists first
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='lot_health' AND column_name='anomaly_score'"))
            if not res.scalar():
                print("Adding anomaly_score column...")
                await conn.execute(text("ALTER TABLE lot_health ADD COLUMN anomaly_score DOUBLE PRECISION DEFAULT 0"))
                print("Column added.")
            else:
                print("Column anomaly_score already exists.")
                
            # Check other potentially missing columns
            cols_to_check = ['failed_items', 'failure_rate']
            for c in cols_to_check:
                res = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='lot_health' AND column_name='{c}'"))
                if not res.scalar():
                    print(f"Adding {c} column...")
                    # types: failed_items int, failure_rate float
                    ctype = "INTEGER" if c == "failed_items" else "DOUBLE PRECISION"
                    await conn.execute(text(f"ALTER TABLE lot_health ADD COLUMN {c} {ctype} DEFAULT 0"))
                    print(f"Column {c} added.")
        except Exception as e:
            print(f"Error fixing schema: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_schema())
