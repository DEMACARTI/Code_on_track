#!/bin/bash
# ============================================================================
# RailChinh Mobile Backend - EC2 Deployment Script
# Run this script on your EC2 instance after SSH login
# ============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🚀 RailChinh EC2 Deployment Script"
echo "=============================================="

# Step 1: Update system
echo ""
echo "📦 Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install Python and dependencies
echo ""
echo "🐍 Step 2: Installing Python and system dependencies..."
sudo apt install -y python3-pip python3-venv git libgl1-mesa-glx libglib2.0-0

# Step 3: Clone repository
echo ""
echo "📂 Step 3: Cloning repository..."
cd ~
if [ -d "Code_on_track" ]; then
    echo "   Repository already exists, pulling latest..."
    cd Code_on_track
    git pull origin main
else
    git clone https://github.com/DEMACARTI/Code_on_track.git
    cd Code_on_track
fi

# Step 4: Setup virtual environment
echo ""
echo "🔧 Step 4: Setting up virtual environment..."
cd mobile_backend
python3 -m venv venv
source venv/bin/activate

# Step 5: Install Python dependencies
echo ""
echo "📚 Step 5: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Install PyTorch (CPU version) first
echo ""
echo "🤖 Step 6: Installing PyTorch (CPU version)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Step 6b: Install YOLO (from regular PyPI)
echo ""
echo "🤖 Step 6b: Installing Ultralytics YOLO..."
pip install ultralytics

# Step 7: Verify model files exist
echo ""
echo "✅ Step 7: Verifying model files..."
if [ -f "../railway-yolo-detection/models/best.pt" ]; then
    echo "   ✅ YOLO model found: railway-yolo-detection/models/best.pt"
else
    echo "   ⚠️  YOLO model not found! You may need to upload it."
fi

# Step 8: Create systemd service
echo ""
echo "⚙️  Step 8: Creating systemd service..."
sudo tee /etc/systemd/system/railchinh.service > /dev/null <<EOF
[Unit]
Description=RailChinh Mobile Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Code_on_track/mobile_backend
Environment="PATH=/home/ubuntu/Code_on_track/mobile_backend/venv/bin"
ExecStart=/home/ubuntu/Code_on_track/mobile_backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable railchinh

# Step 9: Start the service
echo ""
echo "🚀 Step 9: Starting RailChinh service..."
sudo systemctl start railchinh

# Wait for startup
sleep 3

# Step 10: Verify
echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo "=============================================="
echo ""
echo "📊 Service Status:"
sudo systemctl status railchinh --no-pager | head -10
echo ""
echo "🌐 Your API is now available at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo ""
echo "📋 Useful Commands:"
echo "   Check status:  sudo systemctl status railchinh"
echo "   View logs:     sudo journalctl -u railchinh -f"
echo "   Restart:       sudo systemctl restart railchinh"
echo "   Stop:          sudo systemctl stop railchinh"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
