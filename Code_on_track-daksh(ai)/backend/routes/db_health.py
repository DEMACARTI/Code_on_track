from flask import Blueprint, jsonify
from sqlalchemy import text
from services.db import db

db_health_bp = Blueprint('db_health', __name__)

@db_health_bp.route('/', methods=['GET'])
def health_check():
    """
    Check database connectivity and return basic stats.
    """
    try:
        # Check connection explicitly
        with db.engine.connect() as connection:
            # Simple query
            connection.execute(text("SELECT 1"))
            
            # Get counts
            items_count = connection.execute(text("SELECT count(*) FROM items")).scalar()
            vendors_count = connection.execute(text("SELECT count(*) FROM vendors")).scalar()
            
            # Get a sample item to verify data read
            sample_result = connection.execute(text("SELECT id, uid, lot_no FROM items LIMIT 1")).fetchone()
            
            sample_data = None
            if sample_result:
                sample_data = {
                    "id": sample_result.id,
                    "uid": sample_result.uid,
                    "lot_no": sample_result.lot_no
                }

            return jsonify({
                "status": "ok",
                "database": "connected",
                "counts": {
                    "items": items_count,
                    "vendors": vendors_count
                },
                "sample_item": sample_data
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500
