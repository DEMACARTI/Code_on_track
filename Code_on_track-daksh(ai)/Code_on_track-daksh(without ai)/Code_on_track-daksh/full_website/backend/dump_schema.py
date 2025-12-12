
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import text
from app.db.session import engine

async def dump_schema():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT * FROM items LIMIT 1"))
            keys = list(result.keys())
            with open("schema_dump_clean.txt", "w") as f:
                f.write("\n".join(keys))
            print("Dumped schema to schema_dump_clean.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(dump_schema())
