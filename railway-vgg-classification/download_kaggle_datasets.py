"""
Enhanced Dataset Downloader for Railway Defect Classification
Searches and downloads relevant datasets from multiple sources
"""

import os
import subprocess
from pathlib import Path
import shutil
from PIL import Image
from tqdm import tqdm
import random

# Configuration
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
RAW_DATASET_DIR = BASE_DIR / 'raw_datasets'
FINAL_DATASET_DIR = BASE_DIR / 'railway_defect_dataset'

# Kaggle datasets to download
KAGGLE_DATASETS = [
    {
        'name': 'arunrk7/surface-crack-detection',
        'description': 'Concrete surface cracks',
        'target_class': 'Crack'
    },
    {
        'name': 'kaustubhdikshit/railway-track-fault-detection',
        'description': 'Railway track faults',
        'target_class': 'Damaged'
    },
    {
        'name': 'fantacher/neu-metal-surface-defects-data',
        'description': 'Metal surface defects including rust',
        'target_class': 'Rust'
    },
    {
        'name': 'ukveteran/surface-defects-in-steel',
        'description': 'Steel defects: crazing, scratches, pitted',
        'target_class': 'Damaged'
    }
]

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
    
    return True

def download_kaggle_dataset(dataset_name, output_dir):
    """Download a dataset from Kaggle"""
    try:
        print(f"\n📦 Downloading: {dataset_name}")
        
        cmd = f"kaggle datasets download -d {dataset_name} -p {output_dir} --unzip"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Downloaded: {dataset_name}")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading {dataset_name}: {e}")
        return False

def organize_crack_dataset(source_dir, target_class='Crack'):
    """Organize crack detection dataset"""
    print(f"\n🔄 Organizing crack dataset...")
    
    stats = {'train': 0, 'validation': 0, 'test': 0}
    
    # Look for Positive (crack) images
    positive_dir = source_dir / 'Positive'
    if not positive_dir.exists():
        # Try alternative structures
        for subdir in source_dir.rglob('*'):
            if 'positive' in subdir.name.lower() or 'crack' in subdir.name.lower():
                positive_dir = subdir
                break
    
    if positive_dir and positive_dir.exists():
        images = list(positive_dir.glob('*.jpg')) + \
                 list(positive_dir.glob('*.jpeg')) + \
                 list(positive_dir.glob('*.png'))
        
        if images:
            random.shuffle(images)
            total = len(images)
            
            train_split = int(total * 0.7)
            val_split = int(total * 0.2)
            
            splits = {
                'train': images[:train_split],
                'validation': images[train_split:train_split + val_split],
                'test': images[train_split + val_split:]
            }
            
            for split, imgs in splits.items():
                dest_dir = FINAL_DATASET_DIR / split / target_class
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                for img_path in tqdm(imgs, desc=f"Processing {split}"):
                    try:
                        # Verify image is valid
                        Image.open(img_path).verify()
                        shutil.copy2(img_path, dest_dir / img_path.name)
                        stats[split] += 1
                    except:
                        continue
            
            print(f"✅ Added {sum(stats.values())} crack images")
            return stats
    
    print("⚠️  No crack images found")
    return stats

def organize_rust_dataset(source_dir, target_class='Rust'):
    """Organize rust/corrosion dataset"""
    print(f"\n🔄 Organizing rust dataset...")
    
    stats = {'train': 0, 'validation': 0, 'test': 0}
    
    # Search for rust-related images
    rust_keywords = ['rust', 'corrosion', 'corroded', 'oxidation', 'rs', 'pa']
    
    all_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        all_images.extend(source_dir.rglob(ext))
    
    rust_images = []
    for img_path in all_images:
        img_name_lower = img_path.stem.lower()
        if any(keyword in img_name_lower for keyword in rust_keywords):
            rust_images.append(img_path)
    
    if rust_images:
        random.shuffle(rust_images)
        total = len(rust_images)
        
        train_split = int(total * 0.7)
        val_split = int(total * 0.2)
        
        splits = {
            'train': rust_images[:train_split],
            'validation': rust_images[train_split:train_split + val_split],
            'test': rust_images[train_split + val_split:]
        }
        
        for split, imgs in splits.items():
            dest_dir = FINAL_DATASET_DIR / split / target_class
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            for img_path in tqdm(imgs, desc=f"Processing {split}"):
                try:
                    Image.open(img_path).verify()
                    shutil.copy2(img_path, dest_dir / img_path.name)
                    stats[split] += 1
                except:
                    continue
        
        print(f"✅ Added {sum(stats.values())} rust images")
        return stats
    
    print("⚠️  No rust images found")
    return stats

def organize_generic_defects(source_dir, target_class='Damaged'):
    """Organize generic defect images"""
    print(f"\n🔄 Organizing defect dataset...")
    
    stats = {'train': 0, 'validation': 0, 'test': 0}
    
    all_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        all_images.extend(source_dir.rglob(ext))
    
    if all_images:
        random.shuffle(all_images)
        total = min(len(all_images), 500)  # Limit to 500 images
        selected = all_images[:total]
        
        train_split = int(total * 0.7)
        val_split = int(total * 0.2)
        
        splits = {
            'train': selected[:train_split],
            'validation': selected[train_split:train_split + val_split],
            'test': selected[train_split + val_split:]
        }
        
        for split, imgs in splits.items():
            dest_dir = FINAL_DATASET_DIR / split / target_class
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            for img_path in tqdm(imgs, desc=f"Processing {split}"):
                try:
                    Image.open(img_path).verify()
                    new_name = f"{target_class.lower()}_{img_path.stem}_{img_path.suffix}"
                    shutil.copy2(img_path, dest_dir / new_name)
                    stats[split] += 1
                except:
                    continue
        
        print(f"✅ Added {sum(stats.values())} defect images")
        return stats
    
    print("⚠️  No defect images found")
    return stats

def print_final_statistics():
    """Print final dataset statistics"""
    print("\n" + "=" * 70)
    print("📊 Final Dataset Statistics")
    print("=" * 70)
    
    total_stats = {'train': {}, 'validation': {}, 'test': {}}
    
    for split in ['train', 'validation', 'test']:
        split_dir = FINAL_DATASET_DIR / split
        if split_dir.exists():
            for class_dir in split_dir.iterdir():
                if class_dir.is_dir():
                    count = len(list(class_dir.glob('*.jpg')) + 
                               list(class_dir.glob('*.jpeg')) + 
                               list(class_dir.glob('*.png')))
                    total_stats[split][class_dir.name] = count
    
    grand_total = 0
    for split in ['train', 'validation', 'test']:
        print(f"\n{split.capitalize()}:")
        split_total = 0
        for class_name in ['Rust', 'Crack', 'Broken', 'Damaged', 'Normal']:
            count = total_stats[split].get(class_name, 0)
            print(f"   {class_name}: {count}")
            split_total += count
        print(f"   Total: {split_total}")
        grand_total += split_total
    
    print("\n" + "=" * 70)
    print(f"Grand Total: {grand_total} images")
    print("=" * 70)

def main():
    """Main execution"""
    print("=" * 70)
    print("🚂 Enhanced Railway Defect Dataset Downloader")
    print("=" * 70)
    
    # Create directories
    RAW_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check Kaggle credentials
    has_kaggle = check_kaggle_credentials()
    
    if has_kaggle:
        print("\n✅ Kaggle credentials found!")
        print("\n📥 Downloading datasets from Kaggle...")
        
        for dataset in KAGGLE_DATASETS:
            output_dir = RAW_DATASET_DIR / dataset['name'].replace('/', '_')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            success = download_kaggle_dataset(dataset['name'], output_dir)
            
            if success:
                # Organize based on dataset type
                if 'crack' in dataset['description'].lower():
                    organize_crack_dataset(output_dir, dataset['target_class'])
                elif 'rust' in dataset['description'].lower() or 'metal' in dataset['description'].lower():
                    organize_rust_dataset(output_dir, dataset['target_class'])
                else:
                    organize_generic_defects(output_dir, dataset['target_class'])
    else:
        print("\n⚠️  Skipping Kaggle downloads (no credentials)")
        print("Using existing synthetic dataset...")
    
    # Print final statistics
    print_final_statistics()
    
    print("\n✅ Dataset preparation complete!")
    print(f"\n📁 Dataset location: {FINAL_DATASET_DIR}")
    print("\n🚀 Next steps:")
    print("   1. Review images in railway_defect_dataset/")
    print("   2. Manually add more images if needed")
    print("   3. Run: python train_vgg_classification.py")
    print("\n💡 Tip: Aim for at least 100 images per class for good results")
    print("=" * 70)

if __name__ == "__main__":
    main()
