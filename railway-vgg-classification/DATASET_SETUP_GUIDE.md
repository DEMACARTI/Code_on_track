# Railway Defect Dataset Setup Guide

## Quick Start

This guide will help you download and prepare a comprehensive dataset for railway component defect classification.

## Step 1: Setup Kaggle API (Required)

### 1.1 Get Your Kaggle API Token

1. **Go to Kaggle**: Visit https://www.kaggle.com/account
2. **Sign in** to your account (create one if needed - it's free!)
3. **Scroll down** to "API" section
4. **Click "Create New API Token"**
5. This will download `kaggle.json` to your computer

### 1.2 Install Kaggle Credentials

Run these commands in your terminal:

```bash
# Create kaggle directory
mkdir -p ~/.kaggle

# Move the downloaded kaggle.json file
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set proper permissions
chmod 600 ~/.kaggle/kaggle.json

# Verify installation
kaggle --version
```

## Step 2: Download Datasets

### Option A: Automatic Download (Recommended)

```bash
cd /Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification
python download_kaggle_datasets.py
```

This will download and organize:
- ✅ Surface crack detection dataset (20,000+ crack images)
- ✅ Railway track fault detection dataset  
- ✅ Metal surface defects (rust, corrosion)
- ✅ Steel defects (various types)

### Option B: Manual Download

If automatic download fails, manually download from Kaggle:

#### Dataset 1: Surface Crack Detection
```bash
kaggle datasets download -d arunrk7/surface-crack-detection
unzip surface-crack-detection.zip -d raw_datasets/cracks/
```
**URL**: https://www.kaggle.com/datasets/arunrk7/surface-crack-detection

#### Dataset 2: Railway Track Faults
```bash
kaggle datasets download -d kaustubhdikshit/railway-track-fault-detection
unzip railway-track-fault-detection.zip -d raw_datasets/railway_faults/
```
**URL**: https://www.kaggle.com/datasets/kaustubhdikshit/railway-track-fault-detection

#### Dataset 3: Metal Surface Defects
```bash
kaggle datasets download -d fantacher/neu-metal-surface-defects-data
unzip neu-metal-surface-defects-data.zip -d raw_datasets/metal_defects/
```
**URL**: https://www.kaggle.com/datasets/fantacher/neu-metal-surface-defects-data

#### Dataset 4: Steel Defects
```bash
kaggle datasets download -d ukveteran/surface-defects-in-steel
unzip surface-defects-in-steel.zip -d raw_datasets/steel_defects/
```
**URL**: https://www.kaggle.com/datasets/ukveteran/surface-defects-in-steel

## Step 3: Organize Dataset

After downloading, organize images into classification structure:

```bash
python download_kaggle_datasets.py
```

This creates:
```
railway_defect_dataset/
├── train/
│   ├── Rust/           (metal corrosion, oxidation)
│   ├── Crack/          (concrete/metal cracks)
│   ├── Broken/         (shattered components)
│   ├── Damaged/        (wear, deformation)
│   └── Normal/         (healthy components)
├── validation/
└── test/
```

## Step 4: Verify Dataset

Check dataset statistics:

```bash
python -c "
from pathlib import Path
dataset_dir = Path('railway_defect_dataset')
for split in ['train', 'validation', 'test']:
    print(f'\n{split.upper()}:')
    for class_dir in (dataset_dir / split).iterdir():
        if class_dir.is_dir():
            count = len(list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png')))
            print(f'  {class_dir.name}: {count} images')
"
```

## Step 5: Train Model

Once dataset is ready:

```bash
python train_vgg_classification.py
```

Expected training time:
- **Small dataset** (500 images): ~30 minutes
- **Medium dataset** (2000 images): ~1-2 hours  
- **Large dataset** (5000+ images): ~3-4 hours

## Alternative: Use Roboflow

If Kaggle doesn't work, use Roboflow:

### 1. Create Roboflow Account
- Visit: https://roboflow.com/
- Sign up for free account

### 2. Search for Datasets
Search for:
- "railway defects"
- "concrete cracks"
- "metal rust"
- "railway track faults"

### 3. Download via API
```python
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("workspace-name").project("project-name")
dataset = project.version(1).download("folder")
```

## Expected Dataset Size

### Minimum (for testing):
- Train: 250 images (50 per class)
- Validation: 50 images (10 per class)
- Test: 25 images (5 per class)
- **Total: 325 images**

### Recommended (for production):
- Train: 2500 images (500 per class)
- Validation: 500 images (100 per class)
- Test: 250 images (50 per class)
- **Total: 3250 images**

### Ideal (best performance):
- Train: 5000+ images (1000+ per class)
- Validation: 1000+ images (200+ per class)
- Test: 500+ images (100+ per class)
- **Total: 6500+ images**

## Troubleshooting

### Issue: "kaggle: command not found"

**Solution**: Install Kaggle API
```bash
pip install kaggle
```

### Issue: "403 Forbidden" error

**Solution**: 
1. Verify kaggle.json is in ~/.kaggle/
2. Check file permissions: `chmod 600 ~/.kaggle/kaggle.json`
3. Re-download API token from Kaggle

### Issue: "Dataset not found"

**Solution**: Dataset may be removed or renamed
- Search for alternative datasets on Kaggle
- Use Roboflow as backup

### Issue: Too few images in some classes

**Solution**: 
1. Download additional datasets for that class
2. Use aggressive data augmentation
3. Apply class weights during training
4. Consider combining similar classes

### Issue: Out of disk space

**Solution**:
- Each dataset is 500MB-2GB
- Need at least 10GB free space
- Clean up raw_datasets/ after organizing

## Dataset Quality Checklist

Before training, verify:

- [ ] All classes have at least 50 training images
- [ ] Images are clear and not corrupted
- [ ] No duplicate images across splits
- [ ] Labels are correct (spot check 10 images per class)
- [ ] Image sizes are reasonable (min 224x224 after resize)
- [ ] Lighting conditions vary across samples
- [ ] Different angles and perspectives included

## Next Steps After Download

1. **Verify Dataset**:
   ```bash
   ls -R railway_defect_dataset/
   ```

2. **Check Sample Images**:
   ```bash
   open railway_defect_dataset/train/Rust/  # macOS
   ```

3. **Train Model**:
   ```bash
   python train_vgg_classification.py
   ```

4. **Monitor Training**:
   ```bash
   tensorboard --logdir=railway_defect_output/logs
   ```

5. **Test Model**:
   ```bash
   python predict_vgg.py --image test_image.jpg
   ```

## Additional Datasets (Optional)

### RailSem19 Dataset
- **Description**: Railway scene understanding
- **Size**: 8500 images
- **URL**: https://wilddash.cc/railsem19

### NEU Surface Defect Database
- **Description**: Hot-rolled steel defects
- **Size**: 1800 images, 6 classes
- **Includes**: Crazing, inclusion, patches, pitted surface, rolled-in scale, scratches

### SDNET2018
- **Description**: Concrete crack dataset
- **Size**: 56,000+ images
- **URL**: https://data.lib.vt.edu/articles/dataset/SDNET2018_An_annotated_image_dataset_for_training_deep_learning_based_concrete_crack_detection/12097398

## Manual Dataset Creation

If downloads fail, create your own:

1. **Collect Images**: 
   - Use smartphone/camera
   - Download from Google Images (check licenses)
   - Extract frames from inspection videos

2. **Organize**:
   ```bash
   # Create structure
   mkdir -p railway_defect_dataset/{train,validation,test}/{Rust,Crack,Broken,Damaged,Normal}
   
   # Copy images to appropriate folders
   ```

3. **Label Consistently**:
   - Define clear criteria for each class
   - Have multiple people verify labels
   - Document edge cases

## Contact & Support

For issues with:
- **Dataset download**: Check Kaggle/Roboflow status pages
- **Script errors**: Review error messages, check Python version
- **Training issues**: See VGG_TRAINING_GUIDE.md

---

**Ready to start?** Run: `python download_kaggle_datasets.py`
