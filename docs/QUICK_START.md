# Quick Start Guide

## Railway QR Code Tracking System

### Prerequisites Checklist
- [ ] Node.js 16+ installed (`node --version`)
- [ ] MongoDB 5+ installed (`mongod --version`)
- [ ] npm installed (`npm --version`)
- [ ] Git installed (`git --version`)

---

## Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/DEMACARTI/Code_on_track.git
cd Code_on_track

# Run automated setup
chmod +x setup.sh
./setup.sh

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Start MongoDB
mongod

# Start backend (in new terminal)
cd backend
npm start

# Start web portal (in new terminal)
cd frontend
npm run dev

# Start mobile app (in new terminal)
cd mobile
npx expo start
```

---

## Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install

# Mobile
cd ../mobile
npm install

# QR Generation
cd ../qr-generation
npm install
```

### Step 2: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/railway_qr_system
LLM_API_KEY=your_api_key_here  # Optional for development
LLM_MODEL=gpt-3.5-turbo
```

### Step 3: Start Services

**Terminal 1 - Database:**
```bash
mongod
```

**Terminal 2 - Backend:**
```bash
cd backend
npm start
# Server runs on http://localhost:5000
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
# Web portal runs on http://localhost:3000
```

**Terminal 4 - Mobile:**
```bash
cd mobile
npx expo start
# Scan QR code with Expo Go app
```

---

## Verify Installation

### Test Backend API

```bash
curl http://localhost:5000/health
# Expected: {"status":"OK","message":"Railway QR System API is running"}
```

### Test QR Generation

```bash
curl -X POST http://localhost:5000/api/qr/generate \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"info": "Test QR"},
    "materialType": "metal",
    "dimensions": {"width": 50, "height": 50, "unit": "mm"},
    "location": {"station": "Test Station", "platform": "1"}
  }'
```

### Access Web Portal

Open browser: `http://localhost:3000`

### Test Mobile App

1. Install Expo Go on your phone
2. Scan QR code from terminal
3. App should open on your device

---

## Common Issues & Solutions

### MongoDB Connection Error
```bash
# Make sure MongoDB is running
mongod

# Or check if it's already running
ps aux | grep mongod
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process if needed
kill -9 <PID>
```

### Module Not Found
```bash
# Re-install dependencies
rm -rf node_modules package-lock.json
npm install
```

### Expo Not Starting
```bash
# Clear Expo cache
npx expo start -c
```

---

## Development Workflow

### 1. Backend Development
```bash
cd backend
npm run dev  # Uses nodemon for auto-reload
```

### 2. Frontend Development
```bash
cd frontend
npm run dev  # Vite hot reload enabled
```

### 3. Mobile Development
```bash
cd mobile
npx expo start
# Press 'r' to reload
# Press 'm' to toggle menu
```

---

## Testing

### Backend Tests
```bash
cd backend
npm test
```

### Linting
```bash
cd backend
npm run lint
```

---

## API Testing

### Using cURL

**Generate QR Code:**
```bash
curl -X POST http://localhost:5000/api/qr/generate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Get All QR Codes:**
```bash
curl http://localhost:5000/api/qr
```

**Scan QR Code:**
```bash
curl -X POST http://localhost:5000/api/qr/{qrId}/scan \
  -H "Content-Type: application/json" \
  -d '{"scannedBy": "user1", "deviceId": "device001"}'
```

### Using Postman

Import the API endpoints:
- Base URL: `http://localhost:5000/api`
- All endpoints documented in `docs/README.md`

---

## Production Deployment

### Environment Setup
```bash
# Set production environment variables
export NODE_ENV=production
export MONGODB_URI=mongodb+srv://...
export LLM_API_KEY=sk-...
```

### Build Frontend
```bash
cd frontend
npm run build
# Output in frontend/dist
```

### Build Mobile
```bash
cd mobile
expo build:android  # For Android
expo build:ios      # For iOS
```

---

## Monitoring

### Check Logs
```bash
# Backend logs
cd backend
tail -f logs/app.log

# Database status
mongo
> show dbs
> use railway_qr_system
> db.stats()
```

### Performance
```bash
# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/health
```

---

## Backup & Recovery

### Backup Database
```bash
mongodump --db railway_qr_system --out backup/
```

### Restore Database
```bash
mongorestore --db railway_qr_system backup/railway_qr_system
```

---

## Next Steps

1. ✅ Complete setup
2. ✅ Test all endpoints
3. ✅ Explore web portal
4. ✅ Try mobile app
5. 📝 Customize for your needs
6. 🚀 Deploy to production

---

## Getting Help

- **Documentation**: See `docs/README.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Implementation**: See `docs/IMPLEMENTATION_SUMMARY.md`
- **Issues**: Check GitHub issues

---

## Success Indicators

✅ MongoDB connected
✅ Backend API responding
✅ Web portal accessible
✅ Mobile app scanning
✅ QR codes generating
✅ Data saving to database
✅ LLM insights working (if API key provided)

---

**You're all set! 🎉**

The Railway QR Code Tracking System is now running locally.
