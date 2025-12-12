# backend/app/schemas/engravings.py
# Purpose: Engraving Pydantic models - aligned with Supabase database
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EngravingCreate(BaseModel):
    """Create a new engraving job"""
    item_uid: str
    svg_url: str
    max_attempts: int = 3


class EngravingUpdateStatus(BaseModel):
    """Update engraving status"""
    status: str
    error_message: Optional[str] = None


class EngravingHistoryOut(BaseModel):
    """Engraving history response model"""
    id: int
    engraving_job_id: int
    status: str
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EngravingOut(BaseModel):
    """Engraving job response model"""
    id: int
    item_uid: str
    status: str
    svg_url: str
    attempts: int
    max_attempts: int
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EngravingDetailOut(EngravingOut):
    """Detailed engraving response with history"""
    history: List[EngravingHistoryOut] = []
