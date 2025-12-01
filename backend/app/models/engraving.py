# backend/app/models/engraving.py
# Purpose: Engraving model definition
# Author: Antigravity

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Engraving(Base):
    __tablename__ = "engravings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    item_uid: Mapped[str | None] = mapped_column(String, ForeignKey("items.uid"), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    orphan: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    item: Mapped["Item"] = relationship("Item", back_populates="engravings")
