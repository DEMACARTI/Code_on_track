from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class VendorBase(BaseModel):
    name: str
    contact_info: Optional[dict] = None
    metadata: Optional[dict] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[dict] = None
    metadata: Optional[dict] = None
    is_active: Optional[bool] = None

class VendorOut(VendorBase):
    id: int
    created_at: datetime
    is_active: bool
    items_count: int = 0

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
