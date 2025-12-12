from flask import Blueprint, jsonify
from sqlalchemy import text
from services.db import db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/weekly_defects', methods=['GET'])
def weekly_defects():
    """Returns defect counts for the last 7 days with fallback to 30 days."""
    days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    def get_defects(interval_days):
        # Using created_at based on user requirement
        sql = text(f"""
            SELECT 
                TRIM(TO_CHAR(created_at, 'Dy')) as day_name,
                COUNT(*) as count,
                EXTRACT(ISODOW FROM created_at) as dow
            FROM items
            WHERE status IN ('failed', 'scrapped', 'rejected')
              AND created_at >= NOW() - INTERVAL '{interval_days} days'
            GROUP BY day_name, dow
            ORDER BY dow
        """)
        return db.session.execute(sql).fetchall()

    try:
        # 1. Try last 7 days
        result = get_defects(7)
        total_defects = sum(row[1] for row in result)

        # 2. If no data, fallback to last 30 days
        if total_defects == 0:
            result = get_defects(30)

        # 3. Initialize full map Mon-Sun
        data_map = {day: 0 for day in days_order}

        # 4. Fill with DB data
        for row in result:
            day_short = row[0] # 'Mon', 'Tue' from TO_CHAR(..., 'Dy')
            if day_short in data_map:
                data_map[day_short] = row[1]
                 
        # 5. Format as list in strictly Mon -> Sun order
        data = [{"day": day, "count": data_map[day]} for day in days_order]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/system_activity', methods=['GET'])
def system_activity():
    """Returns recent system activity stream."""
    try:
        sql = text("""
            SELECT 
                'anomaly_check' as type,
                lq.lot_no as subject,
                lq.anomaly_score as value,
                lq.last_updated as timestamp
            FROM lot_quality lq
            ORDER BY lq.last_updated DESC
            LIMIT 10
        """)
        
        result = db.session.execute(sql).fetchall()
        data = [{
            "type": row[0],
            "subject": row[1],
            "value": float(row[2]) if row[2] is not None else 0,
            "timestamp": row[3].isoformat() if row[3] else None
        } for row in result]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/health_distribution', methods=['GET'])
def health_distribution():
    """Returns health risk distribution."""
    try:
        sql = text("""
            SELECT risk_level, COUNT(*) 
            FROM lot_health 
            GROUP BY risk_level
        """)
        result = db.session.execute(sql).fetchall()
        data = [{"name": row[0], "value": row[1]} for row in result if row[0] is not None]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/summary', methods=['GET'])
def summary():
    """Returns high-level summary stats for the dashboard."""
    try:
        # Total items
        total_items = db.session.execute(text("SELECT COUNT(*) FROM items")).scalar() 
        
        # Critical Lots: risk_level = 'HIGH' in lot_health
        critical_lots = db.session.execute(text("SELECT COUNT(*) FROM lot_health WHERE risk_level = 'HIGH'")).scalar()

        # Analyzed Lots: all entries in lot_health
        analyzed_lots = db.session.execute(text("SELECT COUNT(*) FROM lot_health")).scalar()

        # Active Vendors
        vendors_count = db.session.execute(text("SELECT COUNT(*) FROM vendors")).scalar()

        # Failures by vendor (Top 5)
        vendor_failures_sql = text("""
            SELECT v.name as vendor_name, COUNT(*) as count
            FROM items i
            JOIN vendors v ON i.vendor_id = v.id
            WHERE i.status = 'failed'
            GROUP BY v.name
            ORDER BY count DESC
            LIMIT 5
        """)
        vendor_failures = [{"vendor_name": row.vendor_name, "count": row.count} for row in db.session.execute(vendor_failures_sql).fetchall()]

        # Status counts
        status_rows = db.session.execute(text("SELECT status, COUNT(*) FROM items GROUP BY status")).fetchall()
        counts_by_status = {row.status: row.count for row in status_rows}

        return jsonify({
            "total_items": total_items,
            "critical_lots": critical_lots,
            "analyzed_lots": analyzed_lots,
            "vendors": vendors_count,
            "counts_by_status": counts_by_status,
            "failures_by_vendor": vendor_failures
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
