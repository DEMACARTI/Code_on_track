# backend/app/api/items.py
# Purpose: Item management endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db.session import get_db
from app.models.item import Item
from app.models.engraving import EngravingJob
from app.models.inspection import Inspection
from app.models.user import User, UserRole
from app.schemas.items import ItemCreate, ItemOut, ItemDetail, ItemUpdate, PaginatedItemsResponse
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
        lot_no=item_in.lot_no,
        vendor_id=item_in.vendor_id,
        # quantity not in DB
        warranty_months=item_in.warranty_months,
        manufacture_date=item_in.manufacture_date,
        # qr_image_url not in DB
        status=item_in.status,
        depot=item_in.depot,
        installation_date=item_in.installation_date,
        failure_date=item_in.failure_date
        # metadata_ not in DB
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/", response_model=PaginatedItemsResponse)
async def list_items(
    uid: Optional[str] = None,
    q: Optional[str] = None,
    status: Optional[str] = None,
    component_type: Optional[str] = None,
    vendor_id: Optional[int] = None,
    lot_number: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List items with filters from Supabase database.
    Returns paginated response with total count.
    """
    try:
        # Build base query
        base_query = select(Item).options(selectinload(Item.vendor))

        if uid:
            base_query = base_query.where(Item.uid == uid)
        if q:
            from sqlalchemy import or_
            base_query = base_query.where(
                or_(
                    Item.uid.ilike(f"%{q}%"),
                    Item.lot_no.ilike(f"%{q}%")
                )
            )
        
        if lot_number:
             base_query = base_query.where(Item.lot_no == lot_number)
        
        if status:
            base_query = base_query.where(Item.status == status)
        if component_type:
            base_query = base_query.where(Item.component_type == component_type)
        if vendor_id:
            base_query = base_query.where(Item.vendor_id == vendor_id)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Order by created_at desc and paginate
        if uid:
             # If filtering by UID, ignore pagination conceptually but still return consistent structure
             items_query = base_query
        else:
             items_query = base_query.order_by(Item.created_at.desc())
             items_query = items_query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(items_query)
        items = result.scalars().all()
        
        # Calculate total pages
        total_pages = 1 if uid else (total + page_size - 1) // page_size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        import traceback
        print("CRITICAL ERROR IN LIST_ITEMS:")
        print(traceback.format_exc())
        with open("items_crash.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Crash in list_items: {str(e)}")


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
        select(Item.status, func.count(Item.id))
        .group_by(Item.status)
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
        lot_no=item.lot_no,
        vendor_id=item.vendor_id,
        # quantity=item.quantity,
        warranty_months=item.warranty_months,
        manufacture_date=item.manufacture_date,
        # qr_image_url=item.qr_image_url,
        status=item.status,
        depot=item.depot,
        installation_date=item.installation_date,
        failure_date=item.failure_date,
        # metadata=item.metadata_,
        created_at=item.created_at,
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
    # Update fields if provided
    if item_in.component_type is not None:
        item.component_type = item_in.component_type
    if item_in.lot_no is not None:
        item.lot_no = item_in.lot_no
    if item_in.vendor_id is not None:
        item.vendor_id = item_in.vendor_id
    # if item_in.quantity is not None:
    #     item.quantity = item_in.quantity
    if item_in.warranty_months is not None:
        item.warranty_months = item_in.warranty_months
    if item_in.manufacture_date is not None:
        item.manufacture_date = item_in.manufacture_date
    # if item_in.qr_image_url is not None:
    #     item.qr_image_url = item_in.qr_image_url
    if item_in.status is not None:
        item.status = item_in.status
    if item_in.depot is not None:
        item.depot = item_in.depot
    if item_in.installation_date is not None:
        item.installation_date = item_in.installation_date
    if item_in.failure_date is not None:
        item.failure_date = item_in.failure_date

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


@router.post("/bulk-delete")
async def bulk_delete_items(
    uids: list[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Delete multiple items by their UIDs. Requires ADMIN role.
    """
    if not uids:
        raise HTTPException(status_code=400, detail="No UIDs provided")
    
    result = await db.execute(select(Item).where(Item.uid.in_(uids)))
    items = result.scalars().all()
    
    deleted_count = len(items)
    
    for item in items:
        await db.delete(item)
    
    await db.commit()
    return {
        "message": f"Successfully deleted {deleted_count} item(s)",
        "deleted_count": deleted_count,
        "requested_count": len(uids)
    }


@router.delete("/all")
async def delete_all_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    confirm: str = None
):
    """
    Delete ALL items in the database. Requires ADMIN role and confirmation.
    WARNING: This action cannot be undone!
    """
    if confirm != "DELETE_ALL_ITEMS":
        raise HTTPException(
            status_code=400, 
            detail="Must provide confirmation string 'DELETE_ALL_ITEMS' to proceed"
        )
    
    result = await db.execute(select(func.count(Item.id)))
    total_count = result.scalar()
    
    await db.execute(delete(Item))
    await db.commit()
    
    return {
        "message": f"Successfully deleted all {total_count} item(s)",
        "deleted_count": total_count
    }
