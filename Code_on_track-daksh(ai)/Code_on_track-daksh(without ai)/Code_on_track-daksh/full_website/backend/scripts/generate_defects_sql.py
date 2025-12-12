
import random
from datetime import datetime, timedelta

# Configuration
TOTAL_DEFECTS = 45
DAYS_BACK = 7
START_ID = 1 # Assuming seeded from 1, or we can use subquery
STATUS = 'failed'

sql_statements = ["BEGIN;"]

# We will select random items to update. 
# Since we don't know exact IDs safely without querying, we will use a subquery approach 
# or just generating random updates if we know the ID range.
# The reseed script cleared the table (TRUNCATE), so IDs likely restarted from 1 (if Identity reset) or continued.
# TRUNCATE CASCADE usually resets identity if explicitly asked or implied? 
# Postgres TRUNCATE does NOT reset identity by default unless RESTART IDENTITY is used.
# The reseed script used `db.execute(text("TRUNCATE TABLE items CASCADE"))`.
# Safe bet: Use `UPDATE items SET ... WHERE id IN (SELECT id FROM items ORDER BY RANDOM() LIMIT 1)` repeated? 
# No, that's inefficient.
# Better: `UPDATE items SET status='failed', created_at = ... WHERE ctid IN (SELECT ctid FROM items ORDER BY RANDOM() LIMIT N)`
# Actually, let's just generate a single block of updates using subqueries or fetching IDs first.
# Fetching IDs first is safer.

# But I "Generate SQL" in this tool step, I can't query and generate in one file easily without running a python script against DB.
# I will write `generate_defects_sql.py` that CONNECTS to DB to find candidates, then writes the `insert_weekly_defects.sql` file.

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def generate_sql():
    async with AsyncSessionLocal() as db:
        # Get 50 random IDs
        result = await db.execute(text("SELECT id FROM items ORDER BY RANDOM() LIMIT 50"))
        ids = [row[0] for row in result.fetchall()]
    
    with open("../artifacts/insert_weekly_defects.sql", "w") as f:
        f.write("-- Update 50 Record for Weekly Defects Trend\n")
        f.write("BEGIN;\n\n")
        
        for i, item_id in enumerate(ids):
            # Spread over last 7 days
            days_ago = random.randint(0, 6)
            # Create a timestamp
            new_date = datetime.now() - timedelta(days=days_ago)
            date_str = new_date.strftime("%Y-%m-%d %H:%M:%S")
            
            f.write(f"UPDATE items SET status = 'failed', created_at = '{date_str}' WHERE id = {item_id};\n")
        
        f.write("\nCOMMIT;\n")
    
    print(f"Generated SQL for {len(ids)} items.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_sql())
