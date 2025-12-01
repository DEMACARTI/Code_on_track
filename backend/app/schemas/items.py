# backend/app/schemas/items.py
# Purpose: Item Pydantic models
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ItemEventBase(BaseModel):
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    performed_by: str
    external_id: Optional[str] = None

class ItemEventOut(ItemEventBase):
    id: int
    item_uid: str
    created_at: datetime

    class Config:
        from_attributes = True

class EngravingBase(BaseModel):
    job_id: str
    status: str
    raw_payload: Optional[Dict[str, Any]] = None
    orphan: bool = False

class EngravingOut(EngravingBase):
    id: int
    item_uid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    uid: str
    component_type: str
    vendor_id: Optional[int] = None
    lot_no: str
    status: str
    metadata_: Optional[Dict[str, Any]] = None

class ItemCreate(ItemBase):
    pass

class ItemOut(ItemBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemDetail(ItemOut):
    events: List[ItemEventOut] = []
    engravings: List[EngravingOut] = []
