# System Integration Guide

## ✅ Database Setup Complete

All three applications are now connected to Supabase PostgreSQL database:

### Database Connection
- **Host**: `aws-1-ap-northeast-2.pooler.supabase.com`
- **Port**: `6543` (Transaction Pooler)
- **Database**: `postgres`
- **Status**: ✅ Active and working

### Applications Connected

1. **App_a** (FastAPI - IRF Backend)
   - Port: 8000
   - Tables Created: `items`, `engraving_queue`, `engraving_history`
   - Connected: ✅

2. **website_backend** (FastAPI - Main Backend)
   - Port: 8001
   - Tables Created: `users`, `items`, `vendors`, `engrave_jobs`, `events`, `item_vendor`
   - Connected: ✅

3. **Flutter App** (Mobile Frontend)
   - Needs Configuration: 🔧

---

## 🔧 Flutter App Configuration

### Current Status
The Flutter app is using **Mock Services**. To connect it to your live backend:

### Option 1: Connect to App_a (Port 8000)
This backend handles:
- QR code generation
- Item creation
- Engraving queue management

**Update `lib/main.dart`:**
```dart
// Replace this:
final authService = MockAuthService();
final qrService = MockQRScanService();

// With this:
const String backendBaseUrl = 'http://YOUR_IP_ADDRESS:8000';
final authService = RestAuthService(baseUrl: backendBaseUrl);
final qrService = RestQRScanService(baseUrl: backendBaseUrl);
```

### Option 2: Connect to website_backend (Port 8001)
This backend handles:
- User authentication
- Full CRUD operations
- Advanced features

**Update `lib/main.dart`:**
```dart
const String backendBaseUrl = 'http://YOUR_IP_ADDRESS:8001';
final authService = RestAuthService(baseUrl: backendBaseUrl);
final qrService = RestQRScanService(baseUrl: backendBaseUrl);
```

### Getting Your IP Address
```bash
# On macOS:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Use the IP that starts with 192.168 or 10.
```

---

## 🚀 Starting the Services

### 1. Start App_a Backend
```bash
cd /Users/dakshrathore/Desktop/Code_on_track/App_a
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**API Endpoints:**
- `POST /api/items` - Create items with QR codes
- `POST /api/engrave` - Add to engraving queue
- `GET /api/engrave/queue` - Get queue status
- `GET /api/items/{uid}/engraving-status` - Check engraving status

### 2. Start website_backend
```bash
cd /Users/dakshrathore/Desktop/Code_on_track/website_backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**API Endpoints:**
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/items` - Create items
- `GET /api/v1/items` - List all items
- `GET /api/v1/dashboard/stats` - Dashboard statistics

### 3. Run Flutter App
```bash
cd /Users/dakshrathore/Desktop/Code_on_track/SIH_app/flutter_sih_app
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home
flutter run
```

---

## 📊 Database Schema

### Shared Tables
Both backends can access these tables in Supabase:

**items** table:
- `id` - Primary key
- `uid` - Unique identifier (IRF-XXX-XXX-XXX)
- `component_type` - Component category
- `lot_number` - Lot/batch number
- `vendor_id` - Associated vendor
- `qr_image_url` - QR code image URL
- `current_status` - Current status
- `metadata` - JSON additional data

**users** table (website_backend):
- `id` - Primary key
- `username` - Unique username
- `email` - User email
- `hashed_password` - Encrypted password
- `role` - User role (admin/user/technician)
- `is_active` - Account status

**engraving_queue** table (App_a):
- `id` - Primary key
- `item_uid` - Foreign key to items
- `status` - pending/in_progress/completed/failed
- `svg_url` - SVG file for engraving
- `attempts` - Retry count

---

## 🔐 Default Admin User

**website_backend** creates a default admin user:

- **Email**: `admin@example.com`
- **Password**: `admin1234`
- **Role**: ADMIN

Use these credentials to log in through the Flutter app (if connected to website_backend).

---

## 🧪 Testing the Integration

### Test 1: Database Connection
```bash
# Test App_a connection
cd /Users/dakshrathore/Desktop/Code_on_track/App_a
python -c "from app.database import engine; conn = engine.connect(); print('✅ App_a connected'); conn.close()"

# Test website_backend connection
cd /Users/dakshrathore/Desktop/Code_on_track/website_backend
python -c "from app.database import engine; conn = engine.connect(); print('✅ website_backend connected'); conn.close()"
```

### Test 2: Create an Item (App_a)
```bash
curl -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "component_type": "EC",
    "lot_number": "LOT001",
    "quantity": 1,
    "vendor_id": 1,
    "warranty_years": 5,
    "qr_size": "250x250"
  }'
```

### Test 3: Login (website_backend)
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin1234"
```

---

## 📱 Flutter App Endpoints Needed

The Flutter app should implement these service methods:

### AuthService
- `login(email, password)` → `POST /api/v1/auth/login`
- `getCurrentUser()` → `GET /api/v1/users/me`

### QRScanService
- `scanQR(uid)` → `GET /api/v1/items/{uid}`
- `getItemDetails(uid)` → `GET /api/v1/items/{uid}`
- `updateItemStatus(uid, status)` → `PUT /api/v1/items/{uid}`

---

## 🔄 API Coordination

### Recommended Setup
- **Flutter App** → **website_backend** (Port 8001)
  - Handles authentication
  - User management
  - Item viewing and updates
  
- **website_backend** → **App_a** (Internal calls)
  - QR code generation
  - Engraving operations

### Alternative Setup (Direct)
- **Flutter App** → **App_a** (Port 8000)
  - Simple QR generation and tracking
  - No authentication required
  - Direct engraving queue access

---

## 📝 Next Steps

1. **Choose Backend**: Decide if Flutter connects to App_a or website_backend
2. **Update Flutter Config**: Edit `lib/main.dart` with correct base URL
3. **Start Backends**: Run both backend services
4. **Test Flutter App**: Run on emulator or physical device
5. **Verify Integration**: Test login, QR scanning, and data flow

---

## ⚠️ Important Notes

- Both backends share the same Supabase database
- Make sure not to run migrations that conflict
- App_a port: 8000, website_backend port: 8001
- Flutter needs network access to backend (use your machine's IP, not localhost)
- For WiFi debugging, ensure phone and computer are on same network

---

## 🆘 Troubleshooting

### "Connection refused" on Flutter
- Check backend is running: `curl http://localhost:8000/health`
- Use computer's IP address, not `localhost` or `127.0.0.1`
- Ensure firewall allows connections on port 8000/8001

### "Database connection failed"
- Verify Supabase connection string in `.env` files
- Check if Supabase project is active (not paused)
- Test connection: See "Test 1" above

### "Tables don't exist"
- Run table creation scripts (see Database Setup section)
- Check Supabase dashboard → Table Editor

---

*Last updated: December 1, 2025*
