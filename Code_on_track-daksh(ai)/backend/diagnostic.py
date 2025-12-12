import os
import sys
import json
from sqlalchemy import text
from flask import Flask

# Add backend dir to sys path to import app factory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import create_app
    from services.db import db
except ImportError as e:
    print(json.dumps({"error": f"Import Error: {e}"}))
    sys.exit(1)

def run_diagnostic():
    app = create_app()
    report = {}
    
    with app.app_context():
        # 1. DB Tables
        try:
            sql_tables = text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%notif%'")
            tables = [row[0] for row in db.session.execute(sql_tables).fetchall()]
            report["tables"] = tables
            
            if tables:
                # Columns
                sql_cols = text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{tables[0]}'")
                columns = [dict(zip(["name", "type", "nullable"], row)) for row in db.session.execute(sql_cols).fetchall()]
                report["notification_table_columns"] = columns
                
                # Top Rows
                sql_rows = text(f"SELECT * FROM {tables[0]} LIMIT 5")
                rows = [dict(row._mapping) for row in db.session.execute(sql_rows).fetchall()]
                # Convert datetime to str
                for r in rows:
                    if 'created_at' in r: r['created_at'] = str(r['created_at'])
                report["top_rows"] = rows
            else:
                report["notification_table_columns"] = []
                report["top_rows"] = []
                
        except Exception as e:
            report["db_error"] = str(e)

        # 2. Backend Routes
        routes = []
        for rule in app.url_map.iter_rules():
            if 'notification' in str(rule):
                routes.append({
                    "endpoint": rule.endpoint,
                    "methods": list(rule.methods),
                    "rule": str(rule)
                })
        report["backend_routes"] = routes
        
        # 3. Scheduler Files (Text search)
        scheduler_path = os.path.join(os.path.dirname(__file__), 'scheduler')
        report["scheduler_files"] = []
        if os.path.exists(scheduler_path):
             for f in os.listdir(scheduler_path):
                 if f.endswith('.py'):
                     report["scheduler_files"].append(f)
                     
    # 4. Frontend Components (Text search)
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Code_on_track-daksh(without ai)/Code_on_track-daksh/full_website/frontend/src'))
    frontend_matches = []
    if os.path.exists(frontend_path):
        for root, dirs, files in os.walk(frontend_path):
            for file in files:
                if file.endswith('.tsx') or file.endswith('.jsx'):
                    if 'Notification' in file or 'bell' in file.lower():
                         frontend_matches.append(os.path.join(root, file))
    report["frontend_components"] = frontend_matches
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_diagnostic()
