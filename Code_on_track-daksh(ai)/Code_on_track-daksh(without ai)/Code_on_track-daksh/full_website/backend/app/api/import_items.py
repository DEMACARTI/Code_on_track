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

router = APIRouter()


@router.post("/items")
async def import_items(
    file: UploadFile = File(...),
    commit: bool = Form(False),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk import items from CSV into Supabase database.
    
    CSV columns expected:
    - uid (required): Unique identifier
    - component_type (required): Type of component
    - lot_no (required): Lot number
    - vendor_id (required): Vendor ID (integer)
    - warranty_months: Warranty period in months
    - manufacture_date: Date of manufacture (YYYY-MM-DD)
    - status: Status (default: 'manufactured')
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))

    total_rows = 0
    valid_rows = 0
    invalid_rows = []
    created_items = []
    
    rows_to_process = []
    
    # First pass: Parse and Validate
    for row_num, row in enumerate(csv_reader, start=1):
        total_rows += 1
        errors = []
        
        uid = row.get('uid', '').strip()
        component_type = row.get('component_type', '').strip()
        lot_no = row.get('lot_no', '').strip()
        vendor_id_str = row.get('vendor_id', '').strip()
        # quantity not in DB
        warranty_months_str = row.get('warranty_months', '').strip()
        manufacture_date_str = row.get('manufacture_date', '').strip()
        status = row.get('status', 'manufactured').strip()
        
        # Validate required fields
        if not uid:
            errors.append("Missing 'uid'")
        if not component_type:
            errors.append("Missing 'component_type'")
        if not lot_no:
            errors.append("Missing 'lot_no'")
        if not vendor_id_str:
            errors.append("Missing 'vendor_id'")
        
        # Validate vendor_id
        vendor_id = None
        if vendor_id_str:
            try:
                vendor_id = int(vendor_id_str)
            except ValueError:
                errors.append("Invalid 'vendor_id' - must be an integer")
        
        # Validate warranty_months
        warranty_months = None
        if warranty_months_str:
            try:
                warranty_months = int(warranty_months_str)
            except ValueError:
                errors.append("Invalid 'warranty_months' - must be an integer")
        
        # Validate manufacture_date
        manufacture_date = None
        if manufacture_date_str:
            try:
                manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid 'manufacture_date' - use YYYY-MM-DD format")
        
        # Check UID uniqueness in database
        if uid:
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
                "uid": uid,
                "component_type": component_type,
                "lot_no": lot_no,
                "vendor_id": vendor_id,
                "warranty_months": warranty_months,
                "manufacture_date": manufacture_date,
                "status": status
            })

    if not commit:
        return {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "preview": True
        }

    # Commit Phase - fail if any invalid rows
    if invalid_rows:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Validation failed", 
                "invalid_rows": invalid_rows
            }
        )

    try:
        for item_data in rows_to_process:
            item = Item(
                uid=item_data['uid'],
                component_type=item_data['component_type'],
                lot_no=item_data['lot_no'],
                vendor_id=item_data['vendor_id'],
                warranty_months=item_data['warranty_months'],
                manufacture_date=item_data['manufacture_date'],
                status=item_data['status']
            )
            db.add(item)
            created_items.append(item.uid)
        
        await db.commit()
        return {
            "created_items": created_items,
            "total_created": len(created_items),
            "preview": False
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
