# 🔍 QR Scanner Dashboard - Complete Guide

## ✅ New Features Implemented

### 1. 🎥 QR Code Scanner

- Real-time camera-based QR code scanning
- Located at the top of the dashboard (60% of screen)
- Uses `mobile_scanner` package for optimal performance
- Pause/Resume functionality via floating action button

### 2. 📦 Backend Integration

- Scanned QR codes sent to backend for validation
- Backend checks if QR exists in database
- Returns complete item information if found
- User-friendly error messages if not found

### 3. 📊 Status Display Box

- Located below scanner (40% of screen)
- Shows real-time status with color coding:
  - 🟢 **Green** = Operational
  - 🟠 **Orange** = Needs Maintenance
  - 🔴 **Red** = Non-Operational / Not Found
  - 🔵 **Blue** = Ready to Scan

### 4. 📋 Item Information Card

Displays when item is found:

- Item ID
- Item Name
- Status Badge
- Location
- Details/Notes
- Last Updated timestamp

---

## 🏗️ Architecture

### Files Created

| File                                | Purpose                                      |
| ----------------------------------- | -------------------------------------------- |
| `lib/services/qr_scan_service.dart` | QR scanning service (abstract + REST + Mock) |
| `lib/pages/qr_scan_dashboard.dart`  | QR scanner UI and logic                      |

### Files Updated

| File                        | Changes                                |
| --------------------------- | -------------------------------------- |
| `lib/main.dart`             | Added QR service, route to dashboard   |
| `lib/pages/login_page.dart` | Updated navigation to use named routes |
| `pubspec.yaml`              | Added `mobile_scanner: ^5.0.0`         |

### Files Removed (Can be deleted)

| File                                  | Reason                   |
| ------------------------------------- | ------------------------ |
| `lib/pages/inspection_interface.dart` | Replaced by QR dashboard |

---

## 🔌 Backend API Contract

### QR Scan Endpoint

```
POST /qr/scan
```

### Request Format

```json
{
  "qr_code": "QR001"
}
```

### Success Response (HTTP 200)

```json
{
  "id": "QR001",
  "name": "Fire Extinguisher - Lobby",
  "status": "operational",
  "location": "Main Lobby",
  "details": "Fire extinguisher checked and operational",
  "last_updated": "2025-11-12T10:30:00Z"
}
```

### Not Found Response (HTTP 404)

```
(Empty response or null)
```

### Response Field Details

| Field          | Type   | Required | Description                                           |
| -------------- | ------ | -------- | ----------------------------------------------------- |
| `id`           | string | ✅       | Unique item identifier                                |
| `name`         | string | ✅       | Item display name                                     |
| `status`       | string | ✅       | `operational`, `needs_maintenance`, `non_operational` |
| `location`     | string | ✅       | Item location                                         |
| `details`      | string | ❌       | Additional information                                |
| `last_updated` | string | ❌       | ISO 8601 timestamp                                    |

---

## 🧪 Test Credentials

Login to test the QR scanner:

```
Username: inspection_team
Password: insp@123
```

### Mock QR Codes (for local testing)

These QR codes work with `MockQRScanService`:

| QR Code | Item Name                    | Status            |
| ------- | ---------------------------- | ----------------- |
| `QR001` | Fire Extinguisher - Lobby    | Operational       |
| `QR002` | Emergency Light - Corridor A | Operational       |
| `QR003` | Safety Equipment - Storage   | Needs Maintenance |

---

## 🚀 How to Use

### 1. Login

```
Username: inspection_team
Password: insp@123
```

### 2. QR Scanner Opens

- Point camera at any QR code
- Auto-detects and processes

### 3. View Results

- If found: See full item details
- If not found: Error message displayed

### 4. Rescan

- After 2 seconds, scanner auto-resumes
- Can scan multiple items in sequence

---

## 🔧 Switch to Backend

### Before (Testing with Mock)

Current setup uses `MockQRScanService` in `lib/main.dart`:

```dart
final qrService = MockQRScanService();
```

### After (Production Backend)

Edit `lib/main.dart` and uncomment:

```dart
const String backendBaseUrl = 'https://your-api.com';
final qrService = RestQRScanService(baseUrl: backendBaseUrl);
```

---

## 📱 Screen Layout

```
┌─────────────────────────────────┐
│  SIH Scanner - Inspection      │ ◄── AppBar with user info + logout
├─────────────────────────────────┤
│                                 │
│      📷 QR Camera View          │
│      (60% of screen)            │
│                                 │
│      [Auto-scanning]            │
│                                 │
├─────────────────────────────────┤
│  Status Box                     │
│  ┌─────────────────────────┐   │
│  │ 🟢 Item Operational     │   │ ◄── Color-coded status
│  │ Item found in database  │   │
│  └─────────────────────────┘   │
│                                 │
│  Item Details Card (if found)  │ ◄── Full item info
│  ┌─────────────────────────┐   │
│  │ QR001                   │   │
│  │ Fire Extinguisher       │   │
│  │ 📍 Main Lobby           │   │
│  │ [OPERATIONAL]           │   │
│  └─────────────────────────┘   │
│                                 │
├─────────────────────────────────┤
│            [▶ Pause] FAB        │ ◄── Play/Pause button
└─────────────────────────────────┘
```

---

## 🎨 UI/UX Features

### Status Color Coding

```
Operational       → 🟢 Green (background)
Needs Maintenance → 🟠 Orange (background)
Non-Operational   → 🔴 Red (background)
Not Found         → 🔴 Red (error state)
Ready to Scan     → 🔵 Blue (default state)
```

### Status Messages

```
✅ Item Operational          → Item found and working
⚠️ Maintenance Required       → Item needs attention
❌ Item Non-Operational       → Item not working
❌ Scan Failed / ⚠️ Not Found  → QR not in database
📱 Ready to Scan             → Waiting for QR code
```

---

## 🔐 Permissions Required

### iOS

```xml
<!-- Info.plist -->
<key>NSCameraUsageDescription</key>
<string>Camera access needed to scan QR codes</string>
```

### Android

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
```

---

## 🛠️ Customization

### Change QR Endpoint

In `lib/services/qr_scan_service.dart`:

```dart
final qrService = RestQRScanService(
  baseUrl: 'https://api.com',
  endpoint: '/api/v1/qr/check', // Custom endpoint
);
```

### Add Custom Headers

```dart
class CustomQRService extends RestQRScanService {
  @override
  Map<String, String> headers() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_TOKEN',
    };
  }
}
```

### Handle Custom Response Format

```dart
class CustomQRService extends RestQRScanService {
  @override
  ScannedItem? parseResponse(Map<String, dynamic> data) {
    final item = data['item_data'];
    return ScannedItem(
      id: item['item_id'],
      name: item['item_name'],
      // ... map other fields
    );
  }
}
```

---

## 🚀 Deployment Checklist

### Backend Setup

- [ ] Create `/qr/scan` endpoint
- [ ] Implement QR validation logic
- [ ] Return proper JSON response
- [ ] Test with QR codes
- [ ] Configure CORS
- [ ] Enable HTTPS

### App Setup

- [ ] Update backend URL in `lib/main.dart`
- [ ] Test with real QR codes
- [ ] Verify camera permissions
- [ ] Build release APK/IPA
- [ ] Test on real devices

---

## 📞 Example Backend Implementation

### Python/Flask

```python
@app.route('/qr/scan', methods=['POST'])
def scan_qr():
    data = request.json
    qr_code = data.get('qr_code')

    # Look up QR in database
    item = database.find_by_qr(qr_code)

    if item:
        return jsonify({
            'id': item.id,
            'name': item.name,
            'status': item.status,
            'location': item.location,
            'details': item.details,
            'last_updated': item.updated_at.isoformat()
        }), 200

    return jsonify({'error': 'QR not found'}), 404
```

### Node.js/Express

```javascript
app.post("/qr/scan", async (req, res) => {
  const { qr_code } = req.body;

  const item = await database.findByQR(qr_code);

  if (item) {
    return res.json({
      id: item.id,
      name: item.name,
      status: item.status,
      location: item.location,
      details: item.details,
      last_updated: item.updatedAt,
    });
  }

  res.status(404).json({ error: "QR not found" });
});
```

---

## ✨ Features Summary

✅ **Real-time QR Scanning** - Camera-based detection
✅ **Backend Validation** - REST API integration
✅ **Status Display** - Color-coded feedback
✅ **Item Details** - Complete information display
✅ **Error Handling** - User-friendly messages
✅ **Mock Testing** - Includes test data
✅ **Easy Backend Switching** - Just update URL
✅ **Professional UI** - Clean, modern design
✅ **Responsive Layout** - Camera + details view
✅ **Auto-resume Scanning** - Quick rescans

---

## 🎉 Summary

Your inspection app now has:

1. ✅ Inspection-only login
2. ✅ QR code scanning interface
3. ✅ Backend item lookup
4. ✅ Real-time status display
5. ✅ Professional dashboard

**Ready for production! Just update the backend URL when connected.** 🚀
