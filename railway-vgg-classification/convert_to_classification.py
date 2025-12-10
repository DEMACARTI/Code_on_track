"""
Convert YOLO Detection Dataset to Classification Dataset
Converts Railway-2 YOLO format to folder-based classification format
"""

import shutil
from pathlib import Path
from PIL import Image
import yaml
from tqdm import tqdm

# Source and destination
SOURCE_DATASET = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-llm/Railway-2')
DEST_DATASET = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-llm/Railway-2-classification')

# Class mapping - adjust based on your needs
# For Railway-2, we have: 0 = 'fault'
# We'll create two classes: 'Faulty' and 'Normal'
CLASS_MAPPING = {
    0: 'Faulty'  # Images with fault labels
}

def create_directory_structure():
    """Create classification dataset structure"""
    print("\n📁 Creating directory structure...")
    
    # Create base directories
    for split in ['train', 'validation', 'test']:
        for class_name in ['Faulty', 'Normal']:
            class_dir = DEST_DATASET / split / class_name
            class_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created: {DEST_DATASET}")

def has_labels(label_file):
    """Check if label file has any annotations"""
    if not label_file.exists():
        return False
    
    with open(label_file, 'r') as f:
        content = f.read().strip()
        return len(content) > 0

def convert_split(split_name, source_split):
    """Convert one split (train/val/test) from YOLO to classification"""
    
    print(f"\n🔄 Converting {split_name}...")
    
    # Get source directories
    images_dir = SOURCE_DATASET / source_split / 'images'
    labels_dir = SOURCE_DATASET / source_split / 'labels'
    
    if not images_dir.exists():
        print(f"⚠️  {split_name} images directory not found, skipping...")
        return
    
    # Get all images
    image_files = list(images_dir.glob('*.jpg')) + \
                  list(images_dir.glob('*.jpeg')) + \
                  list(images_dir.glob('*.png'))
    
    faulty_count = 0
    normal_count = 0
    
    for img_path in tqdm(image_files, desc=f"Processing {split_name}"):
        # Check corresponding label file
        label_path = labels_dir / f"{img_path.stem}.txt"
        
        # Determine class
        if has_labels(label_path):
            class_name = 'Faulty'
            faulty_count += 1
        else:
            class_name = 'Normal'
            normal_count += 1
        
        # Copy image to appropriate class folder
        dest_path = DEST_DATASET / split_name / class_name / img_path.name
        shutil.copy2(img_path, dest_path)
    
    print(f"   ✅ {split_name}: {faulty_count} Faulty, {normal_count} Normal")
    
    return faulty_count, normal_count

def verify_dataset():
    """Verify the created dataset"""
    print("\n📊 Dataset Statistics:")
    print("=" * 60)
    
    total_faulty = 0
    total_normal = 0
    
    for split in ['train', 'validation', 'test']:
        split_dir = DEST_DATASET / split
        if not split_dir.exists():
            continue
        
        faulty_count = len(list((split_dir / 'Faulty').glob('*')))
        normal_count = len(list((split_dir / 'Normal').glob('*')))
        
        print(f"\n{split.capitalize()}:")
        print(f"   Faulty: {faulty_count}")
        print(f"   Normal: {normal_count}")
        print(f"   Total: {faulty_count + normal_count}")
        
        total_faulty += faulty_count
        total_normal += normal_count
    
    print(f"\n{'=' * 60}")
    print(f"Total Dataset:")
    print(f"   Faulty: {total_faulty}")
    print(f"   Normal: {total_normal}")
    print(f"   Grand Total: {total_faulty + total_normal}")
    print(f"{'=' * 60}")

def main():
    """Main conversion pipeline"""
    print("=" * 60)
    print("🔄 YOLO to Classification Dataset Converter")
    print("=" * 60)
    
    # Check source dataset
    if not SOURCE_DATASET.exists():
        print(f"\n❌ Source dataset not found: {SOURCE_DATASET}")
        return
    
    # Create directory structure
    create_directory_structure()
    
    # Convert each split
    convert_split('train', 'train')
    convert_split('validation', 'valid')
    
    if (SOURCE_DATASET / 'test' / 'images').exists():
        convert_split('test', 'test')
    
    # Verify dataset
    verify_dataset()
    
    print("\n✅ Conversion complete!")
    print(f"\n📁 Classification dataset created at:")
    print(f"   {DEST_DATASET}")
    
    print("\n🚀 Next step:")
    print("   python train_vgg_classification.py")

if __name__ == "__main__":
    main()
