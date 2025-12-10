#!/usr/bin/env python3
"""
Comprehensive test script for rust classification
Tests the model with multiple images and provides detailed analysis
"""
import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path
import sys

CLASS_NAMES = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']

def test_image(model, image_path, expected_class=None):
    """Test a single image"""
    # Load and preprocess
    img = Image.open(image_path).convert('RGB')
    original_size = img.size
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    predicted_idx = np.argmax(predictions[0])
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence = predictions[0][predicted_idx] * 100
    
    # Print results
    print(f"\n{'='*70}")
    print(f"Image: {Path(image_path).name}")
    print(f"Original size: {original_size}")
    if expected_class:
        print(f"Expected: {expected_class}")
    print(f"{'='*70}")
    print(f"Predicted: {predicted_class} ({confidence:.2f}%)")
    print(f"\nAll class probabilities:")
    for i, name in enumerate(CLASS_NAMES):
        prob = predictions[0][i] * 100
        bar = '█' * int(prob / 2)
        indicator = " ← PREDICTED" if i == predicted_idx else ""
        print(f"  {name:10s}: {prob:6.2f}% {bar}{indicator}")
    
    # Check if correct
    if expected_class:
        if predicted_class == expected_class:
            print(f"\n✅ CORRECT!")
            return True
        else:
            print(f"\n❌ INCORRECT! Expected {expected_class}, got {predicted_class}")
            return False
    
    return predicted_class == "Rust"  # Default to checking if rust

def main():
    model_path = "/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_output/best_model_initial.keras"
    
    print("\n" + "="*70)
    print(" " * 15 + "RUST CLASSIFICATION TEST SUITE")
    print("="*70)
    
    # Load model
    print(f"\n📦 Loading model: {Path(model_path).name}...")
    try:
        model = tf.keras.models.load_model(model_path, compile=True)
        print(f"✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return 1
    
    # Test with rust images from training set
    rust_dir = Path("/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_dataset/train/Rust")
    rust_images = list(rust_dir.glob("*.jpg"))[:5]  # Test first 5
    
    print(f"\n{'='*70}")
    print(f"TEST 1: RUST IMAGES FROM TRAINING DATASET")
    print(f"{'='*70}")
    
    correct = 0
    for img_path in rust_images:
        if test_image(model, img_path, expected_class="Rust"):
            correct += 1
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {correct}/{len(rust_images)} rust images correctly classified")
    print(f"Accuracy: {(correct/len(rust_images))*100:.1f}%")
    print(f"{'='*70}")
    
    # Test with other classes to check for false positives
    print(f"\n{'='*70}")
    print(f"TEST 2: NON-RUST IMAGES (Checking for false positives)")
    print(f"{'='*70}")
    
    base_dir = Path("/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_dataset/train")
    test_other = []
    for class_name in ['Normal', 'Damaged', 'Crack']:
        class_dir = base_dir / class_name
        imgs = list(class_dir.glob("*.jpg"))[:2]
        for img in imgs:
            test_other.append((img, class_name))
    
    correct_non_rust = 0
    for img_path, expected in test_other:
        if test_image(model, img_path, expected_class=expected):
            correct_non_rust += 1
    
    print(f"\n{'='*70}")
    print(f"NON-RUST RESULTS: {correct_non_rust}/{len(test_other)} correctly classified")
    print(f"Accuracy: {(correct_non_rust/len(test_other))*100:.1f}%")
    print(f"{'='*70}")
    
    # Overall summary
    total_correct = correct + correct_non_rust
    total_tests = len(rust_images) + len(test_other)
    overall_accuracy = (total_correct / total_tests) * 100
    
    print(f"\n{'='*70}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*70}")
    print(f"Total tests: {total_tests}")
    print(f"Correct: {total_correct}")
    print(f"Overall accuracy: {overall_accuracy:.1f}%")
    print(f"\nRust detection: {correct}/{len(rust_images)} ({(correct/len(rust_images))*100:.1f}%)")
    print(f"Non-rust accuracy: {correct_non_rust}/{len(test_other)} ({(correct_non_rust/len(test_other))*100:.1f}%)")
    
    if correct == len(rust_images):
        print(f"\n✅ SUCCESS! Model correctly identifies all rust images!")
        return 0
    else:
        print(f"\n⚠️  WARNING: Model misclassified {len(rust_images) - correct} rust images")
        print(f"   Training needs more iterations to improve rust detection")
        return 1

if __name__ == "__main__":
    exit(main())
