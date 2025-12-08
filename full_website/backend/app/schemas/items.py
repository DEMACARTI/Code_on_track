# backend/app/schemas/items.py
# Purpose: Item Pydantic models - aligned with Supabase database
# Author: Antigravity

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


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


class EngravingJobOut(BaseModel):
    """Engraving job response model for item details"""
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


class ItemBase(BaseModel):
    """Base item model"""
    uid: str
    component_type: str
    lot_number: str
    vendor_id: int
    quantity: int = 1
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    current_status: str = "manufactured"
    metadata_: Optional[Dict[str, Any]] = None


class ItemCreate(BaseModel):
    """Item creation model"""
    uid: str
    component_type: str
    lot_number: str
    vendor_id: int
    quantity: int = 1
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    qr_image_url: Optional[str] = None
    current_status: str = "manufactured"
    metadata: Optional[Dict[str, Any]] = None


class ItemUpdate(BaseModel):
    """Item update model"""
    component_type: Optional[str] = None
    lot_number: Optional[str] = None
    vendor_id: Optional[int] = None
    quantity: Optional[int] = None
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    qr_image_url: Optional[str] = None
    current_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ItemOut(BaseModel):
    """Item response model"""
    id: int
    uid: str
    component_type: str
    lot_number: str
    vendor_id: int
    quantity: int
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    qr_image_url: Optional[str] = None
    current_status: str
    metadata_: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedItemsResponse(BaseModel):
    """Paginated items response"""
    items: List[ItemOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class ItemDetail(ItemOut):
    """Detailed item response with related data"""
    engravings: List[EngravingJobOut] = []
    inspections: List[InspectionOut] = []
