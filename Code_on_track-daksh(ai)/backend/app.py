from flask import Flask, jsonify
from flask_cors import CORS
from services.db import db
import config

# Import blueprints (we will create these files next)
# using lazy imports or standard imports if files exist
# to avoid circular deps, standard imports are fine if structure is clean

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", 
        "http://localhost:5176", "http://localhost:5177", "http://localhost:5178"
    ]}})
    db.init_app(app)
    
    # Register Blueprints
    # We'll import them inside to ensure they can import db from services.db
    from routes.items import items_bp
    from routes.vendors import vendors_bp
    from routes.notifications import notifications_bp
    from routes.lot_quality import lot_quality_bp
    from routes.schedule import schedule_bp
    from routes.assistant import assistant_bp
    from routes.vision import vision_bp
    from routes.reports import reports_bp
    from routes.reports import reports_bp
    from routes.auth import auth_bp
    from routes.lot_health import lot_health_bp
    from routes.debug import debug_bp
    from routes.analytics import analytics_bp
    from routes.db_health import db_health_bp
    from routes.reliability import reliability_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(items_bp, url_prefix='/api/items')
    app.register_blueprint(vendors_bp, url_prefix='/api/vendors')
    app.register_blueprint(reliability_bp, url_prefix='/api/vendors/reliability')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(lot_quality_bp, url_prefix='/api/lot_quality')
    app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
    app.register_blueprint(assistant_bp, url_prefix='/api/assistant')
    app.register_blueprint(vision_bp, url_prefix='/api/vision')
    app.register_blueprint(lot_health_bp, url_prefix='/api/lot_health')
    app.register_blueprint(debug_bp, url_prefix='/api/debug')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(db_health_bp, url_prefix='/api/db-health')

    # Start Scheduler
    print("----------------------------------------")
    print("--- STARTING NEW BACKEND VERSION v2 ---")
    print("----------------------------------------")
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from scheduler.jobs import start_scheduler
        start_scheduler(app)


    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    # Trigger reload v5
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
