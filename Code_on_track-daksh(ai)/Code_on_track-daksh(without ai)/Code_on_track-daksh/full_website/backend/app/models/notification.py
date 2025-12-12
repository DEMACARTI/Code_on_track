from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, BigInteger, text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True) # Using Integer for SQLite compatibility (BigInteger in Postgres)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True, index=True)
    uid = Column(String, nullable=True) # The Item UID string "UID-..."
    type = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    title = Column(String, nullable=True)
    message = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True) # Mapped to metadata column
    read = Column(Boolean, default=False, index=True)
    dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
