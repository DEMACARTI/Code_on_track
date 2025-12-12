from flask import Blueprint, jsonify
from sqlalchemy import create_engine, text
import config

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/status', methods=['GET'])
def get_status():
    status = {
        "db_connected": False,
        "items": 0,
        "vendors": 0,
        "lot_quality": 0,
        "lot_health": 0,
        "inspection_reports": 0
    }
    
    try:
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            status["db_connected"] = True
            
            # Helper to safely get count
            def get_count(table):
                try:
                    return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                except:
                    return -1 # Table might not exist
            
            status["items"] = get_count("items")
            status["vendors"] = get_count("vendors")
            status["lot_quality"] = get_count("lot_quality")
            status["lot_health"] = get_count("lot_health")
            status["inspection_reports"] = get_count("inspection_reports")
            
    except Exception as e:
        status["error"] = str(e)
        
    return jsonify(status)
