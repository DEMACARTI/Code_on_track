# backend/app/api/items.py
# Purpose: Item management endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.session import get_db
from app.models.item import Item
from app.models.engraving import EngravingJob
from app.models.inspection import Inspection
from app.models.user import User, UserRole
from app.schemas.items import ItemCreate, ItemOut, ItemDetail, ItemUpdate
from app.api.dependencies import require_role, get_current_active_user

router = APIRouter()


@router.post("/", response_model=ItemOut)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SERVICE]))
):
    """
    Create a new item. Requires ADMIN or SERVICE role.
    """
    # Check if item already exists
    result = await db.execute(select(Item).where(Item.uid == item_in.uid))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Item with this UID already exists")

    item = Item(
        uid=item_in.uid,
        component_type=item_in.component_type,
        lot_number=item_in.lot_number,
        vendor_id=item_in.vendor_id,
        quantity=item_in.quantity,
        warranty_years=item_in.warranty_years,
        manufacture_date=item_in.manufacture_date,
        qr_image_url=item_in.qr_image_url,
        current_status=item_in.current_status,
        metadata_=item_in.metadata
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/", response_model=List[ItemOut])
async def list_items(
    q: Optional[str] = None,
    status: Optional[str] = None,
    component_type: Optional[str] = None,
    vendor_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List items with filters from Supabase database.
    """
    query = select(Item)

    if q:
        query = query.where(Item.uid.ilike(f"%{q}%"))
    if status:
        query = query.where(Item.current_status == status)
    if component_type:
        query = query.where(Item.component_type == component_type)
    if vendor_id:
        query = query.where(Item.vendor_id == vendor_id)

    # Order by created_at desc
    query = query.order_by(Item.created_at.desc())
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats")
async def get_items_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get item statistics from Supabase database.
    """
    # Total items count
    total_result = await db.execute(select(func.count(Item.id)))
    total_items = total_result.scalar()
    
    # Count by status
    status_result = await db.execute(
        select(Item.current_status, func.count(Item.id))
        .group_by(Item.current_status)
    )
    status_counts = {status: count for status, count in status_result.all()}
    
    # Count by component type
    type_result = await db.execute(
        select(Item.component_type, func.count(Item.id))
        .group_by(Item.component_type)
    )
    type_counts = {ctype: count for ctype, count in type_result.all()}
    
    return {
        "total_items": total_items,
        "by_status": status_counts,
        "by_component_type": type_counts
    }


@router.get("/{uid}", response_model=ItemDetail)
async def get_item(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get item details with engravings and inspections from Supabase.
    """
    # Get item
    result = await db.execute(select(Item).where(Item.uid == uid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get engravings for this item
    engravings_result = await db.execute(
        select(EngravingJob)
        .where(EngravingJob.item_uid == uid)
        .order_by(EngravingJob.created_at.desc())
        .limit(50)
    )
    engravings = engravings_result.scalars().all()
    
    # Get inspections for this item
    inspections_result = await db.execute(
        select(Inspection)
        .where(Inspection.item_uid == uid)
        .order_by(Inspection.created_at.desc())
        .limit(50)
    )
    inspections = inspections_result.scalars().all()
    
    # Build response
    return ItemDetail(
        id=item.id,
        uid=item.uid,
        component_type=item.component_type,
        lot_number=item.lot_number,
        vendor_id=item.vendor_id,
        quantity=item.quantity,
        warranty_years=item.warranty_years,
        manufacture_date=item.manufacture_date,
        qr_image_url=item.qr_image_url,
        current_status=item.current_status,
        metadata=item.metadata_,
        created_at=item.created_at,
        updated_at=item.updated_at,
        engravings=engravings,
        inspections=inspections
    )


@router.put("/{uid}", response_model=ItemOut)
async def update_item(
    uid: str,
    item_in: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SERVICE]))
):
    """
    Update an item. Requires ADMIN or SERVICE role.
    """
    result = await db.execute(select(Item).where(Item.uid == uid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields if provided
    if item_in.component_type is not None:
        item.component_type = item_in.component_type
    if item_in.lot_number is not None:
        item.lot_number = item_in.lot_number
    if item_in.vendor_id is not None:
        item.vendor_id = item_in.vendor_id
    if item_in.quantity is not None:
        item.quantity = item_in.quantity
    if item_in.warranty_years is not None:
        item.warranty_years = item_in.warranty_years
    if item_in.manufacture_date is not None:
        item.manufacture_date = item_in.manufacture_date
    if item_in.qr_image_url is not None:
        item.qr_image_url = item_in.qr_image_url
    if item_in.current_status is not None:
        item.current_status = item_in.current_status
    if item_in.metadata is not None:
        item.metadata_ = item_in.metadata

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{uid}")
async def delete_item(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete an item. Requires ADMIN role.
    """
    result = await db.execute(select(Item).where(Item.uid == uid))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Item deleted successfully"}
