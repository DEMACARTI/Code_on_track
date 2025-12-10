# Quick Start Guide - VGG + Mobile App Integration

## 🚀 5-Minute Quick Start

### 1. Train Model (One-time, 1-2 hours)
```bash
cd railway-vgg-classification
python download_kaggle_datasets.py  # Setup Kaggle API first
python train_vgg_classification.py  # Train VGG model
```

### 2. Start Backend
```bash
cd mobile_backend
pip install -r requirements.txt
python main.py
```

### 3. Test Backend
```bash
cd mobile_backend
python test_ai_integration.py
```

### 4. Run Mobile App
```bash
cd SIH_app/flutter_sih_app
flutter pub get
flutter run
```

## 📱 User Flow in Mobile App

```
Login → Scan QR Code → Item Details Page
                           ↓
                    [AI Scan Button] 📷
                           ↓
                      Camera Opens
                           ↓
                    Capture Photo
                           ↓
                  AI Analyzing... 🔄
                           ↓
         ┌─────────────────┴─────────────────┐
         ↓                                   ↓
   Show Results                         Auto-Fill
   • Icon (🔴🔶⚠️🟡✅)                    • Remark
   • Class Name                           • Status
   • Confidence %                         ↓
   • Severity Level                  Submit ✅
```

## 🔌 API Endpoints

### Check Model Status
```bash
curl http://localhost:8000/api/model-status
```

### Classify Image
```bash
curl -X POST http://localhost:8000/api/classify-defect \
  -F "file=@image.jpg"
```

### Submit Inspection with AI
```bash
curl -X POST http://localhost:8000/qr/inspection-with-ai \
  -F "qr_id=RAIL-001" \
  -F "status=operational" \
  -F "remark=Inspected via AI" \
  -F "file=@photo.jpg"
```

## 🎯 What Each Defect Type Does

| AI Detects | Auto Status | Auto Remark | Icon |
|------------|-------------|-------------|------|
| **Rust** | needs_maintenance | "Component shows signs of rust/corrosion..." | 🔴 |
| **Crack** | damaged | "Crack detected in component..." | 🔶 |
| **Broken** | rejected | "Component is broken or severely damaged..." | ⚠️ |
| **Damaged** | damaged | "General damage/wear detected..." | 🟡 |
| **Normal** | operational | "Component appears to be in good condition..." | ✅ |

## 📊 Files Summary

### Backend Files
- `mobile_backend/main.py` - FastAPI server with VGG integration
- `mobile_backend/requirements.txt` - Python dependencies
- `mobile_backend/AI_INTEGRATION_GUIDE.md` - Complete documentation
- `mobile_backend/test_ai_integration.py` - Test script

### Mobile App Files
- `SIH_app/flutter_sih_app/lib/services/defect_classification_service.dart` - AI service
- `SIH_app/flutter_sih_app/lib/pages/item_details_page.dart` - Inspection UI

### VGG Model Files
- `railway-vgg-classification/train_vgg_classification.py` - Training script
- `railway-vgg-classification/railway_defect_output/best_model.keras` - Trained model

## 🐛 Common Issues

### Model Not Found
```
⚠️  Model not found at: .../best_model.keras
```
**Fix:** Train the model first with `python train_vgg_classification.py`

### Backend Not Running
```
Error: Connection refused
```
**Fix:** Start backend with `python main.py` in mobile_backend folder

### Camera Permission Denied
**Fix:** Add camera permissions to AndroidManifest.xml or Info.plist

### Low Confidence Predictions
**Fix:** Ensure good lighting, capture close-up photos, retrain with more data

## 📞 Testing Checklist

- [ ] Backend starts successfully
- [ ] Model loads (check logs for "✅ VGG model loaded")
- [ ] `/api/model-status` returns `model_loaded: true`
- [ ] Test script passes all tests
- [ ] Mobile app connects to backend
- [ ] Camera opens when clicking "AI Scan"
- [ ] Photo captures successfully
- [ ] AI returns classification result
- [ ] Remark auto-fills
- [ ] Status auto-updates
- [ ] Can submit inspection

## 🎉 Success Indicators

When everything is working:
1. Backend logs show: "✅ VGG model loaded successfully!"
2. Model status endpoint returns: `"model_loaded": true`
3. Test script shows: "✅ All tests passed!"
4. Mobile app shows AI results with confidence %
5. Inspection submits successfully with AI data

## 📚 Full Documentation

See `mobile_backend/AI_INTEGRATION_GUIDE.md` for complete details on:
- API endpoint specifications
- Deployment to production
- Security considerations
- Performance optimization
- Troubleshooting guide
