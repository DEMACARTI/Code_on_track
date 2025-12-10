#!/usr/bin/env python3
"""
Download and integrate rust/corrosion datasets to balance the training data
"""
import os
import shutil
from pathlib import Path
import requests
from PIL import Image
import io

# Paths
BASE_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification')
TRAIN_RUST_DIR = BASE_DIR / 'railway_defect_dataset' / 'train' / 'Rust'
VAL_RUST_DIR = BASE_DIR / 'railway_defect_dataset' / 'validation' / 'Rust'

# Create directories
TRAIN_RUST_DIR.mkdir(parents=True, exist_ok=True)
VAL_RUST_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("🦀 RUST/CORROSION DATASET AUGMENTATION")
print("=" * 80)

# Count current images
current_train = len(list(TRAIN_RUST_DIR.glob('*.jpg')))
current_val = len(list(VAL_RUST_DIR.glob('*.jpg')))
print(f"\nCurrent rust images:")
print(f"  Train: {current_train}")
print(f"  Validation: {current_val}")

# We'll use data augmentation on existing rust images to create more samples
print("\n📦 Applying data augmentation to existing rust images...")

from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_img
import numpy as np

# Augmentation configuration
datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest',
    brightness_range=[0.7, 1.3]
)

def augment_images(source_dir, target_count=500):
    """Augment images in directory to reach target count"""
    images = list(source_dir.glob('rust_*.jpg'))
    current_count = len(images)
    
    if current_count >= target_count:
        print(f"   Already have {current_count} images, no augmentation needed")
        return current_count
    
    needed = target_count - current_count
    augmentations_per_image = needed // current_count + 1
    
    print(f"   Need {needed} more images")
    print(f"   Generating {augmentations_per_image} variations per image")
    
    count = current_count
    for img_path in images:
        # Load image
        img = load_img(img_path, target_size=(224, 224))
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        # Generate augmented images
        i = 0
        for batch in datagen.flow(x, batch_size=1):
            aug_img = array_to_img(batch[0])
            aug_path = source_dir / f'rust_augmented_{count:04d}.jpg'
            aug_img.save(aug_path)
            count += 1
            i += 1
            
            if i >= augmentations_per_image or count >= target_count:
                break
        
        if count >= target_count:
            break
    
    return count

# Augment training set
print("\n📈 Augmenting training rust images...")
final_train_count = augment_images(TRAIN_RUST_DIR, target_count=500)
print(f"   ✅ Training rust images: {final_train_count}")

# Augment validation set
print("\n📈 Augmenting validation rust images...")
final_val_count = augment_images(VAL_RUST_DIR, target_count=100)
print(f"   ✅ Validation rust images: {final_val_count}")

print("\n" + "=" * 80)
print("✅ RUST DATASET AUGMENTATION COMPLETE!")
print("=" * 80)
print(f"\nFinal counts:")
print(f"  Training rust images: {final_train_count}")
print(f"  Validation rust images: {final_val_count}")
