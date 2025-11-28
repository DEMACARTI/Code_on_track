"""
Database CRUD operations for the IRF QR tracking system.
"""
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, timezone, UTC, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import uuid

from . import models, schemas

# User operations
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    # TODO: Hash password before storing
    db_user = models.User(
        username=user.username,
        hashed_password=user.password  # In production, hash this password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Vendor operations
def create_vendor(db: Session, vendor: schemas.VendorCreate) -> models.Vendor:
    """Create a new vendor."""
    db_vendor = models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def get_vendor(db: Session, vendor_id: int) -> Optional[models.Vendor]:
    """Get a vendor by ID."""
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def list_vendors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Vendor]:
    """List all vendors with pagination."""
    return db.query(models.Vendor).offset(skip).limit(limit).all()

# Item operations
def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create a new item."""
    db_item = models.Item(**item.dict(exclude={'quantity'}))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item_by_uid(db: Session, uid: str) -> Optional[models.Item]:
    """Get an item by its UID."""
    return db.query(models.Item).filter(models.Item.uid == uid).first()

def list_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[List[models.Item], int]:
    """List items with optional filtering and pagination."""
    query = db.query(models.Item)
    
    if filters:
        for field, value in filters.items():
            if hasattr(models.Item, field):
                if isinstance(value, list):
                    query = query.filter(getattr(models.Item, field).in_(value))
                else:
                    query = query.filter(getattr(models.Item, field) == value)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def update_item_status(
    db: Session,
    uid: str,
    new_status: schemas.ItemStatus,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[models.Item]:
    """Update an item's status and metadata."""
    db_item = get_item_by_uid(db, uid)
    if db_item:
        db_item.current_status = new_status
        if metadata:
            db_item.metadata = metadata
        db_item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_item)
    return db_item

# Event operations
def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    """Create a new event."""
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def list_events_for_item(db: Session, uid: str) -> List[models.Event]:
    """List all events for a specific item."""
    return db.query(models.Event).filter(
        models.Event.item_uid == uid
    ).order_by(models.Event.created_at.desc()).all()

# Engrave job operations
def upsert_engrave_job(
    db: Session,
    job_id: str,
    item_id: int,
    status: schemas.EngraveJobStatus,
    message: Optional[str] = None,
    log_entry: Optional[str] = None
) -> models.EngraveJob:
    """Create or update an engraving job."""
    db_job = db.query(models.EngraveJob).filter(
        models.EngraveJob.job_id == job_id
    ).first()
    
    # Include message in logs if provided
    log_message = f"{message}: {log_entry}" if message and log_entry else message or log_entry or 'Job created'
    
    if db_job:
        db_job.status = status
        if log_message:
            db_job.logs = f"{db_job.logs or ''}\n{datetime.now(UTC)}: {log_message}"
        db_job.updated_at = datetime.utcnow()
    else:
        db_job = models.EngraveJob(
            job_id=job_id,
            item_id=item_id,
            status=status,
            logs=f"{datetime.now(UTC)}: {log_message}"
        )
        db.add(db_job)
    
    db.commit()
    db.refresh(db_job)
    return db_job

def get_engrave_job_by_jobid(db: Session, job_id: str) -> Optional[models.EngraveJob]:
    """Get an engraving job by its job ID."""
    return db.query(models.EngraveJob).filter(
        models.EngraveJob.job_id == job_id
    ).first()

def list_recent_engrave_jobs(
    db: Session, 
    limit: int = 50
) -> List[models.EngraveJob]:
    """List recent engraving jobs."""
    return db.query(models.EngraveJob).order_by(
        models.EngraveJob.updated_at.desc()
    ).limit(limit).all()

# Inspection operations
def create_inspection(
    db: Session, 
    inspection: schemas.InspectionCreate
) -> models.Inspection:
    """Create a new inspection record."""
    db_inspection = models.Inspection(**inspection.dict())
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection

def list_inspections_for_item(
    db: Session, 
    uid: str
) -> List[models.Inspection]:
    """List all inspections for a specific item."""
    return db.query(models.Inspection).filter(
        models.Inspection.item_uid == uid
    ).order_by(models.Inspection.created_at.desc()).all()

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[models.ItemStatus] = None,
    vendor_id: Optional[int] = None
) -> List[models.Item]:
    """Get a list of items with optional filtering."""
    query = db.query(models.Item)
    
    if status is not None:
        query = query.filter(models.Item.status == status)
    if vendor_id is not None:
        query = query.filter(models.Item.vendor_id == vendor_id)
        
    return query.offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create a new item."""
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(
    db: Session, 
    db_item: models.Item, 
    item_update: Union[schemas.ItemUpdate, Dict[str, Any]]
) -> models.Item:
    """Update an existing item."""
    update_data = item_update.dict(exclude_unset=True) if not isinstance(item_update, dict) else item_update
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
        
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Delete an item by ID."""
    db_item = get_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

# Vendor CRUD operations
def get_vendor(db: Session, vendor_id: int) -> Optional[models.Vendor]:
    """Get a vendor by ID."""
    return db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()

def get_vendor_by_name(db: Session, name: str) -> Optional[models.Vendor]:
    """Get a vendor by name."""
    return db.query(models.Vendor).filter(models.Vendor.name == name).first()

def get_vendors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Vendor]:
    """Get a list of vendors."""
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate) -> models.Vendor:
    """Create a new vendor."""
    db_vendor = models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def update_vendor(
    db: Session, 
    db_vendor: models.Vendor, 
    vendor_update: Union[schemas.VendorUpdate, Dict[str, Any]]
) -> models.Vendor:
    """Update an existing vendor."""
    update_data = vendor_update.dict(exclude_unset=True) if not isinstance(vendor_update, dict) else vendor_update
    
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
        
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# Event CRUD operations
def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    """Create a new event."""
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events_for_item(
    db: Session, 
    item_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Event]:
    """Get events for a specific item."""
    return (
        db.query(models.Event)
        .filter(models.Event.item_id == item_id)
        .order_by(models.Event.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

# Engrave Job CRUD operations
def create_engrave_job(db: Session, job: schemas.EngraveJobCreate) -> models.EngraveJob:
    """Create a new engrave job."""
    db_job = models.EngraveJob(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_engrave_job(db: Session, job_id: int) -> Optional[models.EngraveJob]:
    """Get an engrave job by ID."""
    return db.query(models.EngraveJob).filter(models.EngraveJob.id == job_id).first()

def get_engrave_job_by_external_id(db: Session, job_id: str) -> Optional[models.EngraveJob]:
    """Get an engrave job by external job ID."""
    return db.query(models.EngraveJob).filter(models.EngraveJob.job_id == job_id).first()

def update_engrave_job(
    db: Session, 
    db_job: models.EngraveJob, 
    job_update: Union[schemas.EngraveJobUpdate, Dict[str, Any]]
) -> models.EngraveJob:
    """Update an existing engrave job."""
    update_data = job_update.dict(exclude_unset=True) if not isinstance(job_update, dict) else job_update
    
    # Append logs if they exist
    if 'logs' in update_data and update_data['logs']:
        current_logs = db_job.logs or ""
        update_data['logs'] = f"{current_logs}\n{update_data['logs']}" if current_logs else update_data['logs']
    
    for field, value in update_data.items():
        setattr(db_job, field, value)
        
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get a list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    from .utils.security import get_password_hash
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Dashboard operations
def get_dashboard_summary(db: Session) -> schemas.DashboardSummary:
    """Get summary data for the dashboard."""
    # Count items by status
    status_counts = (
        db.query(
            models.Item.status,
            func.count(models.Item.id).label('count')
        )
        .group_by(models.Item.status)
        .all()
    )
    
    items_by_status = {status.value: count for status, count in status_counts}
    
    # Count items with warranty expiring soon (next 30 days)
    warranty_expiring_soon = (
        db.query(models.Item)
        .filter(
            models.Item.warranty_expiry.between(
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=30)
            )
        )
        .count()
    )
    
    # Calculate vendor fail rates (simplified example)
    vendor_fail_rates = {}
    vendors = db.query(models.Vendor).all()
    for vendor in vendors:
        total_items = db.query(models.Item).filter(models.Item.vendor_id == vendor.id).count()
        if total_items > 0:
            failed_items = (
                db.query(models.Item)
                .join(models.EngraveJob)
                .filter(
                    models.Item.vendor_id == vendor.id,
                    models.EngraveJob.status == models.EngraveJobStatus.FAILED
                )
                .count()
            )
            vendor_fail_rates[vendor.name] = (failed_items / total_items) * 100  # as percentage
    
    return schemas.DashboardSummary(
        total_items=sum(items_by_status.values()),
        items_by_status=items_by_status,
        warranty_expiring_soon=warranty_expiring_soon,
        vendor_fail_rates=vendor_fail_rates
    )
