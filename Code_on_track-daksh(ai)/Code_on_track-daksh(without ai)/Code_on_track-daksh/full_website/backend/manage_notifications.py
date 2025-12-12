
import asyncio
import sys
import os
from datetime import datetime, timedelta, date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app.models.item import Item
from app.models.notification import Notification

# Buckets
BUCKETS = {
    "expired": {"label": "Expired", "days_min": None, "days_max": -1}, # < 0
    "critical": {"label": "< 7 days", "days_min": 0, "days_max": 7},
    "warning": {"label": "7-30 days", "days_min": 7, "days_max": 30},
    "upcoming": {"label": "30-90 days", "days_min": 30, "days_max": 90},
}

async def process_notifications():
    print("Starting Aggregated Notification Job...")
    async with AsyncSessionLocal() as session:
        today = date.today()
        
        # Fetch all items to filter in Python
        # Note: In production, use DB CTE or computed column
        result = await session.execute(select(Item))
        all_items = result.scalars().all()
        
        print(f"Total items in DB: {len(all_items)}")

        # Helper to get expiry
        def get_expiry(item):
            if not item.manufacture_date or not item.warranty_years:
                return None
            try:
                # Assuming manufacture_date is datetime
                m_date = item.manufacture_date.date()
                # Naive calculation: add 365 * years
                return m_date + timedelta(days=365 * item.warranty_years)
            except Exception:
                return None

        # Helper to get days remaining
        def get_days_remaining(expiry):
            if not expiry:
                return None
            delta = expiry - today
            return delta.days

        for bucket_key, bucket_def in BUCKETS.items():
            print(f"Processing bucket: {bucket_key}")
            
            bucket_items = []
            
            for item in all_items:
                expiry = get_expiry(item)
                if not expiry:
                    continue
                    
                days = get_days_remaining(expiry)
                
                # Check bucket
                match = False
                if bucket_key == "expired":
                    if days < 0:
                        match = True
                else:
                    d_min = bucket_def["days_min"]
                    d_max = bucket_def["days_max"]
                    if d_min <= days < d_max:
                        match = True
                
                if match:
                    bucket_items.append(item)
            
            if not bucket_items:
                print("  No items.")
                continue
                
            total_items = len(bucket_items)
            print(f"  Found {total_items} items.")
            
            # Aggregate by lot
            lots = {}
            for item in bucket_items:
                lot = item.lot_number or "Unknown" # Corrected field name from lot_no to lot_number
                if lot not in lots:
                    lots[lot] = {
                        "lot_no": lot,
                        "count": 0,
                        "component_types": set(),
                        "depots": set()
                    }
                lots[lot]["count"] += 1
                if item.component_type:
                    lots[lot]["component_types"].add(item.component_type)
                
                # Depot extraction
                # Try metadata or hardcoded fallback if missing
                item_meta = item.metadata_ or {}
                depot = item_meta.get('depot') or item_meta.get('location') or "Main Depot"
                lots[lot]["depots"].add(depot)
            
            # Formatting for metadata
            by_lot_list = []
            for lot_data in lots.values():
                by_lot_list.append({
                    "lot_no": lot_data["lot_no"],
                    "count": lot_data["count"],
                    "component_types": list(lot_data["component_types"]),
                    "depots": list(lot_data["depots"])
                })
            
            # Sort by count desc
            by_lot_list.sort(key=lambda x: x["count"], reverse=True)
            
            # Top components summary
            comp_counts = {}
            for item in bucket_items:
                ctype = item.component_type or "Unknown"
                comp_counts[ctype] = comp_counts.get(ctype, 0) + 1
            
            top_components = [{k: v} for k, v in sorted(comp_counts.items(), key=lambda item: item[1], reverse=True)[:5]]
            
            # Date Range for metadata (for filter)
            if bucket_key == "expired":
                 # Open ended start? Or just < today
                 dr = {"end_date": today.isoformat()}
            else:
                 dr = {
                     "start_date": (today + timedelta(days=bucket_def["days_min"])).isoformat(),
                     "end_date": (today + timedelta(days=bucket_def["days_max"])).isoformat()
                 }
                 
            metadata = {
                "bucket": bucket_def["label"],
                "bucket_key": bucket_key,
                "total_items": total_items,
                "date_range": dr,
                "by_lot": by_lot_list[:100], # Top 100 lots
                "top_components": top_components,
                "days_remaining_min": bucket_def["days_min"] if bucket_key != 'expired' else None,
                "days_remaining_max": bucket_def["days_max"]
            }
            
            # Create/Update Notification
            stmt = select(Notification).where(
                Notification.type == "aggregated_expiry",
                Notification.title == bucket_def["label"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  Updating existing notification {existing.id}")
                existing.message = f"{total_items} items expiring in {bucket_def['label']}"
                existing.metadata_ = metadata
                existing.severity = "critical" if bucket_key in ["expired", "critical"] else "warning"
                existing.read = False 
                existing.dismissed = False # Bring back if dismissed
                existing.updated_at = datetime.utcnow()
            else:
                print(f"  Creating new notification for {bucket_key}")
                new_notif = Notification(
                    type="aggregated_expiry",
                    title=bucket_def["label"],
                    message=f"{total_items} items expiring in {bucket_def['label']}",
                    severity="critical" if bucket_key in ["expired", "critical"] else "warning",
                    metadata_=metadata,
                    uid="AGG",
                    read=False,
                    dismissed=False
                )
                session.add(new_notif)
            
        await session.commit()
    print("Done.")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(process_notifications())
