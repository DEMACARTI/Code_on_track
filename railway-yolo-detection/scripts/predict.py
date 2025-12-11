"""
Predict Railway Components using trained YOLOv8 model
Detect elastic_clip, liner, rubber_pad, sleeper in images
"""

import os
import sys
from pathlib import Path
import argparse
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_WEIGHTS = MODELS_DIR / "best.pt"
RESULTS_DIR = PROJECT_ROOT / "predictions"

# Class names
CLASS_NAMES = ['elastic_clip', 'liner', 'rubber_pad', 'sleeper']


def load_model(weights_path: str = None):
    """Load YOLOv8 model with trained weights"""
    from ultralytics import YOLO
    
    weights = Path(weights_path) if weights_path else DEFAULT_WEIGHTS
    
    if not weights.exists():
        print(f"❌ Model weights not found: {weights}")
        print("   Train a model first: python scripts/train_yolo.py")
        print("   Or specify weights: --weights path/to/best.pt")
        return None
    
    print(f"📦 Loading model from: {weights}")
    model = YOLO(str(weights))
    print(f"✅ Model loaded successfully")
    
    return model


def predict_single(model, image_path: str, conf_threshold: float = 0.25,
                   save: bool = True, show: bool = False):
    """
    Run prediction on a single image
    
    Returns:
        dict with detections
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return None
    
    # Run inference
    results = model.predict(
        source=str(image_path),
        conf=conf_threshold,
        save=save,
        show=show,
        project=str(RESULTS_DIR),
        name=datetime.now().strftime("%Y%m%d_%H%M%S"),
        exist_ok=True
    )
    
    # Parse results
    detections = []
    for result in results:
        boxes = result.boxes
        
        for i in range(len(boxes)):
            detection = {
                'class_id': int(boxes.cls[i].item()),
                'class_name': CLASS_NAMES[int(boxes.cls[i].item())],
                'confidence': float(boxes.conf[i].item()),
                'bbox': {
                    'x1': float(boxes.xyxy[i][0].item()),
                    'y1': float(boxes.xyxy[i][1].item()),
                    'x2': float(boxes.xyxy[i][2].item()),
                    'y2': float(boxes.xyxy[i][3].item())
                },
                'bbox_normalized': {
                    'x_center': float(boxes.xywhn[i][0].item()),
                    'y_center': float(boxes.xywhn[i][1].item()),
                    'width': float(boxes.xywhn[i][2].item()),
                    'height': float(boxes.xywhn[i][3].item())
                }
            }
            detections.append(detection)
    
    return {
        'image': str(image_path),
        'num_detections': len(detections),
        'detections': detections
    }


def predict_batch(model, source_dir: str, conf_threshold: float = 0.25,
                  save: bool = True, output_json: bool = True):
    """
    Run prediction on a directory of images
    
    Returns:
        list of detection results
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_path}")
        return None
    
    # Get all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    images = [f for f in source_path.iterdir() 
              if f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"⚠️  No images found in: {source_path}")
        return None
    
    print(f"\n📁 Found {len(images)} images in: {source_path}")
    print("=" * 70)
    
    all_results = []
    
    for img_path in images:
        print(f"   Processing: {img_path.name}...", end=" ")
        result = predict_single(model, img_path, conf_threshold, save=save, show=False)
        if result:
            print(f"Found {result['num_detections']} objects")
            all_results.append(result)
        else:
            print("Failed")
    
    # Save results to JSON
    if output_json and all_results:
        output_path = RESULTS_DIR / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✅ Results saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Detection Summary")
    print("=" * 70)
    
    total_detections = sum(r['num_detections'] for r in all_results)
    class_counts = {name: 0 for name in CLASS_NAMES}
    
    for result in all_results:
        for det in result['detections']:
            class_counts[det['class_name']] += 1
    
    print(f"\nTotal images processed: {len(all_results)}")
    print(f"Total detections: {total_detections}")
    print("\nDetections by class:")
    for class_name, count in class_counts.items():
        print(f"   {class_name:15s}: {count:5d}")
    
    return all_results


def predict_image_bytes(model, image_bytes: bytes, conf_threshold: float = 0.25):
    """
    Run prediction on image bytes (for API integration)
    
    Returns:
        dict with detections
    """
    import numpy as np
    from PIL import Image
    import io
    
    # Convert bytes to image
    image = Image.open(io.BytesIO(image_bytes))
    image_np = np.array(image)
    
    # Run inference
    results = model.predict(
        source=image_np,
        conf=conf_threshold,
        save=False,
        show=False
    )
    
    # Parse results
    detections = []
    for result in results:
        boxes = result.boxes
        
        for i in range(len(boxes)):
            detection = {
                'class_id': int(boxes.cls[i].item()),
                'class_name': CLASS_NAMES[int(boxes.cls[i].item())],
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
        'detections': detections
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Predict Railway Components with YOLOv8")
    
    parser.add_argument("--source", type=str, required=True,
                       help="Path to image file or directory")
    parser.add_argument("--weights", type=str, default=None,
                       help="Path to model weights (default: models/best.pt)")
    parser.add_argument("--conf", type=float, default=0.25,
                       help="Confidence threshold (default: 0.25)")
    parser.add_argument("--save", action="store_true", default=True,
                       help="Save annotated images")
    parser.add_argument("--no-save", action="store_true",
                       help="Don't save annotated images")
    parser.add_argument("--show", action="store_true",
                       help="Display results (requires display)")
    parser.add_argument("--json", action="store_true", default=True,
                       help="Save results to JSON")
    
    args = parser.parse_args()
    
    # Load model
    model = load_model(args.weights)
    if model is None:
        sys.exit(1)
    
    source = Path(args.source)
    save_images = not args.no_save
    
    print("\n" + "=" * 70)
    print("🔍 Railway Component Detection")
    print("=" * 70)
    print(f"\nSource: {source}")
    print(f"Confidence threshold: {args.conf}")
    print(f"Save images: {save_images}")
    
    if source.is_file():
        # Single image
        result = predict_single(model, source, args.conf, save=save_images, show=args.show)
        if result:
            print(f"\n✅ Found {result['num_detections']} components:")
            for det in result['detections']:
                print(f"   - {det['class_name']}: {det['confidence']:.2%}")
    
    elif source.is_dir():
        # Multiple images
        results = predict_batch(model, source, args.conf, save=save_images, output_json=args.json)
    
    else:
        print(f"❌ Invalid source: {source}")
        sys.exit(1)
    
    print("\n✅ Prediction complete!")
    if save_images:
        print(f"   Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
