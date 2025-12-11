"""
Convert polygon annotations to YOLO bounding box format
Converts segmentation labels to bounding boxes
"""

import os
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "roboflow_dataset"


def polygon_to_bbox(points):
    """
    Convert polygon points to bounding box
    Points: list of (x, y) normalized coordinates
    Returns: (x_center, y_center, width, height) normalized
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    width = x_max - x_min
    height = y_max - y_min
    x_center = x_min + width / 2
    y_center = y_min + height / 2
    
    return x_center, y_center, width, height


def convert_label_file(input_path: Path, output_path: Path):
    """Convert a single label file from polygon to bbox format"""
    lines = []
    
    with open(input_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            
            class_id = int(parts[0])
            
            # Parse polygon points (remaining values are x,y pairs)
            coords = [float(x) for x in parts[1:]]
            
            # Group into (x, y) pairs
            points = []
            for i in range(0, len(coords) - 1, 2):
                points.append((coords[i], coords[i + 1]))
            
            if len(points) < 3:
                # Not enough points for polygon, skip
                continue
            
            # Convert to bounding box
            x_center, y_center, width, height = polygon_to_bbox(points)
            
            # Clamp values to [0, 1]
            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            width = max(0.001, min(1, width))
            height = max(0.001, min(1, height))
            
            # Write in YOLO bbox format
            lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return len(lines)


def convert_dataset():
    """Convert entire dataset from polygon to bbox format"""
    print("=" * 70)
    print("🔄 Converting Polygon Annotations to YOLO Bounding Boxes")
    print("=" * 70)
    
    total_converted = 0
    total_boxes = 0
    
    for split in ['train', 'valid', 'test']:
        labels_dir = DATA_DIR / split / 'labels'
        
        if not labels_dir.exists():
            print(f"⚠️  {split}/labels not found, skipping")
            continue
        
        print(f"\n📁 Processing {split}...")
        
        # Create backup
        backup_dir = DATA_DIR / split / 'labels_polygon_backup'
        if not backup_dir.exists():
            shutil.copytree(labels_dir, backup_dir)
            print(f"   📦 Backed up original labels to labels_polygon_backup/")
        
        # Convert each file
        for label_file in labels_dir.glob('*.txt'):
            num_boxes = convert_label_file(label_file, label_file)
            total_boxes += num_boxes
            total_converted += 1
        
        print(f"   ✅ Converted {total_converted} files")
    
    print(f"\n" + "=" * 70)
    print(f"✅ Conversion Complete!")
    print(f"   Total files converted: {total_converted}")
    print(f"   Total bounding boxes: {total_boxes}")
    print("=" * 70)
    
    # Show sample of converted format
    sample_file = DATA_DIR / 'train' / 'labels'
    sample_files = list(sample_file.glob('*.txt'))
    if sample_files:
        print(f"\n📋 Sample converted label ({sample_files[0].name}):")
        with open(sample_files[0], 'r') as f:
            for i, line in enumerate(f):
                if i < 3:
                    print(f"   {line.strip()}")
                else:
                    break


if __name__ == "__main__":
    convert_dataset()
