# 🚂 Railway Component Defect Classification

Complete VGG-based deep learning system for classifying defects in railway infrastructure components including rust, cracks, breakages, and general damage.

## 🎯 Classification Categories

| Class | Description | Examples | Severity |
|-------|-------------|----------|----------|
| 🔴 **Rust** | Metal corrosion and oxidation | Rusty rails, corroded fasteners | Medium-High |
| 🔶 **Crack** | Fractures in materials | Rail cracks, concrete fissures | High-Critical |
| ⚠️ **Broken** | Completely broken components | Shattered sleepers, fractured rails | Critical |
| 🟡 **Damaged** | Wear and deformation | Worn rubber, surface damage | Low-Medium |
| ✅ **Normal** | Healthy components | Good condition, no defects | None |

## 🚀 Quick Start

### Step 1: Setup Kaggle Credentials

```bash
# Get API token from: https://www.kaggle.com/account
# Click "Create New API Token"

# Install credentials
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 2: Download Datasets

```bash
cd /Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification

# Automatic download (recommended)
python download_kaggle_datasets.py
```

**Datasets Downloaded:**
- ✅ Surface Crack Detection (20,000+ images)
- ✅ Railway Track Faults
- ✅ Metal Surface Defects (rust, corrosion)
- ✅ Steel Surface Defects

### Step 3: Train Model

```bash
# Start training (1-2 hours)
python train_vgg_classification.py

# Monitor progress
tensorboard --logdir=railway_defect_output/logs
```

### Step 4: Test Predictions

```bash
# Single image
python predict_vgg.py --image path/to/test_image.jpg

# Batch prediction
python predict_vgg.py --folder path/to/images/
```

## 📁 Project Structure

```
railway-vgg-classification/
├── train_vgg_classification.py      # Main training script
├── predict_vgg.py                   # Inference script
├── download_kaggle_datasets.py      # Dataset downloader
├── generate_report.py               # Training report generator
│
├── railway_defect_dataset/          # Organized dataset
│   ├── train/                       # Training images (70%)
│   ├── validation/                  # Validation images (20%)
│   └── test/                        # Test images (10%)
│
├── railway_defect_output/           # Training outputs
│   ├── best_model.keras             # Best performing model
│   ├── final_model.keras            # Final trained model
│   ├── training_history.png         # Loss/accuracy plots
│   ├── confusion_matrix.png         # Confusion matrix
│   └── classification_report.txt    # Detailed metrics
│
└── docs/                            # Documentation
    ├── DATASET_SETUP_GUIDE.md       # Dataset download guide
    ├── RAILWAY_DEFECT_DATASET.md    # Dataset documentation
    └── VGG_TRAINING_GUIDE.md        # Training guide
```

## 🔧 Configuration

### Model Hyperparameters

```python
MODEL_TYPE = 'VGG16'          # or 'VGG19'
IMAGE_SIZE = (224, 224)       # Standard VGG input
BATCH_SIZE = 32               # Adjust for GPU memory
EPOCHS = 50                   # Per training phase
LEARNING_RATE = 0.0001        # Initial learning rate
```

### Training Strategy

**Phase 1: Transfer Learning (50 epochs)**
- Freeze VGG base layers
- Train classification head
- Learning rate: 0.0001

**Phase 2: Fine-Tuning (50 epochs)**
- Unfreeze top 4 layers
- Full model training
- Learning rate: 0.00001 (10x lower)

## 📊 Expected Performance

### Minimum Dataset Requirements
- **Training**: 250 images (50 per class)
- **Validation**: 50 images (10 per class)
- **Test**: 25 images (5 per class)

### Target Metrics
| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| Overall Accuracy | 75% | 85% | 92% |
| Precision (avg) | 70% | 80% | 90% |
| Recall (avg) | 70% | 80% | 90% |
| F1-Score (avg) | 70% | 80% | 90% |

## 🎓 Training Details

### Data Augmentation
```python
- Rotation: ±20°
- Width/Height Shift: ±20%
- Shear: ±20%
- Zoom: ±20%
- Horizontal Flip: Yes
- Fill Mode: Nearest
```

### Callbacks
- **ModelCheckpoint**: Save best model based on val_accuracy
- **EarlyStopping**: Stop if no improvement (patience=10)
- **ReduceLROnPlateau**: Reduce LR on plateau (patience=5, factor=0.5)

### Class Weights
Automatically calculated to handle class imbalance:
```python
class_weight = total_samples / (num_classes * class_count)
```

## 🔍 Model Architecture

```
Input (224x224x3)
    ↓
VGG16/VGG19 Base (pre-trained on ImageNet)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512, relu) + Dropout(0.5)
    ↓
Dense(256, relu) + Dropout(0.5)
    ↓
Dense(5, softmax) → [Rust, Crack, Broken, Damaged, Normal]
```

**Total Parameters:**
- VGG16: ~138M (base) + 1.3M (classifier) = 139.3M
- VGG19: ~144M (base) + 1.3M (classifier) = 145.3M

## 📈 Monitoring Training

### TensorBoard
```bash
tensorboard --logdir=railway_defect_output/logs
# Open: http://localhost:6006
```

### Training Outputs
- `training_history.png` - Loss/accuracy curves
- `confusion_matrix.png` - Class confusion visualization
- `classification_report.txt` - Per-class metrics
- `training_log.txt` - Epoch-by-epoch details

## 🚀 Deployment

### Export Formats

**1. Keras Model**
```python
model.save('model.keras')
```

**2. TensorFlow Lite (Mobile)**
```bash
python export_model.py --format tflite
# Output: model.tflite
```

**3. ONNX (Universal)**
```bash
python export_model.py --format onnx
# Output: model.onnx
```

### Inference Speed
- **CPU**: ~50-100ms per image
- **GPU**: ~5-10ms per image
- **TFLite (mobile)**: ~100-200ms per image

## 📝 Usage Examples

### Training
```python
# Basic training
python train_vgg_classification.py

# Custom configuration
python train_vgg_classification.py \
    --model VGG19 \
    --epochs 100 \
    --batch-size 64 \
    --learning-rate 0.0002
```

### Prediction
```python
# Single image with visualization
python predict_vgg.py --image rail_crack.jpg --visualize

# Batch processing
python predict_vgg.py \
    --folder inspection_images/ \
    --output predictions.csv \
    --confidence 0.8
```

### Python API
```python
from tensorflow import keras
import numpy as np
from PIL import Image

# Load model
model = keras.models.load_model('railway_defect_output/best_model.keras')

# Prepare image
img = Image.open('test.jpg').resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

# Predict
predictions = model.predict(img_array)
class_names = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']
predicted_class = class_names[np.argmax(predictions)]
confidence = np.max(predictions)

print(f"Prediction: {predicted_class} ({confidence:.2%})")
```

## 🛠️ Troubleshooting

### Issue: Low Accuracy (<70%)

**Solutions:**
- ✅ Increase dataset size (aim for 500+ images per class)
- ✅ Verify labels are correct
- ✅ Increase training epochs
- ✅ Try VGG19 instead of VGG16
- ✅ Adjust learning rate (try 0.0002 or 0.00005)

### Issue: Overfitting (train >> val accuracy)

**Solutions:**
- ✅ Increase dropout (0.6-0.7)
- ✅ Add more augmentation
- ✅ Use early stopping (patience=5)
- ✅ Reduce model complexity
- ✅ Get more training data

### Issue: Class Confusion (e.g., Rust ↔ Damaged)

**Solutions:**
- ✅ Clarify class definitions
- ✅ Review mislabeled images
- ✅ Balance dataset classes
- ✅ Increase class-specific samples
- ✅ Consider merging similar classes

### Issue: Out of Memory

**Solutions:**
- ✅ Reduce batch size (try 16 or 8)
- ✅ Use VGG16 instead of VGG19
- ✅ Reduce image size (try 128x128)
- ✅ Enable mixed precision training

## 📚 Documentation

- **[DATASET_SETUP_GUIDE.md](DATASET_SETUP_GUIDE.md)** - Complete dataset download guide
- **[RAILWAY_DEFECT_DATASET.md](RAILWAY_DEFECT_DATASET.md)** - Dataset documentation
- **[VGG_TRAINING_GUIDE.md](VGG_TRAINING_GUIDE.md)** - Detailed training guide

## 🔬 Advanced Features

### Custom Class Weights
```python
class_weights = {
    0: 1.5,  # Rust
    1: 2.0,  # Crack (more important)
    2: 2.5,  # Broken (critical)
    3: 1.0,  # Damaged
    4: 0.8   # Normal
}
```

### Mixed Precision Training
```python
from tensorflow.keras import mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)
```

### Learning Rate Scheduling
```python
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.0001,
    decay_steps=1000,
    decay_rate=0.96
)
```

## 🤝 Contributing

To improve the model:

1. **Add more training data** to railway_defect_dataset/
2. **Balance classes** (aim for equal samples per class)
3. **Verify labels** (review classification_report.txt for confused classes)
4. **Experiment with hyperparameters** (learning rate, batch size, epochs)
5. **Try different architectures** (ResNet, EfficientNet, MobileNet)

## 📊 Project Status

- ✅ Dataset structure created
- ✅ Synthetic dataset generated (325 images for testing)
- ⏳ Real dataset download (pending Kaggle credentials)
- ⏳ Model training (pending real dataset)
- ⏳ Model evaluation
- ⏳ Deployment preparation

## 🎯 Next Steps

1. **Setup Kaggle credentials** (see DATASET_SETUP_GUIDE.md)
2. **Download real datasets** (`python download_kaggle_datasets.py`)
3. **Verify dataset** (check image counts per class)
4. **Train model** (`python train_vgg_classification.py`)
5. **Evaluate results** (review confusion matrix and metrics)
6. **Deploy model** (export to TFLite for mobile)

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review documentation in `docs/` folder
- Verify dataset setup in DATASET_SETUP_GUIDE.md
- Check training guide in VGG_TRAINING_GUIDE.md

## 📄 License

Dataset components may have individual licenses. Check source datasets:
- Kaggle datasets: Individual dataset licenses apply
- Custom data: Specify your license terms

---

**Current Status**: Ready for real dataset download and training  
**Last Updated**: December 9, 2025  
**Model Type**: VGG16/VGG19 Transfer Learning  
**Framework**: TensorFlow 2.15+ / Keras 3.0+  
**Python**: 3.9+
