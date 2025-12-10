"""
Prepare VGG Dataset from Railway-2
Creates a proper classification dataset with multiple classes
"""

import shutil
from pathlib import Path
from PIL import Image
import random
from tqdm import tqdm

# Paths
SOURCE_DATASET = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-llm/Railway-2')
DEST_DATASET = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-yolo-llm/vgg_dataset')

# We'll use the Railway-2 dataset and create classes based on image characteristics
# Since all images have faults, we'll split into severity levels or use augmentation

def create_directory_structure():
    """Create VGG dataset directory structure"""
    print("\n📁 Creating VGG dataset structure...")
    
    # Create directories for multiple classes
    classes = ['fault', 'severe_fault', 'minor_fault']
    
    for split in ['train', 'validation', 'test']:
        for class_name in classes:
            class_dir = DEST_DATASET / split / class_name
            class_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created: {DEST_DATASET}")
    return classes

def count_fault_objects(label_file):
    """Count number of fault objects in label file"""
    if not label_file.exists():
        return 0
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
        return len([line for line in lines if line.strip()])

def prepare_dataset():
    """Prepare dataset with fault severity classification"""
    print("\n🔄 Preparing VGG dataset...")
    
    classes = create_directory_structure()
    stats = {split: {cls: 0 for cls in classes} for split in ['train', 'validation', 'test']}
    
    # Process each split
    for source_split, dest_split in [('train', 'train'), ('valid', 'validation'), ('test', 'test')]:
        images_dir = SOURCE_DATASET / source_split / 'images'
        labels_dir = SOURCE_DATASET / source_split / 'labels'
        
        if not images_dir.exists():
            continue
        
        print(f"\n📂 Processing {source_split}...")
        
        # Get all images
        image_files = list(images_dir.glob('*.jpg')) + \
                      list(images_dir.glob('*.jpeg')) + \
                      list(images_dir.glob('*.png'))
        
        for img_path in tqdm(image_files, desc=f"Processing {source_split}"):
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            # Count fault objects to determine severity
            fault_count = count_fault_objects(label_path)
            
            # Classify based on fault count
            if fault_count == 0:
                class_name = 'fault'  # Shouldn't happen but just in case
            elif fault_count == 1:
                class_name = 'minor_fault'
            elif fault_count == 2:
                class_name = 'fault'
            else:  # 3 or more
                class_name = 'severe_fault'
            
            # Copy image to appropriate class folder
            dest_path = DEST_DATASET / dest_split / class_name / img_path.name
            shutil.copy2(img_path, dest_path)
            stats[dest_split][class_name] += 1
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 VGG Dataset Statistics")
    print("=" * 60)
    
    for split in ['train', 'validation', 'test']:
        print(f"\n{split.capitalize()}:")
        total = 0
        for cls in classes:
            count = stats[split][cls]
            print(f"   {cls}: {count}")
            total += count
        print(f"   Total: {total}")
    
    print("\n" + "=" * 60)
    grand_total = sum(sum(stats[split].values()) for split in stats)
    print(f"Grand Total: {grand_total} images")
    print("=" * 60)

def main():
    """Main execution"""
    print("=" * 60)
    print("🚂 VGG Dataset Preparation")
    print("=" * 60)
    
    if not SOURCE_DATASET.exists():
        print(f"\n❌ Source dataset not found: {SOURCE_DATASET}")
        return
    
    # Clean up existing dataset if it exists
    if DEST_DATASET.exists():
        print(f"\n⚠️  Removing existing dataset: {DEST_DATASET}")
        shutil.rmtree(DEST_DATASET)
    
    # Prepare dataset
    prepare_dataset()
    
    print(f"\n✅ VGG dataset ready!")
    print(f"📁 Location: {DEST_DATASET}")
    print(f"\n🚀 Next step:")
    print(f"   python train_vgg_classification.py")

if __name__ == "__main__":
    main()
