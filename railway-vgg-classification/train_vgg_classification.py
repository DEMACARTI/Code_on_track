"""
VGG-based Railway Component Classification
Transfer Learning approach for classifying railway component conditions
Classes: Normal, Rusted, Cracked, Broken, Faulty
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16, VGG19
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Dataset paths - Update this to your classification dataset
DATASET_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_dataset')
TRAIN_DIR = DATASET_DIR / 'train'
VAL_DIR = DATASET_DIR / 'validation'

# Model configuration
MODEL_TYPE = 'VGG16'  # Options: 'VGG16', 'VGG19'
IMAGE_SIZE = (224, 224)  # Standard VGG input size
BATCH_SIZE = 32
EPOCHS = 50

# Training parameters
LEARNING_RATE = 0.0001
FREEZE_BASE = True  # Freeze pre-trained layers initially
UNFREEZE_LAYERS = 4  # Number of top layers to unfreeze for fine-tuning

# Output directory
OUTPUT_DIR = Path('/Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification/railway_defect_output')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA PREPARATION
# ============================================================================

def create_data_generators():
    """Create data generators with augmentation"""
    
    print("\n" + "=" * 80)
    print("📦 Creating Data Generators")
    print("=" * 80)
    
    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Validation data (only rescaling)
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    # Load validation data
    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    # Print dataset info
    print(f"\n✅ Dataset loaded successfully:")
    print(f"   Training samples: {train_generator.samples}")
    print(f"   Validation samples: {val_generator.samples}")
    print(f"   Number of classes: {len(train_generator.class_indices)}")
    print(f"   Classes: {list(train_generator.class_indices.keys())}")
    print(f"   Image size: {IMAGE_SIZE}")
    print(f"   Batch size: {BATCH_SIZE}")
    
    # Save class indices
    class_indices = train_generator.class_indices
    with open(OUTPUT_DIR / 'class_indices.json', 'w') as f:
        json.dump(class_indices, f, indent=2)
    
    return train_generator, val_generator, class_indices

# ============================================================================
# MODEL BUILDING
# ============================================================================

def build_vgg_model(num_classes, model_type='VGG16'):
    """Build VGG model with transfer learning"""
    
    print("\n" + "=" * 80)
    print(f"🧠 Building {model_type} Model")
    print("=" * 80)
    
    # Load pre-trained VGG model
    if model_type == 'VGG16':
        base_model = VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=(*IMAGE_SIZE, 3)
        )
    else:
        base_model = VGG19(
            weights='imagenet',
            include_top=False,
            input_shape=(*IMAGE_SIZE, 3)
        )
    
    print(f"\n✅ Loaded pre-trained {model_type} from ImageNet")
    print(f"   Base model layers: {len(base_model.layers)}")
    
    # Freeze base model layers
    if FREEZE_BASE:
        base_model.trainable = False
        print(f"   🔒 Frozen all base layers")
    
    # Build classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    print(f"\n📋 Model Architecture:")
    print(f"   Input: {IMAGE_SIZE} RGB images")
    print(f"   Base: {model_type} (pre-trained)")
    print(f"   Classification head: GlobalAvgPool → Dense(512) → Dense(256) → Dense({num_classes})")
    print(f"   Output: {num_classes} classes (softmax)")
    
    return model, base_model

# ============================================================================
# TRAINING
# ============================================================================

def calculate_class_weights(train_gen):
    """Calculate class weights to handle imbalanced dataset"""
    from sklearn.utils.class_weight import compute_class_weight
    
    print("\n" + "=" * 80)
    print("⚖️  Calculating Class Weights for Imbalanced Dataset")
    print("=" * 80)
    
    # Count samples per class
    class_counts = {}
    for class_name, class_idx in train_gen.class_indices.items():
        class_dir = TRAIN_DIR / class_name
        count = len(list(class_dir.glob('*.jpg')))
        class_counts[class_name] = count
    
    print("\nClass distribution:")
    total_samples = sum(class_counts.values())
    for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_samples) * 100
        print(f"  {class_name:10s}: {count:5d} ({percentage:5.2f}%)")
    
    # Calculate class weights
    class_labels = [train_gen.class_indices[name] for name in class_counts.keys()]
    class_counts_list = [class_counts[name] for name in class_counts.keys()]
    
    weights = compute_class_weight(
        class_weight='balanced',
        classes=np.array(class_labels),
        y=np.repeat(class_labels, class_counts_list)
    )
    
    class_weight_dict = {i: w for i, w in enumerate(weights)}
    
    print("\nCalculated class weights:")
    for class_name, class_idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
        print(f"  {class_name:10s}: {class_weight_dict[class_idx]:.4f}")
    
    return class_weight_dict

def train_model(model, train_gen, val_gen, class_weights=None, phase='initial'):
    """Train the model"""
    
    print("\n" + "=" * 80)
    print(f"🚀 Starting Training - Phase: {phase}")
    print("=" * 80)
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    # Callbacks
    checkpoint = ModelCheckpoint(
        OUTPUT_DIR / f'best_model_{phase}.keras',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
    
    callbacks = [checkpoint, early_stop, reduce_lr]
    
    # Train with class weights
    if class_weights:
        print("\n⚖️  Training with class weights to handle imbalance")
    
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    return history

def fine_tune_model(model, base_model, train_gen, val_gen, class_weights=None):
    """Fine-tune the model by unfreezing top layers"""
    
    print("\n" + "=" * 80)
    print("🔧 Fine-Tuning Model")
    print("=" * 80)
    
    # Unfreeze top layers
    base_model.trainable = True
    
    # Freeze all layers except the top ones
    for layer in base_model.layers[:-UNFREEZE_LAYERS]:
        layer.trainable = False
    
    trainable_count = sum([1 for layer in base_model.layers if layer.trainable])
    print(f"\n🔓 Unfrozen top {trainable_count} layers of base model")
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    # Train again with class weights
    history = train_model(model, train_gen, val_gen, class_weights=class_weights, phase='fine_tuned')
    
    return history

# ============================================================================
# EVALUATION AND VISUALIZATION
# ============================================================================

def plot_training_history(history, phase='initial'):
    """Plot training metrics"""
    
    print(f"\n📊 Plotting training history...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Train Accuracy')
    axes[0, 0].plot(history.history['val_accuracy'], label='Val Accuracy')
    axes[0, 0].set_title('Model Accuracy')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Loss
    axes[0, 1].plot(history.history['loss'], label='Train Loss')
    axes[0, 1].plot(history.history['val_loss'], label='Val Loss')
    axes[0, 1].set_title('Model Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Precision
    axes[1, 0].plot(history.history['precision'], label='Train Precision')
    axes[1, 0].plot(history.history['val_precision'], label='Val Precision')
    axes[1, 0].set_title('Model Precision')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Precision')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Recall
    axes[1, 1].plot(history.history['recall'], label='Train Recall')
    axes[1, 1].plot(history.history['val_recall'], label='Val Recall')
    axes[1, 1].set_title('Model Recall')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Recall')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f'training_history_{phase}.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {OUTPUT_DIR / f'training_history_{phase}.png'}")
    plt.close()

def evaluate_model(model, val_gen, class_indices):
    """Evaluate model on validation set"""
    
    print("\n" + "=" * 80)
    print("📊 Model Evaluation")
    print("=" * 80)
    
    # Evaluate
    results = model.evaluate(val_gen, verbose=1)
    
    print(f"\n📈 Final Validation Metrics:")
    print(f"   Loss: {results[0]:.4f}")
    print(f"   Accuracy: {results[1]:.4f}")
    print(f"   Precision: {results[2]:.4f}")
    print(f"   Recall: {results[3]:.4f}")
    
    # Generate predictions for confusion matrix
    val_gen.reset()
    predictions = model.predict(val_gen, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = val_gen.classes
    
    # Confusion matrix
    from sklearn.metrics import confusion_matrix, classification_report
    import seaborn as sns
    
    cm = confusion_matrix(true_classes, predicted_classes)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_indices.keys(),
                yticklabels=class_indices.keys())
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f"\n   ✅ Saved: {OUTPUT_DIR / 'confusion_matrix.png'}")
    plt.close()
    
    # Classification report
    class_names = list(class_indices.keys())
    report = classification_report(true_classes, predicted_classes, 
                                   target_names=class_names, digits=4)
    print(f"\n📋 Classification Report:")
    print(report)
    
    # Save report
    with open(OUTPUT_DIR / 'classification_report.txt', 'w') as f:
        f.write(report)
    
    return results

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main training pipeline"""
    
    print("=" * 80)
    print("🚂 VGG Railway Component Classification")
    print("=" * 80)
    
    # Check dataset
    if not TRAIN_DIR.exists():
        print(f"\n❌ Training directory not found: {TRAIN_DIR}")
        print("\nExpected structure:")
        print("Railway-2-classification/")
        print("├── train/")
        print("│   ├── Normal/")
        print("│   ├── Faulty/")
        print("│   └── ...")
        print("└── validation/")
        print("    ├── Normal/")
        print("    ├── Faulty/")
        print("    └── ...")
        return
    
    # Create data generators
    train_gen, val_gen, class_indices = create_data_generators()
    num_classes = len(class_indices)
    
    # Build model
    model, base_model = build_vgg_model(num_classes, MODEL_TYPE)
    
    # Calculate class weights for imbalanced dataset
    class_weights = calculate_class_weights(train_gen)
    
    # Print model summary
    print("\n" + "=" * 80)
    print("Model Summary")
    print("=" * 80)
    model.summary()
    
    # Phase 1: Train with frozen base
    print("\n" + "=" * 80)
    print("Phase 1: Training with frozen base layers")
    print("=" * 80)
    history1 = train_model(model, train_gen, val_gen, class_weights=class_weights, phase='initial')
    plot_training_history(history1, phase='initial')
    
    # Phase 2: Fine-tune
    print("\n" + "=" * 80)
    print("Phase 2: Fine-tuning top layers")
    print("=" * 80)
    history2 = fine_tune_model(model, base_model, train_gen, val_gen, class_weights=class_weights)
    plot_training_history(history2, phase='fine_tuned')
    
    # Final evaluation
    evaluate_model(model, val_gen, class_indices)
    
    # Save final model
    final_model_path = OUTPUT_DIR / 'final_model.keras'
    model.save(final_model_path)
    print(f"\n✅ Final model saved: {final_model_path}")
    
    # Save model in TensorFlow Lite format
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    tflite_path = OUTPUT_DIR / 'model.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"✅ TFLite model saved: {tflite_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("🎉 Training Complete!")
    print("=" * 80)
    print(f"\n📁 Results saved to: {OUTPUT_DIR}")
    print(f"\n📊 Files generated:")
    print(f"   - best_model_initial.keras")
    print(f"   - best_model_fine_tuned.keras")
    print(f"   - final_model.keras")
    print(f"   - model.tflite")
    print(f"   - training_history_*.png")
    print(f"   - confusion_matrix.png")
    print(f"   - classification_report.txt")
    print(f"   - class_indices.json")
    
    print("\n🚀 Next steps:")
    print("   1. Review training plots and metrics")
    print("   2. Test model on new images")
    print("   3. Deploy using TFLite for mobile/edge devices")
    print("=" * 80)

if __name__ == "__main__":
    main()
