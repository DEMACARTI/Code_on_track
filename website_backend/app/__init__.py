"""
IRF Website Backend - FastAPI Application

This module initializes the FastAPI application and its components.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IRF QR Tracking API",
    description="Backend API for IRF QR code tracking system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes import items, auth, engrave, dashboard

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(engrave.router, prefix="/api/engrave", tags=["Engraving"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
