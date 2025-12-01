# backend/app/api/items.py
# Purpose: Item management endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.session import get_db
from app.models.item import Item
from app.models.user import User, UserRole
from app.schemas.items import ItemCreate, ItemOut, ItemDetail
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

    item = Item(**item_in.model_dump())
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
    List items with filters.
    """
    query = select(Item)

    if q:
        query = query.where(Item.uid.ilike(f"%{q}%"))
    if status:
        query = query.where(Item.status == status)
    if component_type:
        query = query.where(Item.component_type == component_type)
    if vendor_id:
        query = query.where(Item.vendor_id == vendor_id)

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{uid}", response_model=ItemDetail)
async def get_item(
    uid: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get item details with recent history.
    """
    query = select(Item).where(Item.uid == uid).options(
        selectinload(Item.events),
        selectinload(Item.engravings)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Sort events and engravings in memory for now (or could do in query)
    # Ideally we'd limit these in the query but selectinload makes that tricky without subqueries
    item.events.sort(key=lambda x: x.created_at, reverse=True)
    item.events = item.events[:50]
    
    item.engravings.sort(key=lambda x: x.created_at, reverse=True)
    item.engravings = item.engravings[:50]

    return item
