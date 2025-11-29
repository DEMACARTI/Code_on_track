"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, ClassVar
from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict, field_validator, model_validator

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
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "johndoe"
            }
        }
    )

class UserCreate(UserBase):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    is_superuser: bool = Field(default=False, description="Whether the user has superuser privileges")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "role": "viewer"
            }
        }
    )
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserRead(UserBase):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Vendor schemas
class VendorBase(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the vendor")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for the vendor")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address of the vendor")
    is_active: bool = Field(default=True, description="Whether the vendor is active")

class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "ACME Corp",
                "contact_email": "contact@acme.com",
                "phone": "+1234567890",
                "address": "123 Main St, Anytown, USA",
                "is_active": True
            }
        }
    )

class VendorUpdate(VendorBase):
    """Schema for updating vendor data."""
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v
    
    model_config = ConfigDict(from_attributes=True)

class VendorRead(VendorBase):
    """Schema for reading vendor data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "ACME Corp",
                "contact_email": "contact@acme.com",
                "phone": "+1234567890",
                "address": "123 Main St, Anytown, USA",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    )
    
    @classmethod
    def from_orm(cls, obj):
        # Handle the case where the object is already a dict
        if isinstance(obj, dict):
            return cls(**obj)
        return super().model_validate(obj)

class Vendor(VendorRead):
    """Alias for VendorRead for backward compatibility."""
    pass

# Item schemas
class ItemBase(BaseModel):
    component_type: str
    lot_number: str
    vendor_id: int
    warranty_years: int
    manufacture_date: datetime
    item_metadata: Optional[Dict[str, Any]] = None

class ItemCreate(ItemBase):
    quantity: int = Field(gt=0, default=1)

class ItemUpdate(BaseModel):
    component_type: Optional[str] = None
    lot_number: Optional[str] = None
    vendor_id: Optional[int] = None
    warranty_years: Optional[int] = None
    manufacture_date: Optional[datetime] = None
    item_metadata: Optional[Dict[str, Any]] = None
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
    event_metadata: Optional[Dict[str, Any]] = None

class EventUpdate(BaseModel):
    event_type: Optional[EventType] = None
    event_metadata: Optional[Dict[str, Any]] = None

class EventRead(EventCreate):
    id: int
    created_at: datetime
    created_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class EngraveJobBase(BaseModel):
    status: EngraveJobStatus = EngraveJobStatus.PENDING
    item_uid: str
    message: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None
    is_orphan: bool = False

class EngraveJobCreate(EngraveJobBase):
    pass

class EngraveJobUpdate(BaseModel):
    status: Optional[EngraveJobStatus] = None
    message: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None

class EngraveJob(EngraveJobBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    is_orphan: bool = False

    class Config:
        from_attributes = True

class EngraveJobCallback(BaseModel):
    """Schema for engraving job callback data."""
    job_id: str
    status: EngraveJobStatus
    message: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Response wrappers
class VendorsList(BaseModel):
    """Schema for a paginated list of vendors."""
    vendors: List[VendorRead]
    total: int
    
    model_config = ConfigDict(from_attributes=True)

class ItemsList(BaseModel):
    """Schema for a paginated list of items."""
    items: List['ItemRead']
    total: int
    
    model_config = ConfigDict(from_attributes=True)

class UsersList(BaseModel):
    users: List['UserRead']
    total: int

class DashboardSummary(BaseModel):
    total_items: int = 0
    items_by_status: Dict[str, int] = {}
    recent_items: List['ItemRead'] = []
    recent_engravings: List['EngraveJob'] = []

# Update forward references
ItemRead.model_rebuild()
EngraveJob.model_rebuild()
ItemsList.model_rebuild()
VendorRead.model_rebuild()
VendorsList.model_rebuild()
UsersList.model_rebuild()
