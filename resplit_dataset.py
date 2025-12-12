#!/usr/bin/env python3
"""
Re-split YOLO Dataset with Stratified Sampling
Fixes the imbalance where sleepers are missing from validation/test sets
"""

import shutil
from pathlib import Path
from collections import defaultdict
import random
import sys

# Paths
DATASET_ROOT = Path('DETECTION_Model/merged_dataset')
BACKUP_DIR = Path('DETECTION_Model/merged_dataset_backup')

# Split ratios
TRAIN_RATIO = 0.70
VALID_RATIO = 0.15
TEST_RATIO = 0.15

# Class names
CLASS_NAMES = ['clip', 'rail', 'bolt', 'broken_rail', 'sleeper', 'correct', 'overrailed', 'underrailed', 'mf']

# Minimum samples per class in each split
MIN_SAMPLES_PER_SPLIT = 2  # At least 2 samples per class in valid/test

def backup_dataset():
    """Backup current dataset structure"""
    print("\n📦 Backing up current dataset...")
    
    if BACKUP_DIR.exists():
        response = input(f"Backup already exists at {BACKUP_DIR}. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Backup skipped.")
            return False
        shutil.rmtree(BACKUP_DIR)
    
    shutil.copytree(DATASET_ROOT, BACKUP_DIR)
    print(f"✅ Backup created at: {BACKUP_DIR}")
    return True

def collect_all_samples():
    """Collect all image-label pairs from current split"""
    print("\n🔍 Collecting all samples from current dataset...")
    
    samples_by_class = defaultdict(list)
    
    for split in ['train', 'valid', 'test']:
        images_dir = DATASET_ROOT / split / 'images'
        labels_dir = DATASET_ROOT / split / 'labels'
        
        if not images_dir.exists():
            continue
        
        for label_file in labels_dir.glob('*.txt'):
            # Get corresponding image
            image_name = label_file.stem + '.jpg'
            image_file = images_dir / image_name
            
            if not image_file.exists():
                continue
            
            # Read label to determine class(es)
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                continue
            
            # Get all classes in this image
            classes_in_image = set()
            for line in lines:
                parts = line.strip().split()
                if parts:
                    class_id = int(parts[0])
                    classes_in_image.add(class_id)
            
            # Add to each class bucket
            for class_id in classes_in_image:
                samples_by_class[class_id].append({
                    'image': image_file,
                    'label': label_file,
                    'stem': label_file.stem
                })
    
    # Print collection stats
    print(f"\n📊 Collected Samples by Class:")
    for class_id in range(len(CLASS_NAMES)):
        count = len(samples_by_class[class_id])
        print(f"   {class_id}. {CLASS_NAMES[class_id]}: {count} images")
    
    return samples_by_class

def stratified_split(samples_by_class):
    """Create stratified train/valid/test split"""
    print(f"\n🎯 Creating stratified split (Train: {TRAIN_RATIO*100:.0f}%, Valid: {VALID_RATIO*100:.0f}%, Test: {TEST_RATIO*100:.0f}%)...")
    
    train_samples = set()
    valid_samples = set()
    test_samples = set()
    
    # For each class, ensure representation in all splits
    for class_id, samples in samples_by_class.items():
        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"class_{class_id}"
        total = len(samples)
        
        if total == 0:
            print(f"   ⚠️  {class_name}: No samples, skipping")
            continue
        
        # Shuffle samples
        random.shuffle(samples)
        
        # Calculate split sizes
        # Ensure minimum samples in valid and test
        valid_size = max(MIN_SAMPLES_PER_SPLIT, int(total * VALID_RATIO))
        test_size = max(MIN_SAMPLES_PER_SPLIT, int(total * TEST_RATIO))
        train_size = total - valid_size - test_size
        
        # Adjust if not enough samples
        if train_size < MIN_SAMPLES_PER_SPLIT:
            # Not enough samples for all splits
            if total >= MIN_SAMPLES_PER_SPLIT * 2:
                train_size = total - 2 * MIN_SAMPLES_PER_SPLIT
                valid_size = MIN_SAMPLES_PER_SPLIT
                test_size = MIN_SAMPLES_PER_SPLIT
            else:
                # Very few samples, put all in train
                train_size = total
                valid_size = 0
                test_size = 0
        
        # Split samples
        class_train = samples[:train_size]
        class_valid = samples[train_size:train_size + valid_size]
        class_test = samples[train_size + valid_size:]
        
        # Add to sets (use stem to avoid duplicates across classes)
        train_samples.update(s['stem'] for s in class_train)
        valid_samples.update(s['stem'] for s in class_valid)
        test_samples.update(s['stem'] for s in class_test)
        
        print(f"   {class_id}. {class_name}: {len(class_train)} train, {len(class_valid)} valid, {len(class_test)} test")
    
    return train_samples, valid_samples, test_samples

def move_files_to_split(sample_stems, split_name):
    """Move files to the specified split directory"""
    print(f"\n📁 Moving files to {split_name} split...")
    
    images_dir = DATASET_ROOT / split_name / 'images'
    labels_dir = DATASET_ROOT / split_name / 'labels'
    
    # Clear existing files
    if images_dir.exists():
        for f in images_dir.glob('*'):
            f.unlink()
    else:
        images_dir.mkdir(parents=True, exist_ok=True)
    
    if labels_dir.exists():
        for f in labels_dir.glob('*'):
            f.unlink()
    else:
        labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    moved_count = 0
    for stem in sample_stems:
        # Find source files in backup
        for split in ['train', 'valid', 'test']:
            src_image = BACKUP_DIR / split / 'images' / f'{stem}.jpg'
            src_label = BACKUP_DIR / split / 'labels' / f'{stem}.txt'
            
            if src_image.exists() and src_label.exists():
                # Copy to new location
                shutil.copy2(src_image, images_dir / f'{stem}.jpg')
                shutil.copy2(src_label, labels_dir / f'{stem}.txt')
                moved_count += 1
                break
    
    print(f"   ✅ Moved {moved_count} samples to {split_name}")
    return moved_count

def verify_split():
    """Verify the new split has balanced classes"""
    print("\n" + "="*70)
    print("🔍 Verifying New Split")
    print("="*70)
    
    for split in ['train', 'valid', 'test']:
        labels_dir = DATASET_ROOT / split / 'labels'
        
        if not labels_dir.exists():
            continue
        
        class_counts = defaultdict(int)
        total_annotations = 0
        
        for label_file in labels_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                        total_annotations += 1
        
        print(f"\n{split.upper()} Set:")
        print(f"   Files: {len(list(labels_dir.glob('*.txt')))}")
        print(f"   Annotations: {total_annotations}")
        
        # Check for sleepers specifically
        sleeper_count = class_counts.get(4, 0)
        if sleeper_count > 0:
            print(f"   ✅ Sleepers: {sleeper_count} ({sleeper_count/total_annotations*100:.1f}%)")
        else:
            print(f"   ⚠️  Sleepers: 0 (MISSING!)")

def main():
    """Main function"""
    print("="*70)
    print("🔄 YOLO Dataset Re-split with Stratified Sampling")
    print("="*70)
    print("\nThis will re-organize the dataset to ensure balanced class distribution.")
    print(f"Target split: Train {TRAIN_RATIO*100:.0f}% | Valid {VALID_RATIO*100:.0f}% | Test {TEST_RATIO*100:.0f}%")
    
    response = input("\nProceed with re-split? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Step 1: Backup
    if not backup_dataset():
        print("❌ Backup failed. Exiting.")
        return
    
    # Step 2: Collect all samples
    samples_by_class = collect_all_samples()
    
    if not samples_by_class:
        print("❌ No samples found. Exiting.")
        return
    
    # Step 3: Create stratified split
    random.seed(42)  # For reproducibility
    train_stems, valid_stems, test_stems = stratified_split(samples_by_class)
    
    print(f"\n📊 New Split Sizes:")
    print(f"   Train: {len(train_stems)} unique images")
    print(f"   Valid: {len(valid_stems)} unique images")
    print(f"   Test: {len(test_stems)} unique images")
    
    # Step 4: Move files
    move_files_to_split(train_stems, 'train')
    move_files_to_split(valid_stems, 'valid')
    move_files_to_split(test_stems, 'test')
    
    # Step 5: Verify
    verify_split()
    
    print("\n" + "="*70)
    print("✅ Dataset Re-split Complete!")
    print("="*70)
    print(f"\nBackup location: {BACKUP_DIR}")
    print("If you need to restore, copy the backup back to merged_dataset/")

if __name__ == "__main__":
    main()
