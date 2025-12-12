import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

# Configuration
VENDORS = [
    {"name": "TechRail Solutions", "contact": "contact@techrail.com", "reliability": 0.98},
    {"name": "Global Track Systems", "contact": "support@globaltrack.com", "reliability": 0.92},
    {"name": "Metro Build Corp", "contact": "sales@metrobuild.com", "reliability": 0.88},
    {"name": "RapidRail Parts", "contact": "info@rapidrail.com", "reliability": 0.95},
    {"name": "SteelWorks Intl", "contact": "orders@steelworks.com", "reliability": 0.85},
    {"name": "InfraCore Ltd", "contact": "help@infracore.com", "reliability": 0.99},
]
ITEM_TYPES = ["ERC", "Sleeper", "Rail Pad", "Liner"]
STATUSES = ["installed", "manufactured", "in_transit", "failed"]
WEIGHTS = [0.6, 0.3, 0.05, 0.05]  # Probabilities for statuses

async def seed_demo_data():
    async with AsyncSessionLocal() as db:
        print("Starting Demo Seed...")

        # 1. Create Vendors
        print("Seeding Vendors...")
        vendor_ids = []
        for i, v in enumerate(VENDORS):
            code = f"V-{i+1:03d}"
            # Use json.dumps and standard SQL CAST
            import json
            meta_str = json.dumps({"reliability_score": v["reliability"], "vendor_code": code})
            contact_str = json.dumps({"email": v["contact"]})
            
            query = text("""
                INSERT INTO vendors (name, contact_info, "metadata") 
                VALUES (:name, CAST(:contact AS JSON), CAST(:meta AS JSON)) 
                RETURNING id
            """)
            
            result = await db.execute(query, {"name": v["name"], "contact": contact_str, "meta": meta_str})
            vendor_ids.append(result.scalar())
        
        # 2. Create Items & Lots
        print("Seeding Items & Lots...")
        lots = []
        
        # 7 Critical, 20 High, 98 Medium
        lot_risks = ['CRITICAL'] * 7 + ['HIGH'] * 20 + ['MEDIUM'] * 98
        random.shuffle(lot_risks) 

        created_items = 0
        
        for i, risk in enumerate(lot_risks):
            lot_no = f"LOT-2024-{i+1:03d}"
            vendor_id = random.choice(vendor_ids)
            item_count = random.randint(10, 15)
            
            fail_prob = 0.30 if risk == 'CRITICAL' else (0.10 if risk == 'HIGH' else 0.01)

            for _ in range(item_count):
                status = 'failed' if random.random() < fail_prob else random.choices(STATUSES, weights=WEIGHTS)[0]
                if status == 'failed' and risk == 'MEDIUM': status = 'installed'
                if status != 'failed' and risk == 'CRITICAL' and random.random() < 0.5: status = 'failed'

                uid = f"ITEM-{uuid.uuid4().hex[:8].upper()}"
                comp_type = random.choice(ITEM_TYPES)
                days_ago = random.randint(1, 60)
                
                # Use standard string formatting for interval or compute python date
                created_date = datetime.now() - timedelta(days=days_ago)

                await db.execute(text("""
                    INSERT INTO items (uid, lot_no, component_type, vendor_id, status, created_at)
                    VALUES (:uid, :lot, :ctype, :vid, :status, :cdate)
                """), {
                    "uid": uid, "lot": lot_no, "ctype": comp_type, 
                    "vid": vendor_id, "status": status, 
                    "cdate": created_date
                })
                created_items += 1

            # Insert Lot Health (Matches actual schema)
            # Need to aggregate items for the lot to fill these columns correctly
            # But for speed I'll just use the vars I have
            
            # lot_health columns: lot_no, component_type, vendor_id, total_items, failed_items, failure_rate, health_score, risk_level, anomaly_score, computed_at
            
            failed_count = int(item_count * (fail_prob + random.uniform(-0.02, 0.02)))
            if failed_count < 0: failed_count = 0
            if failed_count > item_count: failed_count = item_count
            
            actual_fail_rate = failed_count / item_count if item_count > 0 else 0
            
            health_score = 0.4 if risk == 'CRITICAL' else (0.7 if risk == 'HIGH' else 0.95)
            # Add some noise
            health_score = min(1.0, max(0.0, health_score + random.uniform(-0.05, 0.05)))

            await db.execute(text("""
                INSERT INTO lot_health (
                    lot_no, component_type, vendor_id, 
                    total_items, failed_items, failure_rate, 
                    health_score, risk_level, anomaly_score, computed_at
                )
                VALUES (
                    :lot, :ctype, :vid,
                    :total, :failed, :rate,
                    :hscore, :risk, :anom, NOW()
                )
            """), {
                "lot": lot_no, 
                "ctype": comp_type,
                "vid": vendor_id,
                "total": item_count,
                "failed": failed_count,
                "rate": actual_fail_rate,
                "hscore": health_score,
                "risk": risk, 
                "anom": 0.8 if risk == 'CRITICAL' else 0.02
            })
            
            # Insert Lot Quality
            # columns: lot_no, component_type, vendor_id, total_items, failed_items, failure_rate, anomaly_score, is_anomalous, computed_at
            await db.execute(text("""
                INSERT INTO lot_quality (
                    lot_no, component_type, vendor_id,
                    total_items, failed_items, failure_rate,
                    anomaly_score, is_anomalous, computed_at
                )
                VALUES (
                    :lot, :ctype, :vid,
                    :total, :failed, :rate,
                    :anom, :is_anom, NOW()
                )
            """), {
                "lot": lot_no,
                "ctype": comp_type,
                "vid": vendor_id,
                "total": item_count,
                "failed": failed_count,
                "rate": actual_fail_rate,
                "anom": 0.8 if risk == 'CRITICAL' else 0.02,
                "is_anom": True if risk == 'CRITICAL' else False
            })

            lots.append(lot_no)

        print(f"Created {created_items} items in {len(lots)} lots.")

        # 3. Create Notifications
        print("Seeding Notifications...")
        for _ in range(10):
            mins_ago = random.randint(1, 1000)
            created_at = datetime.now() - timedelta(minutes=mins_ago)
            
            await db.execute(text("""
                INSERT INTO notifications (
                    type, title, message, severity, created_at, "read", 
                    bucket, total_items, metadata
                )
                VALUES (
                    'alert', 'System Alert', 'Generated demo alert', :sev, :cdate, FALSE,
                    'general', 0, '{}'::jsonb
                )
            """), {
                "sev": random.choice(['info', 'warning', 'error']),
                "cdate": created_at
            })

        await db.commit()
        print("Demo Seed Complete!")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
