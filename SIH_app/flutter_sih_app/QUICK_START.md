# 🚀 RailChinh Mobile App - Quick Reference

## 🌐 Backend URL
```
https://railchinh-mobile-backend.onrender.com
```

## 🔐 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| **admin** | admin123 | Admin |
| **inspection** | inspect123 | Inspector |
| **inventory** | inventory123 | Inventory Manager |
| **installation** | install123 | Installation Team |
| **management** | manage123 | Management |

## 📱 Run the App

```bash
cd SIH_app/flutter_sih_app
flutter clean
flutter pub get
flutter run
```

## 🧪 Test Backend

**Browser:**
```
https://railchinh-mobile-backend.onrender.com/health
```

**Terminal:**
```bash
curl https://railchinh-mobile-backend.onrender.com/health
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/auth/login` | POST | Login |
| `/api/items/{uid}` | GET | Get item |
| `/qr/inspection` | POST | Submit inspection |

## 📝 Configuration Files

1. **Main config:** `lib/main.dart` (Line 23)
2. **API service:** `lib/services/api_service.dart` (Line 8)

## ⚠️ Important

- ✅ Backend is on Render.com (always accessible)
- ✅ No local backend needed
- ✅ Works on any device with internet
- ⏱️ First request may take 30-60s (cold start)

## 🆘 Troubleshooting

**Can't connect?**
1. Check internet
2. Wait 60 seconds (backend waking up)
3. Test URL in browser

**Login fails?**
1. Check credentials
2. No extra spaces in username/password
3. Try: admin / admin123

---

**Status:** ✅ READY TO USE
**Last Updated:** December 8, 2025
