"""
Engraving API endpoints for managing QR code engraving jobs.

Example curl commands:

# Create/update engrave job (callback)
curl -X POST "http://localhost:8000/api/engrave/callback" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key_here" \
  -d '{"job_id": "job123", "item_uid": "ABC123", "status": "completed", "message": "Engraving successful"}'

# Get job by ID (requires authentication)
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/api/engrave/jobs/job123"

# List jobs with filters (requires authentication)
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/api/engrave/jobs/?status=completed&limit=10"
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .. import models, schemas
from ..database import get_db
from ..utils.security import get_current_active_user, verify_api_key
from ..crud import engrave as crud_engrave

router = APIRouter(prefix="/api/engrave", tags=["engrave"])
logger = logging.getLogger(__name__)

# Constants
MAX_LIMIT = 1000
DEFAULT_LIMIT = 100

@router.post(
    "/callback",
    response_model=schemas.EngraveJob,
    status_code=status.HTTP_200_OK,
    summary="Process engraving callback",
    description="""Handle callbacks from the engraving service with job status updates.
    This endpoint is idempotent and respects timestamp ordering.""",
    responses={
        200: {"description": "Job processed successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Invalid or missing API key"},
        500: {"description": "Internal server error"}
    }
)
async def process_engrave_callback(
    job: schemas.EngraveJobCallback,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> schemas.EngraveJob:
    """
    Process a callback from the engraving service.
    
    This endpoint is called by the engraving service to update the status of an engraving job.
    It supports idempotent updates based on job_id and respects timestamp ordering.
    """
    try:
        # Validate and parse timestamp
        timestamp = None
        if job.timestamp:
            try:
                timestamp = datetime.fromisoformat(job.timestamp.replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid timestamp format: {job.timestamp}, using current time. Error: {str(e)}")
                timestamp = datetime.now(timezone.utc)
        
        # Process the job update
        db_job, is_new = crud_engrave.upsert_engrave_job(
            db=db,
            job_id=job.job_id,
            item_uid=job.item_uid,
            status=job.status,
            message=job.message,
            timestamp=timestamp
        )
        
        logger.info(
            f"{'Created' if is_new else 'Updated'} engrave job {job.job_id} "
            f"for item {job.item_uid} with status {job.status}"
        )
        return db_job
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in process_engrave_callback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing engrave callback"
        )
    except Exception as e:
        logger.error(f"Unexpected error in process_engrave_callback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get(
    "/jobs/{job_id}",
    response_model=schemas.EngraveJob,
    summary="Get engrave job by ID",
    description="Retrieve details of a specific engrave job",
    responses={
        200: {"description": "Job details retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to view this job"},
        404: {"description": "Job not found"}
    }
)
async def get_engrave_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
) -> schemas.EngraveJob:
    """
    Get an engrave job by its ID.
    
    Only the user who created the job or an admin can view the job details.
    """
    try:
        db_job = crud_engrave.get_engrave_job(db, job_id=job_id)
        if not db_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Engrave job not found"
            )
        
        # Check permissions
        if (current_user.role != models.UserRole.ADMIN and 
            (not db_job.created_by_id or db_job.created_by_id != current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this job"
            )
        
        return db_job
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_engrave_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving job details"
        )

@router.get(
    "/jobs/",
    response_model=List[schemas.EngraveJob],
    summary="List engrave jobs",
    description="""List all engrave jobs with optional filtering.
    Regular users can only see their own jobs, while admins can see all jobs.""",
    responses={
        200: {"description": "List of jobs retrieved successfully"},
        400: {"description": "Invalid filter parameters"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to view these jobs"},
        404: {"description": "Item not found or access denied"}
    }
)
async def list_engrave_jobs(
    skip: int = 0,
    limit: int = DEFAULT_LIMIT,
    status: Optional[models.EngraveJobStatus] = None,
    item_uid: Optional[str] = None,
    orphan: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
) -> List[schemas.EngraveJob]:
    """
    List all engrave jobs with optional filtering.
    
    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (capped at 1000)
    - status: Filter by job status
    - item_uid: Filter by item UID
    - orphan: Filter by orphan status (jobs not linked to an existing item)
    """
    try:
        # Validate limit
        limit = min(max(1, limit), MAX_LIMIT)
        
        # For non-admin users, only show their own jobs
        if current_user.role != models.UserRole.ADMIN:
            # If filtering by item_uid, verify the user has access to that item
            if item_uid:
                item = db.query(models.Item).filter(
                    models.Item.uid == item_uid,
                    models.Item.owner_id == current_user.id
                ).first()
                if not item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Item not found or access denied"
                    )
            
            # Get jobs created by this user
            query = db.query(models.EngraveJob).filter(
                models.EngraveJob.created_by_id == current_user.id
            )
        else:
            # Admin can see all jobs
            query = db.query(models.EngraveJob)
        
        # Apply filters
        if status:
            query = query.filter(models.EngraveJob.status == status)
        
        if item_uid:
            query = query.join(models.Item).filter(models.Item.uid == item_uid)
        
        if orphan is not None:
            query = query.filter(models.EngraveJob.orphan == orphan)
        
        # Apply pagination and ordering
        jobs = query.order_by(
            models.EngraveJob.last_timestamp.desc(),
            models.EngraveJob.id.desc()  # Secondary sort for consistent ordering
        ).offset(skip).limit(limit).all()
        
        return jobs
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_engrave_jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving jobs"
        )
    except Exception as e:
        logger.error(f"Unexpected error in list_engrave_jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )