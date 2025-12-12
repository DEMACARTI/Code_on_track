import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def check_constraints():
    async with engine.connect() as conn:
        print("Checking constraints for lot_health...")
        # Postgres query for constraints
        sql = """
            SELECT conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c 
            JOIN pg_namespace n ON n.oid = c.connamespace 
            WHERE conrelid = 'public.lot_health'::regclass
        """
        try:
            res = await conn.execute(text(sql))
            rows = res.all()
            for r in rows:
                print(r)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_constraints())
