"""
Main Inspection Pipeline
========================
Orchestrates YOLO detection → ResNet classification flow.
"""

from typing import Dict, List, Optional, Union
from PIL import Image
import numpy as np
import io
import base64

from .detector import ComponentDetector, MultiComponentDetector
from .classifiers import (
    ComponentClassifier, 
    ERCClassifier, 
    SleeperClassifier,
    LinerClassifier,
    RubberPadClassifier
)


class InspectionPipeline:
    """
    Main pipeline for railway component inspection.
    
    Flow:
    1. Receive image from mobile app
    2. Run YOLO detection to identify component
    3. Enforce single-component policy
    4. Run ResNet classification for defect detection
    5. Return combined results
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the inspection pipeline.
        
        Args:
            confidence_threshold: Minimum confidence for detection
        """
        self.confidence_threshold = confidence_threshold
        self.detectors = {}
        self.classifiers = {}
        self._initialized = False
        
    def initialize(self):
        """Load all models (call this at startup)."""
        print("🚀 Initializing Inspection Pipeline...")
        
        # Load available detectors
        for model_type in ['erc', 'sleeper']:
            try:
                detector = ComponentDetector(model_type, self.confidence_threshold)
                if detector.is_loaded():
                    self.detectors[model_type] = detector
                    print(f"  ✅ {model_type.upper()} detector loaded")
            except Exception as e:
                print(f"  ❌ Failed to load {model_type} detector: {e}")
        
        # Load classifiers
        classifier_map = {
            'erc': ERCClassifier,
            'sleeper': SleeperClassifier,
            'liner': LinerClassifier,
            'rubber_pad': RubberPadClassifier
        }
        
        for comp_type, classifier_cls in classifier_map.items():
            try:
                self.classifiers[comp_type] = classifier_cls()
                print(f"  ✅ {comp_type.upper()} classifier loaded")
            except Exception as e:
                print(f"  ❌ Failed to load {comp_type} classifier: {e}")
        
        self._initialized = True
        print(f"✅ Pipeline initialized with {len(self.detectors)} detectors and {len(self.classifiers)} classifiers")
    
    def inspect(self, image: Union[bytes, np.ndarray, Image.Image, str], 
                component_type: str = None) -> Dict:
        """
        Run full inspection pipeline on an image.
        
        Args:
            image: Image to inspect (bytes, numpy array, PIL Image, or path)
            component_type: Optional - specify component type ('erc', 'sleeper', etc.)
                          If None, tries all detectors
        
        Returns:
            Dict with inspection results
        """
        if not self._initialized:
            self.initialize()
        
        # Step 1: Detection
        detection_result = self._detect(image, component_type)
        
        if not detection_result['success']:
            return detection_result
        
        # Step 2: Classification
        classification_result = self._classify(
            image, 
            detection_result['component_type'],
            detection_result['component_class']
        )
        
        # Step 3: Combine results
        return {
            'success': True,
            'component_type': detection_result['component_type'],
            'component_class': detection_result['component_class'],
            'detection_confidence': detection_result['confidence'],
            'bbox': detection_result['bbox'],
            'condition': classification_result['condition'],
            'defects': classification_result['defects'],
            'classification_confidence': classification_result['confidence'],
            'recommendations': self._get_recommendations(
                detection_result['component_class'],
                classification_result['condition'],
                classification_result['defects']
            )
        }
    
    def _detect(self, image: Union[bytes, np.ndarray, Image.Image, str],
                component_type: str = None) -> Dict:
        """Run detection step."""
        
        if component_type and component_type in self.detectors:
            # Use specific detector
            return self.detectors[component_type].detect(image)
        
        # Try all detectors and return best result
        best_result = None
        best_confidence = 0
        
        for detector_type, detector in self.detectors.items():
            result = detector.detect(image)
            if result['success'] and result.get('confidence', 0) > best_confidence:
                best_confidence = result['confidence']
                best_result = result
        
        if best_result:
            return best_result
        
        # If no successful detection, return error
        return {
            'success': False,
            'error': 'No railway component detected. Please capture a clear image of a single component.',
            'detections': []
        }
    
    def _classify(self, image: Union[bytes, np.ndarray, Image.Image, str],
                  component_type: str, detection_class: str) -> Dict:
        """Run classification step."""
        
        classifier = self.classifiers.get(component_type)
        
        if classifier:
            return classifier.classify(image, detection_class)
        
        # Fallback classification
        return ComponentClassifier(component_type)._fallback_classify(detection_class)
    
    def _get_recommendations(self, component_class: str, condition: str, 
                            defects: List[str]) -> List[str]:
        """Generate maintenance recommendations based on inspection results."""
        
        recommendations = []
        
        if condition == 'Good':
            recommendations.append("Component is in good condition. No immediate action required.")
        elif condition == 'Fair':
            recommendations.append("Component shows minor wear. Schedule inspection within 30 days.")
            for defect in defects:
                if defect == 'Rust':
                    recommendations.append("Apply anti-corrosion treatment.")
                elif defect == 'Crack':
                    recommendations.append("Monitor crack progression closely.")
                elif defect == 'Worn':
                    recommendations.append("Consider replacement during next maintenance window.")
        elif condition == 'Bad':
            recommendations.append("⚠️ URGENT: Component requires immediate attention.")
            for defect in defects:
                if defect == 'Missing':
                    recommendations.append("Replace missing component immediately.")
                elif defect == 'Broken':
                    recommendations.append("Replace damaged component before next train passage.")
                else:
                    recommendations.append(f"Address {defect} issue urgently.")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """Get pipeline status and loaded models."""
        return {
            'initialized': self._initialized,
            'detectors': {
                name: detector.is_loaded() 
                for name, detector in self.detectors.items()
            },
            'classifiers': {
                name: classifier.is_loaded() 
                for name, classifier in self.classifiers.items()
            },
            'supported_components': list(ComponentDetector.COMPONENT_MODELS.keys())
        }


# Singleton instance
_pipeline_instance = None

def get_pipeline() -> InspectionPipeline:
    """Get or create the singleton pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = InspectionPipeline()
        _pipeline_instance.initialize()
    return _pipeline_instance
