"""
Multi-Model AI Pipeline for Railway Component Inspection
=========================================================
This package provides a cascading pipeline:
1. YOLO Detection - Identifies component type
2. ResNet Classification - Classifies component condition
"""

from .pipeline import InspectionPipeline, get_pipeline
from .detector import ComponentDetector
from .classifiers import ComponentClassifier

__all__ = ['InspectionPipeline', 'get_pipeline', 'ComponentDetector', 'ComponentClassifier']

