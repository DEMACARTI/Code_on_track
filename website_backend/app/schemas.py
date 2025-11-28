"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from .models import ItemStatus, EventType, EngraveJobStatus, UserRole

# Shared properties
class ItemBase(BaseModel):
    uid: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., max_length=255, description="Name of the item")
    description: Optional[str] = Field(None, description="Item description")
    status: ItemStatus = Field(ItemStatus.IN_STOCK, description="Current status of the item")
    vendor_id: Optional[int] = Field(None, description="ID of the vendor")
    purchase_date: Optional[datetime] = Field(None, description="Date when the item was purchased")
    warranty_expiry: Optional[datetime] = Field(None, description="Warranty expiration date")
    location: Optional[str] = Field(None, max_length=255, description="Current location of the item")

# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass

# Properties to receive on item update
class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the item")
    description: Optional[str] = Field(None, description="Item description")
    status: Optional[ItemStatus] = Field(None, description="Current status of the item")
    vendor_id: Optional[int] = Field(None, description="ID of the vendor")
    purchase_date: Optional[datetime] = Field(None, description="Date when the item was purchased")
    warranty_expiry: Optional[datetime] = Field(None, description="Warranty expiration date")
    location: Optional[str] = Field(None, max_length=255, description="Current location of the item")

# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Item(ItemInDBBase):
    pass

# Vendor schemas
class VendorBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the vendor")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for the vendor")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address of the vendor")

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Name of the vendor")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for the vendor")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    address: Optional[str] = Field(None, description="Physical address of the vendor")

class Vendor(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Event schemas
class EventBase(BaseModel):
    event_type: EventType = Field(..., description="Type of event")
    description: Optional[str] = Field(None, description="Event description")
    created_by: str = Field(..., description="Username of who created the event")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event data")

class EventCreate(EventBase):
    item_id: int = Field(..., description="ID of the item this event is for")

class Event(EventBase):
    id: int
    item_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Engrave job schemas
class EngraveJobBase(BaseModel):
    job_id: str = Field(..., description="External job ID from the engraving service")
    status: EngraveJobStatus = Field(EngraveJobStatus.PENDING, description="Current status of the job")
    logs: Optional[str] = Field(None, description="Logs from the engraving process")

class EngraveJobCreate(EngraveJobBase):
    item_id: int = Field(..., description="ID of the item being engraved")

class EngraveJobUpdate(BaseModel):
    status: Optional[EngraveJobStatus] = Field(None, description="Updated status of the job")
    logs: Optional[str] = Field(None, description="Additional logs to append")

class EngraveJob(EngraveJobBase):
    id: int
    item_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    role: UserRole = Field(UserRole.VIEWER, description="User role")
    is_active: bool = Field(True, description="Whether the user is active")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    password: Optional[str] = Field(None, min_length=8, description="New password")

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

# Dashboard schemas
class DashboardSummary(BaseModel):
    total_items: int
    items_by_status: Dict[str, int]
    warranty_expiring_soon: int
    vendor_fail_rates: Dict[str, float]
