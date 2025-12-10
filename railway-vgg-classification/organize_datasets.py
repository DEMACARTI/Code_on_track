"""
Organize already-downloaded Roboflow datasets for VGG training
"""

import os
from pathlib import Path
import shutil
from PIL import Image
import yaml

# Configuration
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
RAW_DATASET_DIR = BASE_DIR / 'raw_datasets' / 'roboflow'
FINAL_DATASET_DIR = BASE_DIR / 'railway_defect_dataset'

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
    'ok': 'Normal',
    'track': 'Normal',  # Assume unlabeled tracks are normal
}

def map_class_name(label):
    """Map various class names to our 5 defect categories"""
    label_lower = label.lower().strip()
    
    for key, value in CLASS_MAPPING.items():
        if key in label_lower:
            return value
    
    # Default mapping based on keywords
    if any(word in label_lower for word in ['normal', 'good', 'clean', 'ok', 'track']):
        return 'Normal'
    elif any(word in label_lower for word in ['rust', 'corrosion', 'oxidation']):
        return 'Rust'
    elif any(word in label_lower for word in ['crack', 'fracture', 'split']):
        return 'Crack'
    elif any(word in label_lower for word in ['broken', 'severe', 'major']):
        return 'Broken'
    else:
        return 'Damaged'  # Default for unclear defects

def organize_dataset(dataset_path):
    """Organize one dataset"""
    if not dataset_path.exists():
        return 0
    
    print(f"\n🗂️  Organizing: {dataset_path.name}")
    
    # Read data.yaml to get class names
    yaml_path = dataset_path / 'data.yaml'
    class_names = []
    
    if yaml_path.exists():
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                class_names = data.get('names', [])
                print(f"   Found {len(class_names)} classes: {class_names}")
        except Exception as e:
            print(f"   ⚠️  Error reading data.yaml: {e}")
    
    image_count = 0
    
    # Process each split
    for split in ['train', 'valid', 'test']:
        split_path = dataset_path / split
        if not split_path.exists():
            continue
        
        # Check for images subdirectory
        images_dir = split_path / 'images'
        labels_dir = split_path / 'labels'
        
        if images_dir.exists():
            images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
        else:
            images = list(split_path.glob('*.jpg')) + list(split_path.glob('*.png'))
            labels_dir = split_path
        
        print(f"   {split}: {len(images)} images")
        
        for img_path in images:
            # Find label file
            if images_dir.exists():
                label_path = labels_dir / (img_path.stem + '.txt')
            else:
                label_path = img_path.with_suffix('.txt')
            
            # Determine target class
            if label_path.exists():
                try:
                    with open(label_path, 'r') as f:
                        lines = f.readlines()
                    
                    if lines:
                        class_id = int(lines[0].split()[0])
                        if class_id < len(class_names):
                            class_name = class_names[class_id]
                            target_class = map_class_name(class_name)
                        else:
                            target_class = 'Damaged'
                    else:
                        target_class = 'Normal'
                except:
                    target_class = 'Normal'
            else:
                # No label = normal/good track
                target_class = 'Normal'
            
            # Map split names
            if split == 'valid':
                target_split = 'validation'
            else:
                target_split = split
            
            # Create target directory
            target_dir = FINAL_DATASET_DIR / target_split / target_class
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy image with unique name
            new_filename = f"{dataset_path.name}_{split}_{img_path.name}"
            target_path = target_dir / new_filename
            
            try:
                shutil.copy2(img_path, target_path)
                image_count += 1
            except Exception as e:
                print(f"   ⚠️  Error copying {img_path.name}: {e}")
        
    print(f"   ✅ Organized {image_count} images")
    return image_count

def cleanup_old_data():
    """Remove old synthetic images"""
    print("\n🧹 Cleaning up old synthetic data...")
    
    removed = 0
    for split in ['train', 'validation', 'test']:
        split_path = FINAL_DATASET_DIR / split
        if not split_path.exists():
            continue
        
        for class_dir in split_path.iterdir():
            if class_dir.is_dir():
                for img in class_dir.glob('generated_*.png'):
                    img.unlink()
                    removed += 1
    
    print(f"   ✅ Removed {removed} synthetic images")

def show_statistics():
    """Show dataset statistics"""
    print("\n📊 DATASET STATISTICS")
    print("=" * 60)
    
    class_totals = {}
    
    for split in ['train', 'validation', 'test']:
        split_path = FINAL_DATASET_DIR / split
        if not split_path.exists():
            continue
        
        print(f"\n{split.upper()}:")
        for class_name in ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']:
            class_path = split_path / class_name
            if class_path.exists():
                count = len(list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')))
                print(f"  {class_name:10s}: {count:4d} images")
                class_totals[class_name] = class_totals.get(class_name, 0) + count
    
    print(f"\nTOTAL ACROSS ALL SPLITS:")
    for class_name, count in sorted(class_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {class_name:10s}: {count:4d} images")
    
    total = sum(class_totals.values())
    print(f"\n🎯 Grand Total: {total} images")

def main():
    print("=" * 60)
    print("🗂️  ORGANIZING ROBOFLOW DATASETS FOR VGG TRAINING")
    print("=" * 60)
    
    # Cleanup old data
    cleanup_old_data()
    
    # Organize all downloaded datasets
    total_images = 0
    datasets = list(RAW_DATASET_DIR.glob('*'))
    
    print(f"\nFound {len(datasets)} downloaded datasets")
    
    for dataset_path in datasets:
        if dataset_path.is_dir():
            count = organize_dataset(dataset_path)
            total_images += count
    
    print(f"\n✅ Total images organized: {total_images}")
    
    # Show statistics
    show_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Organization complete!")
    print("\n🎯 Next: Train the VGG model:")
    print("   python train_vgg_classification.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
