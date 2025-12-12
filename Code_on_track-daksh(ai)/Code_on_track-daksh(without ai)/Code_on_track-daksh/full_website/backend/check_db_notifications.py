
import asyncio
import sys
import os
from sqlalchemy import select, func

sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app.models.notification import Notification

async def check_notifs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Notification))
        notifs = result.scalars().all()
        print(f"Total Notifications: {len(notifs)}")
        for n in notifs:
            print(f"[{n.type}] {n.title} (ID: {n.id}) Msg: {n.message}")
            if n.metadata_:
                import json
                print(json.dumps(n.metadata_, indent=2))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_notifs())
