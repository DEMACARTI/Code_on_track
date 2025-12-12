import asyncio
import sys
import os
from sqlalchemy import select, text
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def check():
    async with AsyncSessionLocal() as session:
        # Try raw SQL first to bypass model issues if any
        result = await session.execute(text("SELECT username FROM users"))
        users = result.fetchall()
        print(f"Users in DB: {users}")

if __name__ == "__main__":
    asyncio.run(check())
