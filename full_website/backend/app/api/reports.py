# backend/app/api/reports.py
# Purpose: Analytics endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.item import Item
from app.models.engraving import EngravingJob
from app.models.inspection import Inspection
from app.models.user import User
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/summary")
async def get_summary_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard summary metrics from Supabase database.
    """
    # 1. Total Items
    total_items_result = await db.execute(select(func.count(Item.id)))
    total_items = total_items_result.scalar()

    # 2. Counts by Status
    status_counts_result = await db.execute(
        select(Item.current_status, func.count(Item.id)).group_by(Item.current_status)
    )
    status_counts = {status: count for status, count in status_counts_result.all()}

    # 3. Counts by Component Type
    type_counts_result = await db.execute(
        select(Item.component_type, func.count(Item.id)).group_by(Item.component_type)
    )
    type_counts = {ctype: count for ctype, count in type_counts_result.all()}

    # 4. Engraving Stats
    engraving_status_result = await db.execute(
        select(EngravingJob.status, func.count(EngravingJob.id))
        .group_by(EngravingJob.status)
    )
    engraving_counts = {status: count for status, count in engraving_status_result.all()}

    # 5. Engravings Last 30 Days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    engravings_result = await db.execute(
        select(func.date(EngravingJob.created_at), func.count(EngravingJob.id))
        .where(EngravingJob.created_at >= thirty_days_ago)
        .group_by(func.date(EngravingJob.created_at))
        .order_by(func.date(EngravingJob.created_at))
    )
    engravings_last_30_days = [
        {"date": str(date), "count": count} 
        for date, count in engravings_result.all()
    ]

    # 6. Inspection Stats
    inspection_status_result = await db.execute(
        select(Inspection.status, func.count(Inspection.id))
        .group_by(Inspection.status)
    )
    inspection_counts = {status: count for status, count in inspection_status_result.all()}

    # 7. Total Inspections
    total_inspections_result = await db.execute(select(func.count(Inspection.id)))
    total_inspections = total_inspections_result.scalar()

    # 8. Items with QR codes
    items_with_qr_result = await db.execute(
        select(func.count(Item.id)).where(Item.qr_image_url.isnot(None))
    )
    items_with_qr = items_with_qr_result.scalar()

    # 9. Warranty expiring in 30 days (check warranty_years from manufacture_date)
    warranty_expiring = 0
    try:
        warranty_result = await db.execute(
            select(func.count(Item.id)).where(
                Item.manufacture_date.isnot(None),
                Item.warranty_years.isnot(None),
                func.date(Item.manufacture_date) + (Item.warranty_years * 365) <= func.current_date() + 30,
                func.date(Item.manufacture_date) + (Item.warranty_years * 365) >= func.current_date()
            )
        )
        warranty_expiring = warranty_result.scalar() or 0
    except:
        warranty_expiring = 0

    return {
        "total_items": total_items,
        "items_with_qr": items_with_qr,
        "counts_by_status": status_counts,
        "counts_by_component_type": type_counts,
        "engraving_counts": engraving_counts,
        "engravings_last_30_days": engravings_last_30_days,
        "total_inspections": total_inspections,
        "inspection_counts": inspection_counts,
        "warranty_expiring_in_30_days": warranty_expiring
    }


@router.get("/items/by-vendor")
async def get_items_by_vendor(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get item counts grouped by vendor_id.
    """
    result = await db.execute(
        select(Item.vendor_id, func.count(Item.id))
        .group_by(Item.vendor_id)
        .order_by(func.count(Item.id).desc())
    )
    vendor_counts = [
        {"vendor_id": vendor_id, "count": count} 
        for vendor_id, count in result.all()
    ]
    return {"items_by_vendor": vendor_counts}


@router.get("/engravings/timeline")
async def get_engravings_timeline(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get engraving counts over time.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(func.date(EngravingJob.created_at), func.count(EngravingJob.id))
        .where(EngravingJob.created_at >= start_date)
        .group_by(func.date(EngravingJob.created_at))
        .order_by(func.date(EngravingJob.created_at))
    )
    timeline = [
        {"date": str(date), "count": count} 
        for date, count in result.all()
    ]
    return {"timeline": timeline, "days": days}


@router.get("/inspections/timeline")
async def get_inspections_timeline(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get inspection counts over time.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(func.date(Inspection.created_at), func.count(Inspection.id))
        .where(Inspection.created_at >= start_date)
        .group_by(func.date(Inspection.created_at))
        .order_by(func.date(Inspection.created_at))
    )
    timeline = [
        {"date": str(date), "count": count} 
        for date, count in result.all()
    ]
    return {"timeline": timeline, "days": days}
