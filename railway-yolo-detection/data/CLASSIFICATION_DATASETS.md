# Railway Component Classification Datasets

This guide explains how to set up classification datasets for training ResNet50 classifiers for each railway component.

## Dataset Structure

Each component needs its own classification dataset organized as:

```
data/{component}_classification/
├── train/
│   ├── good/         # Good condition images
│   ├── worn/         # Worn/degraded images
│   ├── damaged/      # Damaged images
│   └── {other_classes}/
└── valid/
    ├── good/
    ├── worn/
    └── ...
```

## Current Datasets

| Component | Dataset | Status |
|-----------|---------|--------|
| **Sleeper** | `sleeper_classification/` | ✅ 1,000 images (Kaggle) |
| Liner | `liner_classification/` | ⏳ Needs images |
| Rubber Pad | `rubber_pad_classification/` | ⏳ Needs images |

## How to Add Images

### Option 1: Manual Collection
1. Take photos of each component in different conditions
2. Sort into appropriate folders (good, worn, damaged, etc.)
3. Aim for 100+ images per class for good results

### Option 2: Kaggle/Roboflow
Search for:
- "railway liner defect"
- "rail pad classification"
- "track fastener dataset"

### Option 3: Use Track Fault Detection Dataset
The Kaggle "Railway Track Fault Detection" dataset can be adapted:
- Defective → damaged class
- Non-defective → good class

## Training

Once you have images in the folders, run:

```bash
# Train Liner classifier
python scripts/train_component_classifier.py \
    --component liner \
    --data_dir data/liner_classification \
    --epochs 30

# Train Rubber Pad classifier
python scripts/train_component_classifier.py \
    --component rubber_pad \
    --data_dir data/rubber_pad_classification \
    --epochs 30
```

## Recommended Classes

### Liner
- `good` - Normal condition
- `worn` - Surface wear
- `damaged` - Cracks, breaks
- `missing` - Not present

### Rubber Pad
- `good` - Normal condition
- `cracked` - Visible cracks
- `degraded` - Material degradation
- `worn` - Compression damage

## Output

After training, models are saved to:
- `models/liner_classifier_best.pt`
- `models/rubber_pad_classifier_best.pt`
