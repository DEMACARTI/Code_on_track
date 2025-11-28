"""
Item routes for the IRF QR tracking system.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new item.
    
    - **uid**: Unique identifier for the item (required)
    - **name**: Name of the item (required)
    - **description**: Optional description
    - **status**: Item status (default: in_stock)
    - **vendor_id**: ID of the vendor (optional)
    - **purchase_date**: When the item was purchased (optional)
    - **warranty_expiry**: When the warranty expires (optional)
    - **location**: Current location of the item (optional)
    
    Returns the created item.
    """
    # Check if UID already exists
    db_item = crud.get_item_by_uid(db, uid=item.uid)
    if db_item:
        raise HTTPException(
            status_code=400,
            detail="Item with this UID already exists"
        )
    
    # If vendor_id is provided, verify it exists
    if item.vendor_id is not None:
        db_vendor = crud.get_vendor(db, vendor_id=item.vendor_id)
        if not db_vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {item.vendor_id} not found"
            )
    
    # Create the item
    return crud.create_item(db=db, item=item)

@router.get("/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.ItemStatus] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a list of items with optional filtering.
    
    - **skip**: Number of items to skip (pagination)
    - **limit**: Maximum number of items to return (pagination)
    - **status**: Filter by item status
    - **vendor_id**: Filter by vendor ID
    
    Returns a list of items.
    """
    items = crud.get_items(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        vendor_id=vendor_id
    )
    return items

@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific item by ID.
    
    - **item_id**: ID of the item to retrieve
    
    Returns the item details.
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update an existing item.
    
    - **item_id**: ID of the item to update
    - **name**: New name for the item (optional)
    - **description**: New description (optional)
    - **status**: New status (optional)
    - **vendor_id**: New vendor ID (optional)
    - **purchase_date**: New purchase date (optional)
    - **warranty_expiry**: New warranty expiry date (optional)
    - **location**: New location (optional)
    
    Returns the updated item.
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # If updating vendor_id, verify it exists
    if item_update.vendor_id is not None:
        db_vendor = crud.get_vendor(db, vendor_id=item_update.vendor_id)
        if not db_vendor:
            raise HTTPException(
                status_code=404,
                detail=f"Vendor with ID {item_update.vendor_id} not found"
            )
    
    return crud.update_item(db=db, db_item=db_item, item_update=item_update)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete an item.
    
    - **item_id**: ID of the item to delete
    
    Returns 204 No Content on success.
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    crud.delete_item(db=db, item_id=item_id)
    return None

@router.get("/uid/{uid}", response_model=schemas.Item)
def read_item_by_uid(
    uid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get an item by its UID.
    
    - **uid**: UID of the item to retrieve
    
    Returns the item details.
    """
    db_item = crud.get_item_by_uid(db, uid=uid)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.get("/{item_id}/events", response_model=List[schemas.Event])
def get_item_events(
    item_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get events for a specific item.
    
    - **item_id**: ID of the item
    - **skip**: Number of events to skip (pagination)
    - **limit**: Maximum number of events to return (pagination)
    
    Returns a list of events for the item.
    """
    # Verify item exists
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return crud.get_events_for_item(db, item_id=item_id, skip=skip, limit=limit)
