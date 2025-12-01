# backend/app/schemas/events.py
# Purpose: Event Pydantic models
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ItemEventCreate(BaseModel):
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    performed_by: str
    external_id: Optional[str] = None

class ItemEventOut(BaseModel):
    id: int
    item_uid: str
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    performed_by: str
    external_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
