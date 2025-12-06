# backend/app/main.py
# Purpose: Main application entry point
# Author: Antigravity

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, items, engravings, webhooks, reports, import_items, inspections

app = FastAPI(title="IRF QR Tracking System - Connected to Supabase")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:5174"],
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

@app.get("/")
async def root():
    return {
        "message": "Welcome to IRF QR Tracking System API",
        "database": "Connected to Supabase"
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "database": "supabase"}
