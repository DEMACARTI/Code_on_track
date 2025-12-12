# backend/app/models/item.py
# Purpose: Item model definition - aligned with Supabase database
# Author: Antigravity

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Text, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Item(Base):
    """Item model matching the Supabase items table structure"""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    lot_no: Mapped[str] = mapped_column(String, nullable=False)
    component_type: Mapped[str] = mapped_column(String, nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="manufactured", index=True)
    manufacture_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    installation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failure_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    depot: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # quantity, qr_image_url, metadata_, updated_at removed as they are not in DB

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="items")
