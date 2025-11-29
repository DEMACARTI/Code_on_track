"""
Main FastAPI application for the IRF QR tracking system.
"""
import os
from datetime import datetime, timezone, UTC
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

from . import models, schemas, crud
from .database import SessionLocal, engine
from .config import settings
from .utils.security import get_password_hash

# Import all routes
from .routes import (
    auth,
    items,
    users,
    engrave,
    dashboard
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Clean up resources if needed

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for IRF QR Tracking System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix=settings.API_V1_STR,
    tags=["Users"]
)

app.include_router(
    items.router,
    prefix=settings.API_V1_STR,
    tags=["Items"]
)

app.include_router(
    engrave.router,
    prefix=settings.API_V1_STR,
    tags=["Engraving"]
)

app.include_router(
    dashboard.router,
    prefix=settings.API_V1_STR,
    tags=["Dashboard"]
)

# Database dependency
def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with default data."""
    db = SessionLocal()
    try:
        # Create tables
        models.Base.metadata.create_all(bind=engine)
        
        # Create default admin user if not exists
        admin = crud.user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not admin:
            # Create the admin user with all required fields
            user_in = {
                "username": "admin",
                "email": settings.FIRST_SUPERUSER_EMAIL,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
                "full_name": "Admin User",
                "role": schemas.UserRole.ADMIN,
                "is_active": True,
                "is_superuser": True
            }
            
            # Create the user using the CRUD function
            admin = crud.user.create_user(db, user=schemas.UserCreate(**user_in))
            logger.info(f"Created default admin user with ID: {admin.id}")
            
        return admin
        
    except HTTPException as e:
        logger.error(f"HTTP error initializing database: {e.detail}")
        if e.status_code == status.HTTP_400_BAD_REQUEST and "already registered" in str(e.detail).lower():
            logger.info("Admin user already exists, skipping creation")
        else:
            raise
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now(UTC)
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    
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
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
