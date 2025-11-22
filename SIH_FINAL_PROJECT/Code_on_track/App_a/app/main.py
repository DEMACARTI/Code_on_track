from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from pathlib import Path
import logging
import sys
from datetime import datetime

# Import local modules
from . import models, schemas

# Try to import real services, fall back to mocks if they fail
try:
    from . import database
    from .minio_client import minio_client
    print("Using production database and MinIO client")
except Exception as e:
    print(f"Using mock services: {str(e)}")
    from .mock_database import get_db
    from .mock_minio import minio_client
    
    # Create a database module with the mock get_db function
    class DatabaseModule:
        engine = None
        SessionLocal = None
    
    database = DatabaseModule()
    database.get_db = get_db

from .qr_generator import qr_generator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables if using SQLAlchemy directly
if hasattr(database, 'engine') and database.engine is not None:
    models.Base.metadata.create_all(bind=database.engine)
else:
    # For SQLite, the tables are created when the mock_database is imported
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Code on Track - QR-Based Digital Identity System",
    description="Backend API for Indian Railways Track Fittings Management System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to add status history
def add_status_history(db: Session, item: models.Item, status: str, notes: str = None):
    """Add a status change to the item's history."""
    if not item.history:
        item.history = []
        
    history_entry = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "notes": notes
    }
    
    item.history.append(history_entry)
    db.commit()
    db.refresh(item)
    return item

# API Endpoints
@app.post("/api/items/", response_model=schemas.BulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_items(
    item_create: schemas.ItemCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create one or more items with QR codes.
    
    - **component_type**: Type of the component (ERC, RP, LIN, SLP)
    - **lot_number**: Lot number for the items
    - **vendor_id**: Vendor identifier
    - **warranty_years**: Warranty period in years
    - **manufacture_date**: Date of manufacture (YYYY-MM-DD)
    - **quantity**: Number of items to create (default: 1, max: 1000)
    """
    created_items = []
    
    for _ in range(item_create.quantity):
        # Generate a unique ID
        uid = qr_generator.generate_uid(item_create.component_type)
        
        # Create database record
        db_item = models.Item(
            uid=uid,
            component_type=item_create.component_type,
            lot_number=item_create.lot_number,
            vendor_id=item_create.vendor_id,
            warranty_years=item_create.warranty_years,
            manufacture_date=item_create.manufacture_date,
            current_status=models.ItemStatus.MANUFACTURED,
            quantity=1  # Each item has quantity=1 when created individually
        )
        
        # Add to database
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Add initial status to history
        db_item = add_status_history(
            db=db,
            item=db_item,
            status="manufactured",
            notes="Item created"
        )
        
        # Generate QR codes in the background
        background_tasks.add_task(
            generate_and_upload_qr_codes,
            db=db,
            item=db_item,
            uid=uid
        )
        
        # Add to response
        created_items.append({
            "uid": uid,
            "status": "manufactured"
        })
    
    return {
        "items": created_items,
        "total_created": len(created_items)
    }

async def generate_and_upload_qr_codes(db: Session, item: models.Item, uid: str):
    """Background task to generate and upload QR codes."""
    try:
        # Generate QR codes
        png_path, svg_path = qr_generator.generate_qr_code(
            data=f"{item.component_type}:{uid}",
            uid=uid
        )
        
        # Upload to MinIO
        png_url = minio_client.upload_file(png_path, "image/png")
        svg_url = minio_client.upload_file(svg_path, "image/svg+xml")
        
        # Update database with URLs
        item.qr_png_url = png_url
        item.qr_svg_url = svg_url
        db.commit()
        
        # Clean up temporary files
        qr_generator.cleanup_temp_files(png_path, svg_path)
        
        logger.info(f"Successfully generated and uploaded QR codes for {uid}")
        
    except Exception as e:
        logger.error(f"Error generating/uploading QR codes for {uid}: {str(e)}")
        # In a production environment, you might want to implement retry logic here

@app.get("/api/items/{uid}", response_model=schemas.ItemDetailResponse)
async def get_item(uid: str, db: Session = Depends(get_db)):
    """
    Get item details by UID.
    
    - **uid**: The unique identifier of the item
    """
    db_item = db.query(models.Item).filter(models.Item.uid == uid).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with UID {uid} not found"
        )
    return db_item

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# For debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
