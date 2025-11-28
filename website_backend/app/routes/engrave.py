"""
Engraving API endpoints for managing QR code engraving jobs.

Example curl commands:

# Create/update engrave job (callback)
curl -X POST "http://localhost:8000/api/engrave/callback" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key_here" \
  -d '{"job_id": "job123", "uid": "ABC123", "status": "completed", "message": "Engraving successful"}'

# Get job by ID
curl -H "X-API-KEY: your_api_key_here" \
  "http://localhost:8000/api/engrave/job/job123"

# Get latest job by UID
curl -H "X-API-KEY: your_api_key_here" \
  "http://localhost:8000/api/engrave/uid/ABC123"

# List recent jobs
curl -H "X-API-KEY: your_api_key_here" \
  "http://localhost:8000/api/engrave/recent?limit=10"
"""

import os
import time
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/api/engrave", tags=["Engraving"])
logger = logging.getLogger(__name__)

# Get API key from environment
API_KEY = os.getenv("ENGRAVE_API_KEY")
if not API_KEY:
    logger.warning("ENGRAVE_API_KEY not set in environment")

async def verify_api_key(api_key: str = Header(..., alias="X-API-KEY")):
    """Verify the API key for engraving endpoints."""
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured"
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

@router.post(
    "/callback",
    response_model=schemas.EngraveJobRead,
    status_code=status.HTTP_200_OK,
    summary="Update engraving job status (callback)",
    responses={
        401: {"description": "Invalid or missing API key"},
        400: {"description": "Invalid request data"}
    }
)
async def engrave_callback(
    job_data: schemas.EngraveJobCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """
    Callback endpoint for engraving service to update job status.
    
    This endpoint creates a new engraving job for the specified item.
    """
    # Generate a unique job_id using the current timestamp and item_id
    job_id = f"job_{int(time.time())}_{job_data.item_id}"
    
    logger.info(f"Creating engrave job {job_id} for item {job_data.item_id} with status {job_data.status}")
    
    # Create the job record using the crud function
    db_job = crud.upsert_engrave_job(
        db=db,
        job_id=job_id,
        item_id=job_data.item_id,
        status=job_data.status,
        message=job_data.message,
        log_entry=job_data.logs
    )
    
    return db_job

@router.get(
    "/job/{job_id}",
    response_model=schemas.EngraveJobRead,
    summary="Get engraving job by ID",
    responses={
        404: {"description": "Job not found"}
    }
)
def get_engrave_job(
    job_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Get an engraving job by its job ID."""
    db_job = crud.get_engrave_job_by_jobid(db, job_id=job_id)
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Engraving job {job_id} not found"
        )
    return db_job

@router.get(
    "/uid/{uid}",
    response_model=schemas.EngraveJobRead,
    summary="Get latest engraving job by UID",
    responses={
        404: {"description": "No jobs found for this UID"}
    }
)
def get_latest_job_by_uid(
    uid: str,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Get the most recent engraving job for a given UID."""
    jobs = crud.list_recent_engrave_jobs(db, limit=1)
    if not jobs or jobs[0].uid != uid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No engraving jobs found for UID {uid}"
        )
    return jobs[0]

@router.get(
    "/recent",
    response_model=List[schemas.EngraveJobRead],
    summary="List recent engraving jobs"
)
def list_recent_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """List recent engraving jobs, most recent first."""
    return crud.list_recent_engrave_jobs(db, limit=min(limit, 100))