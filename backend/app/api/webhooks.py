# backend/app/api/webhooks.py
# Purpose: Secure webhook endpoints
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hmac
import hashlib
import time
from app.core.config import settings
from app.db.session import get_db
from app.models.engraving import Engraving
from app.models.item import Item
from app.models.item_event import ItemEvent

router = APIRouter()

async def verify_signature(
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
    x_timestamp: str = Header(..., alias="X-Timestamp")
):
    # 1. Verify timestamp freshness (5 minutes)
    try:
        timestamp = float(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    if time.time() - timestamp > 300:
        raise HTTPException(status_code=400, detail="Request expired")

    # 2. Compute signature
    body = await request.body()
    message = f"{x_timestamp}.".encode() + body
    secret = settings.WEBHOOK_SECRET.encode()
    computed_signature = hmac.new(secret, message, hashlib.sha256).hexdigest()

    # 3. Compare signatures
    if not hmac.compare_digest(computed_signature, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/appa/engraving")
async def appa_engraving_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_signature)
):
    payload = await request.json()
    job_id = payload.get("job_id")
    status = payload.get("status")
    
    # Logic to update engraving or create if not exists (simplified)
    # Assuming payload matches what we need
    
    # Check if job_id exists
    result = await db.execute(select(Engraving).where(Engraving.job_id == job_id))
    engraving = result.scalar_one_or_none()
    
    if engraving:
        engraving.status = status
        engraving.raw_payload = payload
    else:
        # Create new (orphan logic handled in regular endpoint, here we just create)
        engraving = Engraving(
            job_id=job_id,
            status=status,
            raw_payload=payload,
            orphan=True # Default to orphan if coming from webhook without item context?
                        # Or try to find item_uid in payload?
        )
        if "item_uid" in payload:
             item_result = await db.execute(select(Item).where(Item.uid == payload["item_uid"]))
             if item_result.scalar_one_or_none():
                 engraving.item_uid = payload["item_uid"]
                 engraving.orphan = False
             else:
                 engraving.item_uid = None # Keep orphan true
        
        db.add(engraving)
    
    await db.commit()
    return {"status": "accepted", "id": job_id}

@router.post("/appb/status")
async def appb_status_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_signature)
):
    payload = await request.json()
    item_uid = payload.get("item_uid")
    event_type = payload.get("event_type")
    
    # Check if item exists
    result = await db.execute(select(Item).where(Item.uid == item_uid))
    item = result.scalar_one_or_none()
    
    if not item:
        # If item doesn't exist, we might log error or ignore. 
        # For now, let's return accepted but do nothing or create item?
        # Requirement says "forward payload to engraving/events handlers".
        # If item missing, we can't attach event.
        return {"status": "ignored", "reason": "item not found"}

    event = ItemEvent(
        item_uid=item_uid,
        event_type=event_type,
        payload=payload,
        performed_by="AppB_Webhook",
        external_id=payload.get("external_id")
    )
    db.add(event)
    await db.commit()
    
    return {"status": "accepted", "id": str(event.id)}
