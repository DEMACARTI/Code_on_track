"""
Engraving routes for the IRF QR tracking system.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..database import get_db
from ..utils.security import get_current_active_user, verify_api_key

router = APIRouter()

@router.post("/callback", status_code=status.HTTP_200_OK)
async def engrave_callback(
    job_update: schemas.EngraveJobUpdate,
    x_api_key: str = Header(..., description="API Key for authentication"),
    db: Session = Depends(get_db)
):
    """
    Callback endpoint for engraving service to update job status.
    
    This endpoint is secured with an API key in the X-API-KEY header.
    
    - **job_id**: The external job ID from the engraving service (required)
    - **status**: The updated status of the job (optional)
    - **logs**: Additional logs to append to the job (optional)
    
    Returns the updated job details.
    """
    # Verify API key
    if not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    # Get the job by external ID
    db_job = crud.get_engrave_job_by_external_id(db, job_id=job_update.job_id)
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_update.job_id} not found"
        )
    
    # Update the job
    updated_job = crud.update_engrave_job(
        db=db,
        db_job=db_job,
        job_update=job_update
    )
    
    # If job is completed, update the item status
    if job_update.status == models.EngraveJobStatus.COMPLETED:
        item = crud.get_item(db, item_id=db_job.item_id)
        if item:
            item.status = models.ItemStatus.IN_STOCK
            db.add(item)
            db.commit()
            db.refresh(item)
    
    return updated_job

@router.post("/jobs/", response_model=schemas.EngraveJob, status_code=status.HTTP_201_CREATED)
def create_engrave_job(
    job: schemas.EngraveJobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new engraving job.
    
    - **job_id**: External job ID from the engraving service (required)
    - **item_id**: ID of the item to be engraved (required)
    - **status**: Initial status (default: pending)
    - **logs**: Initial logs (optional)
    
    Returns the created engraving job.
    """
    # Verify item exists
    db_item = crud.get_item(db, item_id=job.item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {job.item_id} not found"
        )
    
    # Check if job ID already exists
    existing_job = crud.get_engrave_job_by_external_id(db, job_id=job.job_id)
    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with ID {job.job_id} already exists"
        )
    
    # Create the job
    return crud.create_engrave_job(db=db, job=job)

@router.get("/jobs/{job_id}", response_model=schemas.EngraveJob)
def get_engrave_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get an engraving job by ID.
    
    - **job_id**: ID of the job to retrieve
    
    Returns the job details.
    """
    db_job = crud.get_engrave_job(db, job_id=job_id)
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return db_job

@router.get("/items/{item_id}/jobs", response_model=List[schemas.EngraveJob])
def get_item_engrave_jobs(
    item_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all engraving jobs for an item.
    
    - **item_id**: ID of the item
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (pagination)
    
    Returns a list of engraving jobs for the item.
    """
    # Verify item exists
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    
    # Get jobs for the item
    return db.query(models.EngraveJob)\
        .filter(models.EngraveJob.item_id == item_id)\
        .order_by(models.EngraveJob.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
