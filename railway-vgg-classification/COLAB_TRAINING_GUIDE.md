# Google Colab Training Guide

## Why Use Google Colab?

- **FREE GPU access** (NVIDIA T4 GPU)
- **10-15x faster** than MacBook Air M1 (2-3 hours vs 30 hours)
- **No local resource usage** - your laptop stays free
- **Better for experimentation** - restart anytime without losing progress

## Step-by-Step Instructions

### 1. Prepare Your Dataset

First, zip your dataset on your local machine:

```bash
cd /Users/dakshrathore/Desktop/Code_on_track/railway-vgg-classification
zip -r railway_defect_dataset.zip railway_defect_dataset/
```

This will create `railway_defect_dataset.zip` (~200-300 MB).

### 2. Open Google Colab

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Sign in with your Google account
3. Click **File → Upload notebook**
4. Upload `train_vgg_colab.ipynb` from this folder

### 3. Enable GPU

**CRITICAL STEP - Don't skip this!**

1. Click **Runtime** → **Change runtime type**
2. Hardware accelerator: Select **T4 GPU** (or GPU if T4 not available)
3. Click **Save**

You should see "GPU" badge in the top-right corner.

### 4. Upload Dataset

Run the first few cells until you reach the upload cell. You have two options:

**Option A: Direct Upload (Recommended for < 500 MB)**
- Run the upload cell
- Select your `railway_defect_dataset.zip` file
- Wait for upload to complete

**Option B: Google Drive (Recommended for > 500 MB)**
- Upload `railway_defect_dataset.zip` to your Google Drive
- Mount Drive in Colab (run the mount cell)
- Copy from Drive:
  ```python
  !cp /content/drive/MyDrive/railway_defect_dataset.zip /content/
  ```

### 5. Run All Cells

1. Click **Runtime → Run all**
2. Approve any permission requests
3. Watch the training progress!

### 6. Monitor Training

The notebook will show:
- Real-time training progress bars
- Accuracy/loss metrics after each epoch
- Training visualizations
- Estimated time remaining

**Expected training time:**
- Phase 1 (50 epochs): ~1.5-2 hours
- Phase 2 (30 epochs fine-tuning): ~1 hour
- **Total: ~2.5-3 hours**

### 7. Download Your Model

After training completes, the notebook will automatically:
1. Create a zip file with all outputs
2. Trigger a download to your computer

The zip contains:
- `best_model_initial.keras` - Phase 1 model
- `best_model_finetuned.keras` - **Final model (use this one)**
- `class_indices.json` - Class mapping
- `training_history_phase1.png` - Phase 1 plots
- `training_history_phase2.png` - Phase 2 plots

### 8. Use the Model Locally

Extract the downloaded zip and copy the model:

```bash
cd ~/Downloads
unzip railway_defect_output.zip
cd railway_defect_output
cp best_model_finetuned.keras ~/Desktop/Code_on_track/mobile_backend/best_model.keras
```

Test it:

```bash
cd ~/Desktop/Code_on_track
python3 test_rust_comprehensive.py
```

## Tips & Tricks

### ⚡️ Speed Optimizations Already Included

The notebook includes:
- **Mixed precision training** (2x faster)
- **Increased batch size** (64 vs 32)
- **GPU-optimized data loading**
- **Efficient callbacks**

### 💰 Free Tier Limits

Google Colab Free has limits:
- **12 hours max runtime** (plenty for this training)
- **GPU usage limited** (but resets daily)
- **Can disconnect** if inactive (notebook keeps running)

### 🔄 If Training Disconnects

If your browser disconnects but training continues:
1. Reconnect to Colab
2. Check the output - training likely continued
3. Run the download cell again to get results

### 📊 Save to Google Drive (Optional)

To save models directly to Drive (no download needed):

Add this cell after training:
```python
# Save to Google Drive
!cp -r /content/railway_defect_output/ /content/drive/MyDrive/
print("✅ Model saved to Google Drive")
```

### 🧪 Test Model in Colab (Optional)

Add this cell to test the model before downloading:

```python
# Test a single image
from PIL import Image
import numpy as np

# Upload test image
uploaded = files.upload()
img_path = list(uploaded.keys())[0]

# Load and predict
img = Image.open(img_path).resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

predictions = best_model.predict(img_array)
class_names = ['Broken', 'Crack', 'Damaged', 'Normal', 'Rust']
predicted_class = class_names[np.argmax(predictions[0])]
confidence = np.max(predictions[0]) * 100

print(f"Predicted: {predicted_class} ({confidence:.2f}%)")
for i, name in enumerate(class_names):
    print(f"  {name}: {predictions[0][i]*100:.2f}%")
```

## Troubleshooting

### "No GPU available"
- Make sure you selected GPU in Runtime → Change runtime type
- Free GPU may be unavailable - try again in a few hours
- Consider Colab Pro ($10/month) for guaranteed GPU

### "Runtime disconnected"
- Training likely continued - reconnect and check outputs
- Enable "Reconnect automatically" in settings
- Keep the browser tab active

### "Out of memory"
- Reduce BATCH_SIZE to 32 or 16
- Restart runtime and run again

### Upload fails / slow upload
- Use Google Drive method instead
- Compress dataset more (reduce image quality slightly)
- Split dataset into smaller zips

## Performance Comparison

| Platform | Hardware | Time | Cost |
|----------|----------|------|------|
| MacBook Air M1 | CPU (8-core) | ~30 hours | Free |
| Google Colab Free | T4 GPU | ~2.5 hours | Free |
| Google Colab Pro | T4/V100 GPU | ~1.5 hours | $10/month |
| AWS/GCP | V100 GPU | ~1 hour | ~$2-3/run |

**Recommendation**: Use Google Colab Free - best balance of speed and cost!

## Next Steps

After downloading your trained model:

1. **Test rust detection**: Run `test_rust_comprehensive.py`
2. **Deploy to mobile_backend**: Copy model to backend folder
3. **Push to Render**: Commit and push to trigger deployment
4. **Test in production**: Upload rust images via your app

## Questions?

Common issues:
- Model accuracy low? Check dataset balance and augmentation
- Overfitting? Increase dropout or reduce epochs
- Underfitting? Train longer or increase model complexity

Enjoy your **10x faster training**! 🚀
