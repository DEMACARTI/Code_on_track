import asyncio
import sys
import os
import json
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine

# We verify by calling the DB directly with the query that the API uses, 
# or we can assume the API wrapper is thin (which it is).
# Ideally we hit the running API, but we are inside the environment.
# Let's verify via DB query simulating API parameters.

async def verify_api_logic():
    print("Verifying API logic for CRITICAL lots...")
    results = {}
    try:
        async with engine.connect() as conn:
            # Simulate GET /lot_health/?risk_level=CRITICAL
            query = "SELECT * FROM lot_health WHERE risk_level = 'CRITICAL' LIMIT 5"
            res = await conn.execute(text(query))
            rows = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            
            print(f"Found {len(rows)} critical lots (limit 5).")
            print(json.dumps(rows, indent=2, default=str))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_api_logic())
