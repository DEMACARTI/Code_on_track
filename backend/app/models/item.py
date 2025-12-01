# backend/app/models/item.py
# Purpose: Item model definition
# Author: Antigravity

from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Item(Base):
    __tablename__ = "items"

    uid: Mapped[str] = mapped_column(String, primary_key=True)
    component_type: Mapped[str] = mapped_column(String, nullable=False)
    vendor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=True)
    lot_no: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, index=True, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="items")
    events: Mapped[List["ItemEvent"]] = relationship("ItemEvent", back_populates="item")
    engravings: Mapped[List["Engraving"]] = relationship("Engraving", back_populates="item")
