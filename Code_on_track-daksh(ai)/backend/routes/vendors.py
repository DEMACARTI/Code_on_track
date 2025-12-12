from flask import Blueprint, jsonify, request
from sqlalchemy import text
from services.db import db

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/', methods=['GET'])
def get_vendors():
    # Return vendors with items_count
    page = int(request.args.get('page', 1))
    size = int(request.args.get('page_size', 20))
    offset = (page - 1) * size

    # Get total count first
    count_sql = text("SELECT COUNT(*) FROM vendors")
    total = db.session.execute(count_sql).scalar() or 0

    sql = text("""
        SELECT v.id, v.name, v.vendor_code, v.component_supplied,
               (SELECT COUNT(*) FROM items i WHERE i.vendor_id = v.id) as items_count,
               (SELECT COUNT(*) FROM items i WHERE i.vendor_id = v.id AND i.status IN ('failed', 'rejected')) as failed_count
        FROM vendors v
        ORDER BY v.id
        LIMIT :limit OFFSET :offset
    """)
    
    try:
        rows = db.session.execute(sql, {"limit": size, "offset": offset}).fetchall()
        vendors = []
        for row in rows:
            vendors.append({
                "id": row.id,
                "name": row.name,
                "vendor_code": row.vendor_code,
                "component_supplied": row.component_supplied,
                "items_count": row.items_count,
                "failed_count": row.failed_count
            })
            
        return jsonify({
            "total": total,
            "page": page,
            "page_size": size,
            "vendors": vendors
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vendors_bp.route('/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    # Fixed columns based on schema inspection:
    # warranty_months -> default_warranty_months
    # is_active -> missing in DB, assuming True or removing
    sql = text("""
        SELECT v.id, v.name, v.vendor_code, v.component_supplied, 
               v.contact_name, v.contact_email, v.contact_phone, v.address,
               v.default_warranty_months, v.notes, v.created_at,
               (SELECT COUNT(*) FROM items i WHERE i.vendor_id = v.id) as items_count,
               (SELECT COUNT(*) FROM items i WHERE i.vendor_id = v.id AND i.status IN ('failed', 'rejected')) as failed_count
        FROM vendors v
        WHERE v.id = :id
    """)
    
    try:
        row = db.session.execute(sql, {"id": vendor_id}).fetchone()
        if not row:
            return jsonify({"error": "Vendor not found"}), 404
            
        vendor = {
            "id": row.id,
            "name": row.name,
            "vendor_code": row.vendor_code,
            "component_supplied": row.component_supplied,
            "items_count": row.items_count,
            "failed_count": row.failed_count,
            "contact_name": row.contact_name,
            "contact_email": row.contact_email,
            "contact_phone": row.contact_phone,
            "address": row.address,
            "warranty_months": row.default_warranty_months, # Map back to expected key
            "notes": row.notes,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "is_active": True # Default since column missing
        }
        
        # Parse components_supplied
        comps = row.component_supplied
        if comps:
             if ',' in comps:
                 vendor["components_supplied"] = [c.strip() for c in comps.split(',')]
             else:
                 vendor["components_supplied"] = [comps]
        else:
            vendor["components_supplied"] = []

        return jsonify(vendor)
    except Exception as e:
        import traceback
        traceback.print_exc() # Log full stack trace
        return jsonify({"error": str(e)}), 500
