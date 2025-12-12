# backend/app/api/engravings.py
# Purpose: Engraving management endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.models.engraving import EngravingJob, EngravingHistory
from app.models.item import Item
from app.models.user import User
from app.schemas.engravings import EngravingCreate, EngravingOut, EngravingUpdateStatus, EngravingDetailOut, EngravingHistoryOut
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=EngravingOut)
async def create_engraving(
    engraving_in: EngravingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new engraving job in Supabase.
    """
    # Check if item exists
    item_result = await db.execute(select(Item).where(Item.uid == engraving_in.item_uid))
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Item not found")
    
    engraving = EngravingJob(
        item_uid=engraving_in.item_uid,
        svg_url=engraving_in.svg_url,
        status="pending",
        attempts=0,
        max_attempts=engraving_in.max_attempts
    )
    db.add(engraving)
    await db.commit()
    await db.refresh(engraving)
    
    # Add initial history entry
    history = EngravingHistory(
        engraving_job_id=engraving.id,
        status="pending",
        message="Engraving job created"
    )
    db.add(history)
    await db.commit()
    
    return engraving


@router.get("/", response_model=List[EngravingOut])
async def list_engravings(
    status: Optional[str] = None,
    item_uid: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List engraving jobs from Supabase with filters.
    """
    query = select(EngravingJob)

    if status:
        query = query.where(EngravingJob.status == status)
    if item_uid:
        query = query.where(EngravingJob.item_uid == item_uid)

    # Order by created_at desc
    query = query.order_by(EngravingJob.created_at.desc())
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/pending", response_model=List[EngravingOut])
async def get_pending_engravings(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get pending engraving jobs ready for processing.
    """
    query = select(EngravingJob).where(
        EngravingJob.status == "pending"
    ).order_by(EngravingJob.created_at.asc()).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def get_engraving_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get engraving statistics from Supabase.
    """
    # Total count
    total_result = await db.execute(select(func.count(EngravingJob.id)))
    total = total_result.scalar()
    
    # Count by status
    status_result = await db.execute(
        select(EngravingJob.status, func.count(EngravingJob.id))
        .group_by(EngravingJob.status)
    )
    status_counts = {status: count for status, count in status_result.all()}
    
    return {
        "total": total,
        "by_status": status_counts
    }


@router.get("/{job_id}", response_model=EngravingDetailOut)
async def get_engraving(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get engraving job details with history from Supabase.
    """
    result = await db.execute(select(EngravingJob).where(EngravingJob.id == job_id))
    engraving = result.scalar_one_or_none()

    if not engraving:
        raise HTTPException(status_code=404, detail="Engraving job not found")
    
    # Get history
    history_result = await db.execute(
        select(EngravingHistory)
        .where(EngravingHistory.engraving_job_id == job_id)
        .order_by(EngravingHistory.created_at.desc())
    )
    history = history_result.scalars().all()
    
    return EngravingDetailOut(
        id=engraving.id,
        item_uid=engraving.item_uid,
        status=engraving.status,
        svg_url=engraving.svg_url,
        attempts=engraving.attempts,
        max_attempts=engraving.max_attempts,
        created_at=engraving.created_at,
        started_at=engraving.started_at,
        completed_at=engraving.completed_at,
        error_message=engraving.error_message,
        history=history
    )


@router.put("/{job_id}/status", response_model=EngravingOut)
async def update_engraving_status(
    job_id: int,
    status_in: EngravingUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update engraving job status in Supabase.
    """
    result = await db.execute(select(EngravingJob).where(EngravingJob.id == job_id))
    engraving = result.scalar_one_or_none()

    if not engraving:
        raise HTTPException(status_code=404, detail="Engraving job not found")

    old_status = engraving.status
    engraving.status = status_in.status
    
    # Update timestamps based on status
    if status_in.status == "in_progress" and not engraving.started_at:
        engraving.started_at = datetime.utcnow()
        engraving.attempts += 1
    elif status_in.status in ["completed", "failed"]:
        engraving.completed_at = datetime.utcnow()
        if status_in.error_message:
            engraving.error_message = status_in.error_message
    
    # Add history entry
    history = EngravingHistory(
        engraving_job_id=job_id,
        status=status_in.status,
        message=f"Status changed from {old_status} to {status_in.status}"
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(engraving)
    return engraving


@router.post("/{job_id}/retry", response_model=EngravingOut)
async def retry_engraving(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retry a failed engraving job.
    """
    result = await db.execute(select(EngravingJob).where(EngravingJob.id == job_id))
    engraving = result.scalar_one_or_none()

    if not engraving:
        raise HTTPException(status_code=404, detail="Engraving job not found")
    
    if engraving.status != "failed":
        raise HTTPException(status_code=400, detail="Can only retry failed jobs")
    
    if engraving.attempts >= engraving.max_attempts:
        raise HTTPException(status_code=400, detail="Maximum retry attempts reached")
    
    engraving.status = "pending"
    engraving.error_message = None
    engraving.started_at = None
    engraving.completed_at = None
    
    # Add history entry
    history = EngravingHistory(
        engraving_job_id=job_id,
        status="pending",
        message=f"Job retried (attempt {engraving.attempts + 1})"
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(engraving)
    return engraving
