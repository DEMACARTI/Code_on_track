import csv
import io
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.dependencies import require_role
from app.models.user import UserRole, User
from app.models.item import Item
from app.models.vendor import Vendor

router = APIRouter()

@router.post("/items")
async def import_items(
    file: UploadFile = File(...),
    create_vendors: bool = Form(False),
    commit: bool = Form(False),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))

    total_rows = 0
    valid_rows = 0
    invalid_rows = []
    created_items = []
    skipped_rows = []
    
    # Cache vendors to avoid repeated DB lookups
    vendor_cache = {}
    if commit:
        result = await db.execute(select(Vendor))
        vendors = result.scalars().all()
        vendor_cache = {v.name: v for v in vendors}

    rows_to_process = []
    
    # First pass: Parse and Validate
    for row_num, row in enumerate(csv_reader, start=1):
        total_rows += 1
        errors = []
        
        uid = row.get('uid')
        component_type = row.get('component_type')
        vendor_name = row.get('vendor_name')
        metadata_str = row.get('metadata')
        
        if not uid:
            errors.append("Missing 'uid'")
        if not component_type:
            errors.append("Missing 'component_type'")
            
        metadata = {}
        if metadata_str:
            try:
                metadata = json.loads(metadata_str)
            except json.JSONDecodeError:
                errors.append("Invalid JSON in 'metadata'")

        # Check UID uniqueness (basic check, ideally check DB too)
        if uid:
             # Check if item exists in DB
            result = await db.execute(select(Item).where(Item.uid == uid))
            if result.scalar_one_or_none():
                 errors.append(f"Item with UID '{uid}' already exists")

        if errors:
            invalid_rows.append({
                "row_number": row_num,
                "errors": errors,
                "row": row
            })
        else:
            valid_rows += 1
            rows_to_process.append({
                "row": row,
                "metadata": metadata
            })

    if not commit:
        return {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows
        }

    # Commit Phase
    if invalid_rows:
        # If there are invalid rows, we might want to stop or continue?
        # Requirement says: "Any failure should trigger a rollback." 
        # But invalid rows in preview might just be skipped?
        # "The endpoint should re-validate all rows... Any failure should trigger a rollback."
        # This implies if we commit, we expect valid data or we fail.
        # However, usually bulk import skips invalid rows or fails all.
        # Let's fail all if any invalid rows found during commit to be safe/strict, 
        # OR we can process valid ones. 
        # Requirement: "The response should include created_items, skipped_rows, and optional errors."
        # This suggests partial success might be allowed or we report what happened.
        # But "Any failure should trigger a rollback" suggests transaction atomicity.
        # Let's assume if there are invalid rows detected *during* commit (re-validation), we rollback.
        pass

    if invalid_rows:
         raise HTTPException(status_code=400, detail={"message": "Validation failed", "invalid_rows": invalid_rows})

    try:
        for item_data in rows_to_process:
            row = item_data['row']
            metadata = item_data['metadata']
            vendor_name = row.get('vendor_name')
            vendor_id = None
            
            if vendor_name:
                vendor = vendor_cache.get(vendor_name)
                if not vendor:
                    if create_vendors:
                        vendor = Vendor(name=vendor_name, is_active=True)
                        db.add(vendor)
                        await db.flush() # Get ID
                        vendor_cache[vendor_name] = vendor
                    else:
                        raise ValueError(f"Vendor '{vendor_name}' not found and create_vendors=False")
                vendor_id = vendor.id

            item = Item(
                uid=row['uid'],
                component_type=row['component_type'],
                vendor_id=vendor_id,
                lot_no=row.get('lot_no'),
                metadata_=metadata,
                status="In Stock" # Default status
            )
            db.add(item)
            created_items.append(item.uid)
        
        await db.commit()
        return {
            "created_items": created_items,
            "skipped_rows": 0, # We failed if any invalid
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
