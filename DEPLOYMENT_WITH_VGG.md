# Mobile Backend Deployment Guide

## 🚀 Deploy VGG Model + Backend to Render

### Prerequisites
- Trained VGG model: `best_model.keras` (115 MB)
- GitHub repository updated with latest code
- Render account: https://render.com

---

## Step 1: Prepare Model for Deployment

The model file is too large for Git (115 MB). You have two options:

### Option A: Use Git LFS (Large File Storage) - Recommended
```bash
cd /Users/dakshrathore/Desktop/Code_on_track

# Install Git LFS
brew install git-lfs
git lfs install

# Track the model file
cd mobile_backend
git lfs track "best_model.keras"
git add .gitattributes
git add best_model.keras
git commit -m "Add VGG model with Git LFS"
git push origin daksh
```

### Option B: Download Model from External Storage
Upload `best_model.keras` to Google Drive/Dropbox and modify `main.py` to download it on startup.

---

## Step 2: Push Updated Code to GitHub

```bash
cd /Users/dakshrathore/Desktop/Code_on_track

# Add all changes
git add mobile_backend/
git add SIH_app/
git add railway-vgg-classification/

# Commit
git commit -m "Add trained VGG model and AI classification integration"

# Push to GitHub
git push origin daksh
```

---

## Step 3: Deploy to Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click existing service: `railchinh-mobile-backend`

2. **Trigger Manual Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Or go to Settings → "Redeploy"

3. **Monitor Deployment**
   - Watch logs for:
     - `Loading VGG model from: ...`
     - `✅ VGG model loaded successfully!`
   - Build time: ~5-10 minutes (TensorFlow installation)

4. **Verify Deployment**
   - Health: https://railchinh-mobile-backend.onrender.com/health
   - API Docs: https://railchinh-mobile-backend.onrender.com/docs
   - Model Status: https://railchinh-mobile-backend.onrender.com/api/model-status

---

## Step 4: Test AI Classification

### From Browser (Swagger UI)
1. Go to: https://railchinh-mobile-backend.onrender.com/docs
2. Test `/api/model-status` - should show `model_loaded: true`
3. Test `/api/classify-defect` - upload a railway defect image

### From Mobile App
1. Open app on phone
2. Scan QR code
3. Go to Item Details
4. Tap "AI Scan" button
5. Capture photo of railway component
6. See AI classification result!

---

## Troubleshooting

### Build Fails: Out of Memory
Render free tier has limited RAM. Solutions:
- Use smaller model (compress)
- Upgrade to paid tier ($7/mo)
- Use model quantization

### Model Not Loading
Check logs for:
```
⚠️  Model not found at: ...
```
Solution: Verify model file is in repository or download URL works

### Slow First Request
- Free tier: Cold starts take 30-60 seconds
- Model loads on first request
- Subsequent requests are fast

---

## Environment Variables (Already Set)

Your Render service should have these:
- `DATABASE_URL` - Supabase connection string
- `PYTHON_VERSION` - 3.11.0

---

## Cost Estimate

**Free Tier:**
- 750 hours/month free
- Slow cold starts
- 512 MB RAM

**Paid Tier ($7/mo):**
- No cold starts
- 512 MB RAM
- Better for production

---

## Next Steps After Deployment

1. ✅ Verify model loads in production
2. ✅ Test AI classification from mobile app
3. ✅ Monitor performance and accuracy
4. 📊 Collect real-world defect images to retrain model
5. 🔄 Iterate and improve classification accuracy

---

## Current Model Performance

- **Validation Accuracy:** 83.71%
- **Training Accuracy:** 92.74%
- **Precision:** 99.91%
- **Recall:** 90.41%
- **Classes:** Rust, Crack, Broken, Damaged, Normal
- **Training Images:** 2,629 real railway defect images

---

## Support

If deployment fails, check:
1. Render build logs
2. Application logs in Render dashboard
3. Model file size and format
4. TensorFlow installation in requirements.txt

