import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def check_users():
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text("SELECT count(*) FROM website_users"))
            count = res.scalar()
            print(f"User Count: {count}")
            
            if count > 0:
                res_rows = await conn.execute(text("SELECT id, username, role FROM website_users LIMIT 1"))
                for row in res_rows:
                    print(f"Sample User: {row}")
        except Exception as e:
            print(f"Error checking users: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_users())
