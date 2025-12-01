"""
Dashboard routes for the IRF QR tracking system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List
from datetime import datetime, timedelta

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get summary data for the dashboard.
    
    Returns:
        - total_items: Total number of items
        - by_status: Count of items by status
        - warranty_expiring_soon: Number of items with warranty expiring in next 30 days
        - recent_failures: Number of failed engraving jobs in last 7 days
    """
    # Total items count
    total_items = db.query(models.Item).count()
    
    # Count by status
    status_counts = (
        db.query(
            models.Item.status,
            func.count(models.Item.id).label('count')
        )
        .group_by(models.Item.status)
        .all()
    )
    by_status = {status: count for status, count in status_counts}
    
    # Items with warranty expiring in next 30 days
    warranty_expiring_soon = (
        db.query(models.Item)
        .filter(
            models.Item.warranty_expiry.between(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            )
        )
        .count()
    )
    
    # Recent failures (last 7 days)
    recent_failures = (
        db.query(models.EngraveJob)
        .filter(
            models.EngraveJob.status == "failed",
            models.EngraveJob.updated_at >= datetime.utcnow() - timedelta(days=7)
        )
        .count()
    )
    
    return {
        "total_items": total_items,
        "by_status": by_status,
        "warranty_expiring_soon": warranty_expiring_soon,
        "recent_failures": recent_failures
    }
