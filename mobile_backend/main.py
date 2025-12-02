"""
Mobile Scanning Backend - Simple FastAPI server for RailChinh Flutter App
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import hashlib
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    INVENTORY = "inventory"
    INSTALLATION = "installation"
    MANAGEMENT = "management"
    INSPECTION = "inspection"
    ADMIN = "admin"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    department = Column(Enum(UserRole), default=UserRole.INVENTORY)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(100), unique=True, nullable=False, index=True)
    component_type = Column(String(100), nullable=False)
    lot_number = Column(String(100))
    vendor_id = Column(Integer)
    quantity = Column(Integer, default=1)
    warranty_years = Column(Integer, default=0)
    manufacture_date = Column(DateTime)
    current_status = Column(String(50), default="manufactured")
    qr_image_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class StatusUpdate(BaseModel):
    current_status: str

# Create FastAPI app
app = FastAPI(
    title="RailChinh Mobile Backend",
    description="Backend API for Railway Component Tracking Mobile App",
    version="1.0.0"
)

# CORS - Allow all origins for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(username: str) -> str:
    data = f"{username}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "RailChinh Mobile Backend is running"}

@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Authenticate user and return token
    """
    print(f"=== LOGIN ATTEMPT ===")
    print(f"Username: '{request.username}'")
    print(f"Password: '{request.password}'")
    print(f"Password length: {len(request.password)}")
    
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == request.username).first()
        
        print(f"User found: {user is not None}")
        
        if not user:
            print("ERROR: User not found")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not user.is_active:
            print("ERROR: User not active")
            raise HTTPException(status_code=403, detail="User account is disabled")
        
        # Verify password
        provided_hash = hash_password(request.password)
        print(f"Stored hash: {user.hashed_password[:20]}...")
        print(f"Provided hash: {provided_hash[:20]}...")
        print(f"Password match: {user.hashed_password == provided_hash}")
        
        if user.hashed_password != provided_hash:
            print("ERROR: Password mismatch")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate token
        token = generate_token(user.username)
        
        print("SUCCESS: Login successful")
        
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "department": user.department.value if user.department else "user",
                "role": user.department.value if user.department else "user",
                "is_active": user.is_active
            }
        }
    finally:
        db.close()

@app.get("/api/items/{uid}")
def get_item(uid: str):
    """
    Get item details by UID (from QR code scan)
    """
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.uid == uid).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {
            "uid": item.uid,
            "component_type": item.component_type,
            "lot_number": item.lot_number,
            "vendor_id": item.vendor_id,
            "quantity": item.quantity,
            "warranty_years": item.warranty_years,
            "manufacture_date": item.manufacture_date.isoformat() if item.manufacture_date else None,
            "current_status": item.current_status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None
        }
    finally:
        db.close()

@app.get("/api/items")
def get_all_items(skip: int = 0, limit: int = 100):
    """
    Get all items with pagination
    """
    db = SessionLocal()
    try:
        items = db.query(Item).offset(skip).limit(limit).all()
        return [
            {
                "uid": item.uid,
                "component_type": item.component_type,
                "lot_number": item.lot_number,
                "vendor_id": item.vendor_id,
                "quantity": item.quantity,
                "current_status": item.current_status,
            }
            for item in items
        ]
    finally:
        db.close()

@app.put("/api/items/{uid}")
def update_item(uid: str, status_update: StatusUpdate):
    """
    Update item status
    """
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.uid == uid).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item.current_status = status_update.current_status
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        
        return {
            "uid": item.uid,
            "component_type": item.component_type,
            "current_status": item.current_status,
            "updated_at": item.updated_at.isoformat()
        }
    finally:
        db.close()

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
