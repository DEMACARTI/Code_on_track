# macOS Camera Setup Guide 🎥

## Problem

The camera is not working on macOS (selfie camera not opening in the app).

## Solution: Enable Camera Permissions

### Step 1: Grant Camera Permission to the App

1. **Open System Settings** on your Mac
2. Navigate to **Privacy & Security** (usually in the left sidebar)
3. Scroll down and click **Camera**
4. You should see `flutter_sih_app` in the list of applications
5. **Make sure the checkbox next to it is CHECKED** ✓

### Step 2: Restart the App

Once you've enabled camera permissions:

1. **Close the app completely** (not just minimize)
2. **Reopen the app** from Launchpad or applications
3. The camera should now work!

---

## If Camera Still Doesn't Work

### Option 1: Check System Preferences Again

- Go to Settings → Privacy & Security → Camera
- Look for `flutter_sih_app` in the list
- If it's not there, the app will request permission on next launch
- Click "Allow"

### Option 2: Reset Camera Permissions

1. Open Terminal on your Mac
2. Run this command:

```bash
tccutil reset Camera com.your.bundle.id
```

3. Restart the app and grant permission when prompted

### Option 3: Rebuild the App

If permissions are still not working:

```bash
cd /Users/vijvalkumar/Desktop/SIH_app/flutter_sih_app
flutter clean
flutter pub get
flutter run -d macos
```

---

## If Camera Hardware is Not Detected

Some Macs have multiple cameras or camera access conflicts. Try these:

### 1. Check Available Cameras

```bash
system_profiler SPCameraProfile
```

This shows all connected cameras on your Mac.

### 2. Verify iSight/FaceTime Camera

Built-in Mac cameras are usually called:

- "iSight Camera"
- "FaceTime Camera"
- "FaceTime HD Camera"

### 3. Try Using Manual Input Instead

If your Mac's camera is not compatible:

1. Click the **⌨️ Keyboard button** in the scanner
2. Manually type the QR code (e.g., `QR001`)
3. Click "Scan"
4. The app will work perfectly without the camera!

---

## Features That Work Without Camera

Our app includes a **Manual Input Fallback**:

✅ Manual QR Code Entry (⌨️ button)
✅ Backend Validation (same as camera)
✅ Status Display & Item Details
✅ Full App Functionality

So even if the camera doesn't work, you can still scan QR codes by typing them manually!

---

## Info.plist Configuration

The app now includes proper macOS permissions in `macos/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs access to your camera to scan QR codes for inspection purposes</string>
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for camera functionality</string>
```

This allows the system to properly ask for permissions.

---

## Testing Camera Access

After enabling permissions, test with:

1. **Test QR Code 1:** Type `QR001` in manual input
2. **Test QR Code 2:** Type `QR002` in manual input
3. **Test QR Code 3:** Type `QR003` in manual input

All should work! If camera starts working, great! If not, manual input is always available.

---

## Troubleshooting Checklist

- [ ] Camera enabled in System Settings → Privacy & Security → Camera
- [ ] `flutter_sih_app` is in the Camera apps list with ✓ checked
- [ ] App restarted after enabling permission
- [ ] No other app is using the camera
- [ ] Mac camera hardware is working (test with Photo Booth app)
- [ ] Try manual input feature if camera still doesn't work

---

## Need More Help?

If camera still isn't working after all these steps:

1. **Manual Input is always available** - Use the ⌨️ button to enter QR codes by hand
2. **Backend validation works the same way** - Manual input goes through same backend
3. **No functionality lost** - App remains fully operational without camera

Your app won't fail - it will just use the manual input mode instead! 🎉

---

**Last Updated:** November 12, 2025
