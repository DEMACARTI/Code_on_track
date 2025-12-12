# backend/app/api/events.py
# Purpose: Event management endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.item_event import ItemEvent
from app.models.item import Item
from app.models.user import User
from app.schemas.events import ItemEventCreate, ItemEventOut
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.post("/items/{uid}/events", response_model=ItemEventOut)
async def create_item_event(
    uid: str,
    event_in: ItemEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Append event to item.
    Idempotent if external_id is provided.
    """
    # Check if item exists
    result = await db.execute(select(Item).where(Item.uid == uid))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Idempotency check
    if event_in.external_id:
        existing_event_result = await db.execute(
            select(ItemEvent).where(ItemEvent.external_id == event_in.external_id)
        )
        existing_event = existing_event_result.scalar_one_or_none()
        if existing_event:
            return existing_event

    event = ItemEvent(
        item_uid=uid,
        event_type=event_in.event_type,
        payload=event_in.payload,
        performed_by=event_in.performed_by,
        external_id=event_in.external_id
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
