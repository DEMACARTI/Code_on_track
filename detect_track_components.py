#!/usr/bin/env python3
"""
Railway Track Component Detector
Analyzes images to identify which components are installed on railway tracks
"""

import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np
from collections import Counter

# Paths
MODEL_PATH = Path(__file__).parent / 'DETECTION_Model' / 'best.pt'

# Detection class names with descriptions
COMPONENT_INFO = {
    'clip': {
        'name': 'Rail Clip',
        'description': 'Spring clips that secure rails to sleepers',
        'category': 'fastener'
    },
    'rail': {
        'name': 'Rail',
        'description': 'Steel rail track',
        'category': 'structure'
    },
    'bolt': {
        'name': 'Bolt',
        'description': 'Bolts used to secure components',
        'category': 'fastener'
    },
    'broken_rail': {
        'name': 'Broken Rail',
        'description': 'Damaged or broken rail section',
        'category': 'defect'
    },
    'sleeper': {
        'name': 'Sleeper',
        'description': 'Cross-ties supporting the rails',
        'category': 'structure'
    },
    'correct': {
        'name': 'Correct Installation',
        'description': 'Component properly installed',
        'category': 'status'
    },
    'overrailed': {
        'name': 'Over-railed',
        'description': 'Component positioned too high',
        'category': 'defect'
    },
    'underrailed': {
        'name': 'Under-railed',
        'description': 'Component positioned too low',
        'category': 'defect'
    },
    'mf': {
        'name': 'Missing/Faulty',
        'description': 'Missing or faulty component',
        'category': 'defect'
    }
}

def load_model():
    """Load YOLO detection model"""
    if not MODEL_PATH.exists():
        print(f"❌ Model not found at: {MODEL_PATH}")
        print(f"   Please ensure DETECTION_Model/best.pt exists")
        return None
    
    try:
        model = YOLO(str(MODEL_PATH))
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def detect_components(model, image_path, conf_threshold=0.25):
    """Detect components in an image"""
    results = model.predict(
        source=str(image_path),
        conf=conf_threshold,
        save=False,
        verbose=False
    )
    
    detections = []
    for result in results:
        boxes = result.boxes
        for i in range(len(boxes)):
            class_id = int(boxes.cls[i].item())
            class_name = list(COMPONENT_INFO.keys())[class_id] if class_id < len(COMPONENT_INFO) else f"unknown_{class_id}"
            confidence = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy()
            
            detections.append({
                'class_id': class_id,
                'class_name': class_name,
                'confidence': confidence,
                'bbox': bbox,
                'info': COMPONENT_INFO.get(class_name, {})
            })
    
    return detections

def analyze_track_installation(detections):
    """Analyze what components are installed on the track"""
    print("\n" + "="*70)
    print("📊 Track Installation Analysis")
    print("="*70)
    
    if not detections:
        print("\n⚠️  No components detected in this image")
        return
    
    # Categorize detections
    structures = [d for d in detections if d['info'].get('category') == 'structure']
    fasteners = [d for d in detections if d['info'].get('category') == 'fastener']
    defects = [d for d in detections if d['info'].get('category') == 'defect']
    status = [d for d in detections if d['info'].get('category') == 'status']
    
    # Component summary
    print(f"\n🔧 Components Detected: {len(detections)} total")
    
    if structures:
        print(f"\n🏗️  Structural Components ({len(structures)}):")
        for det in structures:
            print(f"   • {det['info']['name']}: {det['confidence']:.1%} confidence")
    
    if fasteners:
        print(f"\n🔩 Fastening Components ({len(fasteners)}):")
        for det in fasteners:
            print(f"   • {det['info']['name']}: {det['confidence']:.1%} confidence")
    
    if status:
        print(f"\n✅ Installation Status ({len(status)}):")
        for det in status:
            print(f"   • {det['info']['name']}: {det['confidence']:.1%} confidence")
    
    if defects:
        print(f"\n⚠️  Issues Detected ({len(defects)}):")
        for det in defects:
            print(f"   • {det['info']['name']}: {det['confidence']:.1%} confidence")
            print(f"      Description: {det['info']['description']}")
    
    # Overall assessment
    print(f"\n📋 Track Assessment:")
    
    has_defects = len(defects) > 0
    has_correct = any(d['class_name'] == 'correct' for d in status)
    
    if has_defects:
        print("   ⚠️  ATTENTION REQUIRED - Issues detected")
        defect_types = [d['info']['name'] for d in defects]
        print(f"      Issue types: {', '.join(defect_types)}")
    elif has_correct:
        print("   ✅ GOOD CONDITION - Components properly installed")
    else:
        print("   ℹ️  Status unclear - Manual inspection recommended")
    
    # Component count summary
    component_counts = Counter(d['class_name'] for d in detections)
    print(f"\n📈 Component Breakdown:")
    for comp, count in component_counts.most_common():
        info = COMPONENT_INFO.get(comp, {})
        name = info.get('name', comp)
        print(f"   • {name}: {count}")

def visualize_detections(model, image_path, output_path='track_analysis.jpg', conf_threshold=0.25):
    """Create annotated visualization"""
    # Read image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"❌ Could not read image: {image_path}")
        return None
    
    # Get detections
    detections = detect_components(model, image_path, conf_threshold)
    
    # Draw bounding boxes
    for det in detections:
        bbox = det['bbox'].astype(int)
        x1, y1, x2, y2 = bbox
        
        # Color based on category
        category = det['info'].get('category', 'unknown')
        colors = {
            'structure': (0, 255, 0),      # Green
            'fastener': (255, 165, 0),     # Orange
            'defect': (0, 0, 255),         # Red
            'status': (255, 255, 0),       # Yellow
            'unknown': (128, 128, 128)     # Gray
        }
        color = colors.get(category, (128, 128, 128))
        
        # Draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{det['info'].get('name', det['class_name'])}: {det['confidence']:.0%}"
        
        # Background for text
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - text_height - 5), (x1 + text_width, y1), color, -1)
        
        # Text
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Save annotated image
    cv2.imwrite(output_path, img)
    print(f"\n💾 Saved annotated image to: {output_path}")
    
    return detections

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python detect_track_components.py <image_path>")
        print("\nExample:")
        print("  python detect_track_components.py DETECTION_Model/merged_dataset/test/images/sample.jpg")
        return
    
    image_path = Path(sys.argv[1])
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    print("="*70)
    print("🚂 Railway Track Component Detection")
    print("="*70)
    print(f"\n📸 Analyzing image: {image_path.name}")
    
    # Load model
    model = load_model()
    if model is None:
        return
    
    # Detect and visualize
    detections = visualize_detections(model, image_path, f'analyzed_{image_path.name}')
    
    # Analyze installation
    if detections:
        analyze_track_installation(detections)
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print("="*70)

if __name__ == "__main__":
    main()
