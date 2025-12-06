from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.vendor import Vendor
from app.models.item import Item
from app.schemas.vendors import VendorCreate, VendorUpdate, VendorOut
from app.api.dependencies import require_role
from app.models.user import UserRole

router = APIRouter()

# Dependencies
require_admin = require_role([UserRole.ADMIN])
require_viewer_or_admin = require_role([UserRole.ADMIN, UserRole.VIEWER])

@router.get("/", response_model=List[VendorOut], dependencies=[Depends(require_viewer_or_admin)])
async def list_vendors(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    
    # Subquery to count items per vendor
    items_count_subquery = (
        select(Item.vendor_id, func.count(Item.uid).label("count"))
        .group_by(Item.vendor_id)
        .subquery()
    )

    query = select(Vendor, func.coalesce(items_count_subquery.c.count, 0).label("items_count"))\
        .outerjoin(items_count_subquery, Vendor.id == items_count_subquery.c.vendor_id)

    if q:
        query = query.where(Vendor.name.ilike(f"%{q}%"))
    
    query = query.order_by(desc(Vendor.created_at)).offset(skip).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Map result to schema
    vendors = []
    for row in rows:
        vendor, count = row
        # Manually construct to handle the extra field
        vendor_dict = {
            "id": vendor.id,
            "name": vendor.name,
            "contact_info": vendor.contact_info,
            "metadata": vendor.metadata_,
            "created_at": vendor.created_at,
            "is_active": vendor.is_active,
            "items_count": count
        }
        vendors.append(VendorOut(**vendor_dict))
        
    return vendors

@router.post("/", response_model=VendorOut, dependencies=[Depends(require_admin)])
async def create_vendor(
    vendor_in: VendorCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if name exists
    result = await db.execute(select(Vendor).where(Vendor.name == vendor_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Vendor with this name already exists")

    vendor = Vendor(
        name=vendor_in.name,
        contact_info=vendor_in.contact_info,
        metadata_=vendor_in.metadata
    )
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    
    # Return with 0 items count
    return VendorOut(
        id=vendor.id,
        name=vendor.name,
        contact_info=vendor.contact_info,
        metadata=vendor.metadata_,
        created_at=vendor.created_at,
        is_active=vendor.is_active,
        items_count=0
    )

@router.get("/{id}", response_model=VendorOut, dependencies=[Depends(require_viewer_or_admin)])
async def get_vendor(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    # Get vendor and item count
    items_count_subquery = (
        select(func.count(Item.uid))
        .where(Item.vendor_id == id)
        .scalar_subquery()
    )
    
    query = select(Vendor, items_count_subquery.label("items_count")).where(Vendor.id == id)
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    vendor, count = row
    return VendorOut(
        id=vendor.id,
        name=vendor.name,
        contact_info=vendor.contact_info,
        metadata=vendor.metadata_,
        created_at=vendor.created_at,
        is_active=vendor.is_active,
        items_count=count
    )

@router.put("/{id}", response_model=VendorOut, dependencies=[Depends(require_admin)])
async def update_vendor(
    id: int,
    vendor_in: VendorUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vendor).where(Vendor.id == id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    if vendor_in.name is not None:
        # Check uniqueness if name changed
        if vendor_in.name != vendor.name:
            existing = await db.execute(select(Vendor).where(Vendor.name == vendor_in.name))
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Vendor name already taken")
        vendor.name = vendor_in.name
        
    if vendor_in.contact_info is not None:
        vendor.contact_info = vendor_in.contact_info
    if vendor_in.metadata is not None:
        vendor.metadata_ = vendor_in.metadata
    if vendor_in.is_active is not None:
        vendor.is_active = vendor_in.is_active
        
    await db.commit()
    await db.refresh(vendor)
    
    # Get count for response
    count_result = await db.execute(
        select(func.count(Item.uid)).where(Item.vendor_id == id)
    )
    count = count_result.scalar()
    
    return VendorOut(
        id=vendor.id,
        name=vendor.name,
        contact_info=vendor.contact_info,
        metadata=vendor.metadata_,
        created_at=vendor.created_at,
        is_active=vendor.is_active,
        items_count=count
    )

@router.delete("/{id}", dependencies=[Depends(require_admin)])
async def delete_vendor(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vendor).where(Vendor.id == id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    vendor.is_active = False
    await db.commit()
    return status.HTTP_204_NO_CONTENT
