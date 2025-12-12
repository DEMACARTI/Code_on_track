# backend/app/models/vendor.py
# Purpose: Vendor model definition
# Author: Antigravity

from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    contact_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    items: Mapped[List["Item"]] = relationship("Item", back_populates="vendor")

    @property
    def vendor_code(self) -> str | None:
        return (self.metadata_ or {}).get("vendor_code")

    @property
    def warranty_months(self) -> int | None:
        return (self.metadata_ or {}).get("warranty_months")

    @property
    def notes(self) -> str | None:
        return (self.metadata_ or {}).get("notes")
