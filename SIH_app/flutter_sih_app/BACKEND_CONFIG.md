# Backend Configuration - RailChinh Mobile App

## 🌐 Production Backend

**Backend URL:** `https://railchinh-mobile-backend.onrender.com`

The mobile app is configured to use the production backend deployed on Render.com.

## 📱 Configuration Files

### 1. Main App Configuration
**File:** `lib/main.dart`

```dart
const String backendBaseUrl = 'https://railchinh-mobile-backend.onrender.com';
final authService = RestAuthService(baseUrl: backendBaseUrl);
final qrService = RestQRScanService(baseUrl: backendBaseUrl);
```

### 2. API Service
**File:** `lib/services/api_service.dart`

```dart
static const String baseUrl = 'https://railchinh-mobile-backend.onrender.com';
```

## 🔄 Switching Between Environments

### Production (Render.com)
Use this for production builds and testing on physical devices:
```dart
const String backendBaseUrl = 'https://railchinh-mobile-backend.onrender.com';
```

### Local Development (Mac/PC)
Use this only when running backend locally on your development machine:
```dart
const String baseUrl = 'http://localhost:8080';
```

### Local Network (Physical Device Testing)
Use this when testing on physical device connected to same WiFi:
```dart
const String baseUrl = 'http://YOUR_LOCAL_IP:8080';
// Example: 'http://192.168.1.100:8080'
```

## 📡 API Endpoints

All endpoints are relative to the base URL:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/api/auth/login` | POST | User authentication |
| `/api/items` | GET | List all items |
| `/api/items/{uid}` | GET | Get item details by UID |
| `/api/items/{uid}` | PUT | Update item status |
| `/qr/inspection` | POST | Submit inspection result |
| `/api/inspections/{uid}` | GET | Get inspection history |

## 🔐 Authentication

The backend uses simple username/password authentication with the following credentials:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| inspection | inspect123 | Inspector |
| inventory | inventory123 | Inventory Manager |
| installation | install123 | Installation Team |
| management | manage123 | Management |

## 🧪 Testing Backend Connection

### From Flutter App
The app automatically checks backend connection on the connection status page.

### From Browser
Visit: https://railchinh-mobile-backend.onrender.com

Expected response:
```json
{
  "status": "ok",
  "message": "RailChinh Mobile Backend is running"
}
```

### From Terminal (curl)
```bash
curl https://railchinh-mobile-backend.onrender.com/health
```

## ⚙️ Backend Configuration

The production backend uses:
- **Database:** Supabase PostgreSQL
- **Port:** 8080 (internal), HTTPS (external)
- **CORS:** Enabled for all origins (mobile app compatible)
- **Auto-deploy:** Enabled on GitHub push

## 🔧 Updating Configuration

If you need to change the backend URL:

1. **Update main.dart:**
   ```dart
   // Line 23
   const String backendBaseUrl = 'YOUR_NEW_URL';
   ```

2. **Update api_service.dart:**
   ```dart
   // Line 8
   static const String baseUrl = 'YOUR_NEW_URL';
   ```

3. **Rebuild the app:**
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

## 📊 Backend Status

You can check the backend status at any time:

- **Live status:** https://railchinh-mobile-backend.onrender.com/health
- **Render Dashboard:** https://dashboard.render.com (requires login)

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"
**Solutions:**
1. Check internet connection
2. Verify backend URL is correct
3. Test backend URL in browser: https://railchinh-mobile-backend.onrender.com
4. Check Render dashboard for backend status

### Issue: "Connection timeout"
**Solutions:**
1. Render free tier may take 30-60 seconds to wake up from sleep
2. Wait and try again
3. Backend auto-sleeps after 15 minutes of inactivity

### Issue: "401 Unauthorized"
**Solutions:**
1. Verify login credentials
2. Check username/password spelling
3. Ensure spaces are not included

### Issue: "404 Not Found"
**Solutions:**
1. Verify API endpoint path
2. Check that item UID is correct
3. Ensure backend is running (check /health endpoint)

## 📝 Notes

- The backend uses HTTPS in production (Render provides SSL automatically)
- No additional configuration needed for mobile app
- Backend automatically scales and handles multiple requests
- Free tier on Render may have cold starts (first request takes longer)

## 🔄 Deployment Updates

When backend is updated on GitHub:
1. Render automatically detects changes
2. Backend redeploys (takes 2-3 minutes)
3. Mobile app continues to work without changes
4. No app rebuild needed

---

**Last Updated:** December 8, 2025
**Backend Version:** 1.0.0
**Deployment Platform:** Render.com
