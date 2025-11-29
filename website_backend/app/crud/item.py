"""
CRUD operations for Item model.
"""
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from ..models import ItemStatus

from .. import models, schemas


def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Get an item by ID."""
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_item_by_uid(db: Session, uid: str) -> Optional[models.Item]:
    """Get an item by UID."""
    return db.query(models.Item).filter(models.Item.uid == uid).first()


def update_item_status(
    db: Session, 
    item_id: int, 
    new_status: Union[str, ItemStatus],
    updated_by: Optional[int] = None
) -> Optional[models.Item]:
    """
    Update an item's status.
    
    Args:
        db: Database session
        item_id: ID of the item to update
        new_status: New status value (can be string or ItemStatus enum)
        updated_by: Optional user ID who made the update
        
    Returns:
        Updated item if found, None otherwise
    """
    # Convert string status to enum if needed
    if isinstance(new_status, str):
        try:
            new_status = ItemStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {new_status}"
            )
    
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    db_item.status = new_status
    db_item.updated_at = datetime.utcnow()
    
    if updated_by:
        db_item.updated_by = updated_by
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating item status: {str(e)}"
        )


def get_items(
    db: Session, skip: int = 0, limit: int = 100, 
    status: Optional[models.ItemStatus] = None,
    owner_id: Optional[int] = None
) -> List[models.Item]:
    """Get a list of items with optional filtering."""
    query = db.query(models.Item)
    
    if status is not None:
        query = query.filter(models.Item.status == status)
    
    if owner_id is not None:
        query = query.filter(models.Item.owner_id == owner_id)
    
    return query.offset(skip).limit(limit).all()


def create_item(db: Session, item: schemas.ItemCreate, owner_id: int) -> models.Item:
    """Create a new item."""
    item_data = item.dict(exclude={"vendor_id"})
    if 'item_metadata' not in item_data:
        item_data['item_metadata'] = None
    
    db_item = models.Item(
        **item_data,
        owner_id=owner_id,
        vendor_id=item.vendor_id if hasattr(item, 'vendor_id') else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError as e:
        db.rollback()
        if "uid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item with this UID already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating item"
        )


def update_item(
    db: Session, db_item: models.Item, item_update: schemas.ItemUpdate
) -> models.Item:
    """Update an item's information."""
    update_data = item_update.dict(exclude_unset=True)
    
    # Handle item_metadata specifically to avoid None overwrites
    if 'item_metadata' in update_data and update_data['item_metadata'] is None:
        if db_item.item_metadata is not None:
            # Only update if the existing value is not None and we're not explicitly setting it to None
            update_data.pop('item_metadata')
    
    # Update the updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError as e:
        db.rollback()
        if "uid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="UID already in use"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating item"
        )


def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item by ID."""
    db_item = get_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        db.delete(db_item)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting item: {str(e)}"
        )
