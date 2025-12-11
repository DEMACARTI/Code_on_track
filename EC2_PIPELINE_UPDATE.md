# EC2 Pipeline Update Guide

Quick guide to deploy the multi-model AI pipeline to your EC2 instance.

## Step 1: Connect to EC2
```bash
cd "/Users/dakshrathore/Documents/SIH 2025/AWS_Service"
ssh -i backendkey.pem ubuntu@16.171.32.31
```

## Step 2: Update Code from GitHub
```bash
cd ~/Code_on_track
git pull origin main
```

## Step 3: Install YOLO Dependencies (if not done)
```bash
cd ~/Code_on_track/mobile_backend
source venv/bin/activate
pip install ultralytics torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Step 4: Restart the Server
```bash
# Stop current process (Ctrl+C if running in foreground)
# Or if using systemd:
sudo systemctl restart railchinh

# Or run manually:
cd ~/Code_on_track/mobile_backend
source venv/bin/activate
python main.py --host 0.0.0.0 --port 8000
```

## Step 5: Verify Pipeline is Working
```bash
# On EC2:
curl http://localhost:8000/api/pipeline-status

# From local machine:
curl http://16.171.32.31:8000/api/pipeline-status
```

Expected response:
```json
{
  "available": true,
  "initialized": true,
  "detectors": {"erc": true, "sleeper": true},
  "classifiers": {"erc": false, "sleeper": false, "liner": false, "rubber_pad": false},
  "supported_components": ["erc", "sleeper"]
}
```

## Quick One-Liner Update
Run this on EC2 to do everything in one command:
```bash
cd ~/Code_on_track && git pull && cd mobile_backend && source venv/bin/activate && sudo systemctl restart railchinh
```

## Troubleshooting

### Model Not Found
Upload models manually:
```bash
# From local terminal:
scp -i backendkey.pem /Users/dakshrathore/Desktop/Code_on_track/railway-yolo-detection/models/sleeper_best.pt ubuntu@16.171.32.31:~/Code_on_track/railway-yolo-detection/models/
```

### Check Logs
```bash
sudo journalctl -u railchinh -f
```

### Memory Issues
If the server crashes, increase swap:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```
