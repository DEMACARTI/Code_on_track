import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def inspect():
    with open("../artifacts/schema_dump.txt", "w") as f:
        async with AsyncSessionLocal() as db:
            for t in ['lot_health', 'lot_quality', 'notifications']:
                f.write(f"--- Columns for {t} ---\n")
                q = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'")
                res = await db.execute(q)
                rows = res.fetchall()
                if not rows:
                    f.write(f"No columns found for {t} (Table might not exist?)\n")
                for row in rows:
                    f.write(f"COLUMN: {row[0]} | TYPE: {row[1]}\n")

if __name__ == "__main__":
    asyncio.run(inspect())
