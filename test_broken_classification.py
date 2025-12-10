#!/usr/bin/env python3
"""
Test script specifically for Broken parts classification
Tests model accuracy on identifying broken railway components
"""
import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path
import sys

# Configuration
MODEL_PATH = 'railway-vgg-classification/railway_defect_output/best_model_initial.keras'
TRAIN_BROKEN_DIR = Path('railway-vgg-classification/railway_defect_dataset/train/Broken')
VAL_BROKEN_DIR = Path('railway-vgg-classification/railway_defect_dataset/validation/Broken')
CLASS_NAMES = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']

def test_image(model, image_path, image_name):
    """Test a single broken image"""
    # Load and preprocess
    img = Image.open(image_path).convert('RGB')
    img_resized = img.resize((224, 224))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    predicted_idx = np.argmax(predictions[0])
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence = predictions[0][predicted_idx] * 100
    broken_confidence = predictions[0][0] * 100  # Broken is index 0
    
    # Check if correct
    is_correct = predicted_class == 'Broken'
    
    return {
        'name': image_name,
        'predicted': predicted_class,
        'confidence': confidence,
        'broken_confidence': broken_confidence,
        'correct': is_correct,
        'all_probs': predictions[0]
    }

def print_result(result, show_details=False):
    """Print formatted result"""
    status = "✅" if result['correct'] else "❌"
    print(f"{status} {result['name']:30s} → {result['predicted']:8s} ({result['confidence']:5.1f}%) | Broken: {result['broken_confidence']:5.1f}%")
    
    if show_details and not result['correct']:
        print(f"   Probabilities: ", end="")
        for i, name in enumerate(CLASS_NAMES):
            print(f"{name}: {result['all_probs'][i]*100:5.1f}%  ", end="")
        print()

def main():
    print("=" * 100)
    print("🔧 BROKEN PARTS CLASSIFICATION TEST")
    print("=" * 100)
    
    # Load model
    print(f"\n📦 Loading model from: {MODEL_PATH}")
    try:
        model = tf.keras.models.load_model(MODEL_PATH, compile=True)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Test training set broken images
    print(f"\n" + "=" * 100)
    print("📊 TESTING TRAINING SET BROKEN IMAGES (First 20)")
    print("=" * 100)
    
    train_images = sorted(list(TRAIN_BROKEN_DIR.glob('*.jpg')))[:20]
    train_results = []
    
    for img_path in train_images:
        result = test_image(model, img_path, img_path.name)
        train_results.append(result)
        print_result(result)
    
    # Test validation set broken images
    print(f"\n" + "=" * 100)
    print("📊 TESTING VALIDATION SET BROKEN IMAGES (All)")
    print("=" * 100)
    
    val_images = sorted(list(VAL_BROKEN_DIR.glob('*.jpg')))
    val_results = []
    
    for img_path in val_images:
        result = test_image(model, img_path, img_path.name)
        val_results.append(result)
        print_result(result, show_details=True)
    
    # Calculate statistics
    print(f"\n" + "=" * 100)
    print("📈 OVERALL STATISTICS")
    print("=" * 100)
    
    # Training set stats
    train_correct = sum(1 for r in train_results if r['correct'])
    train_accuracy = (train_correct / len(train_results)) * 100 if train_results else 0
    train_avg_broken_conf = np.mean([r['broken_confidence'] for r in train_results])
    
    print(f"\n🔹 Training Set (20 images):")
    print(f"   Accuracy: {train_correct}/{len(train_results)} = {train_accuracy:.1f}%")
    print(f"   Avg Broken Confidence: {train_avg_broken_conf:.1f}%")
    
    # Validation set stats
    val_correct = sum(1 for r in val_results if r['correct'])
    val_accuracy = (val_correct / len(val_results)) * 100 if val_results else 0
    val_avg_broken_conf = np.mean([r['broken_confidence'] for r in val_results])
    
    print(f"\n🔹 Validation Set ({len(val_results)} images):")
    print(f"   Accuracy: {val_correct}/{len(val_results)} = {val_accuracy:.1f}%")
    print(f"   Avg Broken Confidence: {val_avg_broken_conf:.1f}%")
    
    # Misclassification analysis
    train_misclassified = [r for r in train_results if not r['correct']]
    val_misclassified = [r for r in val_results if not r['correct']]
    
    if train_misclassified or val_misclassified:
        print(f"\n" + "=" * 100)
        print("⚠️  MISCLASSIFICATION ANALYSIS")
        print("=" * 100)
        
        if train_misclassified:
            print(f"\n❌ Training Set Misclassified ({len(train_misclassified)} images):")
            misclass_count = {}
            for r in train_misclassified:
                misclass_count[r['predicted']] = misclass_count.get(r['predicted'], 0) + 1
            for pred_class, count in sorted(misclass_count.items(), key=lambda x: -x[1]):
                print(f"   Predicted as {pred_class}: {count} images")
        
        if val_misclassified:
            print(f"\n❌ Validation Set Misclassified ({len(val_misclassified)} images):")
            misclass_count = {}
            for r in val_misclassified:
                misclass_count[r['predicted']] = misclass_count.get(r['predicted'], 0) + 1
            for pred_class, count in sorted(misclass_count.items(), key=lambda x: -x[1]):
                print(f"   Predicted as {pred_class}: {count} images")
    
    # Overall assessment
    print(f"\n" + "=" * 100)
    print("🎯 ASSESSMENT")
    print("=" * 100)
    
    overall_accuracy = ((train_correct + val_correct) / (len(train_results) + len(val_results))) * 100
    
    print(f"\n📊 Overall Broken Detection Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 90:
        print("✅ EXCELLENT - Model is highly accurate at detecting broken parts")
    elif overall_accuracy >= 70:
        print("⚠️  GOOD - Model is fairly accurate but could be improved")
    elif overall_accuracy >= 50:
        print("⚠️  FAIR - Model needs more training to reliably detect broken parts")
    else:
        print("❌ POOR - Model struggles to identify broken parts, needs retraining")
    
    print(f"\n💡 Note: Model was trained with class weights:")
    print(f"   Broken weight: 15.12x (highest - only 50 training images)")
    print(f"   This should help the model learn broken patterns despite limited data")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
