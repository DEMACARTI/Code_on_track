# backend/app/models/user.py
# Purpose: User model definition
# Author: Antigravity

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"
    SERVICE = "service"

class WebsiteUser(Base):
    """User model for the website/admin portal"""
    __tablename__ = "website_users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

# Alias for backward compatibility
User = WebsiteUser
