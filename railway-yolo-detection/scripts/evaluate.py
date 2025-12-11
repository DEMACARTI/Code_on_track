"""
Evaluate trained YOLOv8 model for Railway Component Detection
Generate metrics: mAP, precision, recall, confusion matrix
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
DATA_YAML = PROJECT_ROOT / "data" / "data.yaml"
MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_WEIGHTS = MODELS_DIR / "best.pt"
RESULTS_DIR = PROJECT_ROOT / "evaluation"

# Class names
CLASS_NAMES = ['elastic_clip', 'liner', 'rubber_pad', 'sleeper']


def evaluate_model(weights_path: str = None, data_yaml: str = None,
                   conf_threshold: float = 0.001, iou_threshold: float = 0.6,
                   save_plots: bool = True):
    """
    Evaluate YOLOv8 model on validation dataset
    
    Args:
        weights_path: Path to model weights
        data_yaml: Path to data configuration file
        conf_threshold: Confidence threshold for evaluation
        iou_threshold: IoU threshold for mAP calculation
        save_plots: Whether to save confusion matrix and other plots
    
    Returns:
        dict with evaluation metrics
    """
    from ultralytics import YOLO
    
    weights = Path(weights_path) if weights_path else DEFAULT_WEIGHTS
    data = Path(data_yaml) if data_yaml else DATA_YAML
    
    if not weights.exists():
        print(f"❌ Model weights not found: {weights}")
        print("   Train a model first: python scripts/train_yolo.py")
        return None
    
    if not data.exists():
        print(f"❌ Data config not found: {data}")
        return None
    
    print("=" * 70)
    print("📊 Model Evaluation")
    print("=" * 70)
    print(f"\n📦 Weights: {weights}")
    print(f"📁 Data config: {data}")
    print(f"🎯 Confidence threshold: {conf_threshold}")
    print(f"📐 IoU threshold: {iou_threshold}")
    
    # Load model
    model = YOLO(str(weights))
    
    # Create results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Run validation
    print("\n🔍 Running validation...")
    print("=" * 70)
    
    results = model.val(
        data=str(data),
        conf=conf_threshold,
        iou=iou_threshold,
        project=str(RESULTS_DIR),
        name=results_name,
        exist_ok=True,
        plots=save_plots,
        save_json=True,
        verbose=True
    )
    
    # Extract metrics
    metrics = {
        'mAP50': float(results.box.map50),
        'mAP50-95': float(results.box.map),
        'precision': float(results.box.mp),
        'recall': float(results.box.mr),
        'class_metrics': {}
    }
    
    # Per-class metrics
    for i, class_name in enumerate(CLASS_NAMES):
        if i < len(results.box.ap50):
            metrics['class_metrics'][class_name] = {
                'AP50': float(results.box.ap50[i]),
                'AP50-95': float(results.box.ap[i])
            }
    
    # Print summary
    print("\n" + "=" * 70)
    print("📈 Evaluation Results")
    print("=" * 70)
    
    print(f"\n🎯 Overall Metrics:")
    print(f"   mAP@50:     {metrics['mAP50']:.4f} ({metrics['mAP50']*100:.2f}%)")
    print(f"   mAP@50-95:  {metrics['mAP50-95']:.4f} ({metrics['mAP50-95']*100:.2f}%)")
    print(f"   Precision:  {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"   Recall:     {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    
    print(f"\n📊 Per-Class AP@50:")
    for class_name, class_metrics in metrics['class_metrics'].items():
        ap50 = class_metrics['AP50']
        print(f"   {class_name:15s}: {ap50:.4f} ({ap50*100:.2f}%)")
    
    # Quality assessment
    print("\n" + "=" * 70)
    print("🏆 Quality Assessment")
    print("=" * 70)
    
    if metrics['mAP50'] >= 0.75:
        print("✅ EXCELLENT: mAP@50 >= 75% - Model is production ready!")
    elif metrics['mAP50'] >= 0.60:
        print("✅ GOOD: mAP@50 >= 60% - Model performs well")
    elif metrics['mAP50'] >= 0.45:
        print("⚠️  FAIR: mAP@50 >= 45% - Model needs improvement")
    else:
        print("❌ POOR: mAP@50 < 45% - More training data or epochs needed")
    
    # Save metrics to JSON
    metrics_path = RESULTS_DIR / results_name / "metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n📁 Results saved to: {RESULTS_DIR / results_name}")
    print(f"   - metrics.json")
    if save_plots:
        print(f"   - confusion_matrix.png")
        print(f"   - PR_curve.png")
        print(f"   - F1_curve.png")
    
    return metrics


def compare_models(weights_list: list, data_yaml: str = None):
    """
    Compare multiple models on the same dataset
    """
    print("=" * 70)
    print("📊 Model Comparison")
    print("=" * 70)
    
    all_results = []
    
    for weights_path in weights_list:
        print(f"\n🔍 Evaluating: {weights_path}")
        metrics = evaluate_model(weights_path, data_yaml, save_plots=False)
        if metrics:
            metrics['weights'] = str(weights_path)
            all_results.append(metrics)
    
    # Print comparison table
    if all_results:
        print("\n" + "=" * 70)
        print("📈 Comparison Summary")
        print("=" * 70)
        print(f"\n{'Model':<40} {'mAP@50':<10} {'mAP@50-95':<12} {'Precision':<10} {'Recall':<10}")
        print("-" * 82)
        
        for result in all_results:
            name = Path(result['weights']).stem
            print(f"{name:<40} {result['mAP50']:.4f}     {result['mAP50-95']:.4f}       "
                  f"{result['precision']:.4f}     {result['recall']:.4f}")
    
    return all_results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Evaluate YOLOv8 Railway Component Detection Model")
    
    parser.add_argument("--weights", type=str, default=None,
                       help="Path to model weights (default: models/best.pt)")
    parser.add_argument("--data", type=str, default=None,
                       help="Path to data.yaml (default: data/data.yaml)")
    parser.add_argument("--conf", type=float, default=0.001,
                       help="Confidence threshold for evaluation")
    parser.add_argument("--iou", type=float, default=0.6,
                       help="IoU threshold for mAP calculation")
    parser.add_argument("--no-plots", action="store_true",
                       help="Don't save plots")
    parser.add_argument("--compare", nargs='+', type=str,
                       help="Compare multiple models")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_models(args.compare, args.data)
    else:
        evaluate_model(
            weights_path=args.weights,
            data_yaml=args.data, 
            conf_threshold=args.conf,
            iou_threshold=args.iou,
            save_plots=not args.no_plots
        )


if __name__ == "__main__":
    main()
