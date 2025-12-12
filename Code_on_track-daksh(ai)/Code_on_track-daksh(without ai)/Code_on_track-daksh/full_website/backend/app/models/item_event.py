# backend/app/models/item_event.py
# Purpose: ItemEvent model definition
# Author: Antigravity

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ItemEvent(Base):
    __tablename__ = "item_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_uid: Mapped[str] = mapped_column(String, ForeignKey("items.uid"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    performed_by: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    item: Mapped["Item"] = relationship("Item", back_populates="events")
