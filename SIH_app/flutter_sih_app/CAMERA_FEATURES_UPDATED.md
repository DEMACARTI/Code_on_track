# QR Scanner - Enhanced Camera Features 📸

## ✨ New Features Added

### 1. **Camera Controls Overlay**

Located at the top-right of the camera view with quick-access buttons:

#### 🔦 Torch/Flash Toggle

- Click the **Flash icon** to toggle flashlight on/off
- Useful for scanning QR codes in low-light conditions
- Shows error message if device doesn't support torch

#### 📷 Switch Camera

- Click the **Camera switch icon** to switch between front/back cameras
- Available on devices with multiple cameras (phones, tablets, MacBooks with multiple cameras)
- Shows error if only one camera is available or switching not supported

#### ⌨️ Manual Input

- Click the **Keyboard icon** to manually enter QR codes
- Fallback option when camera is not working or unavailable
- Opens a dialog where you can type the QR code value

---

## 🎯 Manual QR Input Dialog

When the camera is not available or not working:

1. Click the **keyboard icon** (⌨️) on the camera controls
2. A dialog appears with an input field
3. Type your QR code (e.g., `QR001`)
4. Click **"Scan"** to process it through the backend
5. Results display just like a scanned QR code

**Perfect for:**

- macOS webcam not detected
- Testing without actual QR codes
- Accessibility needs
- When camera device is unavailable

---

## 🛠️ Technical Implementation

### Modified File

- `lib/pages/qr_scan_dashboard.dart` - Enhanced scanner UI with camera controls

### New Methods Added

**`_showManualInputDialog()`**

- Shows a dialog for manual QR code entry
- Validates user input before processing
- Calls `_processQRCode()` with manually entered value

**`_processQRCode(String qrData)`**

- Unified QR processing logic (camera OR manual input)
- Stops camera, sends to backend, displays results
- Auto-resumes camera after 2 seconds

### Camera Controls Features

```dart
// Torch toggle
await cameraController.toggleTorch();

// Switch camera (front ↔️ back)
await cameraController.switchCamera();

// Manual input dialog
await _showManualInputDialog();
```

---

## 📱 Platform Support

| Feature              | Mobile           | Web | Desktop (macOS) |
| -------------------- | ---------------- | --- | --------------- |
| **Camera Detection** | ✅               | ⚠️  | ⚠️              |
| **Torch Toggle**     | ✅               | ❌  | ❌              |
| **Switch Camera**    | ✅ (if multiple) | ❌  | ⚠️              |
| **Manual Input**     | ✅               | ✅  | ✅              |

---

## 🚀 How to Use

### Auto Camera Scanning (Default)

1. App loads with camera active
2. Point at QR code
3. Automatic detection and backend validation
4. Results display instantly

### Torch Control (Low Light)

1. Look for **🔦 Flash icon** at top-right
2. Click to enable flashlight
3. Improves detection in dark environments

### Switch Camera (Phone)

1. Click **📷 Camera switch icon**
2. Switches between front/back cameras
3. Continue scanning with the new camera

### Manual Input (Camera Not Available)

1. Click **⌨️ Keyboard icon**
2. Type QR code manually (e.g., `QR001`)
3. Click **"Scan"** button
4. Results process like camera scan

---

## 🔧 Error Handling

**"Torch not available"**

- Device doesn't support flashlight
- Try switching to back camera

**"Multiple cameras not available on this device"**

- Device only has one camera
- Manual input remains available

**Camera Error with Manual Input Option**

- If camera completely fails, shows button to use manual input
- Fallback ensures app always has scanning capability

---

## 📚 Test Scenarios

### Test Case 1: Automatic Camera Scanning

1. Launch app on iOS simulator
2. Camera view appears
3. Auto-scans QR codes (test: `QR001`, `QR002`, `QR003`)
4. Status displays with item details

### Test Case 2: Manual Input

1. Click keyboard icon (⌨️)
2. Enter `QR001` manually
3. Click "Scan"
4. Should show same results as auto-scan

### Test Case 3: Camera Controls

1. Try clicking torch icon
2. Try clicking camera switch (if available)
3. Toggle pause/resume FAB button
4. All should work smoothly

### Test Case 4: Error Fallback

1. If camera fails, manual input button appears
2. Use keyboard icon to manually enter codes
3. App remains fully functional

---

## 🎨 UI Layout

```
┌─────────────────────────────────┐
│  QR Scanner - Inspection   👤   │ ← AppBar
├─────────────────────────────────┤
│                                 │
│         📷 Camera View          │
│                                 │
│  ┌──────────────────────────┐   │
│  │ 🔦 📷 ⌨️ (Control Bar)  │   │ ← Camera Controls
│  └──────────────────────────┘   │    (top-right)
│                                 │
│   [Auto-detecting QR code]      │
│                                 │
├─────────────────────────────────┤
│  Status & Details (40% height)  │
│                                 │
│  🟢 Item Operational            │
│  Details card with item info    │
│                                 │
├─────────────────────────────────┤
│         [▶ Pause/Resume FAB]    │
└─────────────────────────────────┘
```

---

## 💡 Tips & Tricks

- **Low Light?** Enable torch (🔦) for better detection
- **Only front camera?** Manual input still works perfectly
- **Testing?** Use manual input to test backend without real QR codes
- **Accessibility?** Manual input supports all accessibility tools

---

## 🔄 Backend Integration

Manual input uses the same backend validation as camera:

- Request: `POST /qr/scan` with `{ "qr_code": "QR001" }`
- Response: Same `ScannedItem` data structure
- Error handling: Identical to camera scans

No backend changes needed! 🎉

---

**Version:** 1.1.0 (Enhanced Camera Features)
**Updated:** November 12, 2025
