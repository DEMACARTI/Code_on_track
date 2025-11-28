"""
Main FastAPI application for the IRF QR tracking system.
"""
import os
from datetime import datetime, timezone, UTC
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime
import logging
from typing import List, Optional

from . import models, schemas, crud
from .database import SessionLocal, engine
from .routes import auth, items, engrave, dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IRF Tracking System API",
    description="Backend API for Indian Railways Fittings (IRF) Tracking System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(engrave.router)
app.include_router(dashboard.router)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create initial data
def init_db():
    """Initialize database with default data."""
    db = SessionLocal()
    try:
        # Create default admin user if not exists
        admin = crud.get_user_by_username(db, username="admin")
        if not admin:
            user_in = schemas.UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="Admin User",
                role=schemas.UserRole.ADMIN,
                is_active=True
            )
            crud.create_user(db, user=user_in)
            print("Created default admin user")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

# Initialize database on startup
init_db()

# Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now(UTC)
    response = await call_next(request)
    process_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} "
        f"in {process_time:.2f}ms"
    )
    return response

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and container orchestration."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IRF Tracking System API"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API information."""
    """Root endpoint with API information."""
    return {
        "name": "IRF QR Tracking API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
