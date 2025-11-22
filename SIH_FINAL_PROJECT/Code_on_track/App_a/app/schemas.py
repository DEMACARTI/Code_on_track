from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from enum import Enum
from .models import ComponentType, ItemStatus

# Enums for request/response
class ComponentTypeEnum(str, Enum):
    ERC = "ERC"
    RP = "RP"
    LIN = "LIN"
    SLP = "SLP"

class ItemStatusEnum(str, Enum):
    MANUFACTURED = "manufactured"
    SUPPLIED = "supplied"
    INSPECTED = "inspected"
    INSTALLED = "installed"
    IN_PERFORMANCE = "performance"
    REPLACED = "replaced"

# Base schemas
class ItemBase(BaseModel):
    component_type: ComponentTypeEnum
    lot_number: str = Field(..., min_length=1, max_length=100)
    vendor_id: str = Field(..., min_length=1, max_length=100)
    warranty_years: int = Field(..., gt=0, le=30)  # Assuming max 30 years warranty
    manufacture_date: date

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "component_type": "ERC",
                "lot_number": "LOT12345",
                "vendor_id": "VENDOR001",
                "warranty_years": 5,
                "manufacture_date": "2025-11-22"
            }
        }

class ItemCreate(ItemBase):
    quantity: int = Field(1, gt=0, le=1000)  # Limit bulk creation to 1000 items at once

class ItemUpdate(BaseModel):
    status: ItemStatusEnum
    notes: Optional[str] = None

# Response schemas
class ItemResponse(ItemBase):
    id: int
    uid: str
    current_status: ItemStatusEnum
    qr_png_url: Optional[str] = None
    qr_svg_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemBulkResponse(BaseModel):
    items: List[ItemResponse]

# Status history model
class StatusHistory(BaseModel):
    status: str
    timestamp: datetime
    notes: Optional[str] = None

# Response for item details including history
class ItemDetailResponse(ItemResponse):
    history: List[StatusHistory] = []

# QR Code response
class QRCodeResponse(BaseModel):
    uid: str
    qr_png_url: Optional[str] = None
    qr_svg_url: Optional[str] = None
    status: str

# Bulk creation response
class BulkCreateResponse(BaseModel):
    items: List[QRCodeResponse]
    total_created: int
