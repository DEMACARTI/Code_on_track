"""
CRUD operations for EngraveJob model.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from .. import models, schemas

def get_engrave_job(db: Session, job_id: str) -> Optional[models.EngraveJob]:
    """Get an engrave job by job_id."""
    return db.query(models.EngraveJob).filter(models.EngraveJob.job_id == job_id).first()

def get_engrave_jobs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[models.EngraveJobStatus] = None,
    item_id: Optional[int] = None,
    orphan: Optional[bool] = None
) -> List[models.EngraveJob]:
    """Get a list of engrave jobs with optional filtering."""
    query = db.query(models.EngraveJob)
    
    if status is not None:
        query = query.filter(models.EngraveJob.status == status)
    
    if item_id is not None:
        query = query.filter(models.EngraveJob.item_id == item_id)
    
    if orphan is not None:
        query = query.filter(models.EngraveJob.orphan == orphan)
    
    return query.offset(skip).limit(limit).all()

def create_engrave_job(
    db: Session, 
    job_in: schemas.EngraveJobCreate, 
    user_id: int
) -> models.EngraveJob:
    """Create a new engraving job."""
    job_data = job_in.dict()
    if 'job_metadata' not in job_data:
        job_data['job_metadata'] = None
        
    db_job = models.EngraveJob(
        **job_data,
        created_by_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_engrave_job(
    db: Session, 
    db_job: models.EngraveJob, 
    job_in: schemas.EngraveJobUpdate
) -> models.EngraveJob:
    """Update an existing engraving job."""
    update_data = job_in.dict(exclude_unset=True)
    
    # Handle job_metadata specifically to avoid None overwrites
    if 'job_metadata' in update_data and update_data['job_metadata'] is None:
        if db_job.job_metadata is not None:
            # Only update if the existing value is not None and we're not explicitly setting it to None
            update_data.pop('job_metadata')
    
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    db_job.updated_at = datetime.utcnow()
    try:
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating engrave job: {str(e)}"
        )

def delete_engrave_job(db: Session, job_id: str) -> bool:
    """Delete an engrave job by job_id."""
    db_job = get_engrave_job(db, job_id)
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engrave job not found"
        )
    
    try:
        db.delete(db_job)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting engrave job: {str(e)}"
        )

def upsert_engrave_job(
    db: Session,
    job_id: str,
    item_uid: str,
    status: models.EngraveJobStatus,
    message: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> Tuple[models.EngraveJob, bool]:
    """
    Create or update an engrave job with timestamp-based ordering.
    
    Args:
        db: Database session
        job_id: Unique job identifier
        item_uid: UID of the item being engraved
        status: Current job status
        message: Optional status message or log entry
        timestamp: Timestamp of this update (defaults to current time if not provided)
    
    Returns:
        Tuple of (engrave_job, is_new) where is_new is True if the job was created
    """
    current_time = datetime.now(timezone.utc)
    job_timestamp = timestamp or current_time
    
    # Check if item exists
    item = db.query(models.Item).filter(models.Item.uid == item_uid).first()
    
    # Check if job already exists
    db_job = get_engrave_job(db, job_id)
    
    if db_job is None:
        # Create new job
        db_job = models.EngraveJob(
            job_id=job_id,
            item_id=item.id if item else None,
            status=status,
            logs=message,
            attempts=1,
            orphan=not bool(item),
            last_timestamp=job_timestamp,
            created_at=current_time,
            updated_at=current_time
        )
        
        try:
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            return db_job, True
        except IntegrityError as e:
            db.rollback()
            if "duplicate key" in str(e).lower():
                # Race condition - another request created the job, retry the operation
                db_job = get_engrave_job(db, job_id)
                if not db_job:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create or retrieve engrave job"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error creating engrave job: {str(e)}"
                )
    
    # Update existing job if timestamp is newer or not set
    if db_job.last_timestamp is None or job_timestamp >= db_job.last_timestamp:
        # Update status and timestamp
        db_job.status = status
        db_job.last_timestamp = job_timestamp
        
        # Update item reference if needed
        if item:
            db_job.item_id = item.id
            db_job.orphan = False
        
        # Increment attempts counter
        db_job.attempts += 1
    
    # Always append logs if message is provided
    if message:
        timestamp_str = job_timestamp.isoformat()
        if db_job.logs:
            db_job.logs = f"{db_job.logs}\n{timestamp_str}: {message}"
        else:
            db_job.logs = f"{timestamp_str}: {message}"
    
    # Update the updated_at timestamp
    db_job.updated_at = current_time
    
    try:
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job, False
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating engrave job: {str(e)}"
        )
