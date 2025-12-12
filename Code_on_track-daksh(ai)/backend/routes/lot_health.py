from flask import Blueprint, jsonify, request
from ml.health_score_job import run_job
from sqlalchemy import text
from services.db import db
from datetime import datetime, timedelta

lot_health_bp = Blueprint('lot_health', __name__)

@lot_health_bp.route('/', methods=['GET'])
def get_lot_health():
    try:
        # Get optional risk_level filter from query params
        risk_level = request.args.get('risk_level')
        
        # Build query with optional filter
        base_sql = """
            SELECT 
                lot_no, 
                component_type, 
                health_score, 
                risk_level, 
                recommended_action, 
                next_suggested_inspection_date,
                computed_at
            FROM lot_health
        """
        
        if risk_level:
            base_sql += " WHERE risk_level = :risk_level"
        
        # Sort by health_score DESC (highest scores first)
        base_sql += " ORDER BY health_score DESC LIMIT 50"
        
        sql = text(base_sql)
        
        # Execute with params if filtering, otherwise without
        if risk_level:
            result = db.session.execute(sql, {"risk_level": risk_level}).fetchall()
        else:
            result = db.session.execute(sql).fetchall()
        
        if result:
            data = [{
                "lot_no": row.lot_no,
                "component_type": row.component_type,
                "health_score": row.health_score,
                "risk_level": row.risk_level,
                "recommended_action": row.recommended_action,
                "next_suggested_inspection_date": row.next_suggested_inspection_date.isoformat() if row.next_suggested_inspection_date else None,
                "last_updated": row.computed_at.isoformat() if row.computed_at else None
            } for row in result]
            return jsonify(data), 200
            
        # Fallback to simulated data if DB is empty to ensure UI shows something
        # This matches the user request to "never show 0 lots" if possible or provide simulated dataset
        ref_date = datetime.now()
        simulated_data = [
            {
                "lot_no": "SIM-L001",
                "component_type": "Elastic Rail Clip",
                "health_score": 95.5,
                "risk_level": "LOW",
                "recommended_action": "Routine Check",
                "next_suggested_inspection_date": (ref_date + timedelta(days=30)).isoformat(),
                "last_updated": ref_date.isoformat()
            },
            {
                "lot_no": "SIM-L002",
                "component_type": "Rubber Pad",
                "health_score": 45.0,
                "risk_level": "HIGH",
                "recommended_action": "Inspect Immediately",
                "next_suggested_inspection_date": (ref_date + timedelta(days=2)).isoformat(),
                "last_updated": ref_date.isoformat()
            },
            {
                "lot_no": "SIM-L003",
                "component_type": "Switch Rail",
                "health_score": 72.0,
                "risk_level": "MEDIUM",
                "recommended_action": "Monitor Wear",
                "next_suggested_inspection_date": (ref_date + timedelta(days=14)).isoformat(),
                "last_updated": ref_date.isoformat()
            }
        ]
        return jsonify(simulated_data), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@lot_health_bp.route('/run_job', methods=['POST'])
def trigger_health_job():
    try:
        result = run_job()
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
