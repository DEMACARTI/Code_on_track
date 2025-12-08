#!/usr/bin/env python3
"""
Railway Component Detection using YOLOv11
Detects defects in railway components (tracks, sleepers, fasteners, etc.)
Outputs results to JSON for LLM report generation
"""

from ultralytics import YOLO
import json
import os
from pathlib import Path
from datetime import datetime

# Configuration
MODEL_PATH = 'yolo11n.pt'  # Use YOLOv11 nano model (or your custom .pt file)
IMAGE_DIR = 'images'
OUTPUT_JSON = 'yolo_output.json'
CONFIDENCE_THRESHOLD = 0.25  # Lower threshold for detection, filter later
DEVICE = 'mps'  # Use 'mps' for Apple Silicon, 'cuda' for NVIDIA GPU, 'cpu' otherwise

# Defect class names (customize based on your trained model)
DEFECT_CLASSES = {
    'crack': 'Crack detected in component',
    'loose_bolt': 'Loose or missing bolt/fastener',
    'missing_clip': 'Missing rail clip',
    'loose_fastener': 'Loose fastener detected',
    'corrosion': 'Corrosion detected',
    'deformation': 'Component deformation',
    'wear': 'Excessive wear detected'
}

def load_yolo_model(model_path: str):
    """Load YOLO model from path"""
    print(f"Loading YOLO model from {model_path}...")
    model = YOLO(model_path)
    print(f"Model loaded successfully. Classes: {model.names}")
    return model

def run_detection(model, image_dir: str, confidence: float):
    """Run YOLO detection on all images in directory"""
    print(f"\nRunning detection on images in {image_dir}/")
    print(f"Confidence threshold: {confidence}")
    print(f"Device: {DEVICE}\n")
    
    # Run prediction
    results = model.predict(
        source=image_dir,
        conf=confidence,
        device=DEVICE,
        save=True,  # Save annotated images
        save_txt=False,  # Don't save txt labels
        save_json=False,  # We'll create custom JSON
        project='runs/detect',
        name='railway_inspection',
        exist_ok=True
    )
    
    return results

def format_results_to_json(results, output_path: str):
    """Convert YOLO results to structured JSON"""
    detections = []
    
    for result in results:
        image_path = result.path
        image_name = Path(image_path).name
        
        # Extract detection info
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[cls_id]
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detection = {
                    'image': image_name,
                    'class': class_name,
                    'confidence': round(confidence, 3),
                    'bbox': {
                        'x1': round(x1, 2),
                        'y1': round(y1, 2),
                        'x2': round(x2, 2),
                        'y2': round(y2, 2)
                    },
                    'description': DEFECT_CLASSES.get(class_name, 'Unknown defect')
                }
                detections.append(detection)
    
    # Create final output
    output_data = {
        'inspection_date': datetime.now().isoformat(),
        'total_images': len(results),
        'total_detections': len(detections),
        'model': MODEL_PATH,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'detections': detections
    }
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Detection results saved to {output_path}")
    print(f"  Total images processed: {output_data['total_images']}")
    print(f"  Total detections: {output_data['total_detections']}")
    
    return output_data

def main():
    """Main execution function"""
    print("=" * 60)
    print("Railway Component YOLO Detection Pipeline")
    print("=" * 60)
    
    # Check if image directory exists
    if not os.path.exists(IMAGE_DIR):
        print(f"\n❌ Error: Image directory '{IMAGE_DIR}/' not found!")
        print(f"Please create the directory and add images to inspect.")
        return
    
    # Check if images exist
    image_files = list(Path(IMAGE_DIR).glob('*.[jp][pn]g')) + list(Path(IMAGE_DIR).glob('*.jpeg'))
    if not image_files:
        print(f"\n❌ Error: No images found in '{IMAGE_DIR}/' directory!")
        print(f"Supported formats: .jpg, .jpeg, .png")
        return
    
    print(f"\nFound {len(image_files)} image(s) to process")
    
    # Load model
    try:
        model = load_yolo_model(MODEL_PATH)
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        print(f"\nModel file '{MODEL_PATH}' not found!")
        print(f"Downloading YOLOv11 nano model...")
        # YOLO will auto-download if model doesn't exist
        model = YOLO('yolo11n.pt')
    
    # Run detection
    results = run_detection(model, IMAGE_DIR, CONFIDENCE_THRESHOLD)
    
    # Format and save results
    output_data = format_results_to_json(results, OUTPUT_JSON)
    
    # Print summary by class
    print("\nDetection Summary by Class:")
    print("-" * 40)
    class_counts = {}
    for det in output_data['detections']:
        cls = det['class']
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    for cls, count in sorted(class_counts.items()):
        print(f"  {cls}: {count}")
    
    print("\n" + "=" * 60)
    print(f"✓ Detection complete! Results saved to: {OUTPUT_JSON}")
    print(f"✓ Annotated images saved to: runs/detect/railway_inspection/")
    print("=" * 60)

if __name__ == "__main__":
    main()
