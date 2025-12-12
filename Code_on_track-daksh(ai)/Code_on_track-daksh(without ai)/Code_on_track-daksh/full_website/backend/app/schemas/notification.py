from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: str
    severity: Optional[str] = None
    metadata_: Optional[Any] = None # Using Any for flexible JSON

class NotificationOut(NotificationBase):
    id: int
    item_id: Optional[int] = None
    uid: Optional[str] = None
    read: bool
    dismissed: bool
    created_at: datetime
    updated_at: datetime
    
    # Map 'metadata_' from model to 'metadata' in output for cleaner API
    # But wait, frontend expects 'metadata'. 
    # SQLAlchemy model has 'metadata_' mapping to column 'metadata'.
    # If we use `from_attributes=True`, it picks up `metadata_`?
    # Let's map it explicitly or rely on alias.
    # Alias 'metadata_' to 'metadata' in output?
    # User requested response: "metadata": {...}
    
    # We can use field alias.
    # metadata: Optional[Any] = Field(alias="metadata_")
    # But let's check how vendor does it. vendor has `metadata_`.
    # in vendor schema, we manually extract it.
    
    metadata: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)

class NotificationUpdateBatch(BaseModel):
    ids: list[int]

class UnreadCount(BaseModel):
    unread_count: int
