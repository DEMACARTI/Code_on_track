
import asyncio
import sys
import os
import json
from sqlalchemy import select

sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app.models.notification import Notification

async def check_notifs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Notification))
        notifs = result.scalars().all()
        
        output = []
        for n in notifs:
            n_data = {
                "id": n.id,
                "title": n.title,
                "msg": n.message,
                "metadata": n.metadata_
            }
            output.append(n_data)
            
        with open("notif_dump_utf8.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
            
        print(f"Dumped {len(notifs)} notifications to notif_dump_utf8.json")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_notifs())
