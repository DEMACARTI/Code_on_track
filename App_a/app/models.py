# App_a/app/models.py
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, JSON, UniqueConstraint, func
from sqlalchemy.sql import func as sqlfunc
from .database import Base

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

    __table_args__ = (
        UniqueConstraint('uid', name='uq_items_uid'),
    )
