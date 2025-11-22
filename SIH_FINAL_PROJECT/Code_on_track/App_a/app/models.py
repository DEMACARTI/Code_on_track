from sqlalchemy import Column, Integer, String, Date, JSON, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from .database import Base
import enum

# Enums for component types and statuses
class ComponentType(str, enum.Enum):
    ERC = "ERC"  # Elastic Rail Clips
    RP = "RP"    # Rail Pads
    LIN = "LIN"  # Liners
    SLP = "SLP"  # Sleepers

class ItemStatus(str, enum.Enum):
    MANUFACTURED = "manufactured"
    SUPPLIED = "supplied"
    INSPECTED = "inspected"
    INSTALLED = "installed"
    IN_PERFORMANCE = "performance"
    REPLACED = "replaced"

# Define the Item model
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    component_type = Column(Enum(ComponentType), nullable=False)
    lot_number = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    warranty_years = Column(Integer, nullable=False)
    manufacture_date = Column(Date, nullable=False)
    current_status = Column(Enum(ItemStatus), default=ItemStatus.MANUFACTURED)
    qr_png_url = Column(String, nullable=True)
    qr_svg_url = Column(String, nullable=True)
    history = Column(JSON, default=list)  # Store status change history
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Item {self.uid} - {self.component_type} - {self.current_status}>"
