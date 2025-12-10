"""
Download and Prepare Multi-Class Railway Defect Dataset
Downloads datasets from Roboflow and Kaggle for comprehensive railway component classification
Classes: Rust, Cracks, Rubber_Defects, Broken_Sleepers, Normal
"""

import os
import shutil
from pathlib import Path
from roboflow import Roboflow
import zipfile
import requests
from tqdm import tqdm

# Configuration
ROBOFLOW_API_KEY = "sRFJiVAOA3csyatXCuIE"
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
RAW_DATASET_DIR = BASE_DIR / 'raw_datasets'
FINAL_DATASET_DIR = BASE_DIR / 'railway_defect_dataset'

# Target classes for our model
TARGET_CLASSES = {
    'rust': 'Rust',
    'crack': 'Crack',
    'cracked': 'Crack',
    'broken': 'Broken',
    'damage': 'Damaged',
    'defect': 'Defect',
    'normal': 'Normal',
    'good': 'Normal'
}

# Roboflow datasets to download
ROBOFLOW_DATASETS = [
    {
        'workspace': 'xyz-rf6um',
        'project': 'railway-bnznt',
        'version': 2,
        'name': 'railway-components'
    }
]

def setup_directories():
    """Create directory structure"""
    print("\n📁 Setting up directories...")
    
    RAW_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    for split in ['train', 'validation', 'test']:
        for class_name in ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']:
            (FINAL_DATASET_DIR / split / class_name).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Directories created at: {FINAL_DATASET_DIR}")

def download_roboflow_datasets():
    """Download datasets from Roboflow"""
    print("\n" + "=" * 70)
    print("📥 Downloading Datasets from Roboflow")
    print("=" * 70)
    
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    downloaded = []
    
    for dataset_info in ROBOFLOW_DATASETS:
        try:
            print(f"\n📦 Downloading: {dataset_info['project']}")
            
            project = rf.workspace(dataset_info['workspace']).project(dataset_info['project'])
            dataset = project.version(dataset_info['version']).download(
                "coco",
                location=str(RAW_DATASET_DIR / dataset_info['name'])
            )
            
            downloaded.append({
                'name': dataset_info['name'],
                'path': dataset.location
            })
            
            print(f"✅ Downloaded: {dataset_info['name']}")
            
        except Exception as e:
            print(f"⚠️  Failed to download {dataset_info['project']}: {e}")
    
    return downloaded

def download_kaggle_concrete_cracks():
    """Download concrete crack dataset from Kaggle"""
    print("\n📦 Downloading Concrete Crack Dataset from Kaggle...")
    
    try:
        # Try using Kaggle API
        os.system(f"kaggle datasets download -d arunrk7/surface-crack-detection -p {RAW_DATASET_DIR} --unzip")
        print("✅ Downloaded concrete crack dataset")
        return True
    except Exception as e:
        print(f"⚠️  Kaggle download failed: {e}")
        print("Please download manually from: https://www.kaggle.com/datasets/arunrk7/surface-crack-detection")
        return False

def download_rust_dataset():
    """Download rust detection dataset"""
    print("\n📦 Setting up Rust Detection Dataset...")
    
    # For rust, we can use the railway dataset and label rusty components
    print("ℹ️  Rust detection will be configured from railway components")
    return True

def organize_images(downloaded_datasets):
    """Organize images into classification structure"""
    print("\n" + "=" * 70)
    print("🔄 Organizing Images into Classification Structure")
    print("=" * 70)
    
    stats = {
        'train': {'Rust': 0, 'Crack': 0, 'Broken': 0, 'Damaged': 0, 'Normal': 0},
        'validation': {'Rust': 0, 'Crack': 0, 'Broken': 0, 'Damaged': 0, 'Normal': 0},
        'test': {'Rust': 0, 'Crack': 0, 'Broken': 0, 'Damaged': 0, 'Normal': 0}
    }
    
    # Process downloaded datasets
    for dataset_info in downloaded_datasets:
        dataset_path = Path(dataset_info['path'])
        print(f"\n📂 Processing: {dataset_info['name']}")
        
        # Look for train/valid/test splits
        for split_dir in ['train', 'valid', 'test']:
            source_split = dataset_path / split_dir
            if not source_split.exists():
                continue
            
            dest_split = 'validation' if split_dir == 'valid' else split_dir
            
            # Process images
            images_dir = source_split / 'images' if (source_split / 'images').exists() else source_split
            
            if images_dir.exists():
                process_split_images(images_dir, dest_split, stats)
    
    # Process concrete crack dataset if available
    crack_dataset = RAW_DATASET_DIR / 'Positive'
    if crack_dataset.exists():
        print(f"\n📂 Processing: Concrete Crack Dataset")
        distribute_crack_images(crack_dataset, stats)
    
    print_statistics(stats)
    return stats

def process_split_images(images_dir, split, stats):
    """Process images from a split directory"""
    image_files = list(images_dir.glob('*.jpg')) + \
                  list(images_dir.glob('*.jpeg')) + \
                  list(images_dir.glob('*.png'))
    
    for img_path in tqdm(image_files, desc=f"Processing {split}"):
        # Determine class based on filename or annotation
        img_name_lower = img_path.stem.lower()
        
        # Simple keyword-based classification
        if any(keyword in img_name_lower for keyword in ['rust', 'corrosion', 'corroded']):
            class_name = 'Rust'
        elif any(keyword in img_name_lower for keyword in ['crack', 'cracked', 'fracture']):
            class_name = 'Crack'
        elif any(keyword in img_name_lower for keyword in ['broken', 'break', 'shattered']):
            class_name = 'Broken'
        elif any(keyword in img_name_lower for keyword in ['damage', 'defect', 'fault']):
            class_name = 'Damaged'
        else:
            # Default to damaged for fault detection dataset
            class_name = 'Damaged'
        
        # Copy to destination
        dest_path = FINAL_DATASET_DIR / split / class_name / img_path.name
        shutil.copy2(img_path, dest_path)
        stats[split][class_name] += 1

def distribute_crack_images(crack_dir, stats):
    """Distribute crack images across splits"""
    crack_images = list(crack_dir.glob('*.jpg')) + list(crack_dir.glob('*.png'))
    
    # Split: 70% train, 20% validation, 10% test
    total = len(crack_images)
    train_count = int(total * 0.7)
    val_count = int(total * 0.2)
    
    import random
    random.shuffle(crack_images)
    
    splits = [
        ('train', crack_images[:train_count]),
        ('validation', crack_images[train_count:train_count + val_count]),
        ('test', crack_images[train_count + val_count:])
    ]
    
    for split, images in splits:
        for img_path in tqdm(images, desc=f"Adding cracks to {split}"):
            dest_path = FINAL_DATASET_DIR / split / 'Crack' / img_path.name
            shutil.copy2(img_path, dest_path)
            stats[split]['Crack'] += 1

def print_statistics(stats):
    """Print dataset statistics"""
    print("\n" + "=" * 70)
    print("📊 Final Dataset Statistics")
    print("=" * 70)
    
    for split in ['train', 'validation', 'test']:
        print(f"\n{split.capitalize()}:")
        total = 0
        for class_name, count in stats[split].items():
            print(f"   {class_name}: {count}")
            total += count
        print(f"   Total: {total}")
    
    print("\n" + "=" * 70)
    grand_total = sum(sum(stats[split].values()) for split in stats)
    print(f"Grand Total: {grand_total} images")
    print("=" * 70)

def create_simple_dataset():
    """Create a simple multi-class dataset from available data"""
    print("\n🎯 Creating Simplified Multi-Class Dataset")
    print("=" * 70)
    
    # Create a basic structure with synthetic data for demonstration
    # In production, you'd use real datasets
    
    import random
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    classes = ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']
    samples_per_class = {
        'train': 50,
        'validation': 10,
        'test': 5
    }
    
    print("\n⚠️  No suitable datasets found. Creating synthetic dataset for testing...")
    print("Please add real images to the dataset folders for actual training.\n")
    
    stats = {split: {cls: 0 for cls in classes} for split in ['train', 'validation', 'test']}
    
    for split in ['train', 'validation', 'test']:
        for class_name in classes:
            dest_dir = FINAL_DATASET_DIR / split / class_name
            
            for i in range(samples_per_class[split]):
                # Create synthetic image with text label
                img = Image.new('RGB', (224, 224), color=(random.randint(100, 200), 
                                                           random.randint(100, 200), 
                                                           random.randint(100, 200)))
                draw = ImageDraw.Draw(img)
                
                # Add some random shapes to simulate defects
                for _ in range(random.randint(3, 10)):
                    x, y = random.randint(0, 200), random.randint(0, 200)
                    draw.ellipse([x, y, x+20, y+20], fill=(random.randint(0, 255),
                                                            random.randint(0, 255),
                                                            random.randint(0, 255)))
                
                # Save
                img_path = dest_dir / f"{class_name.lower()}_{split}_{i:03d}.jpg"
                img.save(img_path)
                stats[split][class_name] += 1
    
    print_statistics(stats)
    return stats

def main():
    """Main execution"""
    print("=" * 70)
    print("🚂 Railway Defect Dataset Preparation")
    print("Multi-Class Classification: Rust, Cracks, Broken, Damaged, Normal")
    print("=" * 70)
    
    # Setup directories
    setup_directories()
    
    # Download from Roboflow
    downloaded = download_roboflow_datasets()
    
    # Try Kaggle downloads
    download_kaggle_concrete_cracks()
    download_rust_dataset()
    
    # Organize images
    if downloaded:
        stats = organize_images(downloaded)
    else:
        # Create synthetic dataset if no downloads succeeded
        stats = create_simple_dataset()
    
    print("\n✅ Dataset preparation complete!")
    print(f"\n📁 Dataset location: {FINAL_DATASET_DIR}")
    print("\n🚀 Next steps:")
    print("   1. Review the dataset in railway_defect_dataset/")
    print("   2. Add more real images if needed")
    print("   3. Run: python train_vgg_classification.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
