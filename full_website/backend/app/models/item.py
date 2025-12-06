# backend/app/models/item.py
# Purpose: Item model definition - aligned with Supabase database
# Author: Antigravity

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base


class Item(Base):
    """Item model matching the Supabase items table structure"""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    component_type: Mapped[str] = mapped_column(String, nullable=False)
    lot_number: Mapped[str] = mapped_column(String, nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    warranty_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    manufacture_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    qr_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_status: Mapped[str] = mapped_column(String, nullable=False, default="manufactured", index=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
