# backend/app/models/engraving.py
# Purpose: Engraving models definition - aligned with Supabase database
# Author: Antigravity

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class EngravingStatus(str, enum.Enum):
    """Engraving status enum matching Supabase"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class EngravingJob(Base):
    """Engraving job model matching the Supabase engraving_queue table"""
    __tablename__ = "engraving_queue"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_uid: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    svg_url: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class EngravingHistory(Base):
    """Engraving history model matching the Supabase engraving_history table"""
    __tablename__ = "engraving_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    engraving_job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("engraving_queue.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# Alias for backward compatibility
Engraving = EngravingJob
