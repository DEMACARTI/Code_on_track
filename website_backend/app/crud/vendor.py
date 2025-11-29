"""
CRUD operations for vendors.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas

def create_vendor(db: Session, vendor: schemas.VendorCreate) -> models.Vendor:
    """Create a new vendor."""
    db_vendor = models.Vendor(
        name=vendor.name,
        contact_email=vendor.contact_email,
        phone=vendor.phone,
        address=vendor.address
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def get_vendor(db: Session, vendor_id: int) -> Optional[models.Vendor]:
    """Get a vendor by ID."""
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def get_vendor_by_name(db: Session, name: str) -> Optional[models.Vendor]:
    """Get a vendor by name."""
    return db.query(models.Vendor).filter(models.Vendor.name == name).first()

def list_vendors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Vendor]:
    """List all vendors with pagination."""
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def update_vendor(
    db: Session, db_vendor: models.Vendor, vendor: schemas.VendorUpdate
) -> models.Vendor:
    """Update a vendor."""
    update_data = vendor.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int) -> None:
    """Delete a vendor."""
    db_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
    return None
