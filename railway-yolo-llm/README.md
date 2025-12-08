# Railway Component Detection - YOLO v11 + LLM Pipeline

Automated railway component inspection system using YOLOv11 for defect detection and LLM-based report generation.

## 🚂 Overview

This pipeline detects defects in railway components (tracks, sleepers, fasteners, clips) using computer vision and generates human-readable inspection reports with maintenance priorities.

**Pipeline Flow:**
```
Images → YOLO Detection → JSON Output → LLM Report Generation
```

## 📋 Features

- **YOLOv11 Object Detection**: State-of-the-art defect detection
- **Apple Silicon Optimized**: Uses MPS acceleration on macOS
- **Multi-Class Detection**: Cracks, loose bolts, missing clips, corrosion, wear, deformation
- **Confidence Filtering**: Configurable thresholds for detection vs. reporting
- **Priority Classification**: HIGH/MEDIUM/LOW severity assignment
- **Dual Report Formats**: Text and HTML reports
- **Annotated Images**: Visual output with bounding boxes

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- macOS with Apple Silicon (or NVIDIA GPU/CPU)

### Setup

1. **Activate virtual environment:**
```bash
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download YOLO model** (optional - auto-downloads on first run):
```bash
# YOLOv11 nano model (fast, good for real-time)
# Will be downloaded automatically as yolo11n.pt

# Or use your custom trained model by placing it in this directory
```

## 📂 Directory Structure

```
railway-yolo-llm/
├── venv/                          # Python virtual environment
├── images/                        # Input images (add your inspection photos here)
├── runs/detect/railway_inspection # Output annotated images
├── run_yolo.py                    # YOLO detection script
├── generate_report.py             # Report generation script
├── yolo_output.json              # Detection results (generated)
├── inspection_report.txt         # Text report (generated)
├── inspection_report.html        # HTML report (generated)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Usage

### Step 1: Add Images

Place railway component images in the `images/` directory:
```bash
# Supported formats: .jpg, .jpeg, .png
cp /path/to/your/photos/*.jpg images/
```

### Step 2: Run YOLO Detection

```bash
python run_yolo.py
```

**Output:**
- `yolo_output.json` - Structured detection data
- `runs/detect/railway_inspection/` - Annotated images with bounding boxes

**Sample Console Output:**
```
==============================================================
Railway Component YOLO Detection Pipeline
==============================================================

Found 15 image(s) to process
Loading YOLO model from yolo11n.pt...
Model loaded successfully. Classes: {...}

Running detection on images in images/
Confidence threshold: 0.25
Device: mps

✓ Detection results saved to yolo_output.json
  Total images processed: 15
  Total detections: 23

Detection Summary by Class:
----------------------------------------
  crack: 5
  loose_bolt: 8
  missing_clip: 3
  corrosion: 7

==============================================================
✓ Detection complete! Results saved to: yolo_output.json
✓ Annotated images saved to: runs/detect/railway_inspection/
==============================================================
```

### Step 3: Generate Reports

```bash
python generate_report.py
```

**Output:**
- `inspection_report.txt` - Human-readable text report
- `inspection_report.html` - Formatted HTML report

**Sample Report:**
```
================================================================================
RAILWAY COMPONENT INSPECTION REPORT
================================================================================
Inspection Date: 2025-01-20T15:30:45
Total Images Analyzed: 15
Total Detections: 23
Model Used: yolo11n.pt
================================================================================

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
High-Confidence Defects Detected: 18
  - High Priority Issues: 5
  - Medium Priority Issues: 8
  - Low Priority Issues: 5

DETAILED FINDINGS
--------------------------------------------------------------------------------

Image: track_section_01.jpg
  Defects Found: 3

  [1] CRACK (Priority: HIGH)
      Confidence: 85.3%
      Description: Crack detected in component
      Location: bbox(245, 120, 380, 210)

  [2] LOOSE_BOLT (Priority: MEDIUM)
      Confidence: 72.1%
      Description: Loose or missing bolt/fastener
      Location: bbox(450, 300, 520, 365)

--------------------------------------------------------------------------------
MAINTENANCE RECOMMENDATIONS
--------------------------------------------------------------------------------

⚠️  URGENT: 5 high-priority issue(s) require immediate attention!
   - Schedule emergency maintenance within 24 hours
   - Consider track closure if safety is compromised

⚠️  8 medium-priority issue(s) detected
   - Schedule maintenance within 7 days
   - Monitor condition closely

================================================================================
END OF REPORT
================================================================================
```

## ⚙️ Configuration

### Detection Settings (`run_yolo.py`)

```python
MODEL_PATH = 'yolo11n.pt'          # Model file (yolo11n/yolo11s/yolo11m/custom.pt)
IMAGE_DIR = 'images'                # Input image directory
OUTPUT_JSON = 'yolo_output.json'    # Detection results file
CONFIDENCE_THRESHOLD = 0.25         # Detection threshold (lower = more detections)
DEVICE = 'mps'                      # 'mps' (Apple Silicon) / 'cuda' (NVIDIA) / 'cpu'
```

### Report Settings (`generate_report.py`)

```python
INPUT_JSON = 'yolo_output.json'           # Detection results input
OUTPUT_REPORT = 'inspection_report.txt'   # Text report output
OUTPUT_HTML = 'inspection_report.html'    # HTML report output

# Confidence threshold for reporting (filter low-confidence detections)
REPORT_CONFIDENCE = 0.60  # Only report detections ≥60% confidence

# Priority/Severity mapping
SEVERITY_MAP = {
    'crack': 'HIGH',
    'missing_clip': 'HIGH',
    'deformation': 'HIGH',
    'loose_bolt': 'MEDIUM',
    'loose_fastener': 'MEDIUM',
    'corrosion': 'MEDIUM',
    'wear': 'LOW'
}
```

## 🎯 Defect Classes

| Class | Description | Default Priority |
|-------|-------------|------------------|
| `crack` | Structural cracks in rails, sleepers | HIGH |
| `missing_clip` | Missing rail clips | HIGH |
| `deformation` | Bent or deformed components | HIGH |
| `loose_bolt` | Loose or missing bolts | MEDIUM |
| `loose_fastener` | Loose fastening components | MEDIUM |
| `corrosion` | Rust or corrosion damage | MEDIUM |
| `wear` | Surface wear and tear | LOW |

## 🔧 Custom Model Training

To train a custom YOLO model for your specific railway components:

1. **Collect and label images** using tools like [Label Studio](https://labelstud.io/) or [Roboflow](https://roboflow.com/)

2. **Export in YOLO format** (txt annotations)

3. **Create dataset YAML:**
```yaml
# dataset.yaml
train: /path/to/train/images
val: /path/to/val/images
nc: 7  # Number of classes
names: ['crack', 'loose_bolt', 'missing_clip', 'loose_fastener', 'corrosion', 'deformation', 'wear']
```

4. **Train the model:**
```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolo11n.pt')

# Train on custom dataset
model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device='mps'  # or 'cuda' or 'cpu'
)
```

5. **Use trained model:**
```python
# In run_yolo.py
MODEL_PATH = 'runs/detect/train/weights/best.pt'
```

## 📊 Performance

### YOLOv11 Model Comparison

| Model | Size (MB) | mAP | Speed (ms) | Use Case |
|-------|-----------|-----|------------|----------|
| yolo11n | 6.2 | 37.3 | 1.5 | Real-time, edge devices |
| yolo11s | 21.5 | 44.9 | 2.3 | Balanced speed/accuracy |
| yolo11m | 49.7 | 49.7 | 4.2 | High accuracy needed |
| yolo11l | 86.7 | 52.9 | 6.7 | Maximum accuracy |

### Hardware Acceleration

- **Apple Silicon (M1/M2/M3)**: Use `device='mps'` (5-10x faster than CPU)
- **NVIDIA GPU**: Use `device='cuda'` (10-50x faster than CPU)
- **CPU Only**: Use `device='cpu'` (slowest but works everywhere)

## 🐛 Troubleshooting

### Issue: No images found
```
❌ Error: No images found in 'images/' directory!
```
**Solution:** Add .jpg, .jpeg, or .png images to the `images/` folder

### Issue: Model not found
```
❌ Error loading model: [Errno 2] No such file or directory: 'yolo11n.pt'
```
**Solution:** The model will auto-download on first run. Ensure internet connection.

### Issue: MPS device not available
```
RuntimeError: MPS device not available
```
**Solution:** Change `DEVICE = 'cpu'` in `run_yolo.py` (for non-Apple Silicon Macs)

### Issue: Low detection accuracy
**Solutions:**
- Ensure good image quality (min 640px resolution)
- Adjust `CONFIDENCE_THRESHOLD` (lower = more detections)
- Train custom model on your specific railway images
- Use larger model (yolo11s/yolo11m instead of yolo11n)

### Issue: Too many false positives in report
**Solution:** Increase `REPORT_CONFIDENCE` threshold in `generate_report.py` (e.g., 0.70 or 0.80)

## 🔮 Future Enhancements

- [ ] Real-time video processing
- [ ] GPS/location tagging for defects
- [ ] Integration with maintenance management systems
- [ ] Mobile app for field inspections
- [ ] Multi-language report generation
- [ ] Automated email/SMS alerts for high-priority defects
- [ ] Historical defect tracking and trend analysis
- [ ] Integration with LLM APIs (OpenAI GPT-4, Claude) for enhanced reports

## 📝 License

This project is for educational and research purposes. Ensure compliance with railway safety regulations in your jurisdiction before production deployment.

## 🤝 Contributing

To improve the detection pipeline:
1. Add more defect classes to `DEFECT_CLASSES`
2. Adjust priority mappings in `SEVERITY_MAP`
3. Train custom models on your railway infrastructure
4. Enhance report formatting and recommendations

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review YOLO documentation: https://docs.ultralytics.com
- Inspect `yolo_output.json` for detection details

---

**⚡ Quick Start:**
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Add images
cp your_photos/*.jpg images/

# 3. Run detection
python run_yolo.py

# 4. Generate report
python generate_report.py

# 5. View results
open inspection_report.html
```
