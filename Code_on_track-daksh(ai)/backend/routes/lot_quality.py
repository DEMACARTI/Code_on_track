from flask import Blueprint, jsonify, current_app
from sqlalchemy import text, inspect
from services.db import db
from datetime import datetime, timedelta
import random

lot_quality_bp = Blueprint('lot_quality', __name__)

@lot_quality_bp.route('/', methods=['GET'])
def get_lot_quality():
    """
    Returns list of lot quality records.
    Schema: [ {lot_no, component, vendor_id, item_count, failed, rate, anomaly_score, reason, status, last_inspected}, ... ]
    Fallback: 7 days -> 30 days -> Simulated Data.
    """
    try:
        # 1. Detect table name and timestamps
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Determine table name
        table_name = 'lot_quality'
        if 'lot_quality' not in tables and 'lotquality' in tables:
            table_name = 'lotquality'
        
        # 2. Query Logic (7 days)
        # Check columns to decide which timestamp to use
        columns = [c['name'] for c in inspector.get_columns(table_name)]
        ts_col = 'computed_at' if 'computed_at' in columns else 'created_at'
        if 'last_updated' in columns and 'computed_at' not in columns:
            ts_col = 'last_updated'

        query = text(f"""
            SELECT * FROM {table_name} 
            WHERE {ts_col} >= :since 
            ORDER BY {ts_col} DESC
        """)
        
        # Try 7 days
        since_7d = datetime.now() - timedelta(days=7)
        rows = db.session.execute(query, {'since': since_7d}).fetchall()

        # Try 30 days if empty
        if not rows:
            since_30d = datetime.now() - timedelta(days=30)
            rows = db.session.execute(query, {'since': since_30d}).fetchall()

        results = []
        if rows:
            for row in rows:
                # Map SQL row to primitive dict
                # Mapping user prompt keys <-> DB columns
                # DB: total_items, failed_items, failure_rate, is_anomalous, component_type
                # API: item_count, failed, rate, status, component
                
                # Dynamic mapping for safety
                d = dict(row._mapping)
                
                status_val = "FAILED" if d.get('is_anomalous') else "PASSED"
                if d.get('risk_level') == 'CRITICAL': status_val = "CRITICAL"
                
                mapped = {
                    "lot_no": d.get('lot_no', 'UNK'),
                    "component": d.get('component_type', 'Unknown'),
                    "vendor_id": d.get('vendor_id', 0),
                    "item_count": d.get('total_items', 0),
                    "failed": d.get('failed_items', 0),
                    "rate": float(d.get('failure_rate', 0.0)) * 100, # Convert 0.04 -> 4.0
                    "anomaly_score": float(d.get('anomaly_score', 0.0)),
                    "reason": d.get('reason') or str(d.get('reasons') or 'None'),
                    "status": status_val,
                    "last_inspected": d.get(ts_col).isoformat() if d.get(ts_col) else None
                }
                results.append(mapped)

        # 3. Simulation Fallback
        if not results:
            ref_date = datetime.now()
            results = [
                {
                    "lot_no": "SIM-L001",
                    "component": "Elastic Rail Clip",
                    "vendor_id": 3,
                    "item_count": 100,
                    "failed": 4,
                    "rate": 4.0,
                    "anomaly_score": 0.87,
                    "reason": "rust_spots",
                    "status": "FAILED",
                    "last_inspected": (ref_date - timedelta(hours=2)).isoformat()
                },
                {
                    "lot_no": "SIM-L005",
                    "component": "Rubber Pad",
                    "vendor_id": 12,
                    "item_count": 250,
                    "failed": 0,
                    "rate": 0.0,
                    "anomaly_score": 0.12,
                    "reason": "None",
                    "status": "PASSED",
                    "last_inspected": (ref_date - timedelta(days=1)).isoformat()
                },
                 {
                    "lot_no": "SIM-L009",
                    "component": "Switch Rail",
                    "vendor_id": 7,
                    "item_count": 50,
                    "failed": 2,
                    "rate": 4.0,
                    "anomaly_score": 0.65,
                    "reason": "micro_cracks",
                    "status": "WARNING",
                    "last_inspected": (ref_date - timedelta(days=3)).isoformat()
                }
            ]
            
        return jsonify(results)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

@lot_quality_bp.route('/recompute', methods=['POST']) # Added standard endpoint name
@lot_quality_bp.route('/run_job', methods=['POST'])   # Keep existing for compat
def run_job_endpoint():
    try:
        from ml.lot_anomaly_job import run_anomaly_job as run_job
        result = run_job()
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
