# main.py

import os
import io
import uuid
import binascii
import qrcode
import boto3
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

from .database import get_db, engine, Base
from . import models

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IRF Backend (App A)")

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
        qr = qrcode.QRCode(box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)

        key = f"qrs/{item.uid}.png"
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=bio.getvalue(), ContentType="image/png")

        item.qr_image_url = f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"
        db.commit()
        return item

    raise HTTPException(status_code=500, detail="Could not generate unique UID")
