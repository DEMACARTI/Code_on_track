# backend/app/api/reports.py
# Purpose: Analytics endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.db.session import get_db
from app.models.item import Item
from app.models.engraving import Engraving
from app.models.vendor import Vendor
from app.models.user import User
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/summary")
async def get_summary_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard summary metrics.
    """
    # 1. Total Items
    total_items_result = await db.execute(select(func.count(Item.uid)))
    total_items = total_items_result.scalar()

    # 2. Counts by Status
    status_counts_result = await db.execute(
        select(Item.status, func.count(Item.uid)).group_by(Item.status)
    )
    status_counts = {status: count for status, count in status_counts_result.all()}

    # 3. Failures by Vendor (assuming 'failed' status or similar logic)
    # For demo, let's assume status='failed' indicates failure
    failures_by_vendor_result = await db.execute(
        select(Vendor.name, func.count(Item.uid))
        .join(Item, Item.vendor_id == Vendor.id)
        .where(Item.status == 'failed')
        .group_by(Vendor.name)
    )
    failures_by_vendor = [
        {"vendor_name": name, "count": count} 
        for name, count in failures_by_vendor_result.all()
    ]

    # 4. Engravings Last 30 Days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    engravings_result = await db.execute(
        select(func.date(Engraving.created_at), func.count(Engraving.id))
        .where(Engraving.created_at >= thirty_days_ago)
        .group_by(func.date(Engraving.created_at))
        .order_by(func.date(Engraving.created_at))
    )
    engravings_last_30_days = [
        {"date": str(date), "count": count} 
        for date, count in engravings_result.all()
    ]

    # 5. Warranty Expiring in 30 Days (Placeholder logic)
    # Assuming metadata has 'warranty_expiry'
    # Since we use JSONB, this is tricky without specific structure. 
    # Returning 0 for now or mocking if we had data.
    warranty_expiring_in_30_days = 0 
    # Real query would be something like:
    # select count(*) from items where metadata->>'warranty_expiry' between now and now+30d

    return {
        "total_items": total_items,
        "counts_by_status": status_counts,
        "failures_by_vendor": failures_by_vendor,
        "engravings_last_30_days": engravings_last_30_days,
        "warranty_expiring_in_30_days": warranty_expiring_in_30_days
    }
