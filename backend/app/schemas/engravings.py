# backend/app/schemas/engravings.py
# Purpose: Engraving Pydantic models
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class EngravingCreate(BaseModel):
    job_id: str
    item_uid: Optional[str] = None
    status: str
    raw_payload: Optional[Dict[str, Any]] = None

class EngravingUpdateStatus(BaseModel):
    status: str

class EngravingOut(BaseModel):
    id: int
    job_id: str
    item_uid: Optional[str] = None
    status: str
    raw_payload: Optional[Dict[str, Any]] = None
    orphan: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
