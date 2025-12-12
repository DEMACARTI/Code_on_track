import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())
from app.db.session import engine

async def check_columns():
    async with engine.connect() as conn:
        try:
            # Postgres specific
            query = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications'")
            result = await conn.execute(query)
            for row in result:
                print(f"{row.column_name}: {row.data_type}")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_columns())
