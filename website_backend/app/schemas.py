"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, ClassVar
from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict, validator

# Enums
class ItemStatus(str, Enum):
    MANUFACTURED = "manufactured"
    SUPPLIED = "supplied"
    INSTALLED = "installed"
    INSPECTED = "inspected"
    PERFORMANCE = "performance"
    REPLACED = "replaced"

class EventType(str, Enum):
    STATUS_CHANGE = "status_change"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    OTHER = "other"

class EngraveJobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ENGRAVING = "engraving"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"

class InspectionResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Vendor schemas
class VendorBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorRead(VendorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Item schemas
class ItemBase(BaseModel):
    component_type: str
    lot_number: str
    vendor_id: int
    warranty_years: int
    manufacture_date: datetime
    metadata: Optional[Dict[str, Any]] = None

class ItemCreate(ItemBase):
    quantity: int = Field(gt=0, default=1)

class ItemUpdate(BaseModel):
    component_type: Optional[str] = None
    lot_number: Optional[str] = None
    vendor_id: Optional[int] = None
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    current_status: Optional[ItemStatus] = None
    qr_png_url: Optional[str] = None
    qr_svg_url: Optional[str] = None

class ItemRead(ItemBase):
    id: int
    uid: str
    current_status: ItemStatus
    qr_png_url: Optional[str] = None
    qr_svg_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Event schemas
class EventCreate(BaseModel):
    item_uid: str
    event_type: EventType
    metadata: Optional[Dict[str, Any]] = None

class EventRead(EventCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the vendor")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for the vendor")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address of the vendor")

class Vendor(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Engrave job schemas
class EngraveJobBase(BaseModel):
    status: EngraveJobStatus = Field(default=EngraveJobStatus.PENDING, description="Current status of the engraving job")
    message: Optional[str] = Field(None, description="Status message or error details")
    logs: Optional[str] = Field(None, description="Detailed logs of the engraving process")

class EngraveJobCreate(EngraveJobBase):
    item_id: int = Field(..., description="ID of the item being engraved")

class EngraveJobRead(EngraveJobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EngraveJobUpdate(BaseModel):
    status: Optional[EngraveJobStatus] = Field(None, description="Updated status of the job")
    logs: Optional[str] = Field(None, description="Additional logs to append")

# Inspection schemas
class InspectionCreate(BaseModel):
    item_uid: str
    inspector: str
    result: InspectionResult
    comments: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class InspectionRead(InspectionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Response wrappers
class ItemsList(BaseModel):
    items: List[ItemRead]
    total: int

    model_config = ConfigDict(from_attributes=True)

# Auth schemas (simplified)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class DashboardSummary(BaseModel):
    total_items: int = 0
    items_by_status: Dict[str, int] = {}
    warranty_expiring_soon: List[ItemRead] = []
    recent_failures: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)
