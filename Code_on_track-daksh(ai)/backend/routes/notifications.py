from flask import Blueprint, jsonify, request
from sqlalchemy import text
from services.db import db
from datetime import datetime
import json

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'], strict_slashes=False)
def get_notifications():
    """Returns latest notifications."""
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        check_table_sql = text("SELECT to_regclass('public.notifications')")
        if not db.session.execute(check_table_sql).scalar():
            return jsonify([])

        query_parts = ["SELECT id, type, title, message, severity, is_read, metadata, created_at FROM notifications"]
        params = {}
        
        if unread_only:
            query_parts.append("WHERE is_read = FALSE")
            
        query_parts.append("ORDER BY created_at DESC LIMIT :limit")
        params['limit'] = limit
        
        sql = text(" ".join(query_parts))
        result = db.session.execute(sql, params).fetchall()
        
        notifications = []
        for row in result:
            notifications.append({
                "id": row.id,
                "type": row.type,
                "title": row.title,
                "message": row.message,
                "severity": row.severity or 'info',
                "is_read": row.is_read if row.is_read is not None else False,
                "metadata": row.metadata if hasattr(row, 'metadata') else {},
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
            
        return jsonify(notifications)
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('', methods=['POST'], strict_slashes=False)
def create_notification():
    """Internal endpoint to create notification."""
    data = request.json
    try:
        sql = text("""
            INSERT INTO notifications (type, title, message, severity, is_read, metadata, created_at)
            VALUES (:type, :title, :message, :severity, FALSE, :metadata, NOW())
            RETURNING id, created_at, is_read
        """)
        
        meta = data.get("metadata", {})
        if isinstance(meta, dict):
            # Ensure it's json dumpable string if DB expects JSON/Text or pass dict if using JSONB with SQLAlchemy
            # text() + params usually handles JSONB if driver supports it, else dump to str
            import json
            meta = json.dumps(meta)

        params = {
            "type": data.get("type", "info"),
            "title": data.get("title", "Notification"),
            "message": data.get("message", ""),
            "severity": data.get("severity", "info"),
            "metadata": meta
        }
        result = db.session.execute(sql, params)
        db.session.commit()
        
        row = result.fetchone()
        return jsonify({
            "status": "created", 
            "notification": {
                "id": row.id,
                "type": params["type"],
                "title": params["title"],
                "severity": params["severity"],
                "is_read": row.is_read,
                "created_at": row.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/<int:id>/read', methods=['PATCH'])
def mark_read(id):
    """Mark notification as read."""
    try:
        sql = text("UPDATE notifications SET is_read = TRUE WHERE id = :id RETURNING id")
        result = db.session.execute(sql, {"id": id})
        db.session.commit()
        
        if result.rowcount == 0:
            return jsonify({"error": "Notification not found"}), 404
            
        return jsonify({"status": "updated", "id": id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

