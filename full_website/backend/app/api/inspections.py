# backend/app/api/inspections.py
# Purpose: Inspection management endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.models.inspection import Inspection
from app.models.item import Item
from app.models.user import User
from app.schemas.inspections import InspectionCreate, InspectionOut, InspectionUpdate
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=InspectionOut)
async def create_inspection(
    inspection_in: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new inspection record in Supabase.
    """
    # Check if item exists
    item_result = await db.execute(select(Item).where(Item.uid == inspection_in.item_uid))
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Item not found")
    
    inspection = Inspection(
        item_uid=inspection_in.item_uid,
        status=inspection_in.status,
        remark=inspection_in.remark,
        inspector_id=inspection_in.inspector_id,
        photo_url=inspection_in.photo_url,
        inspected_at=inspection_in.inspected_at or datetime.utcnow()
    )
    db.add(inspection)
    await db.commit()
    await db.refresh(inspection)
    return inspection


@router.get("/", response_model=List[InspectionOut])
async def list_inspections(
    status: Optional[str] = None,
    item_uid: Optional[str] = None,
    inspector_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List inspections from Supabase with filters.
    """
    query = select(Inspection)

    if status:
        query = query.where(Inspection.status == status)
    if item_uid:
        query = query.where(Inspection.item_uid == item_uid)
    if inspector_id:
        query = query.where(Inspection.inspector_id == inspector_id)

    # Order by created_at desc
    query = query.order_by(Inspection.created_at.desc())
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def get_inspection_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get inspection statistics from Supabase.
    """
    # Total count
    total_result = await db.execute(select(func.count(Inspection.id)))
    total = total_result.scalar()
    
    # Count by status
    status_result = await db.execute(
        select(Inspection.status, func.count(Inspection.id))
        .group_by(Inspection.status)
    )
    status_counts = {status: count for status, count in status_result.all()}
    
    return {
        "total": total,
        "by_status": status_counts
    }


@router.get("/{inspection_id}", response_model=InspectionOut)
async def get_inspection(
    inspection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get inspection details from Supabase.
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return inspection


@router.put("/{inspection_id}", response_model=InspectionOut)
async def update_inspection(
    inspection_id: int,
    inspection_in: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an inspection record in Supabase.
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # Update fields if provided
    if inspection_in.status is not None:
        inspection.status = inspection_in.status
    if inspection_in.remark is not None:
        inspection.remark = inspection_in.remark
    if inspection_in.inspector_id is not None:
        inspection.inspector_id = inspection_in.inspector_id
    if inspection_in.photo_url is not None:
        inspection.photo_url = inspection_in.photo_url
    if inspection_in.inspected_at is not None:
        inspection.inspected_at = inspection_in.inspected_at

    await db.commit()
    await db.refresh(inspection)
    return inspection


@router.delete("/{inspection_id}")
async def delete_inspection(
    inspection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an inspection record from Supabase.
    """
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    await db.delete(inspection)
    await db.commit()
    return {"message": "Inspection deleted successfully"}
