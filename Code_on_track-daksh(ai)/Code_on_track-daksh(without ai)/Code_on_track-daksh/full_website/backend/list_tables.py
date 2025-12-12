import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def list_tables():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        print([row[0] for row in result])

if __name__ == "__main__":
    asyncio.run(list_tables())
