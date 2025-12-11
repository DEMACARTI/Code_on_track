"""
YOLO Component Detector
=======================
Detects railway components using YOLOv8 model.
Enforces single-component policy.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import io


class ComponentDetector:
    """YOLO-based railway component detector with single-component enforcement."""
    
    # Supported component types and their model mappings
    COMPONENT_MODELS = {
        'erc': {
            'model_path': 'railway-yolo-detection/models/best.pt',
            'classes': ['elastic_clip_good', 'elastic_clip_missing'],
            'display_name': 'Elastic Rail Clip'
        },
        'sleeper': {
            'model_path': 'railway-yolo-detection/models/sleeper_best.pt', 
            'classes': ['clips', 'sleepers'],
            'display_name': 'Sleeper'
        }
    }
    
    def __init__(self, model_type: str = 'erc', confidence_threshold: float = 0.5):
        """
        Initialize the component detector.
        
        Args:
            model_type: Type of component to detect ('erc', 'sleeper', 'liner', 'rubber_pad')
            confidence_threshold: Minimum confidence for detection
        """
        self.model_type = model_type
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.classes = []
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model for the specified component type."""
        try:
            from ultralytics import YOLO
            
            if self.model_type not in self.COMPONENT_MODELS:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            config = self.COMPONENT_MODELS[self.model_type]
            
            # Try multiple paths for model
            base_paths = [
                Path(__file__).parent.parent.parent,  # From pipeline folder
                Path.cwd(),
                Path.home() / 'Code_on_track'
            ]
            
            model_loaded = False
            for base in base_paths:
                model_path = base / config['model_path']
                if model_path.exists():
                    self.model = YOLO(str(model_path))
                    self.classes = config['classes']
                    model_loaded = True
                    print(f"✅ Loaded {self.model_type} detector from: {model_path}")
                    break
            
            if not model_loaded:
                print(f"⚠️ Model not found for {self.model_type}, using default YOLOv8n")
                self.model = YOLO('yolov8n.pt')
                
        except ImportError:
            print("⚠️ ultralytics not installed, detector will not work")
            self.model = None
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def detect(self, image: Union[bytes, np.ndarray, Image.Image, str]) -> Dict:
        """
        Detect components in an image.
        
        Args:
            image: Image as bytes, numpy array, PIL Image, or file path
            
        Returns:
            Dict with detection results including single-component enforcement
        """
        if self.model is None:
            return {
                'success': False,
                'error': 'Model not loaded',
                'detections': []
            }
        
        try:
            # Convert image to appropriate format
            if isinstance(image, bytes):
                img = Image.open(io.BytesIO(image))
                img_array = np.array(img)
            elif isinstance(image, Image.Image):
                img_array = np.array(image)
            elif isinstance(image, str):
                img_array = np.array(Image.open(image))
            else:
                img_array = image
            
            # Run detection
            results = self.model(img_array, conf=self.confidence_threshold, verbose=False)
            
            # Parse results
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        detection = {
                            'class_id': int(box.cls[0]),
                            'class_name': self.classes[int(box.cls[0])] if int(box.cls[0]) < len(self.classes) else f"class_{int(box.cls[0])}",
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                            'bbox_normalized': box.xywhn[0].tolist()  # [x_center, y_center, w, h] normalized
                        }
                        detections.append(detection)
            
            # Single-component enforcement
            unique_classes = set(d['class_name'] for d in detections)
            
            if len(detections) == 0:
                return {
                    'success': False,
                    'error': 'No component detected. Please ensure the component is clearly visible.',
                    'detections': [],
                    'component_count': 0
                }
            
            if len(unique_classes) > 1:
                return {
                    'success': False,
                    'error': f'Multiple component types detected ({", ".join(unique_classes)}). Please capture only ONE component.',
                    'detections': detections,
                    'component_count': len(detections)
                }
            
            # Return successful detection (single component)
            primary_detection = max(detections, key=lambda x: x['confidence'])
            
            return {
                'success': True,
                'component_type': self.model_type,
                'component_class': primary_detection['class_name'],
                'confidence': primary_detection['confidence'],
                'bbox': primary_detection['bbox'],
                'detections': detections,
                'component_count': len(detections)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Detection failed: {str(e)}',
                'detections': []
            }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None


class MultiComponentDetector:
    """Wrapper that can detect multiple component types."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.detectors = {}
        
        # Load all available detectors
        for model_type in ComponentDetector.COMPONENT_MODELS.keys():
            try:
                detector = ComponentDetector(model_type, confidence_threshold)
                if detector.is_loaded():
                    self.detectors[model_type] = detector
            except Exception as e:
                print(f"⚠️ Could not load {model_type} detector: {e}")
    
    def detect_all(self, image: Union[bytes, np.ndarray, Image.Image, str]) -> Dict:
        """
        Run all detectors on an image and return combined results.
        
        Returns the detection with highest confidence across all detectors.
        """
        all_results = {}
        best_result = None
        best_confidence = 0
        
        for model_type, detector in self.detectors.items():
            result = detector.detect(image)
            all_results[model_type] = result
            
            if result['success'] and result['confidence'] > best_confidence:
                best_confidence = result['confidence']
                best_result = result
        
        if best_result:
            return best_result
        
        # Return first error if no successful detection
        for result in all_results.values():
            return result
        
        return {
            'success': False,
            'error': 'No detectors available',
            'detections': []
        }
