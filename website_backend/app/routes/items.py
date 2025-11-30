"""
Items API endpoints for managing railway components.

Example curl commands:

# Create a single item
curl -X POST "http://localhost:8000/api/items" \
  -H "Content-Type: application/json" \
  -d '{"component_type": "Bearing", "lot_number": "LOT123", "vendor_id": 1, "warranty_years": 2, "manufacture_date": "2023-01-15T00:00:00", "quantity": 1}'

# Create multiple items
curl -X POST "http://localhost:8000/api/items" \
  -H "Content-Type: application/json" \
  -d '{"component_type": "Bolt", "lot_number": "BOLT456", "vendor_id": 2, "warranty_years": 5, "manufacture_date": "2023-01-15T00:00:00", "quantity": 10}'

# List items with filters
curl "http://localhost:8000/api/items?component_type=Bearing&limit=5"

# Get item by UID
curl "http://localhost:8000/api/items/ABC123"

# Update item status
curl -X PATCH "http://localhost:8000/api/items/ABC123/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "installed", "metadata": {"location": "Engine Bay 1"}}'
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/items", tags=["Items"])
logger = logging.getLogger(__name__)

class ItemStatusUpdate(schemas.BaseModel):
    status: schemas.ItemStatus
    metadata: Optional[dict] = None

@router.post(
    "/",
    response_model=schemas.ItemsList,
    status_code=status.HTTP_201_CREATED,
    summary="Create one or more items"
)
def create_items(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create one or more items.
    
    - If quantity = 1, returns a single item in the list
    - If quantity > 1, creates multiple items with sequential UIDs
    """
    if item.quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1"
        )
    
    created_items = []
    for _ in range(item.quantity):
        db_item = crud.create_item(db=db, item=item, owner_id=current_user.id)
        created_items.append(db_item)
    
    logger.info(f"Created {len(created_items)} items")
    return {
        "items": created_items,
        "total": len(created_items)
    }

@router.get(
    "/",
    response_model=schemas.ItemsList,
    summary="List items with optional filtering"
)
def list_items(
    skip: int = 0,
    limit: int = 50,
    component_type: Optional[str] = None,
    vendor_id: Optional[int] = None,
    item_status: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List items with pagination and filtering.
    """
    filters = {}
    if component_type:
        filters["component_type"] = component_type
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if item_status:
        filters["current_status"] = item_status
    
    # Convert status string to enum if provided
    status_enum = None
    if item_status:
        try:
            status_enum = models.ItemStatus(item_status)
        except ValueError:
            # If invalid status, return empty list or raise error? 
            # For filtering, maybe just return empty list or ignore?
            # Let's raise 400 for better DX
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {item_status}"
            )

    items = crud.get_items(
        db=db,
        skip=skip,
        limit=min(limit, 100),  # Cap limit at 100
        status=status_enum,
        # filters=filters # TODO: Implement advanced filtering in CRUD if needed
    )
    # Mock total count for now as get_items doesn't return it
    total = len(items)
    
    return {
        "items": items,
        "total": total
    }

@router.get(
    "/{uid}",
    response_model=schemas.ItemRead,
    responses={
        404: {"description": "Item not found"}
    },
    summary="Get item by UID"
)
def get_item(
    uid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a single item by its UID.
    """
    db_item = crud.get_item_by_uid(db, uid=uid)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with UID {uid} not found"
        )
    return db_item

@router.patch(
    "/{uid}/status",
    response_model=schemas.ItemRead,
    responses={
        400: {"description": "Invalid status or metadata"},
        404: {"description": "Item not found"}
    },
    summary="Update item status"
)
def update_status(
    uid: str,
    status_update: ItemStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update an item's status and optional metadata.
    """
    # Verify item exists
    db_item = crud.get_item_by_uid(db, uid=uid)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with UID {uid} not found"
        )
    
    # Update status
    # Update status
    updated_item = crud.update_item_status(
        db=db,
        item_id=db_item.id,
        new_status=status_update.status,
        updated_by=current_user.id
    )
    
    # Update metadata if provided
    if status_update.metadata:
        # Create a partial update for metadata
        # We need to fetch the item again or update the object
        # For now let's use update_item
        item_update = schemas.ItemUpdate(item_metadata=status_update.metadata)
        updated_item = crud.update_item(db=db, db_item=updated_item, item_update=item_update)
    
    logger.info(f"Updated status for item {uid} to {status_update.status}")
    return updated_item

