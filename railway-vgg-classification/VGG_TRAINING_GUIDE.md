# VGG Classification Training Guide

Complete guide for training VGG-based image classification models for railway component condition assessment.

## 🎯 Overview

This approach uses **Transfer Learning with VGG** models (VGG16/VGG19) to classify railway components into different condition categories.

### YOLO vs VGG Comparison

| Aspect | YOLO (Object Detection) | VGG (Classification) |
|--------|------------------------|----------------------|
| **Goal** | Locate and classify defects | Classify overall component condition |
| **Output** | Bounding boxes + labels | Single class label per image |
| **Input** | Full images with multiple objects | Pre-cropped component images |
| **Labels** | Requires bbox coordinates | Requires folder-based organization |
| **Use Case** | Finding defects in images | Determining component health status |

## 📊 Dataset Preparation

### Step 1: Convert YOLO to Classification Format

Your Railway-2 YOLO dataset needs to be converted to classification format:

```bash
python convert_to_classification.py
```

This creates:
```
Railway-2-classification/
├── train/
│   ├── Faulty/
│   │   ├── image_001.jpg
│   │   └── ...
│   └── Normal/
│       ├── image_101.jpg
│       └── ...
└── validation/
    ├── Faulty/
    └── Normal/
```

### Step 2: Manual Dataset Organization (Optional)

For multi-class classification (Rusted, Cracked, Broken, Normal):

```
railway_components/
├── train/
│   ├── Normal/
│   ├── Rusted/
│   ├── Cracked/
│   ├── Broken/
│   └── Damaged/
└── validation/
    ├── Normal/
    ├── Rusted/
    ├── Cracked/
    ├── Broken/
    └── Damaged/
```

**Recommended split:**
- Training: 70-80%
- Validation: 15-20%
- Test: 10-15%

## 🧠 Model Architecture

### VGG16 (Recommended for starting)
- **Layers:** 16 weight layers (13 conv + 3 FC)
- **Parameters:** ~138M (base) + custom head
- **Speed:** Fast
- **Accuracy:** Good

### VGG19 (For higher accuracy)
- **Layers:** 19 weight layers (16 conv + 3 FC)
- **Parameters:** ~144M (base) + custom head
- **Speed:** Slightly slower
- **Accuracy:** Better

### Custom Classification Head
```
VGG Base (frozen/fine-tuned)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512, ReLU) + Dropout(0.5)
    ↓
Dense(256, ReLU) + Dropout(0.3)
    ↓
Dense(num_classes, Softmax)
```

## 🚀 Training Pipeline

### Two-Phase Training

#### Phase 1: Feature Extraction
- **Freeze** all VGG base layers
- Train only the custom classification head
- Learn to use pre-trained features
- Fast training (~10-20 epochs)

#### Phase 2: Fine-Tuning
- **Unfreeze** top 4 layers of VGG
- Train with lower learning rate
- Adapt features to railway components
- Better accuracy (~20-30 epochs)

### Training Script

```bash
python train_vgg_classification.py
```

### Configuration Options

Edit `train_vgg_classification.py`:

```python
# Model selection
MODEL_TYPE = 'VGG16'  # or 'VGG19'

# Training parameters
EPOCHS = 50
BATCH_SIZE = 32
LEARNING_RATE = 0.0001

# Fine-tuning
FREEZE_BASE = True
UNFREEZE_LAYERS = 4
```

## 📈 Expected Results

### Typical Performance (Railway Components)

| Metric | Phase 1 (Frozen) | Phase 2 (Fine-tuned) |
|--------|------------------|----------------------|
| Training Accuracy | 85-90% | 92-96% |
| Validation Accuracy | 80-85% | 88-94% |
| Training Time | 15-25 min | 20-35 min |

### Good Results Indicators
- ✅ Val accuracy > 85%
- ✅ Small gap between train/val accuracy
- ✅ Precision and recall > 0.80
- ✅ Low loss values (< 0.5)

### Warning Signs
- ⚠️ Val accuracy < 70%
- ⚠️ Large train/val gap (overfitting)
- ⚠️ Loss not decreasing
- ⚠️ Precision/recall imbalance

## 📊 Output Files

Training generates:

```
runs/vgg_classification/
├── best_model_initial.keras          # Best model from Phase 1
├── best_model_fine_tuned.keras       # Best model from Phase 2
├── final_model.keras                 # Final trained model
├── model.tflite                      # TensorFlow Lite (mobile)
├── training_history_initial.png      # Phase 1 metrics plots
├── training_history_fine_tuned.png   # Phase 2 metrics plots
├── confusion_matrix.png              # Confusion matrix
├── classification_report.txt         # Detailed metrics
└── class_indices.json                # Class mapping
```

## 🔮 Inference / Prediction

### Single Image Prediction

```python
from predict_vgg import load_model_and_classes, predict_image

# Load model
model, class_names = load_model_and_classes()

# Predict
predicted_class, confidence, probs = predict_image(
    model, 
    class_names, 
    'path/to/railway_component.jpg'
)

print(f"Prediction: {predicted_class} ({confidence:.2%})")
```

### Batch Prediction

```python
from predict_vgg import batch_predict

results = batch_predict(
    model,
    class_names,
    'path/to/image/folder'
)

# Results is a list of dictionaries:
# [{'image': 'img1.jpg', 'predicted_class': 'Rusted', 'confidence': 0.92}, ...]
```

### Interactive Mode

```bash
python predict_vgg.py
```

Enter image paths to get instant predictions with visualization.

## 🎨 Data Augmentation

Automatic augmentation applied during training:

- **Rotation:** ±20 degrees
- **Width/Height shift:** 20%
- **Shear:** 20%
- **Zoom:** 20%
- **Horizontal flip:** Yes
- **Rescaling:** 0-1 normalization

This helps the model generalize to various conditions:
- Different angles
- Various lighting
- Different positions
- Mirrored components

## 🔧 Troubleshooting

### Issue: Low Accuracy

**Solutions:**
1. Check data quality and labels
2. Increase epochs (50-100)
3. Use VGG19 instead of VGG16
4. Collect more training data
5. Adjust augmentation parameters

### Issue: Overfitting

**Symptoms:** Train accuracy >> Val accuracy

**Solutions:**
1. Increase dropout rates (0.5 → 0.6)
2. Add more augmentation
3. Use smaller learning rate
4. Collect more validation data
5. Reduce model complexity

### Issue: Training Too Slow

**Solutions:**
1. Reduce batch size
2. Use VGG16 instead of VGG19
3. Reduce image size (224 → 160)
4. Enable GPU acceleration
5. Use fewer epochs for Phase 1

### Issue: Class Imbalance

**Symptoms:** Poor performance on minority classes

**Solutions:**
1. Use class weights:
   ```python
   from sklearn.utils.class_weight import compute_class_weight
   
   class_weights = compute_class_weight(
       'balanced',
       classes=np.unique(train_labels),
       y=train_labels
   )
   ```
2. Oversample minority classes
3. Undersample majority classes
4. Use focal loss instead of categorical crossentropy

## 📱 Deployment

### TensorFlow Lite (Mobile/Edge)

```python
import tensorflow as tf

# Convert model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### TensorFlow.js (Web)

```bash
pip install tensorflowjs

tensorflowjs_converter \
    --input_format=keras \
    final_model.keras \
    web_model/
```

### ONNX (Universal)

```python
import tf2onnx

spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
output_path = "model.onnx"

model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec)
with open(output_path, "wb") as f:
    f.write(model_proto.SerializeToString())
```

## 🎯 Best Practices

### Data Collection
- ✅ Balanced classes (similar number of samples)
- ✅ High-quality images (clear, well-lit)
- ✅ Diverse conditions (angles, lighting, distances)
- ✅ Consistent image quality

### Training
- ✅ Start with frozen base (Phase 1)
- ✅ Monitor val_loss for early stopping
- ✅ Use learning rate scheduling
- ✅ Save checkpoints regularly

### Validation
- ✅ Keep validation set separate
- ✅ Test on unseen data
- ✅ Check confusion matrix
- ✅ Verify per-class performance

### Deployment
- ✅ Test on real-world images
- ✅ Measure inference time
- ✅ Consider model compression
- ✅ Monitor model performance

## 📚 Further Improvements

### Advanced Techniques
1. **Ensemble Models:** Combine VGG16 + VGG19
2. **Attention Mechanisms:** Focus on important regions
3. **Multi-Task Learning:** Classify + localize simultaneously
4. **Self-Supervised Learning:** Use unlabeled data
5. **Test-Time Augmentation:** Average predictions over augmented versions

### Alternative Architectures
- **ResNet50/101:** Better for deeper networks
- **EfficientNet:** Better accuracy/speed tradeoff
- **MobileNet:** Faster inference for edge devices
- **Vision Transformer:** State-of-the-art accuracy

## 🔗 Resources

- [VGG Paper](https://arxiv.org/abs/1409.1556)
- [Transfer Learning Guide](https://www.tensorflow.org/tutorials/images/transfer_learning)
- [Keras Documentation](https://keras.io/api/applications/vgg/)
- [Image Classification Best Practices](https://www.tensorflow.org/tutorials/images/classification)

---

**Ready to train?**

```bash
# 1. Convert dataset
python convert_to_classification.py

# 2. Train model
python train_vgg_classification.py

# 3. Make predictions
python predict_vgg.py
```

Good luck! 🚂✨
