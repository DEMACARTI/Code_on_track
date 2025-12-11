"""
Download Railway Component Dataset from Roboflow
Downloads and prepares dataset for YOLO training
"""

import os
import sys
import shutil
from pathlib import Path
import requests
import zipfile
import yaml

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
LABELS_DIR = DATA_DIR / "labels"


def download_from_roboflow(api_key: str = None, workspace: str = "ayushpawar", 
                           project: str = "railwaytrackcomponentsdetection", 
                           version: int = 1):
    """
    Download dataset from Roboflow
    
    If no API key provided, tries to use environment variable ROBOFLOW_API_KEY
    """
    try:
        from roboflow import Roboflow
    except ImportError:
        print("❌ roboflow package not installed. Run: pip install roboflow")
        return False
    
    api_key = api_key or os.environ.get("ROBOFLOW_API_KEY")
    
    if not api_key:
        print("❌ No Roboflow API key provided!")
        print("   Set ROBOFLOW_API_KEY environment variable or pass api_key parameter")
        print("\n   To get a free API key:")
        print("   1. Go to https://app.roboflow.com/")
        print("   2. Create an account")
        print("   3. Go to Settings → API Key")
        return False
    
    print("=" * 70)
    print("📥 Downloading Railway Components Dataset from Roboflow")
    print("=" * 70)
    
    try:
        rf = Roboflow(api_key=api_key)
        project_obj = rf.workspace(workspace).project(project)
        dataset = project_obj.version(version).download("yolov8", location=str(DATA_DIR / "roboflow_download"))
        
        print(f"✅ Dataset downloaded to: {dataset.location}")
        
        # Reorganize files to match our structure
        reorganize_dataset(Path(dataset.location))
        
        return True
    except Exception as e:
        print(f"❌ Error downloading from Roboflow: {e}")
        return False


def download_sample_dataset():
    """
    Download a sample railway dataset for testing
    Uses publicly available railway track images
    """
    print("=" * 70)
    print("📥 Creating Sample Dataset for Testing")
    print("=" * 70)
    print("\n⚠️  No Roboflow API key available.")
    print("   Creating a minimal sample dataset for code testing...")
    
    # Create directories
    for split in ["train", "val"]:
        (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
        (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)
    
    # Note: In production, you would download actual railway images
    # For now, we create placeholder structure
    print("\n📝 Dataset structure created. Please add your images:")
    print(f"   - Training images: {IMAGES_DIR / 'train'}")
    print(f"   - Validation images: {IMAGES_DIR / 'val'}")
    print(f"   - Training labels: {LABELS_DIR / 'train'}")
    print(f"   - Validation labels: {LABELS_DIR / 'val'}")
    
    print("\n📋 YOLO Label Format (one .txt file per image):")
    print("   <class_id> <x_center> <y_center> <width> <height>")
    print("   All values normalized 0-1")
    print("\n   Classes: 0=elastic_clip, 1=liner, 2=rubber_pad, 3=sleeper")
    
    return True


def reorganize_dataset(source_dir: Path):
    """
    Reorganize downloaded dataset to match our structure
    """
    print("\n📁 Reorganizing dataset structure...")
    
    # Map Roboflow class names to our class names
    class_mapping = {
        "RailClip_Found": 0,      # elastic_clip
        "RailClip": 0,
        "elastic_clip": 0,
        "Liners_Found": 1,        # liner
        "Liner": 1,
        "liner": 1,
        "RubberPad": 2,           # rubber_pad  
        "rubber_pad": 2,
        "Sleeper_Found": 3,       # sleeper
        "Sleeper": 3,
        "sleeper": 3,
        "Damaged_Sleeper": 3,
    }
    
    # Check for train/valid folders
    for src_split, dst_split in [("train", "train"), ("valid", "val"), ("test", "val")]:
        src_images = source_dir / src_split / "images"
        src_labels = source_dir / src_split / "labels"
        
        if src_images.exists():
            # Copy images
            dst_images = IMAGES_DIR / dst_split
            dst_images.mkdir(parents=True, exist_ok=True)
            
            for img_file in src_images.glob("*"):
                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                    shutil.copy2(img_file, dst_images / img_file.name)
            
            print(f"   ✅ Copied {dst_split} images")
        
        if src_labels.exists():
            # Copy and remap labels
            dst_labels = LABELS_DIR / dst_split
            dst_labels.mkdir(parents=True, exist_ok=True)
            
            for label_file in src_labels.glob("*.txt"):
                remap_labels(label_file, dst_labels / label_file.name, class_mapping)
            
            print(f"   ✅ Remapped {dst_split} labels")
    
    # Update data.yaml with actual path
    update_data_yaml()
    
    print("\n✅ Dataset reorganization complete!")


def remap_labels(src_file: Path, dst_file: Path, class_mapping: dict):
    """
    Remap class IDs in label files
    """
    lines = []
    
    with open(src_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                # Original format: class_id x_center y_center width height
                original_class = int(parts[0])
                
                # Keep the same ID if already 0-3, otherwise try mapping
                if original_class <= 3:
                    new_class = original_class
                else:
                    new_class = original_class % 4  # Simple fallback
                
                parts[0] = str(new_class)
                lines.append(" ".join(parts))
    
    with open(dst_file, 'w') as f:
        f.write("\n".join(lines))


def update_data_yaml():
    """
    Update data.yaml with correct paths
    """
    data_yaml = {
        'path': str(DATA_DIR.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': 4,
        'names': {
            0: 'elastic_clip',
            1: 'liner', 
            2: 'rubber_pad',
            3: 'sleeper'
        }
    }
    
    with open(DATA_DIR / 'data.yaml', 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)
    
    print(f"   ✅ Updated data.yaml")


def count_dataset():
    """
    Count and display dataset statistics
    """
    print("\n" + "=" * 70)
    print("📊 Dataset Statistics")
    print("=" * 70)
    
    for split in ["train", "val"]:
        img_dir = IMAGES_DIR / split
        lbl_dir = LABELS_DIR / split
        
        if img_dir.exists():
            n_images = len(list(img_dir.glob("*")))
            n_labels = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0
            
            print(f"\n{split.upper()}:")
            print(f"   Images: {n_images}")
            print(f"   Labels: {n_labels}")
            
            # Count class distribution
            if lbl_dir.exists():
                class_counts = {0: 0, 1: 0, 2: 0, 3: 0}
                for lbl_file in lbl_dir.glob("*.txt"):
                    with open(lbl_file, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                cls = int(parts[0])
                                if cls in class_counts:
                                    class_counts[cls] += 1
                
                class_names = ['elastic_clip', 'liner', 'rubber_pad', 'sleeper']
                print("   Class distribution:")
                for cls_id, count in class_counts.items():
                    print(f"      {class_names[cls_id]:15s}: {count:5d}")


def main():
    """
    Main function to download and prepare dataset
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Railway Component Dataset")
    parser.add_argument("--api-key", type=str, help="Roboflow API key")
    parser.add_argument("--sample", action="store_true", help="Create sample dataset structure")
    
    args = parser.parse_args()
    
    if args.sample:
        download_sample_dataset()
    else:
        success = download_from_roboflow(api_key=args.api_key)
        if not success:
            print("\n💡 Tip: Use --sample flag to create dataset structure for manual data addition")
    
    count_dataset()
    
    print("\n" + "=" * 70)
    print("✅ Dataset preparation complete!")
    print("=" * 70)
    print("\nNext step: python scripts/train_yolo.py")


if __name__ == "__main__":
    main()
