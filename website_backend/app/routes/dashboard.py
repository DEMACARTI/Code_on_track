"""
Dashboard routes for the IRF QR tracking system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user

router = APIRouter()

@router.get("/summary", response_model=schemas.DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get summary data for the dashboard.
    
    Returns:
        - Total number of items
        - Count of items by status
        - Number of items with warranty expiring soon (next 30 days)
        - Vendor fail rates for engraving jobs
    """
    return crud.get_dashboard_summary(db)

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get recent activity across the system.
    
    - **limit**: Maximum number of activities to return (default: 10)
    
    Returns a list of recent activities including item updates, events, and engraving jobs.
    """
    # Get recent events
    recent_events = (
        db.query(models.Event)
        .order_by(models.Event.created_at.desc())
        .limit(limit)
        .all()
    )
    
    # Get recent engraving jobs
    recent_jobs = (
        db.query(models.EngraveJob)
        .order_by(models.EngraveJob.updated_at.desc())
        .limit(limit)
        .all()
    )
    
    # Get recent item updates
    recent_items = (
        db.query(models.Item)
        .order_by(models.Item.updated_at.desc())
        .limit(limit)
        .all()
    )
    
    # Combine and sort all activities
    activities = []
    
    for event in recent_events:
        activities.append({
            "type": "event",
            "id": event.id,
            "item_id": event.item_id,
            "event_type": event.event_type,
            "description": event.description,
            "created_at": event.created_at,
            "created_by": event.created_by
        })
    
    for job in recent_jobs:
        activities.append({
            "type": "engrave_job",
            "id": job.id,
            "item_id": job.item_id,
            "status": job.status,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        })
    
    for item in recent_items:
        activities.append({
            "type": "item_update",
            "id": item.id,
            "uid": item.uid,
            "name": item.name,
            "status": item.status,
            "updated_at": item.updated_at
        })
    
    # Sort by timestamp in descending order
    activities.sort(key=lambda x: x.get('updated_at', x.get('created_at')), reverse=True)
    
    return activities[:limit]

@router.get("/warranty-expiring")
async def get_warranty_expiring(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get items with warranty expiring soon.
    
    - **days**: Number of days to look ahead for expiring warranties (default: 30)
    
    Returns a list of items with warranties expiring within the specified number of days.
    """
    today = datetime.utcnow().date()
    future_date = today + timedelta(days=days)
    
    expiring_items = (
        db.query(models.Item)
        .filter(
            models.Item.warranty_expiry.isnot(None),
            models.Item.warranty_expiry >= today,
            models.Item.warranty_expiry <= future_date
        )
        .order_by(models.Item.warranty_expiry)
        .all()
    )
    
    return [
        {
            "id": item.id,
            "uid": item.uid,
            "name": item.name,
            "warranty_expiry": item.warranty_expiry,
            "vendor": item.vendor.name if item.vendor else None,
            "days_until_expiry": (item.warranty_expiry - today).days
        }
        for item in expiring_items
    ]

@router.get("/vendor-metrics")
async def get_vendor_metrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get metrics for vendors.
    
    Returns statistics about vendors including item counts, failure rates, etc.
    """
    # Get vendor item counts
    vendor_item_counts = (
        db.query(
            models.Vendor.name,
            models.Vendor.id,
            func.count(models.Item.id).label('item_count')
        )
        .outerjoin(models.Item)
        .group_by(models.Vendor.id, models.Vendor.name)
        .all()
    )
    
    # Get vendor fail rates from dashboard summary
    summary = crud.get_dashboard_summary(db)
    
    # Combine the data
    vendor_metrics = []
    for vendor in vendor_item_counts:
        vendor_metrics.append({
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "item_count": vendor.item_count,
            "fail_rate": summary.vendor_fail_rates.get(vendor.name, 0)
        })
    
    return vendor_metrics
