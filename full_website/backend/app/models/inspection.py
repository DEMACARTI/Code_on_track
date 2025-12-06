# backend/app/models/inspection.py
# Purpose: Inspection model definition - aligned with Supabase database
# Author: Antigravity

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base


class Inspection(Base):
    """Inspection model matching the Supabase inspections table"""
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_uid: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspector_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now()
    )
