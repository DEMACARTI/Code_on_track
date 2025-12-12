from flask import Blueprint, request, jsonify
from sqlalchemy import text
from services.db import db
from vision.inference import run_inference
import base64

vision_bp = Blueprint('vision', __name__)

@vision_bp.route('/inspect', methods=['POST'])
def inspect_component():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files['image']
        uid = request.form.get('uid')
        lot_no = request.form.get('lot_no')
        
        if not uid and not lot_no:
            return jsonify({"error": "UID or Lot No required"}), 400

        image_bytes = file.read()
        
        # Run inference
        result = run_inference(image_bytes)
        
        # Encode image to save (mock storage in DB for simplicity as per requirements)
        # In prod, S3 or filesystem is better.
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Save report
        sql = text("""
            INSERT INTO inspection_reports (uid, lot_no, issue, confidence, severity, recommended_action, image_base64)
            VALUES (:uid, :lot_no, :issue, :confidence, :severity, :recommended_action, :image_base64)
            RETURNING id, created_at
        """)
        
        params = {
            "uid": uid,
            "lot_no": lot_no,
            "issue": result["issue"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "recommended_action": result["recommended_action"],
            "image_base64": image_b64
        }
        
        row = db.session.execute(sql, params).fetchone()
        db.session.commit()
        
        # Return result with saved ID
        response = result.copy()
        response["report_id"] = row.id
        response["created_at"] = row.created_at.isoformat()
        del response["bbox"] # Optional to return bbox or not, prompt said "Return detection result" which implies all info.
        # But wait, frontend needs bbox to draw rectangle. 
        response["bbox"] = result["bbox"]
        
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vision_bp.route('/history/<uid>', methods=['GET'])
def get_history(uid):
    try:
        sql = text("""
            SELECT id, issue, confidence, severity, recommended_action, created_at
            FROM inspection_reports
            WHERE uid = :uid
            ORDER BY created_at DESC
        """)
        
        rows = db.session.execute(sql, {"uid": uid}).fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": row.id,
                "issue": row.issue,
                "confidence": row.confidence,
                "severity": row.severity,
                "recommended_action": row.recommended_action,
                "created_at": row.created_at.isoformat()
            })
            
        return jsonify(history)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
