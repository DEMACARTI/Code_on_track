import asyncio
import sys
import os
import traceback
from sqlalchemy import text
from datetime import datetime

sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app.models.notification import Notification

async def create_notif():
    async with AsyncSessionLocal() as session:
        try:
            # Raw SQL insert to bypass ORM issues
            await session.execute(text("""
                INSERT INTO notifications (type, title, message, severity, read, dismissed, created_at, metadata)
                VALUES ('system_alert', 'System Verification', 'This is a test notification.', 'info', false, false, NOW(), '{"test": true}')
            """))
            await session.commit()
            print("Created test notification via raw SQL.")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_notif())
