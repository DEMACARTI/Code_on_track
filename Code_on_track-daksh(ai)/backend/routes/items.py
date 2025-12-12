from flask import Blueprint, request, jsonify
from sqlalchemy import text
from services.db import db
from services.expiry import compute_expiry

items_bp = Blueprint('items', __name__)

@items_bp.route('/', methods=['GET'])
def get_items():
    uid_filter = request.args.get('uid')
    lot_filter = request.args.get('lot_no')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    offset = (page - 1) * size

    # Build query
    base_query = "FROM items i"
    where_clauses = []
    params = {}

    if uid_filter:
        where_clauses.append("i.uid ILIKE :uid")
        params['uid'] = f"%{uid_filter}%"
    
    if lot_filter:
        where_clauses.append("i.lot_no ILIKE :lot_no")
        params['lot_no'] = f"%{lot_filter}%"
    
    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)

    count_sql = text(f"SELECT COUNT(*) {base_query} {where_str}")
    data_sql = text(f"""
        SELECT i.id, i.uid, i.lot_no, i.component_type, i.status, 
               i.manufacture_date, i.vendor_id, i.depot, i.warranty_months
        {base_query} {where_str}
        ORDER BY i.id
        LIMIT :limit OFFSET :offset
    """)
    
    params['limit'] = size
    params['offset'] = offset

    try:
        total = db.session.execute(count_sql, params).scalar()
        rows = db.session.execute(data_sql, params).fetchall()
        
        items = []
        for row in rows:
            # Row access by integer index or key depending on driver, mapped result is generally key-accessible
            # SQLAlchemy 1.4+ Row objects are dict-like
            m_date = row.manufacture_date
            w_months = row.warranty_months
            e_date = compute_expiry(m_date, w_months)
            
            items.append({
                "id": row.id,
                "uid": row.uid,
                "lot_no": row.lot_no,
                "component_type": row.component_type,
                "status": row.status,
                "manufacture": m_date.isoformat() if m_date else None, # Explicit "manufacture" key
                "manufacture_date": m_date.isoformat() if m_date else None,
                "expiry_date": e_date.isoformat() if e_date else None,
                "vendor_id": row.vendor_id,
                "depot": row.depot
            })

        return jsonify({"total": total, "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
