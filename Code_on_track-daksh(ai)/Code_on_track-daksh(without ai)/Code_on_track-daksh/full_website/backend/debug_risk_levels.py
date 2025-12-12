import asyncio
import sys
import os
from sqlalchemy import text

# Add backend dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.core.config import settings

async def analyze_data():
    print(f"CONNECTING TO: {settings.DATABASE_URL}")
    async with engine.connect() as conn:
        print("--- ANALYZING lot_health TABLE ---")
        
        # 1. Group by risk_level and count
        print("\nRisk Level Distribution:")
        result = await conn.execute(text("SELECT risk_level, COUNT(*), COUNT(DISTINCT lot_no) FROM lot_health GROUP BY risk_level"))
        for row in result:
            print(f"Risk: '{row[0]}' | Count: {row[1]} | Distinct Lots: {row[2]}")

        # 2. Check for hidden characters in CRITICAL
        print("\nChecking length of 'CRITICAL' entries:")
        result = await conn.execute(text("SELECT length(risk_level), count(*) FROM lot_health WHERE risk_level LIKE '%CRITICAL%' GROUP BY length(risk_level)"))
        for row in result:
            print(f"Length: {row[0]} | Count: {row[1]}")

        # 3. Simulate analytics query
        print("\nAnalytics Query (count distinct 'CRITICAL'):")
        res_a = await conn.execute(text("SELECT count(DISTINCT lot_no) FROM lot_health WHERE risk_level = 'CRITICAL'"))
        print(f"Result: {res_a.scalar()}")

        # 4. Simulate list query
        print("\nList Query (SELECT * ... 'CRITICAL'):")
        res_l = await conn.execute(text("SELECT count(*) FROM lot_health WHERE risk_level = 'CRITICAL'"))
        print(f"Result: {res_l.scalar()}")
        
        # 5. Check exact string hex to find invisible chars
        print("\nChecking Hex representation of risk_level for CRITICAL:")
        # encode to hex to see hidden bytes
        res_hex = await conn.execute(text("SELECT encode(risk_level::bytea, 'hex'), count(*) FROM lot_health WHERE risk_level LIKE '%CRITICAL%' GROUP BY 1"))
        for row in res_hex:
            print(f"Hex: {row[0]} | Count: {row[1]}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(analyze_data())
