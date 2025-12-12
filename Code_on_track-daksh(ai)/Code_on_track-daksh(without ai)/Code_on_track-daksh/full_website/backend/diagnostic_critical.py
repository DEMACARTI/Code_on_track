import asyncio
import sys
import os
import json
from sqlalchemy import text
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def run_diagnostics():
    results = {}
    
    try:
        async with engine.connect() as conn:
            # 1. Row counts
            counts = {}
            for table in ['items', 'lot_quality', 'lot_health', 'vendors']:
                try:
                    res = await conn.execute(text(f"SELECT count(*) FROM {table}"))
                    counts[table] = res.scalar()
                except Exception:
                    counts[table] = "Error/Missing"
            
            res = await conn.execute(text("SELECT count(DISTINCT lot_no) FROM items"))
            counts['distinct_lots'] = res.scalar()
            results['db_counts'] = counts

            # 2. Schema Info (Postgres specific)
            schemas = {}
            for table in ['lot_quality', 'lot_health']:
                res = await conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                """))
                schemas[table] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            results['schemas'] = schemas

            # 3. Sample Rows - Lot Quality
            try:
                res = await conn.execute(text("SELECT * FROM lot_quality ORDER BY failure_rate DESC LIMIT 10"))
                results['top_lot_quality'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                results['top_lot_quality'] = str(e)

            # 4. Sample Rows - Lot Health
            try:
                res = await conn.execute(text("SELECT * FROM lot_health ORDER BY health_score ASC LIMIT 10"))
                results['top_lot_health'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                results['top_lot_health'] = str(e)

            # 5. High Risk Lots
            try:
                res = await conn.execute(text("SELECT lot_no, health_score, risk_level FROM lot_health WHERE risk_level='HIGH' LIMIT 50"))
                results['high_risk_lots'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                results['high_risk_lots'] = str(e)

            # 6. Null Fields
            try:
                res = await conn.execute(text("""
                    SELECT lq.lot_no, lq.failure_rate, lh.health_score 
                    FROM lot_quality lq 
                    LEFT JOIN lot_health lh ON lq.lot_no = lh.lot_no
                    WHERE lq.failure_rate IS NULL OR lh.health_score IS NULL
                    LIMIT 20
                """))
                results['null_fields_info'] = [dict(zip(res.keys(), row)) for row in res.fetchall()]
            except Exception as e:
                results['null_fields_info'] = str(e)

    except Exception as e:
        results['error'] = str(e)

    print(json.dumps(results, indent=2, cls=DateTimeEncoder))

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostics())
