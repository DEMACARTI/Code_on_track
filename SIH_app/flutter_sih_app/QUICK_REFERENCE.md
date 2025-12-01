# ⚡ QUICK REFERENCE CARD

## 🎯 What Your Backend Needs

```
Endpoint:  POST /auth/login
Protocol:  HTTPS (or HTTP for localhost)
Content:   application/json

REQUEST:
{
  "username": "user_input",
  "password": "password_input"
}

RESPONSE (Success):
HTTP 200
{
  "username": "user_input",
  "email": "user@company.com"
}

RESPONSE (Failure):
HTTP 401 or 403
(any non-200 status means login failed)
```

---

## 📱 What to Change in Flutter App

**File:** `lib/main.dart`

**Line:** 20

**Change this:**

```dart
const String backendBaseUrl = 'https://api.yourcompany.com';
```

**To your API:**

- Production: `https://api.company.com`
- Staging: `https://staging-api.company.com`
- Local dev: `http://localhost:5000`

**That's it!** Save and run `flutter run -d macos`

---

## ✅ Integration Steps

1. **Backend:** Implement `POST /auth/login` endpoint
2. **App:** Update `backendBaseUrl` in `lib/main.dart`
3. **Run:** `flutter run -d macos`
4. **Test:** Login with your credentials
5. **Deploy:** Build and release

---

## 🔐 What Gets Sent to Backend

When user clicks LOGIN with username "john" and password "secret":

```
POST https://api.yourcompany.com/auth/login
Content-Type: application/json

{
  "username": "john",
  "password": "secret"
}
```

---

## 🎯 What Backend Should Return

If credentials are valid:

```
HTTP 200 OK
Content-Type: application/json

{
  "username": "john",
  "email": "john@company.com"
}
```

**IMPORTANT:** `username` field is REQUIRED. `email` can be empty string if not available.

---

## ❌ Error Cases

### Invalid Credentials

```
HTTP 401 Unauthorized
```

### User Not Found

```
HTTP 401 Unauthorized
```

### Server Error

```
HTTP 500 Internal Server Error
```

**App will show:** "Invalid username or password"

---

## 🧪 How to Test

### Option 1: Using Postman

1. Create POST request to `http://localhost:5000/auth/login`
2. Set header: `Content-Type: application/json`
3. Set body: `{"username":"test","password":"test"}`
4. Click Send
5. Should return `{"username":"test","email":"..."}`

### Option 2: Using curl

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### Option 3: Using Flutter app

1. Update `backendBaseUrl` in `lib/main.dart`
2. Run: `flutter run -d macos`
3. Enter credentials
4. Click LOGIN
5. Check if dashboard opens

---

## 📋 Files to Know

| File                             | Purpose           | Edit?                      |
| -------------------------------- | ----------------- | -------------------------- |
| `lib/main.dart`                  | App configuration | ✅ YES - Update baseUrl    |
| `lib/services/auth_service.dart` | Backend connector | ❌ No - unless customizing |
| `lib/pages/login_page.dart`      | Login UI          | ❌ No - clean as-is        |
| `lib/models/user_model.dart`     | User data         | ❌ No                      |

---

## 🚀 Quick Commands

```bash
# Install dependencies
flutter pub get

# Run app on macOS
flutter run -d macos

# Run app on iOS
flutter run -d ios

# Run app on Android
flutter run -d android

# Build for iOS (production)
flutter build ios --release

# Build for Android (production)
flutter build apk --release

# Build for Android (bundle for Play Store)
flutter build appbundle --release
```

---

## 🔍 Debug Checklist

```
Is app crashing?
□ Check app logs: Look for error messages
□ Check backend logs: Is endpoint being called?
□ Test endpoint with Postman first

Is "Invalid password" showing?
□ Are credentials correct in backend?
□ Is endpoint returning HTTP 200?
□ Is response format correct?

Is there a network error?
□ Is backend running?
□ Is baseUrl correct?
□ Are you on HTTPS (not HTTP)?
□ Is firewall blocking connection?

Is app hanging?
□ Backend is taking >10 seconds
□ Increase timeout in RestAuthService if needed
```

---

## 💡 Pro Tips

1. **Test endpoint first** - Use Postman before testing in app
2. **Use localhost** - Easier to debug during development
3. **Check server logs** - See exactly what's happening
4. **HTTPS only** - For production security
5. **Rate limit** - Prevent brute force attacks on backend
6. **Hash passwords** - Never store plain text passwords
7. **Add logging** - Log login attempts for security

---

## 🎯 Success Indicators

✅ **Working correctly if:**

- User clicks LOGIN
- App shows loading spinner
- Backend receives POST request
- App receives 200 response
- Dashboard opens
- User is logged in

❌ **Problem if:**

- App crashes
- Loading spinner stays forever
- Error message shown
- Backend not receiving request
- Backend returning error status

---

## 📞 Common Issues

### "Invalid username or password"

**Cause:** Backend returned non-200 status
**Fix:** Check backend logs, verify credentials

### Network timeout

**Cause:** Backend not responding within 10 seconds
**Fix:** Check if backend is running, network connectivity

### CORS error (web only)

**Cause:** Browser blocking request
**Fix:** Add CORS headers to backend

### App crashes

**Cause:** Response format mismatch
**Fix:** Ensure response has `username` and `email` fields

---

## 🔐 Security Reminders

- ✅ Always use HTTPS in production
- ✅ Hash passwords on backend
- ✅ Add rate limiting to prevent brute force
- ✅ Validate credentials server-side
- ✅ Don't log sensitive data
- ✅ Use HTTPS only for mobile app
- ✅ Implement session timeout
- ✅ Add fail attempt counter

---

## 📊 Example Response Times

| Network   | Time           |
| --------- | -------------- |
| Fast 4G   | 100-200ms ⚡   |
| Wifi      | 50-150ms ⚡    |
| Slow 3G   | 500-2000ms 📡  |
| Very Slow | >3 seconds 🐌  |
| Timeout   | >10 seconds ❌ |

---

## 🎉 You're Ready!

```
1. Backend: Implement /auth/login endpoint ✓
2. App: Update baseUrl in lib/main.dart ✓
3. Run: flutter run -d macos ✓
4. Test: Login with credentials ✓
5. Deploy: Build and release ✓
```

**Everything is set up. Just connect and go!** 🚀

---

## 📚 Full Guides

For more details, see:

- `BACKEND_INTEGRATION.md` - Complete guide
- `BACKEND_SETUP_EXAMPLES.md` - Code examples
- `VISUAL_GUIDE.md` - Diagrams and flows
- `FINAL_SUMMARY.md` - Full summary

---

**Your app is clean, professional, and ready for your backend!** ✨
