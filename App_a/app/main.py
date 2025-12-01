# main.py

import os
import io
import uuid
import binascii
import qrcode
import boto3
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from datetime import datetime

from .database import get_db, engine, Base
from . import models
# Commenting out engraving imports for now - not needed for QR scanning
# from .engraving_queue import EngravingQueueManager, engraving_queue as rq_queue
# from .engraving_worker import process_engraving_job
from .auth import router as auth_router

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IRF Backend (App A)")

# Include authentication routes
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# MinIO config
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_BUCKET = os.getenv("S3_BUCKET", "irf-dev")
S3_ACCESS = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION,
)

class ItemCreateReq(BaseModel):
    component_type: str
    lot_number: str
    quantity: int = 1
    vendor_id: int
    warranty_years: int = 0
    manufacture_date: str = None
    metadata: dict = None
    qr_size: str = Field(
        ..., 
        description="QR code size (options: '250x250', '125x125', '100x100', '50x50')",
        pattern="^(250x250|125x125|100x100|50x50)$"
    )

class EngraveRequest(BaseModel):
    uid: str
    mode: str = "normal"

class EngravingStatusResponse(BaseModel):
    status: str
    job_id: int
    position: Optional[int] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None

def generate_uid(component_type: str, vendor_id: int, lot_number: str) -> str:
    t = component_type.strip().upper()
    v = str(vendor_id).strip()
    b = lot_number.strip().replace(" ", "").upper()
    seq = uuid.uuid4().hex[:6]
    payload = f"{t}-{v}-{b}-{seq}"
    chk = binascii.crc_hqx(payload.encode(), 0) & 0xFFFF
    return f"IRF-{payload}-{chk:04x}"

@app.post("/api/items", status_code=201)
def create_items(payload: ItemCreateReq, db: Session = Depends(get_db)):
    MAX_ATTEMPTS = 5

    for _ in range(MAX_ATTEMPTS):
        uid = generate_uid(payload.component_type, payload.vendor_id, payload.lot_number)
        item = models.Item(
            uid=uid,
            component_type=payload.component_type.upper(),
            lot_number=payload.lot_number,
            vendor_id=payload.vendor_id,
            quantity=payload.quantity,
            warranty_years=payload.warranty_years,
            manufacture_date=payload.manufacture_date,
            current_status="manufactured",
            metadata=payload.metadata or {}
        )

        db.add(item)
        try:
            db.commit()
            db.refresh(item)
        except IntegrityError:
            db.rollback()
            continue

        # Generate QR
        qr_payload = f"http://localhost:8000/scan/{item.uid}"
        qr = qrcode.QRCode(
            box_size={
                "250x250": 10,
                "125x125": 5,
                "100x100": 4,
                "50x50": 2
            }[payload.qr_size],
            border=4,
            error_correction=qrcode.constants.ERROR_CORRECT_M
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)

        # Store QR code as base64 in database (no S3 needed)
        import base64
        qr_base64 = base64.b64encode(bio.getvalue()).decode('utf-8')
        item.qr_image_url = f"data:image/png;base64,{qr_base64}"
        
        db.commit()
        return item

    raise HTTPException(status_code=500, detail="Could not generate unique UID")


# Engraving endpoints commented out - not needed for QR scanning feature
# @app.post("/api/engrave", response_model=EngravingStatusResponse)
# def add_to_engraving_queue(request: EngraveRequest, db: Session = Depends(get_db)):
#     ...

# @app.get("/api/engrave/queue", response_model=Dict[str, List[Dict[str, Any]]])
# def get_engraving_queue(db: Session = Depends(get_db)):
#     ...

# @app.get("/api/items/{uid}/engraving-status", response_model=EngravingStatusResponse)
# def get_engraving_status(uid: str, db: Session = Depends(get_db)):
#     ...

@app.get("/api/items/{uid}")
def get_item_by_uid(uid: str, db: Session = Depends(get_db)):
    """
    Get item details by UID (for QR code scanning)
    """
    item = db.query(models.Item).filter(models.Item.uid == uid).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return {
        "uid": item.uid,
        "component_type": item.component_type,
        "lot_number": item.lot_number,
        "vendor_id": item.vendor_id,
        "quantity": item.quantity,
        "warranty_years": item.warranty_years,
        "manufacture_date": item.manufacture_date.isoformat() if item.manufacture_date else None,
        "current_status": item.current_status,
        "qr_image_url": item.qr_image_url,
        "meta": item.meta,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None
    }

@app.get("/api/items")
def get_all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all items with pagination
    """
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.put("/api/items/{uid}")
def update_item_status(uid: str, status: str, db: Session = Depends(get_db)):
    """
    Update item status
    """
    item = db.query(models.Item).filter(models.Item.uid == uid).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item.current_status = status
    item.updated_at = datetime.now()
    db.commit()
    db.refresh(item)
    
    return item


