from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class VendorBase(BaseModel):
    name: str

class VendorCreate(VendorBase):
    vendor_code: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    warranty_months: Optional[int] = None
    notes: Optional[str] = None

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    vendor_code: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    warranty_months: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class VendorOut(VendorBase):
    id: int
    created_at: datetime
    is_active: bool
    items_count: int = 0
    # Include mapped fields in output if needed, or just return them as part of VendorBase if added there?
    # Spec: Successful response includes vendor_code, warranty_months.
    vendor_code: Optional[str] = None
    warranty_months: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    components_supplied: list[str] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class VendorBrief(VendorBase):
    """Simplified vendor model for nested responses"""
    id: int
    is_active: bool
    vendor_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
