# 🔌 Backend Integration Guide

## ✅ Clean Setup Complete

Your SIH Flutter app is now **100% ready for backend integration**. All debug elements and test credentials have been removed.

---

## 🎯 Quick Start (5 minutes)

### Step 1: Configure Backend URL

Edit `lib/main.dart` and update the `backendBaseUrl`:

```dart
const String backendBaseUrl = 'https://api.yourcompany.com';
```

That's it! The app will now use your backend.

---

## 📡 API Contract Your Backend Must Implement

### Endpoint

```
POST /auth/login
```

### Request

```json
{
  "username": "string",
  "password": "string"
}
```

### Success Response (HTTP 200)

```json
{
  "username": "john_doe",
  "email": "john@company.com"
}
```

**Required fields:**

- `username` (string) - User's username
- `email` (string) - User's email

**Optional fields:**

- Any other fields your system needs (will be available via the User object)

### Failure Response (Any non-200 status)

```
HTTP 401 Unauthorized
HTTP 403 Forbidden
HTTP 500 Internal Server Error
```

The app will display "Invalid username or password" message.

---

## 💻 Architecture Overview

### How the App Communicates with Backend

```
┌─────────────────────────────────────┐
│  User enters credentials            │
│  (LoginPage UI)                     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  RestAuthService.authenticate()     │
│  - Constructs JSON request          │
│  - Sends POST to /auth/login        │
│  - Handles 10-second timeout        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Your Backend API                   │
│  - Validates username/password      │
│  - Returns user info or 401         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Response parsing (parseResponse)   │
│  - Extracts username + email        │
│  - Creates User object              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  InspectionInterface Dashboard      │
│  (User logged in successfully)      │
└─────────────────────────────────────┘
```

---

## 🛠️ Advanced Customization

### Adding Custom Headers (e.g., API Key)

Override `headers()` in a custom AuthService:

```dart
class CustomAuthService extends RestAuthService {
  @override
  Map<String, String> headers() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY',
      'X-Custom-Header': 'value',
    };
  }
}
```

Then in `main.dart`:

```dart
final authService = CustomAuthService(baseUrl: backendBaseUrl);
```

### Handling Custom Response Formats

Override `parseResponse()` for complex responses:

```dart
class CustomAuthService extends RestAuthService {
  @override
  User? parseResponse(Map<String, dynamic> data) {
    // Your backend returns nested response?
    final userData = data['data'] as Map<String, dynamic>?;
    if (userData == null) return null;

    return User(
      username: userData['username'] as String? ?? '',
      email: userData['user_email'] as String? ?? '', // Different field name
    );
  }
}
```

### Changing Endpoint Path

If your login endpoint is not `/auth/login`:

```dart
final authService = RestAuthService(
  baseUrl: backendBaseUrl,
  endpoint: '/api/v1/authenticate', // Custom endpoint
);
```

---

## 📋 File Structure for Backend Integration

```
lib/
├── main.dart                     ← Update backendBaseUrl here
├── services/
│   └── auth_service.dart         ← RestAuthService (backend connector)
├── pages/
│   ├── login_page.dart           ← Clean login UI (no test credentials)
│   └── inspection_interface.dart ← Dashboard after login
└── models/
    └── user_model.dart           ← User data model
```

---

## ✨ What's Included

✅ **Clean Login UI** - No debug info or test credentials
✅ **RestAuthService** - Production-ready HTTP client
✅ **Extensible** - Override methods for custom behavior
✅ **Error Handling** - 10-second timeout, network error handling
✅ **Type Safe** - Full Dart typing throughout
✅ **Zero Mock Code** - App designed for real backend only

---

## 🚀 Backend Requirements Checklist

- [ ] Implement `POST /auth/login` endpoint
- [ ] Accept JSON: `{"username": "...", "password": "..."}`
- [ ] Return JSON on success: `{"username": "...", "email": "..."}`
- [ ] Return HTTP 401 or 403 on invalid credentials
- [ ] HTTPS enabled (recommended for production)
- [ ] CORS configured (if app runs on different domain)
- [ ] 10-second response time (app will timeout after)

---

## 🔧 Testing Your Integration

### Step 1: Update Backend URL

```dart
const String backendBaseUrl = 'http://localhost:8080'; // Your backend
```

### Step 2: Run App

```bash
flutter run -d macos  # or ios/android
```

### Step 3: Enter Credentials

- Username: (any valid username in your system)
- Password: (corresponding password)

### Step 4: Verify

- ✅ Login successful → Dashboard opens
- ✅ Login failed → Error message shown
- ✅ Network error → Error message shown

---

## 💡 Pro Tips

1. **Use localhost during development:** `http://localhost:8000`
2. **Add logging:** Use `print()` statements in `RestAuthService` for debugging
3. **Test with Postman:** Verify your endpoint before testing in app
4. **Use HTTPS:** Always use HTTPS in production
5. **Add refresh tokens:** Extend `User` model if needed for session management

---

## 🎓 Example Backend Implementation (Python/Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # TODO: Validate credentials against your database
    if validate_user(username, password):
        return jsonify({
            'username': username,
            'email': get_user_email(username)
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

---

## ❓ Troubleshooting

### "Invalid username or password" message

- Check endpoint URL is correct
- Verify backend is running
- Test endpoint with Postman first

### Network timeout

- Backend is not responding
- Check firewall/network connectivity
- Increase timeout in `RestAuthService` if needed

### CORS errors (Web only)

- Add CORS headers to your backend
- Set `Access-Control-Allow-Origin: *`

---

## 📞 Summary

Your app is now:

- ✅ Clean (no test credentials)
- ✅ Production-ready (using RestAuthService)
- ✅ Backend-agnostic (works with any API)
- ✅ Easily customizable (override methods as needed)
- ✅ Ready to integrate (just update baseUrl)

**Next step:** Update `backendBaseUrl` in `lib/main.dart` and run the app! 🚀
