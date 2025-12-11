"""
ResNet Component Classifiers
=============================
Classifies component condition (Good, Rust, Crack, Broken, etc.)
using ResNet50 models.
"""

from typing import Dict, List, Optional, Union
import numpy as np
from PIL import Image
import io


class ComponentClassifier:
    """
    Base class for component-specific ResNet classifiers.
    
    Each component type (ERC, Sleeper, Liner, Rubber Pad) can have
    its own classifier for defect detection.
    """
    
    # Condition categories
    CONDITIONS = ['Good', 'Fair', 'Bad']
    
    # Defect types per component
    DEFECT_TYPES = {
        'erc': ['Good', 'Rust', 'Crack', 'Broken', 'Missing'],
        'sleeper': ['Good', 'Crack', 'Broken', 'Abrasion', 'Weathered'],
        'liner': ['Good', 'Worn', 'Damaged', 'Missing'],
        'rubber_pad': ['Good', 'Worn', 'Cracked', 'Degraded']
    }
    
    def __init__(self, component_type: str = 'erc'):
        """
        Initialize classifier for a specific component type.
        
        Args:
            component_type: 'erc', 'sleeper', 'liner', or 'rubber_pad'
        """
        self.component_type = component_type
        self.model = None
        self.classes = self.DEFECT_TYPES.get(component_type, ['Good', 'Defective'])
        self._load_model()
    
    def _load_model(self):
        """
        Load the ResNet model for classification.
        
        Tries to load a trained PyTorch model from the models directory.
        Falls back to rule-based logic if model not found.
        """
        try:
            import torch
            import torch.nn as nn
            from torchvision import models
            from pathlib import Path
            
            # Look for trained model file
            model_paths = [
                Path(__file__).parent.parent.parent / 'railway-yolo-detection' / 'models' / f'{self.component_type}_classifier_best.pt',
                Path.cwd() / 'models' / f'{self.component_type}_classifier_best.pt',
                Path.home() / 'Code_on_track' / 'railway-yolo-detection' / 'models' / f'{self.component_type}_classifier_best.pt',
            ]
            
            for model_path in model_paths:
                if model_path.exists():
                    # Load checkpoint
                    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
                    
                    # Get class info from checkpoint
                    if 'class_names' in checkpoint:
                        self.classes = checkpoint['class_names']
                    num_classes = checkpoint.get('num_classes', len(self.classes))
                    
                    # Create model architecture
                    model = models.resnet50(weights=None)
                    model.fc = nn.Sequential(
                        nn.Dropout(0.5),
                        nn.Linear(model.fc.in_features, 512),
                        nn.ReLU(),
                        nn.Dropout(0.3),
                        nn.Linear(512, num_classes)
                    )
                    
                    # Load weights
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.eval()
                    
                    self.model = model
                    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                    self.model.to(self.device)
                    
                    print(f"✅ Loaded ResNet classifier for {self.component_type} from {model_path}")
                    print(f"   Classes: {self.classes}")
                    return
            
            # Model not found
            print(f"ℹ️ ResNet classifier for {self.component_type} using fallback mode (model not trained)")
            self.model = None
            
        except ImportError:
            print(f"ℹ️ PyTorch not available, {self.component_type} classifier using fallback mode")
            self.model = None
        except Exception as e:
            print(f"⚠️ Error loading {self.component_type} classifier: {e}")
            self.model = None
    
    def classify(self, image: Union[bytes, np.ndarray, Image.Image], 
                 detection_class: str = None) -> Dict:
        """
        Classify the condition of a detected component.
        
        Args:
            image: Cropped image of the component
            detection_class: Class name from YOLO detection (for fallback logic)
            
        Returns:
            Dict with classification results
        """
        # If ResNet model is not loaded, use fallback logic
        if self.model is None:
            return self._fallback_classify(detection_class)
        
        try:
            # Preprocess image
            if isinstance(image, bytes):
                img = Image.open(io.BytesIO(image))
            elif isinstance(image, np.ndarray):
                img = Image.fromarray(image)
            else:
                img = image
            
            # Resize to model input size
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Run inference
            predictions = self.model.predict(img_array, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            
            predicted_class = self.classes[predicted_class_idx]
            
            # Determine condition based on class
            if predicted_class == 'Good':
                condition = 'Good'
                defects = []
            else:
                condition = 'Bad' if confidence > 0.8 else 'Fair'
                defects = [predicted_class]
            
            return {
                'success': True,
                'condition': condition,
                'defect_class': predicted_class,
                'confidence': confidence,
                'defects': defects,
                'all_probabilities': {
                    cls: float(predictions[0][i]) 
                    for i, cls in enumerate(self.classes)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Classification failed: {str(e)}',
                'condition': 'Unknown',
                'defects': []
            }
    
    def _fallback_classify(self, detection_class: str = None) -> Dict:
        """
        Fallback classification based on YOLO detection class.
        
        Uses the YOLO class name to infer condition.
        """
        if detection_class is None:
            return {
                'success': True,
                'condition': 'Unknown',
                'defect_class': 'Unknown',
                'confidence': 0.0,
                'defects': [],
                'note': 'Classification model not available'
            }
        
        # Map YOLO class names to conditions
        detection_lower = detection_class.lower()
        
        if 'good' in detection_lower or 'normal' in detection_lower:
            condition = 'Good'
            defects = []
        elif 'missing' in detection_lower:
            condition = 'Bad'
            defects = ['Missing']
        elif 'bad' in detection_lower or 'broken' in detection_lower:
            condition = 'Bad'
            defects = ['Damaged']
        elif 'rust' in detection_lower or 'corroded' in detection_lower:
            condition = 'Fair'
            defects = ['Rust']
        elif 'crack' in detection_lower:
            condition = 'Fair'
            defects = ['Crack']
        elif 'worn' in detection_lower:
            condition = 'Fair'
            defects = ['Worn']
        else:
            # Default to Good if cannot determine
            condition = 'Good'
            defects = []
        
        return {
            'success': True,
            'condition': condition,
            'defect_class': detection_class,
            'confidence': 0.85,  # Fallback confidence
            'defects': defects,
            'note': 'Classification based on detection model (ResNet not available)'
        }
    
    def is_loaded(self) -> bool:
        """Check if classification model is loaded."""
        return self.model is not None


class ERCClassifier(ComponentClassifier):
    """Classifier for Elastic Rail Clip defects."""
    def __init__(self):
        super().__init__('erc')


class SleeperClassifier(ComponentClassifier):
    """Classifier for Sleeper defects."""
    def __init__(self):
        super().__init__('sleeper')


class LinerClassifier(ComponentClassifier):
    """Classifier for Liner defects."""
    def __init__(self):
        super().__init__('liner')


class RubberPadClassifier(ComponentClassifier):
    """Classifier for Rubber Pad defects."""
    def __init__(self):
        super().__init__('rubber_pad')
