from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc

from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationOut, UnreadCount, NotificationUpdateBatch
from app.api.dependencies import require_role
from app.models.user import UserRole
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/unread_count", response_model=UnreadCount)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = select(func.count(Notification.id)).where(
        Notification.read == False,
        Notification.dismissed == False
    )
    result = await db.execute(query)
    count = result.scalar()
    return {"unread_count": count}

@router.get("/", response_model=dict) # Returning dict as wrapper {unread_count, notifications}
async def list_notifications(
    unread: bool = False,
    limit: int = 50,
    filter: Optional[str] = None, # 'expiring'
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Base query
    query = select(Notification).where(Notification.dismissed == False)
    
    if unread:
        query = query.where(Notification.read == False)
    
    if filter == 'expiring':
        query = query.where(Notification.type.in_(['warranty_expiring', 'warranty_expired']))
        
    query = query.order_by(desc(Notification.created_at)).limit(limit)
    
    result = await db.execute(query)
    notifs = result.scalars().all()
    
    # Get unread count (always included based on user spec "Add unread_count to header responses if convenient")
    
    count_query = select(func.count(Notification.id)).where(
        Notification.read == False,
        Notification.dismissed == False
    )
    count_res = await db.execute(count_query)
    unread_count = count_res.scalar()
    
    # Map to schema manually to handle `metadata_` -> `metadata` mapping cleaner
    notif_list = []
    for n in notifs:
        notif_list.append(NotificationOut(
            id=n.id,
            item_id=n.item_id,
            uid=n.uid,
            type=n.type,
            severity=n.severity,
            title=n.title,
            message=n.message,
            metadata=n.metadata_, 
            read=n.read,
            dismissed=n.dismissed,
            created_at=n.created_at,
            updated_at=n.updated_at
        ))

    return {
        "unread_count": unread_count,
        "notifications": notif_list
    }

@router.post("/mark_read", response_model=UnreadCount)
async def mark_read(
    payload: NotificationUpdateBatch,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not payload.ids:
        return await get_unread_count(db, current_user)

    stmt = update(Notification).where(Notification.id.in_(payload.ids)).values(read=True)
    await db.execute(stmt)
    await db.commit()
    
    return await get_unread_count(db, current_user)

@router.post("/dismiss", response_model=UnreadCount)
async def dismiss(
    payload: NotificationUpdateBatch,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not payload.ids:
        return await get_unread_count(db, current_user)

    stmt = update(Notification).where(Notification.id.in_(payload.ids)).values(dismissed=True)
    await db.execute(stmt)
    await db.commit()
    
    return await get_unread_count(db, current_user)

@router.get("/{id}", response_model=NotificationOut)
async def get_notification(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    return NotificationOut(
        id=n.id,
        item_id=n.item_id,
        uid=n.uid,
        type=n.type,
        severity=n.severity,
        title=n.title,
        message=n.message,
        metadata=n.metadata_,
        read=n.read,
        dismissed=n.dismissed,
        created_at=n.created_at,
        updated_at=n.updated_at
    )
