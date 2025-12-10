#!/usr/bin/env python3
"""
Extended test - Check if model incorrectly labels non-broken images as broken
Tests for false positives on Normal, Damaged, Crack, and Rust images
"""
import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path

MODEL_PATH = 'railway-vgg-classification/railway_defect_output/best_model_initial.keras'
DATASET_DIR = Path('railway-vgg-classification/railway_defect_dataset/validation')
CLASS_NAMES = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']

def test_class(model, class_name, num_images=10):
    """Test images from a specific class"""
    class_dir = DATASET_DIR / class_name
    images = sorted(list(class_dir.glob('*.jpg')))[:num_images]
    
    results = {
        'total': len(images),
        'correct': 0,
        'false_positive_broken': 0,
        'predictions': {}
    }
    
    for img_path in images:
        img = Image.open(img_path).convert('RGB')
        img_array = np.array(img.resize((224, 224))) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        predicted_class = CLASS_NAMES[predicted_idx]
        confidence = predictions[0][predicted_idx] * 100
        broken_conf = predictions[0][0] * 100
        
        is_correct = predicted_class == class_name
        is_false_broken = (predicted_class == 'Broken' and class_name != 'Broken')
        
        if is_correct:
            results['correct'] += 1
        if is_false_broken:
            results['false_positive_broken'] += 1
        
        results['predictions'][predicted_class] = results['predictions'].get(predicted_class, 0) + 1
        
        status = "✅" if is_correct else "❌"
        if is_false_broken:
            status = "⚠️ "
        
        print(f"{status} {img_path.name:30s} → {predicted_class:8s} ({confidence:5.1f}%) | Broken conf: {broken_conf:5.1f}%")
    
    return results

def main():
    print("=" * 100)
    print("🔍 FALSE POSITIVE TEST - Checking if model over-predicts 'Broken'")
    print("=" * 100)
    
    # Load model
    print(f"\n📦 Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=True)
    print("✅ Model loaded\n")
    
    all_results = {}
    
    # Test each non-broken class
    for class_name in ['Normal', 'Damaged', 'Crack', 'Rust']:
        print("=" * 100)
        print(f"📊 Testing {class_name.upper()} Images (Expected: {class_name})")
        print("=" * 100)
        
        results = test_class(model, class_name, num_images=10)
        all_results[class_name] = results
        
        accuracy = (results['correct'] / results['total']) * 100
        print(f"\n   Accuracy: {results['correct']}/{results['total']} = {accuracy:.1f}%")
        print(f"   False Positives (labeled as Broken): {results['false_positive_broken']}")
        if results['predictions']:
            print(f"   Prediction breakdown: {results['predictions']}")
        print()
    
    # Summary
    print("=" * 100)
    print("📊 SUMMARY - False Positive Analysis")
    print("=" * 100)
    
    total_tested = sum(r['total'] for r in all_results.values())
    total_correct = sum(r['correct'] for r in all_results.values())
    total_false_broken = sum(r['false_positive_broken'] for r in all_results.values())
    
    overall_accuracy = (total_correct / total_tested) * 100
    false_positive_rate = (total_false_broken / total_tested) * 100
    
    print(f"\n🔹 Overall Non-Broken Classification:")
    print(f"   Total images tested: {total_tested}")
    print(f"   Correctly classified: {total_correct} ({overall_accuracy:.1f}%)")
    print(f"   Incorrectly labeled as Broken: {total_false_broken} ({false_positive_rate:.1f}%)")
    
    print(f"\n🎯 Broken Detection Assessment:")
    print(f"   True Positive (Broken → Broken): 100% (30/30 from previous test)")
    print(f"   False Positive (Non-Broken → Broken): {false_positive_rate:.1f}% ({total_false_broken}/{total_tested})")
    
    if false_positive_rate == 0:
        print(f"\n✅ PERFECT - No false positives! Model doesn't over-predict 'Broken'")
    elif false_positive_rate < 5:
        print(f"\n✅ EXCELLENT - Very low false positive rate")
    elif false_positive_rate < 15:
        print(f"\n⚠️  GOOD - Acceptable false positive rate")
    else:
        print(f"\n⚠️  CAUTION - Model may be over-predicting 'Broken' class")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
