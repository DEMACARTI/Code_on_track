"""
Train YOLOv8 for Railway Component Detection
Fine-tune YOLOv8 to detect: elastic_clip, liner, rubber_pad, sleeper
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import yaml
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATA_YAML = PROJECT_ROOT / "data" / "data.yaml"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "runs"


def check_requirements():
    """Check if required packages are installed"""
    print("=" * 70)
    print("🔍 Checking Requirements")
    print("=" * 70)
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"   Apple MPS: Available")
    except ImportError:
        print("❌ PyTorch not installed!")
        return False
    
    try:
        from ultralytics import YOLO
        import ultralytics
        print(f"✅ Ultralytics: {ultralytics.__version__}")
    except ImportError:
        print("❌ Ultralytics not installed! Run: pip install ultralytics")
        return False
    
    return True


def check_dataset():
    """Verify dataset exists and is properly formatted"""
    print("\n" + "=" * 70)
    print("📊 Checking Dataset")
    print("=" * 70)
    
    if not DATA_YAML.exists():
        print(f"❌ data.yaml not found at: {DATA_YAML}")
        print("   Run: python scripts/download_dataset.py")
        return False
    
    with open(DATA_YAML, 'r') as f:
        data_config = yaml.safe_load(f)
    
    data_path = Path(data_config.get('path', PROJECT_ROOT / 'data'))
    train_path = data_path / data_config.get('train', 'images/train')
    val_path = data_path / data_config.get('val', 'images/val')
    
    print(f"📁 Data path: {data_path}")
    print(f"📁 Train path: {train_path}")
    print(f"📁 Val path: {val_path}")
    
    # Count images
    train_images = list(train_path.glob("*")) if train_path.exists() else []
    val_images = list(val_path.glob("*")) if val_path.exists() else []
    
    train_images = [f for f in train_images if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
    val_images = [f for f in val_images if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Training images: {len(train_images)}")
    print(f"   Validation images: {len(val_images)}")
    print(f"   Classes: {data_config.get('nc', 0)}")
    print(f"   Class names: {data_config.get('names', {})}")
    
    if len(train_images) == 0:
        print("\n⚠️  No training images found!")
        print("   Run: python scripts/download_dataset.py")
        return False
    
    return True


def train(
    model_size: str = "n",  # n, s, m, l, x
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    patience: int = 20,
    device: str = None,
    resume: bool = False,
    pretrained: str = None
):
    """
    Train YOLOv8 model for railway component detection
    
    Args:
        model_size: YOLOv8 model size (n=nano, s=small, m=medium, l=large, x=xlarge)
        epochs: Number of training epochs
        batch_size: Batch size (reduce if OOM)
        img_size: Input image size
        patience: Early stopping patience
        device: Device to train on (cuda, mps, cpu, or specific GPU index)
        resume: Resume training from last checkpoint
        pretrained: Path to pretrained weights
    """
    from ultralytics import YOLO
    import torch
    
    print("\n" + "=" * 70)
    print("🚀 Starting YOLOv8 Training")
    print("=" * 70)
    
    # Determine device
    if device is None:
        if torch.cuda.is_available():
            device = "0"  # First GPU
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon
        else:
            device = "cpu"
    
    print(f"\n⚙️  Training Configuration:")
    print(f"   Model size: YOLOv8{model_size}")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Image size: {img_size}")
    print(f"   Early stopping patience: {patience}")
    print(f"   Device: {device}")
    
    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load model
    if pretrained and Path(pretrained).exists():
        print(f"\n📦 Loading pretrained weights: {pretrained}")
        model = YOLO(pretrained)
    else:
        print(f"\n📦 Loading YOLOv8{model_size} pretrained on COCO")
        model = YOLO(f"yolov8{model_size}.pt")
    
    # Training configuration
    train_args = {
        'data': str(DATA_YAML),
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'patience': patience,
        'device': device,
        'project': str(RESULTS_DIR),
        'name': f'railway_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'close_mosaic': 10,
        'resume': resume,
        # Data augmentation
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 10,
        'translate': 0.1,
        'scale': 0.5,
        'shear': 5,
        'perspective': 0.0,
        'flipud': 0.0,  # Railway components have orientation
        'fliplr': 0.5,
        'mosaic': 1.0,
        'mixup': 0.1,
        'copy_paste': 0.1,
        # Saving
        'save': True,
        'save_period': 10,
        'val': True,
        'plots': True,
    }
    
    print("\n🏋️ Starting training...")
    print("=" * 70)
    
    # Train the model
    results = model.train(**train_args)
    
    # Copy best model to models directory
    best_model_src = Path(results.save_dir) / "weights" / "best.pt"
    best_model_dst = MODELS_DIR / "best.pt"
    
    if best_model_src.exists():
        import shutil
        shutil.copy2(best_model_src, best_model_dst)
        print(f"\n✅ Best model saved to: {best_model_dst}")
    
    # Print results summary
    print("\n" + "=" * 70)
    print("📊 Training Complete!")
    print("=" * 70)
    print(f"\n📁 Results saved to: {results.save_dir}")
    print(f"📦 Best model: {best_model_dst}")
    
    # Print metrics
    if hasattr(results, 'results_dict'):
        print("\n📈 Final Metrics:")
        for key, value in results.results_dict.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
    
    print("\n🚀 Next steps:")
    print("   1. Review training plots in results directory")
    print("   2. Test model: python scripts/predict.py --source test_images/")
    print("   3. Evaluate: python scripts/evaluate.py")
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Train YOLOv8 for Railway Component Detection")
    
    parser.add_argument("--model", type=str, default="n", 
                       choices=["n", "s", "m", "l", "x"],
                       help="Model size: n(ano), s(mall), m(edium), l(arge), x(large)")
    parser.add_argument("--epochs", type=int, default=100,
                       help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16,
                       help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640,
                       help="Input image size")
    parser.add_argument("--patience", type=int, default=20,
                       help="Early stopping patience")
    parser.add_argument("--device", type=str, default=None,
                       help="Device: cuda, mps, cpu, or GPU index")
    parser.add_argument("--resume", action="store_true",
                       help="Resume training from last checkpoint")
    parser.add_argument("--weights", type=str, default=None,
                       help="Path to pretrained weights")
    parser.add_argument("--test", action="store_true",
                       help="Test mode: train for 1 epoch only")
    
    args = parser.parse_args()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check dataset
    if not check_dataset():
        print("\n⚠️  Dataset not ready. Please prepare dataset first.")
        print("   Run: python scripts/download_dataset.py")
        sys.exit(1)
    
    # Test mode
    if args.test:
        args.epochs = 1
        args.batch = 4
        print("\n🧪 TEST MODE: Training for 1 epoch with batch size 4")
    
    # Train
    train(
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        patience=args.patience,
        device=args.device,
        resume=args.resume,
        pretrained=args.weights
    )


if __name__ == "__main__":
    main()
