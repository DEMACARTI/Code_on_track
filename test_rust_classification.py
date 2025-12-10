#!/usr/bin/env python3
"""
Test script to classify the rusted railway component image
"""
import tensorflow as tf
import numpy as np
from PIL import Image
from pathlib import Path

# Class names
CLASS_NAMES = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']

def preprocess_image(image_path):
    """Preprocess image for VGG model"""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def test_model(model_path, image_path):
    """Test the model with the given image"""
    print(f"\n{'='*60}")
    print(f"Testing Model: {Path(model_path).name}")
    print(f"Image: {image_path}")
    print(f"{'='*60}\n")
    
    try:
        # Load model
        print("Loading model...")
        model = tf.keras.models.load_model(model_path, compile=True)
        print(f"✅ Model loaded successfully!")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        
        # Preprocess image
        print("\nPreprocessing image...")
        img_array = preprocess_image(image_path)
        print(f"✅ Image preprocessed: shape {img_array.shape}")
        
        # Make prediction
        print("\nMaking prediction...")
        predictions = model.predict(img_array, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence = predictions[0][predicted_class_idx] * 100
        
        # Display results
        print(f"\n{'='*60}")
        print(f"PREDICTION RESULTS")
        print(f"{'='*60}")
        print(f"Predicted Class: {predicted_class}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"\nAll Class Probabilities:")
        for i, class_name in enumerate(CLASS_NAMES):
            prob = predictions[0][i] * 100
            bar = '█' * int(prob / 2)
            print(f"  {class_name:10s}: {prob:6.2f}% {bar}")
        print(f"{'='*60}\n")
        
        # Check if rust is detected
        if predicted_class == 'Rust':
            print("✅ SUCCESS: Model correctly identified RUST!")
            return True
        else:
            print(f"❌ FAILED: Model predicted '{predicted_class}' instead of 'Rust'")
            print(f"   Rust probability: {predictions[0][4] * 100:.2f}%")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Paths
    model_path = "/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_output/best_model_initial.keras"
    
    # Test with the uploaded rust image (assuming it's saved as rust_test.jpg)
    # You'll need to save the uploaded image first
    image_path = "/Users/dakshrathore/Desktop/Code_on_track/rust_test_image.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        print("Please save the uploaded image to this location first.")
    else:
        success = test_model(model_path, image_path)
        exit(0 if success else 1)
