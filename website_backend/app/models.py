"""
Database models for the IRF QR tracking system.
"""
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, String, DateTime, 
    JSON, Enum, Index, Text, event, Table
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from .database import Base

# Enums as SQLAlchemy types
class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    TECHNICIAN = "technician"
    VENDOR = "vendor"
    VIEWER = "viewer"

class ItemStatus(str, PyEnum):
    MANUFACTURED = "manufactured"
    SUPPLIED = "supplied"
    INSTALLED = "installed"
    INSPECTED = "inspected"
    PERFORMANCE = "performance"
    REPLACED = "replaced"

class EngraveJobStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Association table for many-to-many relationship between Item and Vendor
item_vendor = Table(
    'item_vendor',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id', ondelete='CASCADE')),
    Column('vendor_id', Integer, ForeignKey('vendors.id', ondelete='CASCADE')),
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Index('idx_item_vendor', 'item_id', 'vendor_id', unique=True)
)

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    contact_email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    items = relationship(
        "Item",
        secondary=item_vendor,
        back_populates="vendors",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Vendor {self.name}>"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    engrave_jobs = relationship("EngraveJob", back_populates="created_by")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.MANUFACTURED, nullable=False)
    item_metadata = Column('metadata', JSON, nullable=True)  # Using 'metadata' as the actual column name in DB
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    owner = relationship("User", back_populates="items")
    vendor = relationship("Vendor", back_populates="items")
    vendors = relationship(
        "Vendor",
        secondary=item_vendor,
        back_populates="items"
    )
    engrave_jobs = relationship(
        "EngraveJob", 
        back_populates="item",
        primaryjoin="Item.uid == foreign(EngraveJob.item_uid)",
        uselist=True
    )
    events = relationship("Event", back_populates="item", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_item_uid', 'uid', unique=True, postgresql_using='btree'),
    )

    @validates('uid')
    def validate_uid(self, key, uid):
        if not uid or len(uid.strip()) == 0:
            raise ValueError("UID cannot be empty")
        return uid.strip()

    def __repr__(self):
        return f"<Item {self.uid} - {self.name}>"

class EngraveJob(Base):
    __tablename__ = "engrave_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(EngraveJobStatus), default=EngraveJobStatus.PENDING, nullable=False)
    item_uid = Column(String(50), index=True, nullable=False)
    message = Column(Text, nullable=True)
    job_metadata = Column('metadata', JSON, nullable=True)  # Using 'metadata' as the actual column name in DB
    is_orphan = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    created_by = relationship("User", back_populates="engrave_jobs")
    item = relationship(
        "Item", 
        back_populates="engrave_jobs",
        foreign_keys="[EngraveJob.item_uid]",
        primaryjoin="Item.uid == EngraveJob.item_uid",
        uselist=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_engrave_job_item_uid', 'item_uid'),
        Index('idx_engrave_job_status', 'status'),
    )

    def __repr__(self):
        return f"<EngraveJob {self.id} - {self.status} for item {self.item_uid}>"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # e.g., "status_change", "maintenance", "repair"
    item_uid = Column(String(50), ForeignKey("items.uid", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_metadata = Column(JSON, nullable=True)  # Store additional event-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("Item", back_populates="events")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Event {self.id} - {self.event_type} for item {self.item_uid}>"

# Event listeners
@event.listens_for(Vendor, 'before_insert')
def before_vendor_insert(mapper, connection, target):
    """Set created_at timestamp on insert"""
    target.created_at = datetime.now(timezone.utc)

@event.listens_for(Vendor, 'before_update')
def before_vendor_update(mapper, connection, target):
    """Set updated_at timestamp on update"""
    target.updated_at = datetime.now(timezone.utc)

@event.listens_for(EngraveJob, 'before_insert')
def before_engrave_job_insert(mapper, connection, target):
    """Set created_at timestamp on insert"""
    target.created_at = datetime.now(timezone.utc)

@event.listens_for(EngraveJob, 'before_update')
def before_engrave_job_update(mapper, connection, target):
    """Set updated_at timestamp on update"""
    target.updated_at = datetime.now(timezone.utc)

@event.listens_for(Item, 'before_insert')
def before_item_insert(mapper, connection, target):
    """Set created_at timestamp on insert"""
    target.created_at = datetime.now(timezone.utc)

@event.listens_for(Item, 'before_update')
def before_item_update(mapper, connection, target):
    """Set updated_at timestamp on update"""
    target.updated_at = datetime.now(timezone.utc)

@event.listens_for(User, 'before_insert')
def before_user_insert(mapper, connection, target):
    """Set created_at timestamp on insert"""
    target.created_at = datetime.now(timezone.utc)

@event.listens_for(User, 'before_update')
def before_user_update(mapper, connection, target):
    """Set updated_at timestamp on update"""
    target.updated_at = datetime.now(timezone.utc)
