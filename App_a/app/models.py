# App_a/app/models.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, JSON, UniqueConstraint, ForeignKey, Enum
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.orm import relationship
import enum
from .database import Base

class EngravingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ENGRAVING = "engraving"
    COMPLETED = "completed"
    FAILED = "failed"

class Item(Base):
    __tablename__ = "items"
    id = Column(BigInteger, primary_key=True, index=True)
    uid = Column(String(128), unique=True, nullable=False, index=True)
    component_type = Column(String(16), nullable=False)   # EC, SLP, RP, LIN
    lot_number = Column(String(64), nullable=False)
    vendor_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    warranty_years = Column(Integer, nullable=True)
    manufacture_date = Column(DateTime, nullable=True)
    qr_image_url = Column(Text, nullable=True)
    current_status = Column(String(32), nullable=False, default="manufactured")
    # Use a non-reserved attribute name for JSON column
    meta = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sqlfunc.now())
    updated_at = Column(DateTime(timezone=True), onupdate=sqlfunc.now())
    
    # Relationship to EngravingQueue
    engraving_jobs = relationship("EngravingQueue", back_populates="item")

    __table_args__ = (
        UniqueConstraint('uid', name='uq_items_uid'),
    )

class EngravingQueue(Base):
    __tablename__ = "engraving_queue"
    
    id = Column(BigInteger, primary_key=True, index=True)
    item_uid = Column(String(128), ForeignKey('items.uid'), nullable=False, index=True)
    status = Column(Enum(EngravingStatus), nullable=False, default=EngravingStatus.PENDING)
    svg_url = Column(Text, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sqlfunc.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship to Item
    item = relationship("Item", back_populates="engraving_jobs")
    # Relationship to History
    history = relationship("EngravingHistory", back_populates="engraving_job")

class EngravingHistory(Base):
    __tablename__ = "engraving_history"
    
    id = Column(BigInteger, primary_key=True, index=True)
    engraving_job_id = Column(BigInteger, ForeignKey('engraving_queue.id'), nullable=False)
    status = Column(Enum(EngravingStatus), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sqlfunc.now())
    
    # Relationship to EngravingQueue
    engraving_job = relationship("EngravingQueue", back_populates="history")
