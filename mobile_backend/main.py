"""
Mobile Scanning Backend - Simple FastAPI server for RailChinh Flutter App
With VGG Defect Classification Integration
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import hashlib
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import io
from PIL import Image
import numpy as np
import base64

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

class InspectionRequest(BaseModel):
    qr_id: str
    status: str
    remark: str
    inspector_id: Optional[int] = None

class DefectClassificationRequest(BaseModel):
    image_base64: str  # Base64 encoded image

class DefectClassificationResponse(BaseModel):
    predicted_class: str
    confidence: float
    all_probabilities: Dict[str, float]
    remark: str  # Human-readable remark
    status: Optional[str] = "OK"
    model_available: Optional[bool] = True

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ComponentDetection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox

class ComponentDetectionResponse(BaseModel):
    num_detections: int
    detections: list[ComponentDetection]
    model_available: bool = True
    inference_time_ms: Optional[float] = None

# Database Model for Inspections
class Inspection(Base):
    __tablename__ = "inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    item_uid = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    remark = Column(Text)
    inspector_id = Column(Integer)
    photo_url = Column(Text)
    # AI fields are commented out until migration is run
    # ai_classification = Column(String(50))  # AI predicted defect class
    # ai_confidence = Column(Float)  # AI confidence score
    inspected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables if they don't exist
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

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

# ============================================================================
# VGG MODEL LOADING AND PREDICTION
# ============================================================================

# Global variable to store loaded model
_vgg_model = None
_class_names = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']

# ============================================================================
# YOLO OBJECT DETECTION MODEL
# ============================================================================

# Global variable to store YOLO model
_yolo_model = None
_component_class_names = ['elastic_clip_good', 'elastic_clip_missing']

# Component descriptions for API response
COMPONENT_DESCRIPTIONS = {
    'elastic_clip_good': 'Elastic Railway Clip - Good condition, properly secured',
    'elastic_clip_missing': 'Elastic Railway Clip - Missing or damaged, needs replacement'
}

# Remark templates for each defect class
DEFECT_REMARKS = {
    'Rust': 'Component shows signs of rust/corrosion. Metal surface oxidation detected.',
    'Crack': 'Crack detected in component. Structural integrity compromised.',
    'Broken': 'Component is broken or severely damaged. Immediate replacement required.',
    'Damaged': 'General damage/wear detected. Component shows signs of deterioration.',
    'Normal': 'Component appears to be in good condition. No visible defects detected.'
}

def load_vgg_model():
    """Load VGG model on startup"""
    global _vgg_model
    
    try:
        import tensorflow as tf
        from pathlib import Path
        
        # Path to the trained model - try multiple locations
        # Priority 1: Try best_model_initial.keras (created during training)
        model_path = Path(__file__).parent.parent / 'railway-vgg-classification' / 'railway_defect_output' / 'best_model_initial.keras'
        
        if not model_path.exists():
            # Priority 2: Alternative absolute path (local dev)
            model_path = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_output/best_model_initial.keras')
        
        if not model_path.exists():
            # Priority 3: Local best_model.keras (for Render deployment)
            model_path = Path(__file__).parent / 'best_model.keras'
        
        if not model_path.exists():
            # Priority 4: Try /opt/render paths for production
            render_path = Path('/opt/render/project/src/mobile_backend/best_model.keras')
            if render_path.exists():
                model_path = render_path
        
        if model_path.exists():
            print(f"Loading VGG model from: {model_path}")
            # Load model with Keras 3
            _vgg_model = tf.keras.models.load_model(
                str(model_path),
                compile=True
            )
            print("✅ VGG model loaded successfully!")
            return True
        else:
            print(f"⚠️  Model not found at: {model_path}")
            print("Model will need to be trained first. Run: python train_vgg_classification.py")
            return False
            
    except ImportError:
        print("⚠️  TensorFlow not installed. Install with: pip install tensorflow")
        return False
    except Exception as e:
        print(f"⚠️  Error loading model: {e}")
        return False

def load_yolo_model():
    """Load YOLO object detection model on startup"""
    global _yolo_model
    
    try:
        from ultralytics import YOLO
        from pathlib import Path
        
        # Path to the trained YOLO model - try multiple locations
        # Priority 1: Railway YOLO detection project
        model_path = Path(__file__).parent.parent / 'railway-yolo-detection' / 'models' / 'best.pt'
        
        if not model_path.exists():
            # Priority 2: Alternative absolute path (local dev)
            model_path = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-detection/models/best.pt')
        
        if not model_path.exists():
            # Priority 3: Local yolo_best.pt (for deployment)
            model_path = Path(__file__).parent / 'yolo_best.pt'
        
        if not model_path.exists():
            # Priority 4: Try /opt/render paths for production
            render_path = Path('/opt/render/project/src/mobile_backend/yolo_best.pt')
            if render_path.exists():
                model_path = render_path
        
        if model_path.exists():
            print(f"Loading YOLO model from: {model_path}")
            _yolo_model = YOLO(str(model_path))
            print("✅ YOLO object detection model loaded successfully!")
            return True
        else:
            print(f"⚠️  YOLO model not found at: {model_path}")
            print("Model will need to be trained first. Run: python railway-yolo-detection/scripts/train_yolo.py")
            return False
            
    except ImportError:
        print("⚠️  Ultralytics not installed. Install with: pip install ultralytics")
        return False
    except Exception as e:
        print(f"⚠️  Error loading YOLO model: {e}")
        return False

def detect_components(image: Image.Image, conf_threshold: float = 0.25) -> dict:
    """Detect railway components using YOLO model"""
    global _yolo_model, _component_class_names
    import time
    
    if _yolo_model is None:
        # Try to load model if not already loaded
        if not load_yolo_model():
            return {
                "num_detections": 0,
                "detections": [],
                "model_available": False,
                "message": "YOLO model not available. Please train the model first."
            }
    
    try:
        start_time = time.time()
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Run inference
        results = _yolo_model.predict(
            source=img_array,
            conf=conf_threshold,
            save=False,
            verbose=False
        )
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            
            for i in range(len(boxes)):
                class_id = int(boxes.cls[i].item())
                class_name = _component_class_names[class_id] if class_id < len(_component_class_names) else f"class_{class_id}"
                
                detection = {
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': float(boxes.conf[i].item()),
                    'bbox': {
                        'x1': float(boxes.xyxy[i][0].item()),
                        'y1': float(boxes.xyxy[i][1].item()),
                        'x2': float(boxes.xyxy[i][2].item()),
                        'y2': float(boxes.xyxy[i][3].item())
                    }
                }
                detections.append(detection)
        
        return {
            'num_detections': len(detections),
            'detections': detections,
            'model_available': True,
            'inference_time_ms': round(inference_time, 2)
        }
        
    except Exception as e:
        raise Exception(f"Detection error: {str(e)}")

def preprocess_image_for_vgg(image: Image.Image) -> np.ndarray:
    """Preprocess image for VGG model prediction"""
    # Resize to VGG input size
    image = image.resize((224, 224))
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to array and normalize
    img_array = np.array(image) / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def predict_defect(image: Image.Image) -> dict:
    """Predict defect class using VGG model"""
    global _vgg_model, _class_names
    
    if _vgg_model is None:
        # Try to load model if not already loaded
        if not load_vgg_model():
            # Return a fallback response instead of error
            return {
                "predicted_class": "Normal",
                "confidence": 0.0,
                "status": "Manual inspection required",
                "remark": "⚠️ AI model unavailable. Please inspect manually.",
                "all_probabilities": {name: 0.0 for name in _class_names},
                "model_available": False
            }
    
    try:
        # Preprocess image
        img_array = preprocess_image_for_vgg(image)
        
        # Make prediction
        predictions = _vgg_model.predict(img_array, verbose=0)
        
        # Get predicted class
        predicted_idx = np.argmax(predictions[0])
        predicted_class = _class_names[predicted_idx]
        confidence = float(predictions[0][predicted_idx])
        
        # Get all probabilities
        all_probs = {
            class_name: float(prob)
            for class_name, prob in zip(_class_names, predictions[0])
        }
        
        # CONFIDENCE THRESHOLD: If confidence is below 50%, consider it Normal
        # This helps prevent false positives from an undertrained model
        CONFIDENCE_THRESHOLD = 0.50
        normal_prob = all_probs.get('Normal', 0.0)
        
        # If top prediction confidence is low, or Normal has decent probability, classify as Normal
        if confidence < CONFIDENCE_THRESHOLD or (predicted_class != 'Normal' and normal_prob > 0.25):
            # Check if Normal class has reasonable probability
            if normal_prob >= confidence * 0.5:  # Normal is at least half as likely
                predicted_class = 'Normal'
                confidence = normal_prob
        
        # Generate remark
        remark = DEFECT_REMARKS.get(predicted_class, "Analysis complete.")
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_probabilities': all_probs,
            'remark': remark,
            'status': 'OK',
            'model_available': True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

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

@app.post("/qr/inspection")
def submit_inspection(request: InspectionRequest):
    """
    Submit inspection result for a QR scanned item
    """
    db = SessionLocal()
    try:
        # Check if item exists
        item = db.query(Item).filter(Item.uid == request.qr_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Create inspection record without AI fields (optional)
        inspection_data = {
            'item_uid': request.qr_id,
            'status': request.status,
            'remark': request.remark,
            'inspector_id': request.inspector_id,
            'inspected_at': datetime.utcnow()
        }
        
        inspection = Inspection(**inspection_data)
        db.add(inspection)
        
        # Update item status based on inspection
        if request.status in ["approved", "passed", "ok"]:
            item.current_status = "inspected"
        elif request.status in ["rejected", "failed", "damaged"]:
            item.current_status = "rejected"
        else:
            item.current_status = request.status
        
        item.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Inspection submitted successfully",
            "inspection_id": inspection.id,
            "item_uid": request.qr_id,
            "new_status": item.current_status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving inspection: {str(e)}")
    finally:
        db.close()

@app.get("/api/inspections/{uid}")
def get_inspections(uid: str):
    """
    Get all inspections for an item
    """
    db = SessionLocal()
    try:
        inspections = db.query(Inspection).filter(Inspection.item_uid == uid).order_by(Inspection.inspected_at.desc()).all()
        return [
            {
                "id": insp.id,
                "item_uid": insp.item_uid,
                "status": insp.status,
                "remark": insp.remark,
                "inspector_id": insp.inspector_id,
                "ai_classification": insp.ai_classification,
                "ai_confidence": insp.ai_confidence,
                "inspected_at": insp.inspected_at.isoformat() if insp.inspected_at else None
            }
            for insp in inspections
        ]
    finally:
        db.close()

# ============================================================================
# VGG DEFECT CLASSIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/classify-defect", response_model=DefectClassificationResponse)
async def classify_defect(file: UploadFile = File(...)):
    """
    Classify railway component defect from uploaded image
    Returns: Predicted defect class (Rust, Crack, Broken, Damaged, Normal) with confidence
    """
    try:
        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Predict defect
        result = predict_defect(image)
        
        return DefectClassificationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/api/classify-defect-base64", response_model=DefectClassificationResponse)
def classify_defect_base64(request: DefectClassificationRequest):
    """
    Classify railway component defect from base64 encoded image
    Used by mobile app to send captured photos
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Predict defect
        result = predict_defect(image)
        
        return DefectClassificationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/qr/inspection-with-ai")
def submit_inspection_with_ai(
    qr_id: str,
    status: str,
    remark: str,
    inspector_id: Optional[int] = None,
    file: Optional[UploadFile] = File(None)
):
    """
    Submit inspection with optional AI classification from photo
    """
    db = SessionLocal()
    try:
        # Check if item exists
        item = db.query(Item).filter(Item.uid == qr_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        ai_classification = None
        ai_confidence = None
        
        # If photo provided, run AI classification
        if file:
            try:
                image_data = file.file.read()
                image = Image.open(io.BytesIO(image_data))
                prediction = predict_defect(image)
                
                ai_classification = prediction['predicted_class']
                ai_confidence = prediction['confidence']
                
                # Use AI remark if no manual remark provided
                if not remark or remark.strip() == "":
                    remark = prediction['remark']
                    
            except Exception as e:
                print(f"AI classification failed: {e}")
                # Continue without AI classification
        
        # Create inspection record
        inspection = Inspection(
            item_uid=qr_id,
            status=status,
            remark=remark,
            inspector_id=inspector_id,
            ai_classification=ai_classification,
            ai_confidence=ai_confidence,
            inspected_at=datetime.utcnow()
        )
        db.add(inspection)
        
        # Update item status based on inspection
        if status in ["approved", "passed", "ok"]:
            item.current_status = "inspected"
        elif status in ["rejected", "failed", "damaged"]:
            item.current_status = "rejected"
        else:
            item.current_status = status
        
        item.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Inspection submitted successfully",
            "inspection_id": inspection.id,
            "item_uid": qr_id,
            "new_status": item.current_status,
            "ai_classification": ai_classification,
            "ai_confidence": ai_confidence
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving inspection: {str(e)}")
    finally:
        db.close()

@app.get("/api/model-status")
def get_model_status():
    """Check if VGG model is loaded and ready"""
    global _vgg_model
    
    is_loaded = _vgg_model is not None
    
    return {
        "model_loaded": is_loaded,
        "model_type": "VGG16 Transfer Learning" if is_loaded else None,
        "classes": _class_names if is_loaded else [],
        "status": "ready" if is_loaded else "not loaded",
        "message": "Model is ready for predictions" if is_loaded else "Model needs to be trained first"
    }

# ============================================================================
# YOLO COMPONENT DETECTION ENDPOINTS
# ============================================================================

@app.get("/api/detection-model-status")
def get_detection_model_status():
    """Check if YOLO object detection model is loaded and ready"""
    global _yolo_model
    
    is_loaded = _yolo_model is not None
    
    return {
        "model_loaded": is_loaded,
        "model_type": "YOLOv8 Object Detection" if is_loaded else None,
        "classes": _component_class_names if is_loaded else [],
        "class_descriptions": COMPONENT_DESCRIPTIONS if is_loaded else {},
        "status": "ready" if is_loaded else "not loaded",
        "message": "Model is ready for component detection" if is_loaded else "Model needs to be trained first"
    }

@app.post("/api/detect-components", response_model=ComponentDetectionResponse)
async def detect_railway_components(
    file: UploadFile = File(...),
    conf: float = 0.25
):
    """
    Detect railway track components in uploaded image
    
    Components detected:
    - elastic_clip: Spring clip holding rails to sleepers
    - liner: Metal plate between rail and sleeper
    - rubber_pad: Rubber cushion for vibration dampening
    - sleeper: Concrete/wooden cross-tie supporting rails
    
    Returns bounding boxes, class labels, and confidence scores for each detected component
    """
    try:
        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Detect components
        result = detect_components(image, conf_threshold=conf)
        
        # Convert to response model format
        detections = []
        for det in result.get('detections', []):
            detections.append(ComponentDetection(
                class_id=det['class_id'],
                class_name=det['class_name'],
                confidence=det['confidence'],
                bbox=BoundingBox(**det['bbox'])
            ))
        
        return ComponentDetectionResponse(
            num_detections=result['num_detections'],
            detections=detections,
            model_available=result.get('model_available', True),
            inference_time_ms=result.get('inference_time_ms')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/api/detect-components-base64")
def detect_components_base64(request: DefectClassificationRequest, conf: float = 0.25):
    """
    Detect railway components from base64 encoded image
    Used by mobile app to send captured photos
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Detect components
        result = detect_components(image, conf_threshold=conf)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.get("/api/component-classes")
def get_component_classes():
    """Get list of detectable railway component classes with descriptions"""
    return {
        "classes": _component_class_names,
        "descriptions": COMPONENT_DESCRIPTIONS
    }

# Load models on startup
@app.on_event("startup")
async def startup_event():
    """Load VGG and YOLO models when server starts"""
    print("\n" + "="*70)
    print("🚂 Railway Component Inspection Backend Starting...")
    print("="*70)
    print("\n📦 Loading AI Models...")
    load_vgg_model()
    load_yolo_model()
    print("="*70 + "\n")

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
