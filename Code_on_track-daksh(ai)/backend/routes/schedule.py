from flask import Blueprint, request, jsonify
from services.scheduler_stub import generate_schedule_preview, save_schedule_record

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    lots = data.get('lots', [])
    name = data.get('name')
    date = data.get('date')
    
    preview = generate_schedule_preview(lots, name, date)
    schedule_id = save_schedule_record(preview)
    
    return jsonify({
        "schedule_id": schedule_id,
        "preview": preview
    })

@schedule_bp.route('/<id>/apply', methods=['POST'])
def apply_schedule(id):
    # Retrieve schedule by ID and set status = approved
    # Mock implementation since we mocked the save
    return jsonify({"success": True, "message": f"Schedule {id} applied"})
    
@schedule_bp.route('/optimize', methods=['POST'])
def optimize():
    from ml.scheduler_engine import generate_optimal_routes
    # Optional params
    limit_hours = request.json.get('limit_hours', 8)
    
    result = generate_optimal_routes(limit_hours=limit_hours)
    
    # Save the latest optimized route automatically (or via a separate save call?)
    # "Button: Save -> POST /api/schedule/generate with optimized output"
    # So this endpoint just returns the preview.
    
    return jsonify(result)

# Store for the dashboard since we don't have a full schedule table management UI yet
_latest_schedule = {}

@schedule_bp.route('/routes', methods=['GET'])
def get_routes():
    # Return the latest saved schedule or just the optimized one?
    # "Fetch previously optimized schedule for dashboard display"
    return jsonify(_latest_schedule.get('routes', []))

@schedule_bp.route('/save_optimized', methods=['POST'])
def save_optimized():
    global _latest_schedule
    data = request.json
    _latest_schedule = data # Mock persistence
    return jsonify({"success": True})
