#!/usr/bin/env python3
"""
Merge ERC and Sleeper datasets into a unified dataset.
Maps class IDs to:
  0: erc_good
  1: erc_missing  
  2: sleeper
"""

import os
import shutil
from pathlib import Path

# Paths
BASE = Path("/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-detection/data")
ERC_DIR = BASE / "erc_dataset"
SLEEPER_DIR = BASE / "sleeper_only_dataset"
UNIFIED_DIR = BASE / "unified_dataset"

# Class mapping
# ERC: 0 -> 0 (erc_good), 1 -> 1 (erc_missing)
# Sleeper: 0 -> 2 (sleeper)

def copy_dataset(src_dir: Path, dst_dir: Path, class_offset: int, prefix: str):
    """Copy images and labels, adjusting class IDs."""
    splits = ['train', 'valid', 'test']
    
    for split in splits:
        src_images = src_dir / split / 'images'
        src_labels = src_dir / split / 'labels'
        dst_images = dst_dir / split / 'images'
        dst_labels = dst_dir / split / 'labels'
        
        if not src_images.exists():
            print(f"  Skipping {split} - no images folder")
            continue
            
        # Copy images
        image_count = 0
        for img in src_images.glob('*'):
            if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                new_name = f"{prefix}_{img.name}"
                shutil.copy(img, dst_images / new_name)
                image_count += 1
        
        # Copy and modify labels
        label_count = 0
        if src_labels.exists():
            for lbl in src_labels.glob('*.txt'):
                new_name = f"{prefix}_{lbl.name}"
                
                # Read and modify class IDs
                with open(lbl, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        old_class = int(parts[0])
                        new_class = old_class + class_offset
                        new_lines.append(f"{new_class} {' '.join(parts[1:])}\n")
                
                with open(dst_labels / new_name, 'w') as f:
                    f.writelines(new_lines)
                label_count += 1
        
        print(f"  {split}: {image_count} images, {label_count} labels")

def main():
    print("=" * 50)
    print("Creating Unified Railway Component Detector Dataset")
    print("=" * 50)
    
    # Create directories
    print("\n1. Creating directory structure...")
    for split in ['train', 'valid', 'test']:
        (UNIFIED_DIR / split / 'images').mkdir(parents=True, exist_ok=True)
        (UNIFIED_DIR / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Copy ERC dataset (class offset = 0)
    print("\n2. Copying ERC dataset (classes 0-1)...")
    copy_dataset(ERC_DIR, UNIFIED_DIR, class_offset=0, prefix='erc')
    
    # Copy Sleeper dataset (class offset = 2)
    print("\n3. Copying Sleeper dataset (class 2)...")
    copy_dataset(SLEEPER_DIR, UNIFIED_DIR, class_offset=2, prefix='sleeper')
    
    # Create data.yaml
    print("\n4. Creating data.yaml...")
    yaml_content = f"""# Unified Railway Component Detection Dataset
path: {UNIFIED_DIR}
train: train/images
val: valid/images
test: test/images

nc: 3
names:
  0: erc_good
  1: erc_missing
  2: sleeper
"""
    
    with open(UNIFIED_DIR / 'data.yaml', 'w') as f:
        f.write(yaml_content)
    
    # Count final dataset
    print("\n5. Final dataset summary:")
    for split in ['train', 'valid', 'test']:
        img_count = len(list((UNIFIED_DIR / split / 'images').glob('*')))
        lbl_count = len(list((UNIFIED_DIR / split / 'labels').glob('*.txt')))
        print(f"   {split}: {img_count} images, {lbl_count} labels")
    
    print("\n" + "=" * 50)
    print("✅ Unified dataset created at:")
    print(f"   {UNIFIED_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()
