#!/usr/bin/env python3
"""
Analyze YOLO dataset class distribution
"""
from pathlib import Path
from collections import Counter
import sys

LABEL_DIR = Path('DETECTION_Model/merged_dataset')
CLASS_NAMES = ['clip', 'rail', 'bolt', 'broken_rail', 'sleeper', 'correct', 'overrailed', 'underrailed', 'mf']

def analyze_labels(split='train'):
    """Analyze labels in a dataset split"""
    label_path = LABEL_DIR / split / 'labels'
    
    if not label_path.exists():
        print(f"❌ Label directory not found: {label_path}")
        return {}
    
    label_files = list(label_path.glob('*.txt'))
    print(f"\n{'='*70}")
    print(f"📊 {split.upper()} Set Analysis")
    print(f"{'='*70}")
    print(f"Total label files: {len(label_files)}")
    
    class_counts = Counter()
    total_annotations = 0
    
    for label_file in label_files:
        with open(label_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if parts:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                        total_annotations += 1
    
    print(f"Total annotations: {total_annotations}")
    print(f"\n🏷️  Class Distribution:")
    print(f"{'Class ID':<10} {'Class Name':<15} {'Count':<10} {'%':<10}")
    print('-' * 50)
    
    for class_id in range(len(CLASS_NAMES)):
        count = class_counts.get(class_id, 0)
        percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
        class_name = CLASS_NAMES[class_id]
        print(f"{class_id:<10} {class_name:<15} {count:<10} {percentage:>6.2f}%")
    
    return class_counts

def main():
    print("="*70)
    print("🔍 YOLO Dataset Analysis")
    print("="*70)
    
    all_counts = {}
    for split in ['train', 'valid', 'test']:
        counts = analyze_labels(split)
        all_counts[split] = counts
    
    # Overall summary
    print(f"\n{'='*70}")
    print("📈 Overall Summary")
    print(f"{'='*70}")
    
    total_by_class = Counter()
    for split_counts in all_counts.values():
        total_by_class.update(split_counts)
    
    print(f"\nTotal annotations across all splits: {sum(total_by_class.values())}")
    print(f"\n🏆 Top 5 Most Common Classes:")
    for class_id, count in total_by_class.most_common(5):
        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"class_{class_id}"
        print(f"   {class_id}. {class_name}: {count}")
    
    print(f"\n⚠️  Classes with ZERO Annotations:")
    for class_id in range(len(CLASS_NAMES)):
        if total_by_class[class_id] == 0:
            print(f"   {class_id}. {CLASS_NAMES[class_id]}")

if __name__ == "__main__":
    main()
