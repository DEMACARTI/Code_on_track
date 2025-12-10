"""
VGG Model Inference Script
Predict railway component condition from images
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import json
from pathlib import Path
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model and class indices paths
MODEL_PATH = '/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/vgg_output/final_model.keras'
CLASS_INDICES_PATH = '/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/vgg_output/class_indices.json'

# Image settings
IMAGE_SIZE = (224, 224)

# ============================================================================
# LOAD MODEL
# ============================================================================

def load_model_and_classes():
    """Load trained model and class indices"""
    
    print("=" * 60)
    print("🧠 Loading Model")
    print("=" * 60)
    
    # Load model
    model = keras.models.load_model(MODEL_PATH)
    print(f"✅ Model loaded from: {MODEL_PATH}")
    
    # Load class indices
    with open(CLASS_INDICES_PATH, 'r') as f:
        class_indices = json.load(f)
    
    # Reverse mapping (index -> class name)
    class_names = {v: k for k, v in class_indices.items()}
    print(f"✅ Classes: {list(class_indices.keys())}")
    
    return model, class_names

# ============================================================================
# PREDICTION
# ============================================================================

def preprocess_image(image_path):
    """Preprocess image for VGG model"""
    
    # Load and resize image
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMAGE_SIZE)
    
    # Convert to array and normalize
    img_array = np.array(img) / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array, img

def predict_image(model, class_names, image_path, show_plot=True):
    """Predict class for a single image"""
    
    print(f"\n📸 Processing: {image_path}")
    
    # Preprocess
    img_array, original_img = preprocess_image(image_path)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)[0]
    
    # Get top prediction
    predicted_class_idx = np.argmax(predictions)
    predicted_class = class_names[predicted_class_idx]
    confidence = predictions[predicted_class_idx]
    
    # Print results
    print(f"\n🎯 Prediction Results:")
    print(f"   Class: {predicted_class}")
    print(f"   Confidence: {confidence:.2%}")
    
    print(f"\n📊 All class probabilities:")
    for idx, prob in enumerate(predictions):
        print(f"   {class_names[idx]}: {prob:.2%}")
    
    # Visualize
    if show_plot:
        plot_prediction(original_img, predicted_class, confidence, predictions, class_names)
    
    return predicted_class, confidence, predictions

def plot_prediction(image, predicted_class, confidence, predictions, class_names):
    """Visualize prediction results"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Show image
    ax1.imshow(image)
    ax1.axis('off')
    ax1.set_title(f'Predicted: {predicted_class}\nConfidence: {confidence:.2%}',
                  fontsize=12, fontweight='bold')
    
    # Show probability distribution
    class_labels = [class_names[i] for i in range(len(predictions))]
    colors = ['green' if i == np.argmax(predictions) else 'gray' 
              for i in range(len(predictions))]
    
    ax2.barh(class_labels, predictions, color=colors)
    ax2.set_xlabel('Probability')
    ax2.set_title('Class Probabilities')
    ax2.set_xlim([0, 1])
    
    # Add percentage labels
    for i, prob in enumerate(predictions):
        ax2.text(prob + 0.02, i, f'{prob:.1%}', va='center')
    
    plt.tight_layout()
    plt.show()

def batch_predict(model, class_names, image_directory):
    """Predict for all images in a directory"""
    
    image_dir = Path(image_directory)
    image_files = list(image_dir.glob('*.jpg')) + \
                  list(image_dir.glob('*.jpeg')) + \
                  list(image_dir.glob('*.png'))
    
    print(f"\n🔍 Found {len(image_files)} images in {image_directory}")
    
    results = []
    
    for img_path in image_files:
        predicted_class, confidence, _ = predict_image(model, class_names, img_path, show_plot=False)
        results.append({
            'image': img_path.name,
            'predicted_class': predicted_class,
            'confidence': float(confidence)
        })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Batch Prediction Summary")
    print("=" * 60)
    
    # Count predictions per class
    class_counts = {}
    for result in results:
        cls = result['predicted_class']
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    for cls, count in class_counts.items():
        print(f"   {cls}: {count} images")
    
    return results

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main prediction pipeline"""
    
    print("=" * 60)
    print("🚂 VGG Railway Component Classifier - Inference")
    print("=" * 60)
    
    # Load model
    model, class_names = load_model_and_classes()
    
    # Example usage
    print("\n" + "=" * 60)
    print("Usage Examples:")
    print("=" * 60)
    print("\n1. Single image prediction:")
    print("   predicted_class, confidence, probs = predict_image(")
    print("       model, class_names, 'path/to/image.jpg'")
    print("   )")
    
    print("\n2. Batch prediction:")
    print("   results = batch_predict(")
    print("       model, class_names, 'path/to/image/folder'")
    print("   )")
    
    print("\n" + "=" * 60)
    
    # Interactive mode
    print("\n💡 Enter image path to classify (or 'quit' to exit):")
    
    while True:
        user_input = input("\nImage path: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        image_path = Path(user_input)
        
        if not image_path.exists():
            print(f"❌ File not found: {image_path}")
            continue
        
        try:
            predict_image(model, class_names, image_path, show_plot=True)
        except Exception as e:
            print(f"❌ Error processing image: {e}")

if __name__ == "__main__":
    # Check if model exists
    if not Path(MODEL_PATH).exists():
        print(f"❌ Model not found: {MODEL_PATH}")
        print("\nPlease train the model first:")
        print("   1. python convert_to_classification.py")
        print("   2. python train_vgg_classification.py")
    else:
        main()
