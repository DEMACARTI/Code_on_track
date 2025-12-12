from flask import Blueprint, jsonify
from sqlalchemy import text
from services.db import db

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/summary', methods=['GET'])
def get_summary():
    try:
        # Total items
        total_items = db.session.execute(text("SELECT COUNT(*) FROM items")).scalar() 
        
        # Status counts
        status_rows = db.session.execute(text("SELECT status, COUNT(*) FROM items GROUP BY status")).fetchall()
        counts_by_status = {row.status: row.count for row in status_rows}

        # Failures by vendor
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

        # Engravings last 30 days (mock data or based on created_at)
        # Assuming created_at roughly correlates to engraving/production
        engravings_sql = text("""
            SELECT date(created_at) as date, COUNT(*) as count
            FROM items
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY date(created_at)
            ORDER BY date
        """)
        engravings = [{"date": str(row.date), "count": row.count} for row in db.session.execute(engravings_sql).fetchall()]

        # Warranty expiring
        # Assuming we have logic for this, or just placeholder query
        expiring = 0 # Placeholder implementation

        # Vision Defect Stats (Last 24h)
        defect_sql = text("""
            SELECT issue, COUNT(*) as count
            FROM inspection_reports
            WHERE created_at > NOW() - INTERVAL '24 hours' AND issue IS NOT NULL
            GROUP BY issue
        """)
        vision_defects = [{"issue": row.issue, "count": row.count} for row in db.session.execute(defect_sql).fetchall()]
        
        total_defects_today = sum(d["count"] for d in vision_defects)
        critical_defects_today = db.session.execute(text("SELECT COUNT(*) FROM inspection_reports WHERE created_at > NOW() - INTERVAL '24 hours' AND severity = 'CRITICAL'")).scalar()

        return jsonify({
            "total_items": total_items,
            "counts_by_status": counts_by_status,
            "failures_by_vendor": vendor_failures,
            "engravings_last_30_days": engravings,
            "warranty_expiring_in_30_days": expiring,
            "vision_stats": {
                "total_defects_today": total_defects_today,
                "critical_defects_today": critical_defects_today,
                "breakdown": vision_defects
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
