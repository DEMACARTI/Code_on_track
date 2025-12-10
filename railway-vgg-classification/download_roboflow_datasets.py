"""
Roboflow Dataset Downloader for Railway Defect Classification
Downloads and organizes datasets from Roboflow for VGG training
"""

import os
import subprocess
from pathlib import Path
import shutil
from PIL import Image
from tqdm import tqdm
import random
import json

# Configuration
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
RAW_DATASET_DIR = BASE_DIR / 'raw_datasets' / 'roboflow'
FINAL_DATASET_DIR = BASE_DIR / 'railway_defect_dataset'

# Roboflow datasets to download
ROBOFLOW_DATASETS = [
    {
        'url': 'https://universe.roboflow.com/own-zsacw/images-xbssq',
        'workspace': 'own-zsacw',
        'project': 'images-xbssq',
        'version': 1,
        'description': 'Railway images'
    },
    {
        'url': 'https://universe.roboflow.com/own-zsacw/yolov5_v1-5ca16',
        'workspace': 'own-zsacw',
        'project': 'yolov5_v1-5ca16',
        'version': 1,
        'description': 'YOLOv5 railway dataset'
    },
    {
        'url': 'https://universe.roboflow.com/track-detection-0kr1b/track-fault-detection-badcq',
        'workspace': 'track-detection-0kr1b',
        'project': 'track-fault-detection-badcq',
        'version': 1,
        'description': 'Track fault detection'
    },
    {
        'url': 'https://universe.roboflow.com/own-zsacw/yolov5-rjbgn',
        'workspace': 'own-zsacw',
        'project': 'yolov5-rjbgn',
        'version': 1,
        'description': 'YOLOv5 railway defects'
    },
    {
        'url': 'https://universe.roboflow.com/xyz-rf6um/rail-track-5njgn',
        'workspace': 'xyz-rf6um',
        'project': 'rail-track-5njgn',
        'version': 1,
        'description': 'Rail track dataset'
    },
    {
        'url': 'https://universe.roboflow.com/w-t-a/rail_track_test',
        'workspace': 'w-t-a',
        'project': 'rail_track_test',
        'version': 1,
        'description': 'Rail track test'
    },
    {
        'url': 'https://universe.roboflow.com/xyz-rf6um/railway-bnznt',
        'workspace': 'xyz-rf6um',
        'project': 'railway-bnznt',
        'version': 1,
        'description': 'Railway dataset'
    }
]

# Class mapping for defect classification
CLASS_MAPPING = {
    'rust': 'Rust',
    'corrosion': 'Rust',
    'crack': 'Crack',
    'cracked': 'Crack',
    'fracture': 'Crack',
    'broken': 'Broken',
    'damaged': 'Damaged',
    'defect': 'Damaged',
    'fault': 'Damaged',
    'normal': 'Normal',
    'good': 'Normal',
    'ok': 'Normal'
}

def check_roboflow_api():
    """Check if Roboflow API key is configured"""
    try:
        from roboflow import Roboflow
        api_key = os.getenv('ROBOFLOW_API_KEY')
        
        if not api_key:
            print("\n⚠️  Roboflow API key not found!")
            print("\n📝 To download datasets from Roboflow:")
            print("1. Go to https://app.roboflow.com/settings/api")
            print("2. Copy your API key")
            print("3. Set it as environment variable:")
            print("   export ROBOFLOW_API_KEY='your_api_key_here'")
            print("4. Or add to your ~/.zshrc or ~/.bash_profile\n")
            return False
        
        return True
    except ImportError:
        print("\n⚠️  Roboflow Python package not installed!")
        print("Install it with: pip install roboflow\n")
        return False

def install_roboflow():
    """Install roboflow package"""
    print("📦 Installing roboflow package...")
    try:
        subprocess.run(['pip', 'install', 'roboflow'], check=True)
        print("✅ Roboflow installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install roboflow")
        return False

def download_roboflow_dataset(dataset_info, api_key):
    """Download a single dataset from Roboflow"""
    from roboflow import Roboflow
    
    workspace = dataset_info['workspace']
    project = dataset_info['project']
    version = dataset_info['version']
    
    print(f"\n📥 Downloading: {dataset_info['description']}")
    print(f"   Project: {workspace}/{project}")
    
    try:
        rf = Roboflow(api_key=api_key)
        project_obj = rf.workspace(workspace).project(project)
        
        # Try YOLOv8 format first (most common for object detection)
        try:
            dataset = project_obj.version(version).download("yolov8", 
                                                             location=str(RAW_DATASET_DIR / project))
        except:
            # Fallback to YOLOv5 format
            try:
                dataset = project_obj.version(version).download("yolov5pytorch", 
                                                                 location=str(RAW_DATASET_DIR / project))
            except:
                # Try COCO format
                dataset = project_obj.version(version).download("coco", 
                                                                 location=str(RAW_DATASET_DIR / project))
        
        print(f"✅ Downloaded to: {RAW_DATASET_DIR / project}")
        return RAW_DATASET_DIR / project
    except Exception as e:
        print(f"❌ Error downloading {project}: {str(e)}")
        return None

def map_class_name(label):
    """Map various class names to our 5 defect categories"""
    label_lower = label.lower().strip()
    
    for key, value in CLASS_MAPPING.items():
        if key in label_lower:
            return value
    
    # Default mapping based on keywords
    if any(word in label_lower for word in ['normal', 'good', 'clean', 'ok']):
        return 'Normal'
    elif any(word in label_lower for word in ['rust', 'corrosion', 'oxidation']):
        return 'Rust'
    elif any(word in label_lower for word in ['crack', 'fracture', 'split']):
        return 'Crack'
    elif any(word in label_lower for word in ['broken', 'severe', 'major']):
        return 'Broken'
    else:
        return 'Damaged'  # Default for unclear defects

def organize_downloaded_dataset(dataset_path):
    """Organize downloaded Roboflow dataset into classification structure"""
    if not dataset_path or not dataset_path.exists():
        return 0
    
    print(f"\n🗂️  Organizing dataset: {dataset_path.name}")
    
    image_count = 0
    
    # Look for train/valid/test folders
    for split in ['train', 'valid', 'test']:
        split_path = dataset_path / split
        if not split_path.exists():
            continue
        
        print(f"   Processing {split} split...")
        
        # Check if images are in a subdirectory (common Roboflow structure)
        images_dir = split_path / 'images'
        labels_dir = split_path / 'labels'
        
        if images_dir.exists():
            # Images are in subdirectory
            images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
        else:
            # Images are directly in split folder
            images = list(split_path.glob('*.jpg')) + list(split_path.glob('*.png'))
            labels_dir = split_path
        
        for img_path in images:
            # Try to find corresponding label file
            if images_dir.exists():
                # Labels are in separate labels directory
                label_path = labels_dir / (img_path.stem + '.txt')
            else:
                # Labels are in same directory as images
                label_path = img_path.with_suffix('.txt')
            
            if label_path.exists():
                # Read YOLO format label
                with open(label_path, 'r') as f:
                    lines = f.readlines()
                
                if lines:
                    # Get class ID from first line
                    class_id = int(lines[0].split()[0])
                    
                    # Read class names from data.yaml if exists
                    yaml_path = dataset_path / 'data.yaml'
                    if yaml_path.exists():
                        import yaml
                        with open(yaml_path, 'r') as f:
                            data = yaml.safe_load(f)
                            class_names = data.get('names', [])
                            if class_id < len(class_names):
                                class_name = class_names[class_id]
                                target_class = map_class_name(class_name)
                            else:
                                target_class = 'Damaged'
                    else:
                        target_class = 'Damaged'
                else:
                    target_class = 'Normal'
            else:
                # No label means it's likely a normal/good image
                target_class = 'Normal'
            
            # Determine target split (map valid to validation)
            if split == 'valid':
                target_split = 'validation'
            elif split == 'test':
                target_split = 'test'
            else:
                target_split = 'train'
            
            # Copy to final dataset structure
            target_dir = FINAL_DATASET_DIR / target_split / target_class
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create unique filename
            new_filename = f"{dataset_path.name}_{split}_{img_path.stem}{img_path.suffix}"
            target_path = target_dir / new_filename
            
            try:
                shutil.copy2(img_path, target_path)
                image_count += 1
            except Exception as e:
                print(f"   ⚠️  Error copying {img_path.name}: {e}")
    
    print(f"   ✅ Organized {image_count} images")
    return image_count

def balance_dataset():
    """Balance the dataset by ensuring each class has similar number of images"""
    print("\n⚖️  Balancing dataset across classes...")
    
    class_counts = {}
    
    for split in ['train', 'validation', 'test']:
        split_path = FINAL_DATASET_DIR / split
        if not split_path.exists():
            continue
        
        print(f"\n{split.upper()} split:")
        for class_name in ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']:
            class_path = split_path / class_name
            if class_path.exists():
                count = len(list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')))
                class_counts[class_name] = class_counts.get(class_name, 0) + count
                print(f"   {class_name}: {count} images")
    
    print("\n📊 Total class distribution:")
    for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {class_name}: {count} images")
    
    return class_counts

def cleanup_old_synthetic_data():
    """Remove old synthetic placeholder images"""
    print("\n🧹 Cleaning up old synthetic data...")
    
    removed_count = 0
    for split in ['train', 'validation', 'test']:
        split_path = FINAL_DATASET_DIR / split
        if not split_path.exists():
            continue
        
        for class_name in ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']:
            class_path = split_path / class_name
            if not class_path.exists():
                continue
            
            # Remove synthetic images (generated_*.png)
            for img in class_path.glob('generated_*.png'):
                img.unlink()
                removed_count += 1
    
    print(f"   ✅ Removed {removed_count} synthetic images")

def main():
    """Main function to download and organize all datasets"""
    print("=" * 60)
    print("🚂 ROBOFLOW DATASET DOWNLOADER FOR RAILWAY DEFECT CLASSIFICATION")
    print("=" * 60)
    
    # Create directories
    RAW_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check and install roboflow
    try:
        from roboflow import Roboflow
    except ImportError:
        if not install_roboflow():
            return
        from roboflow import Roboflow
    
    # Check API key
    api_key = os.getenv('ROBOFLOW_API_KEY')
    if not api_key:
        if not check_roboflow_api():
            print("\n💡 Tip: You can get a free API key at https://app.roboflow.com")
            print("Then run: export ROBOFLOW_API_KEY='your_key_here'\n")
            return
    
    print(f"\n✅ Roboflow API key found")
    print(f"📁 Raw datasets will be saved to: {RAW_DATASET_DIR}")
    print(f"📁 Organized dataset will be in: {FINAL_DATASET_DIR}")
    
    # Cleanup old synthetic data
    cleanup_old_synthetic_data()
    
    # Download all datasets
    total_images = 0
    successful_downloads = 0
    
    for dataset_info in ROBOFLOW_DATASETS:
        dataset_path = download_roboflow_dataset(dataset_info, api_key)
        
        if dataset_path:
            count = organize_downloaded_dataset(dataset_path)
            total_images += count
            successful_downloads += 1
    
    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully downloaded: {successful_downloads}/{len(ROBOFLOW_DATASETS)} datasets")
    print(f"📸 Total images organized: {total_images}")
    
    # Show final distribution
    balance_dataset()
    
    print("\n✅ Dataset preparation complete!")
    print(f"\n🎯 Next step: Train the VGG model with:")
    print(f"   python train_vgg_classification.py")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
