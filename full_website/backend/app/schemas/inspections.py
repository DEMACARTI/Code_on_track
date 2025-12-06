# backend/app/schemas/inspections.py
# Purpose: Inspection Pydantic models - aligned with Supabase database
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InspectionCreate(BaseModel):
    """Create a new inspection"""
    item_uid: str
    status: str
    remark: Optional[str] = None
    inspector_id: Optional[int] = None
    photo_url: Optional[str] = None
    inspected_at: Optional[datetime] = None


class InspectionUpdate(BaseModel):
    """Update an inspection"""
    status: Optional[str] = None
    remark: Optional[str] = None
    inspector_id: Optional[int] = None
    photo_url: Optional[str] = None
    inspected_at: Optional[datetime] = None


class InspectionOut(BaseModel):
    """Inspection response model"""
    id: int
    item_uid: str
    status: str
    remark: Optional[str] = None
    inspector_id: Optional[int] = None
    photo_url: Optional[str] = None
    inspected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
