# backend/app/api/engravings.py
# Purpose: Engraving management endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db.session import get_db
from app.models.engraving import Engraving
from app.models.item import Item
from app.models.user import User
from app.schemas.engravings import EngravingCreate, EngravingOut, EngravingUpdateStatus
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.post("/", response_model=EngravingOut)
async def create_engraving(
    engraving_in: EngravingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new engraving.
    If item_uid is provided but not found, mark as orphan.
    """
    # Check if job_id already exists
    result = await db.execute(select(Engraving).where(Engraving.job_id == engraving_in.job_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Engraving job_id already exists")

    orphan = False
    if engraving_in.item_uid:
        item_result = await db.execute(select(Item).where(Item.uid == engraving_in.item_uid))
        if not item_result.scalar_one_or_none():
            orphan = True
            # We keep the item_uid in the record even if it doesn't exist in items table?
            # Foreign key constraint will fail if we try to insert a non-existent item_uid.
            # So if it's orphan, we should probably set item_uid to None or handle it differently.
            # The prompt says "if item not found, mark orphan=true".
            # The model has `item_uid` as FK. So we must set it to None if it doesn't exist.
            engraving_in.item_uid = None
    
    engraving = Engraving(
        job_id=engraving_in.job_id,
        item_uid=engraving_in.item_uid,
        status=engraving_in.status,
        raw_payload=engraving_in.raw_payload,
        orphan=orphan
    )
    db.add(engraving)
    await db.commit()
    await db.refresh(engraving)
    return engraving

@router.get("/", response_model=List[EngravingOut])
async def list_engravings(
    orphan: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List engravings with filters.
    """
    query = select(Engraving)

    if orphan is not None:
        query = query.where(Engraving.orphan == orphan)

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/{job_id}/status", response_model=EngravingOut)
async def update_engraving_status(
    job_id: str,
    status_in: EngravingUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update engraving status.
    """
    result = await db.execute(select(Engraving).where(Engraving.job_id == job_id))
    engraving = result.scalar_one_or_none()

    if not engraving:
        raise HTTPException(status_code=404, detail="Engraving not found")

    engraving.status = status_in.status
    await db.commit()
    await db.refresh(engraving)
    return engraving
