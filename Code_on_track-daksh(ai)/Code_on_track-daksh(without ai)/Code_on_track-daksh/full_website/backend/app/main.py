# backend/app/main.py
# Purpose: Main application entry point
# Author: Antigravity

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, items, engravings, webhooks, reports, import_items, inspections, vendors, notifications, analytics, lot_health, lot_quality

# ... (rest of imports)

app = FastAPI(title="IRF QR Tracking System - Connected to PostgreSQL")

@app.get("/api/db-health")
async def db_health():
    from app.db.session import engine
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT count(*) FROM items"))
            count = result.scalar()
            return {"status": "ok", "database": "connected", "items_count": count}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}

# CORS
app.add_middleware(
    CORSMiddleware,
    # Explicitly allow frontend origins for Credentials to work
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(engravings.router, prefix="/engravings", tags=["engravings"])
app.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
app.include_router(webhooks.router, prefix="/webhook", tags=["webhooks"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(import_items.router, prefix="/api/import", tags=["import"])
app.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(analytics.router, tags=["analytics"]) # Root level for /debug and /analytics
app.include_router(lot_health.router, prefix="/lot_health", tags=["lot_health"])
app.include_router(lot_quality.router, prefix="/lot_quality", tags=["lot_quality"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to IRF QR Tracking System API",
        "database": "Connected to Supabase"
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "database": "supabase"}
