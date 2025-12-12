from flask import Blueprint, jsonify, request
from sqlalchemy import text
from services.db import db

reliability_bp = Blueprint('reliability', __name__)

@reliability_bp.route('', methods=['GET'], strict_slashes=False)
def get_vendor_reliability():
    """Returns vendor reliability scores and sub-metrics."""
    try:
        # Optional sorting via query param, e.g., ?sort=score_desc
        sort_param = request.args.get('sort', 'score_desc')
        
        query = "SELECT * FROM vendor_reliability_view"
        
        if sort_param == 'score_desc':
            query += " ORDER BY reliability_score DESC"
        elif sort_param == 'score_asc':
            query += " ORDER BY reliability_score ASC"
        elif sort_param == 'name_asc':
            query += " ORDER BY vendor_name ASC"
            
        result = db.session.execute(text(query)).fetchall()
        
        data = []
        for row in result:
            data.append({
                "vendor_id": row.vendor_id,
                "vendor_name": row.vendor_name,
                "otr": float(row.otr) if row.otr is not None else 0.0,
                "qr": float(row.qr) if row.qr is not None else 0.0,
                "fr": float(row.fr) if row.fr is not None else 0.0,
                "rts": float(row.rts) if row.rts is not None else 0.0,
                "ccr": float(row.ccr) if row.ccr is not None else 0.0,
                "reliability_score": float(row.reliability_score) if row.reliability_score is not None else 0.0
            })
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
