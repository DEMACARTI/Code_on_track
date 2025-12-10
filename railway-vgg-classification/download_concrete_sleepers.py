"""
Download and integrate Kaggle Concrete Sleepers dataset
Dataset: https://www.kaggle.com/datasets/wachyuutami/concrete-sleepers
Classes: Fair, Good, Poor
"""

import os
import subprocess
from pathlib import Path
import shutil
from PIL import Image
from tqdm import tqdm

# Configuration
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
RAW_DATASET_DIR = BASE_DIR / 'raw_datasets' / 'concrete_sleepers'
FINAL_DATASET_DIR = BASE_DIR / 'railway_defect_dataset'

# Class mapping from concrete sleepers dataset to our classification
CLASS_MAPPING = {
    'good': 'Normal',      # Good condition → Normal
    'fair': 'Crack',       # Fair condition (minor issues) → Crack
    'poor': 'Damaged'      # Poor condition → Damaged
}

def check_kaggle_credentials():
    """Check if Kaggle credentials are configured"""
    kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
    
    if not kaggle_json.exists():
        print("\n⚠️  Kaggle credentials not found!")
        print("\n📝 To download datasets from Kaggle:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Click 'Create New API Token'")
        print("3. Save kaggle.json to ~/.kaggle/")
        print("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    # Check permissions
    kaggle_json.chmod(0o600)
    return True

def download_dataset():
    """Download concrete sleepers dataset from Kaggle"""
    print("\n" + "=" * 80)
    print("📦 Downloading Concrete Sleepers Dataset")
    print("=" * 80)
    
    RAW_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = f"kaggle datasets download -d wachyuutami/concrete-sleepers -p {RAW_DATASET_DIR} --unzip"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dataset downloaded successfully!")
            return True
        else:
            print(f"❌ Download failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def is_valid_image(image_path):
    """Check if file is a valid image"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except:
        return False

def copy_images_to_dataset(source_dir, target_class, split='train'):
    """Copy images from source to target dataset directory"""
    target_dir = FINAL_DATASET_DIR / split / target_class
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_files.extend(list(source_dir.glob(ext)))
        image_files.extend(list(source_dir.rglob(ext)))
    
    # Remove duplicates
    image_files = list(set(image_files))
    
    if not image_files:
        return 0
    
    # Copy images with progress bar
    copied = 0
    for img_path in tqdm(image_files, desc=f"Copying to {target_class}/{split}"):
        if is_valid_image(img_path):
            # Generate unique filename
            new_name = f"concrete_sleepers_{copied:04d}{img_path.suffix}"
            target_path = target_dir / new_name
            
            try:
                shutil.copy2(img_path, target_path)
                copied += 1
            except Exception as e:
                print(f"⚠️  Failed to copy {img_path.name}: {e}")
    
    return copied

def organize_dataset():
    """Organize concrete sleepers dataset into our classification structure"""
    print("\n" + "=" * 80)
    print("🔄 Organizing Dataset")
    print("=" * 80)
    
    total_copied = 0
    stats = {}
    
    # Find the actual dataset directory
    possible_roots = [
        RAW_DATASET_DIR / 'concrete railway sleepers',
        RAW_DATASET_DIR / 'concrete-sleepers',
        RAW_DATASET_DIR / 'concrete_sleepers',
        RAW_DATASET_DIR
    ]
    
    dataset_root = None
    for root in possible_roots:
        if root.exists():
            train_dir = root / 'data train'
            test_dir = root / 'data test'
            if train_dir.exists() or test_dir.exists():
                dataset_root = root
                break
    
    if not dataset_root:
        print("❌ Could not find dataset directory!")
        print(f"Searched in: {RAW_DATASET_DIR}")
        return False
    
    print(f"📁 Dataset root: {dataset_root}")
    
    # Process train and test splits
    for split_name, split_subdir in [('train', 'data train'), ('test', 'data test')]:
        split_dir = dataset_root / split_subdir
        
        if not split_dir.exists():
            print(f"⚠️  {split_name} directory not found: {split_dir}")
            continue
        
        print(f"\n📁 Processing {split_name.upper()} split from: {split_subdir}")
        
        # Process each class within this split
        for source_class, target_class in CLASS_MAPPING.items():
            print(f"  📂 {source_class} → {target_class}")
            
            # Find source class directory (case-insensitive)
            source_dir = None
            for subdir in split_dir.iterdir():
                if subdir.is_dir() and source_class.lower() in subdir.name.lower():
                    source_dir = subdir
                    break
            
            if not source_dir or not source_dir.exists():
                print(f"    ⚠️  Directory not found: {source_class}")
                continue
            
            # Get all images
            all_images = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                all_images.extend(list(source_dir.glob(ext)))
            
            all_images = list(set(all_images))  # Remove duplicates
            
            if not all_images:
                print(f"    ⚠️  No images found in {source_dir}")
                continue
            
            # Determine target split (train stays train, test becomes validation)
            target_split = 'train' if split_name == 'train' else 'validation'
            target_dir = FINAL_DATASET_DIR / target_split / target_class
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy images
            copied = 0
            for img_path in tqdm(all_images, desc=f"    {target_split.capitalize()} {target_class}"):
                if is_valid_image(img_path):
                    new_name = f"concrete_{source_class}_{split_name}_{copied:04d}{img_path.suffix}"
                    target_path = target_dir / new_name
                    try:
                        shutil.copy2(img_path, target_path)
                        copied += 1
                    except:
                        pass
            
            # Update statistics
            if target_class not in stats:
                stats[target_class] = {'train': 0, 'val': 0, 'total': 0}
            
            if target_split == 'train':
                stats[target_class]['train'] += copied
            else:
                stats[target_class]['val'] += copied
            stats[target_class]['total'] += copied
            total_copied += copied
            
            print(f"    ✅ Copied {copied} images to {target_split}/{target_class}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Dataset Integration Summary")
    print("=" * 80)
    
    for class_name in sorted(stats.keys()):
        s = stats[class_name]
        print(f"{class_name:12s}: {s['train']:4d} train + {s['val']:4d} val = {s['total']:4d} total")
    
    print(f"\n{'TOTAL':12s}: {sum(s['train'] for s in stats.values()):4d} train + {sum(s['val'] for s in stats.values()):4d} val = {total_copied:4d} total")
    
    # Show updated dataset statistics
    print("\n" + "=" * 80)
    print("📈 Complete Dataset Statistics")
    print("=" * 80)
    
    for split in ['train', 'validation']:
        print(f"\n{split.upper()}:")
        split_dir = FINAL_DATASET_DIR / split
        if split_dir.exists():
            for class_dir in sorted(split_dir.iterdir()):
                if class_dir.is_dir():
                    count = len([f for f in class_dir.glob('*') if f.is_file()])
                    print(f"  {class_dir.name:12s}: {count:4d} images")
    
    return True

def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("🚂 Concrete Sleepers Dataset Integration")
    print("=" * 80)
    
    # Check Kaggle credentials
    if not check_kaggle_credentials():
        return
    
    # Download dataset
    if not download_dataset():
        print("\n❌ Failed to download dataset")
        return
    
    # Organize dataset
    if organize_dataset():
        print("\n" + "=" * 80)
        print("✅ Dataset integration complete!")
        print("=" * 80)
        print("\n📝 Next steps:")
        print("1. Review the integrated dataset")
        print("2. Run: python train_vgg_classification.py")
        print("3. Monitor training progress")
        print("4. Deploy updated model")
    else:
        print("\n❌ Failed to organize dataset")

if __name__ == '__main__':
    main()
