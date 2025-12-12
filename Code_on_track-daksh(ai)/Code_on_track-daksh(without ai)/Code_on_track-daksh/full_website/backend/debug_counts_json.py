import asyncio
import sys
import os
import json
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine

async def analyze_data():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT risk_level, count(*) FROM lot_health GROUP BY risk_level"))
        data = {row[0]: row[1] for row in res}
        
        output = {
            "CRITICAL": data.get('CRITICAL', 0),
            "HIGH": data.get('HIGH', 0),
            "MEDIUM": data.get('MEDIUM', 0),
            "LOW": data.get('LOW', 0),
            "SUM_CRIT_HIGH": data.get('CRITICAL', 0) + data.get('HIGH', 0)
        }
        
        with open("debug_counts.json", "w") as f:
            json.dump(output, f)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(analyze_data())
