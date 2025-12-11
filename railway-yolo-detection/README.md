# Railway Component Object Detection with YOLOv8

Detect 4 railway track components using YOLOv8 object detection.

## Classes
1. **elastic_clip** - Spring clip holding rails to sleepers
2. **liner** - Metal plate between rail and sleeper  
3. **rubber_pad** - Rubber cushion for vibration dampening
4. **sleeper** - Concrete/wooden cross-tie

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Dataset
```bash
python scripts/download_dataset.py
```

### 3. Train Model
```bash
python scripts/train_yolo.py
```

### 4. Run Inference
```bash
python scripts/predict.py --source test_images/ --weights models/best.pt
```

## Project Structure
```
railway-yolo-detection/
├── data/
│   ├── images/{train,val}/
│   ├── labels/{train,val}/
│   └── data.yaml
├── models/
│   └── best.pt
├── scripts/
│   ├── download_dataset.py
│   ├── train_yolo.py
│   ├── predict.py
│   └── evaluate.py
├── requirements.txt
└── README.md
```

## API Integration

After training, the model is integrated into the mobile backend:
- `POST /api/detect-components` - Detect components in uploaded image

## Performance

| Metric | Target |
|--------|--------|
| mAP@50 | > 75% |
| mAP@50-95 | > 55% |
| Inference | < 50ms |
