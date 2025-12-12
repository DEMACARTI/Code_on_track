#!/usr/bin/env python3
"""
YOLO Detection Model Test Script
Tests the railway component detection model from DETECTION_Model directory
"""

import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import random

# Paths
MODEL_PATH = Path(__file__).parent / 'DETECTION_Model' / 'best.pt'
TEST_IMAGES_DIR = Path(__file__).parent / 'DETECTION_Model' / 'merged_dataset' / 'test' / 'images'
VALID_IMAGES_DIR = Path(__file__).parent / 'DETECTION_Model' / 'merged_dataset' / 'valid' / 'images'

# Detection class names (from data.yaml)
CLASS_NAMES = [
    'clip',
    'rail', 
    'bolt',
    'broken_rail',
    'sleeper',
    'correct',
    'overrailed',
    'underrailed',
    'mf'
]

def load_model():
    """Load YOLO detection model"""
    print(f"📦 Loading YOLO model from: {MODEL_PATH}")
    
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at: {MODEL_PATH}")
        return None
    
    try:
        model = YOLO(str(MODEL_PATH))
        print(f"✅ Model loaded successfully!")
        print(f"   Classes: {', '.join(CLASS_NAMES)}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def get_sample_images(num_samples=5):
    """Get random sample images from test/validation sets"""
    images = []
    
    # Try test images first
    if TEST_IMAGES_DIR.exists():
        test_images = list(TEST_IMAGES_DIR.glob('*.jpg'))
        images.extend(test_images)
    
    # Add validation images
    if VALID_IMAGES_DIR.exists():
        valid_images = list(VALID_IMAGES_DIR.glob('*.jpg'))
        images.extend(valid_images)
    
    if not images:
        print(f"❌ No images found in test or validation directories")
        return []
    
    # Random sample
    sample_size = min(num_samples, len(images))
    return random.sample(images, sample_size)

def run_detection(model, image_path, conf_threshold=0.25):
    """Run detection on a single image"""
    print(f"\n🔍 Detecting components in: {image_path.name}")
    
    # Run inference
    results = model.predict(
        source=str(image_path),
        conf=conf_threshold,
        save=False,
        verbose=False
    )
    
    # Parse results
    detections = []
    for result in results:
        boxes = result.boxes
        
        for i in range(len(boxes)):
            class_id = int(boxes.cls[i].item())
            class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"class_{class_id}"
            confidence = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy()
            
            detections.append({
                'class_id': class_id,
                'class_name': class_name,
                'confidence': confidence,
                'bbox': bbox
            })
    
    return detections

def display_detections(detections):
    """Display detection results in a formatted way"""
    if not detections:
        print("   ⚠️  No components detected")
        return
    
    print(f"   ✅ Found {len(detections)} component(s):")
    
    # Group by class
    by_class = {}
    for det in detections:
        class_name = det['class_name']
        if class_name not in by_class:
            by_class[class_name] = []
        by_class[class_name].append(det)
    
    # Display grouped results
    for class_name, dets in sorted(by_class.items()):
        count = len(dets)
        avg_conf = sum(d['confidence'] for d in dets) / count
        print(f"      • {class_name.upper()}: {count} detected (avg confidence: {avg_conf:.2%})")

def visualize_detection(model, image_path, output_dir='detection_results'):
    """Run detection and save annotated image"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Run inference with visualization
    results = model.predict(
        source=str(image_path),
        conf=0.25,
        save=True,
        project=str(output_path),
        name=image_path.stem,
        exist_ok=True
    )
    
    print(f"   💾 Saved annotated image to: {output_path}")

def main():
    """Main test function"""
    print("="*70)
    print("🚂 Railway Component Detection Model Test")
    print("="*70)
    
    # Load model
    model = load_model()
    if model is None:
        return
    
    print(f"\n📊 Model Information:")
    print(f"   Model file: {MODEL_PATH.name}")
    print(f"   Model size: {MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")
    print(f"   Classes: {len(CLASS_NAMES)}")
    
    # Get sample images
    print(f"\n🖼️  Loading sample images...")
    sample_images = get_sample_images(num_samples=5)
    
    if not sample_images:
        print("❌ No sample images found")
        return
    
    print(f"   Found {len(sample_images)} sample images")
    
    # Run detection on samples
    print(f"\n{'='*70}")
    print("Running Component Detection")
    print('='*70)
    
    all_detections = []
    for img_path in sample_images:
        detections = run_detection(model, img_path)
        display_detections(detections)
        all_detections.extend(detections)
    
    # Summary statistics
    print(f"\n{'='*70}")
    print("Detection Summary")
    print('='*70)
    
    if all_detections:
        # Count by class
        class_counts = {}
        for det in all_detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        print(f"\n📈 Total Components Detected: {len(all_detections)}")
        print(f"\n🏷️  Breakdown by Component Type:")
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_detections)) * 100
            print(f"   • {class_name.upper()}: {count} ({percentage:.1f}%)")
        
        avg_confidence = sum(d['confidence'] for d in all_detections) / len(all_detections)
        print(f"\n🎯 Average Confidence: {avg_confidence:.2%}")
    else:
        print("⚠️  No components detected in any images")
    
    # Visualize one sample
    print(f"\n{'='*70}")
    print("Creating Visualizations")
    print('='*70)
    
    if sample_images:
        print(f"\n📸 Creating annotated image for: {sample_images[0].name}")
        visualize_detection(model, sample_images[0])
    
    print(f"\n{'='*70}")
    print("✅ Test Complete!")
    print('='*70)

if __name__ == "__main__":
    main()
