# backend/app/api/webhooks.py
# Purpose: Secure webhook endpoints - aligned with Supabase database
# Author: Antigravity

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hmac
import hashlib
import time
from datetime import datetime
from app.core.config import settings
from app.db.session import get_db
from app.models.engraving import EngravingJob, EngravingHistory
from app.models.item import Item
from app.models.inspection import Inspection

router = APIRouter()


async def verify_signature(
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
    x_timestamp: str = Header(..., alias="X-Timestamp")
):
    """Verify webhook signature for security."""
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
    """
    Webhook to receive engraving updates from App A (Generation App).
    """
    payload = await request.json()
    item_uid = payload.get("item_uid")
    status = payload.get("status")
    svg_url = payload.get("svg_url")
    error_message = payload.get("error_message")
    
    if not item_uid:
        raise HTTPException(status_code=400, detail="item_uid is required")
    
    # Check if engraving job exists for this item
    result = await db.execute(
        select(EngravingJob).where(EngravingJob.item_uid == item_uid)
        .order_by(EngravingJob.created_at.desc())
    )
    engraving = result.scalar_one_or_none()
    
    if engraving:
        # Update existing job
        old_status = engraving.status
        engraving.status = status
        
        if status == "in_progress" and not engraving.started_at:
            engraving.started_at = datetime.utcnow()
            engraving.attempts += 1
        elif status in ["completed", "failed"]:
            engraving.completed_at = datetime.utcnow()
        
        if error_message:
            engraving.error_message = error_message
        
        # Add history entry
        history = EngravingHistory(
            engraving_job_id=engraving.id,
            status=status,
            message=f"Webhook update: {old_status} -> {status}"
        )
        db.add(history)
    else:
        # Create new engraving job
        if not svg_url:
            raise HTTPException(status_code=400, detail="svg_url required for new job")
        
        engraving = EngravingJob(
            item_uid=item_uid,
            status=status or "pending",
            svg_url=svg_url,
            attempts=0,
            max_attempts=3
        )
        db.add(engraving)
        await db.flush()
        
        # Add initial history
        history = EngravingHistory(
            engraving_job_id=engraving.id,
            status=status or "pending",
            message="Created via webhook"
        )
        db.add(history)
    
    await db.commit()
    return {"status": "accepted", "id": engraving.id}


@router.post("/appb/status")
async def appb_status_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_signature)
):
    """
    Webhook to receive status/inspection updates from App B (Mobile App).
    """
    payload = await request.json()
    item_uid = payload.get("item_uid")
    inspection_status = payload.get("status")
    remark = payload.get("remark")
    inspector_id = payload.get("inspector_id")
    photo_url = payload.get("photo_url")
    
    if not item_uid:
        raise HTTPException(status_code=400, detail="item_uid is required")
    
    # Check if item exists
    result = await db.execute(select(Item).where(Item.uid == item_uid))
    item = result.scalar_one_or_none()
    
    if not item:
        return {"status": "ignored", "reason": "item not found"}

    # Create inspection record
    inspection = Inspection(
        item_uid=item_uid,
        status=inspection_status or "inspected",
        remark=remark,
        inspector_id=inspector_id,
        photo_url=photo_url,
        inspected_at=datetime.utcnow()
    )
    db.add(inspection)
    
    # Update item status if provided
    if inspection_status:
        item.current_status = inspection_status
    
    await db.commit()
    
    return {"status": "accepted", "id": inspection.id}


@router.post("/engraving/complete")
async def engraving_complete_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_signature)
):
    """
    Webhook to mark engraving as complete from the engraving machine.
    """
    payload = await request.json()
    job_id = payload.get("job_id")
    success = payload.get("success", True)
    error_message = payload.get("error_message")
    
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")
    
    result = await db.execute(select(EngravingJob).where(EngravingJob.id == job_id))
    engraving = result.scalar_one_or_none()
    
    if not engraving:
        raise HTTPException(status_code=404, detail="Engraving job not found")
    
    old_status = engraving.status
    engraving.status = "completed" if success else "failed"
    engraving.completed_at = datetime.utcnow()
    
    if error_message:
        engraving.error_message = error_message
    
    # Add history entry
    history = EngravingHistory(
        engraving_job_id=job_id,
        status=engraving.status,
        message=f"Engraving {'completed' if success else 'failed'}: {error_message or 'Success'}"
    )
    db.add(history)
    
    # Update item status
    item_result = await db.execute(select(Item).where(Item.uid == engraving.item_uid))
    item = item_result.scalar_one_or_none()
    if item and success:
        item.current_status = "engraved"
    
    await db.commit()
    
    return {"status": "accepted", "engraving_status": engraving.status}
