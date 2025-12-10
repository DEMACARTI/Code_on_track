# Railway Component Defect Classification Dataset

## Overview
Multi-class classification dataset for detecting various types of defects in railway components including tracks, sleepers, fasteners, and other infrastructure elements.

## Classification Categories

### 1. **Rust** 🔴
- **Description**: Corrosion and oxidation on metal components
- **Examples**:
  - Rusty rails
  - Corroded fasteners
  - Oxidized metal connectors
  - Surface rust on steel components
- **Severity**: Medium to High
- **Impact**: Structural weakness, reduced lifespan

### 2. **Crack** 🔶
- **Description**: Fractures and cracks in concrete, metal, or composite materials
- **Examples**:
  - Rail cracks (transverse, longitudinal)
  - Concrete sleeper cracks
  - Fractured fasteners
  - Cement component fissures
- **Severity**: High to Critical
- **Impact**: Safety hazard, potential failure

### 3. **Broken** ⚠️
- **Description**: Completely broken or shattered components
- **Examples**:
  - Broken sleepers
  - Shattered fasteners
  - Fractured rails
  - Destroyed insulators
- **Severity**: Critical
- **Impact**: Immediate safety risk, requires urgent replacement

### 4. **Damaged** 🟡
- **Description**: General damage including wear, deformation, and discrepancies
- **Examples**:
  - Worn rubber components
  - Deformed fasteners
  - Surface wear on rails
  - Discrepancies in rubber pads
  - Misaligned components
- **Severity**: Low to Medium
- **Impact**: Requires monitoring, planned maintenance

### 5. **Normal** ✅
- **Description**: Components in good condition without defects
- **Examples**:
  - Healthy rails
  - Intact sleepers
  - Well-maintained fasteners
  - Clean rubber components
- **Severity**: None
- **Impact**: No action required

## Dataset Structure

```
railway_defect_dataset/
├── train/
│   ├── Rust/           # Training images of rusty components
│   ├── Crack/          # Training images of cracked components
│   ├── Broken/         # Training images of broken components
│   ├── Damaged/        # Training images of damaged components
│   └── Normal/         # Training images of normal components
├── validation/
│   ├── Rust/
│   ├── Crack/
│   ├── Broken/
│   ├── Damaged/
│   └── Normal/
└── test/
    ├── Rust/
    ├── Crack/
    ├── Broken/
    ├── Damaged/
    └── Normal/
```

## Data Sources

### Roboflow Datasets
1. **Railway Component Detection**
   - Workspace: `xyz-rf6um`
   - Project: `railway-bnznt`
   - Version: 2
   - Original format: Object detection (converted to classification)

### Kaggle Datasets
1. **Surface Crack Detection**
   - Dataset: `arunrk7/surface-crack-detection`
   - Focus: Concrete cracks
   - Classes: Positive (crack), Negative (no crack)

2. **Steel Defect Detection** (Recommended)
   - Dataset: `ukveteran/surface-defects-in-steel`
   - Types: Crazing, inclusion, patches, pitted surface, rolled-in scale, scratches

3. **Railway Track Fault Detection** (Recommended)
   - Search: "railway track defects" on Kaggle
   - Includes various fault types

### Additional Sources
- **RailSem19**: Railway scene understanding dataset
- **Open Rail Data Portal**: Real-world railway infrastructure images
- **Custom collected data**: Field inspection images

## Dataset Preparation Steps

### 1. Download Datasets
```bash
python download_railway_datasets.py
```

This script will:
- Download from Roboflow using API key
- Attempt to download Kaggle datasets (requires `kaggle.json` credentials)
- Organize images into classification structure

### 2. Manual Dataset Enhancement

If automatic downloads fail or you want to add custom data:

1. **Collect images** from various sources
2. **Organize** into respective class folders
3. **Ensure proper split**:
   - Training: 70% (minimum 100 images per class)
   - Validation: 20% (minimum 20 images per class)
   - Test: 10% (minimum 10 images per class)

### 3. Data Augmentation

The training script automatically applies augmentation:
- Rotation: ±20 degrees
- Width/Height shift: ±20%
- Shear: ±20%
- Zoom: ±20%
- Horizontal flip
- Fill mode: Nearest

### 4. Image Requirements

- **Format**: JPG, JPEG, PNG
- **Size**: Automatically resized to 224×224
- **Color**: RGB (3 channels)
- **Quality**: Minimum 480p recommended
- **Variety**: Different lighting, angles, distances

## Dataset Statistics (Target)

### Minimum Recommended Size
| Split      | Rust | Crack | Broken | Damaged | Normal | Total |
|------------|------|-------|--------|---------|--------|-------|
| Train      | 100  | 100   | 100    | 100     | 100    | 500   |
| Validation | 20   | 20    | 20     | 20      | 20     | 100   |
| Test       | 10   | 10    | 10     | 10      | 10     | 50    |
| **Total**  | 130  | 130   | 130    | 130     | 130    | **650** |

### Ideal Dataset Size
| Split      | Rust | Crack | Broken | Damaged | Normal | Total  |
|------------|------|-------|--------|---------|--------|--------|
| Train      | 500  | 500   | 500    | 500     | 500    | 2,500  |
| Validation | 100  | 100   | 100    | 100     | 100    | 500    |
| Test       | 50   | 50    | 50     | 50      | 50     | 250    |
| **Total**  | 650  | 650   | 650    | 650     | 650    | **3,250** |

## Class Balance Considerations

### Handling Imbalanced Data

1. **Class Weights**: Automatically calculated in training script
   ```python
   class_weights = {
       0: total_samples / (num_classes * rust_count),
       1: total_samples / (num_classes * crack_count),
       ...
   }
   ```

2. **Oversampling Minority Classes**: Use `ImageDataGenerator`
3. **Focal Loss**: For heavily imbalanced datasets
4. **Synthetic Data**: Create augmented samples for rare classes

## Validation Guidelines

### Quality Checks

1. **Image Clarity**: No blurry or corrupted images
2. **Correct Labeling**: Verify each class folder contains correct defect type
3. **No Duplicates**: Remove duplicate images across splits
4. **Consistent Perspective**: Similar viewing angles across classes
5. **Lighting Consistency**: Balanced lighting conditions

### Manual Review

```bash
# View sample images from each class
python -c "
from PIL import Image
from pathlib import Path
import random

dataset_dir = Path('railway_defect_dataset/train')
for class_dir in dataset_dir.iterdir():
    if class_dir.is_dir():
        images = list(class_dir.glob('*.jpg'))
        if images:
            sample = random.choice(images)
            Image.open(sample).show()
            print(f'{class_dir.name}: {len(images)} images')
"
```

## Training Recommendations

### Model Selection
- **VGG16**: Faster training, 138M parameters, good for smaller datasets
- **VGG19**: Better accuracy, 144M parameters, requires more data

### Hyperparameters
```python
BATCH_SIZE = 32           # Adjust based on GPU memory
EPOCHS = 50               # Phase 1: frozen base
FINE_TUNE_EPOCHS = 50     # Phase 2: unfrozen layers
LEARNING_RATE = 0.0001    # Phase 1
FINE_TUNE_LR = 0.00001    # Phase 2 (10x lower)
```

### Expected Performance

| Metric          | Minimum | Good | Excellent |
|-----------------|---------|------|-----------|
| Overall Accuracy| 75%     | 85%  | 92%       |
| mAP50          | 70%     | 80%  | 90%       |
| Precision (avg) | 70%     | 80%  | 90%       |
| Recall (avg)    | 70%     | 80%  | 90%       |

## Deployment

### Model Export Formats
1. **Keras**: `.keras` for TensorFlow applications
2. **TFLite**: `.tflite` for mobile/edge devices
3. **ONNX**: `.onnx` for cross-framework compatibility
4. **SavedModel**: TensorFlow serving format

### Inference Speed
- **CPU**: ~50-100ms per image
- **GPU**: ~5-10ms per image
- **TFLite (mobile)**: ~100-200ms per image

## Usage Example

### Training
```bash
# 1. Download datasets
python download_railway_datasets.py

# 2. Verify dataset structure
ls -R railway_defect_dataset/

# 3. Train model
python train_vgg_classification.py

# 4. Monitor training
tensorboard --logdir=railway_defect_output/logs
```

### Inference
```bash
# Single image prediction
python predict_vgg.py --image path/to/image.jpg

# Batch prediction
python predict_vgg.py --folder path/to/images/

# Export model
python export_model.py --format tflite
```

## Known Issues & Solutions

### Issue 1: Insufficient Data
**Solution**: Use data augmentation aggressively, consider transfer learning from larger datasets

### Issue 2: Class Imbalance
**Solution**: Apply class weights, oversample minority classes, use focal loss

### Issue 3: Overfitting
**Solution**: Increase dropout (0.5-0.7), add more augmentation, reduce model complexity

### Issue 4: Poor Crack Detection
**Solution**: Add edge detection preprocessing, use attention mechanisms, collect more crack samples

### Issue 5: Rust vs Damaged Confusion
**Solution**: Create clearer class definitions, add intermediate classes, use multi-label classification

## Citation

If using this dataset structure or methodology, please cite:

```bibtex
@dataset{railway_defect_classification_2024,
  title={Railway Component Defect Classification Dataset},
  author={Railway Inspection Team},
  year={2024},
  note={Multi-class classification for railway infrastructure defects}
}
```

## License

Dataset components may have individual licenses. Check source datasets:
- Roboflow: Check workspace license
- Kaggle: Individual dataset licenses apply
- Custom data: Specify your license terms

## Contact & Contributions

For dataset issues, contributions, or questions:
- Add more diverse samples to underrepresented classes
- Report labeling errors
- Suggest new defect categories
- Share preprocessing techniques

---

**Last Updated**: December 9, 2025  
**Version**: 1.0  
**Status**: Ready for training with minimum dataset size
