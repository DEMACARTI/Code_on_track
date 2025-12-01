# 🔌 Backend Integration - Step by Step

## ⚡ Quick Integration (Copy-Paste Ready)

### Your Backend Must Implement This

```
Endpoint: POST /auth/login
```

---

## 📝 Step 1: Backend API Implementation

### Example in Python (Flask)

```python
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash

app = Flask(__name__)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate against your database
    user = get_user_from_database(username)

    if user and check_password_hash(user.password, password):
        return jsonify({
            'username': user.username,
            'email': user.email
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

# Run: python app.py
```

### Example in Node.js (Express)

```javascript
const express = require("express");
const app = express();

app.post("/auth/login", async (req, res) => {
  const { username, password } = req.body;

  try {
    // Validate against your database
    const user = await User.findOne({ username });

    if (user && (await user.verifyPassword(password))) {
      return res.json({
        username: user.username,
        email: user.email,
      });
    }

    res.status(401).json({ error: "Invalid credentials" });
  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
});

// Run: node app.js
```

### Example in PHP

```php
<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $username = $data['username'] ?? null;
    $password = $data['password'] ?? null;

    // Validate against database
    $user = get_user_from_database($username);

    if ($user && password_verify($password, $user['password_hash'])) {
        echo json_encode([
            'username' => $user['username'],
            'email' => $user['email']
        ]);
        http_response_code(200);
    } else {
        http_response_code(401);
        echo json_encode(['error' => 'Invalid credentials']);
    }
}
?>
```

### Example in Java (Spring Boot)

```java
@RestController
@RequestMapping("/auth")
public class AuthController {

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername());

        if (user != null && passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return ResponseEntity.ok(new LoginResponse(
                user.getUsername(),
                user.getEmail()
            ));
        }

        return ResponseEntity.status(401).build();
    }
}
```

---

## 📱 Step 2: Update Flutter App

### Edit `lib/main.dart`

**Change line 20 from:**

```dart
const String backendBaseUrl = 'https://api.yourcompany.com';
```

**To your actual backend URL:**

```dart
// Development (local)
const String backendBaseUrl = 'http://localhost:5000';

// OR Production
const String backendBaseUrl = 'https://api.mycompany.com';
```

---

## 🧪 Step 3: Test the Integration

### Option A: Local Testing

#### Backend

```bash
# Python
python app.py  # Runs on http://localhost:5000

# Node.js
node app.js    # Runs on http://localhost:3000

# PHP
php -S localhost:8000
```

#### Flutter App

```dart
const String backendBaseUrl = 'http://localhost:5000'; // Match your backend
```

#### Run App

```bash
flutter run -d macos
```

#### Test Login

1. Open app
2. Enter username & password
3. Should see dashboard if credentials valid
4. Should see error if invalid

### Option B: Production Testing

#### Backend

```
https://api.mycompany.com
```

#### Flutter App

```dart
const String backendBaseUrl = 'https://api.mycompany.com';
```

#### Run & Test

```bash
flutter run -d macos
flutter run -d ios
flutter run -d android
```

---

## 🔐 Advanced: Adding Security

### Add JWT Token Support

Modify `lib/services/auth_service.dart`:

```dart
class RestAuthService implements AuthService {
  final String baseUrl;
  String? _authToken; // Store token

  @override
  Map<String, String> headers() {
    final h = {'Content-Type': 'application/json'};
    if (_authToken != null) {
      h['Authorization'] = 'Bearer $_authToken';
    }
    return h;
  }

  @override
  User? parseResponse(Map<String, dynamic> data) {
    // Save token for future requests
    _authToken = data['token'] as String?;

    return User(
      username: data['username'] as String? ?? '',
      email: data['email'] as String? ?? '',
    );
  }
}
```

Backend should return:

```json
{
  "username": "john_doe",
  "email": "john@company.com",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## 🛡️ Production Checklist

- [ ] Backend implements `POST /auth/login`
- [ ] Backend validates credentials against database
- [ ] Backend returns proper error codes (401 for invalid)
- [ ] HTTPS enabled (not HTTP)
- [ ] CORS headers configured (if cross-origin)
- [ ] Rate limiting implemented (prevent brute force)
- [ ] Password hashing used (never plain text)
- [ ] Input validation on backend (sanitize inputs)
- [ ] Error messages don't leak user information
- [ ] Session/token management implemented
- [ ] Tested with multiple client apps
- [ ] Monitored for failed login attempts

---

## 📊 Request/Response Flow

```
┌─────────────────────────────────────┐
│  Flutter App                        │
│  lib/main.dart                      │
│  baseUrl = 'https://api.../`        │
└────────────┬────────────────────────┘
             │
             │ POST /auth/login
             │ {"username":"...",
             │  "password":"..."}
             │
             ▼
┌─────────────────────────────────────┐
│  Your Backend API                   │
│  /auth/login endpoint               │
│  - Validate credentials             │
│  - Check database                   │
│  - Return user or error             │
└────────────┬────────────────────────┘
             │
             │ HTTP 200 OK
             │ {"username":"...",
             │  "email":"..."}
             │
             ▼
┌─────────────────────────────────────┐
│  Flutter App                        │
│  ParseResponse() parses data        │
│  Creates User object                │
│  Routes to Dashboard                │
└─────────────────────────────────────┘
```

---

## 🚀 Deploy Checklist

### Before Going Live

1. **Backend**

   - [ ] All endpoints tested
   - [ ] Database configured
   - [ ] Error handling complete
   - [ ] HTTPS certificate installed
   - [ ] CORS configured
   - [ ] Rate limiting enabled

2. **Flutter App**

   - [ ] `backendBaseUrl` updated
   - [ ] No debug build
   - [ ] All tests passing
   - [ ] Signed APK/IPA created

3. **Testing**

   - [ ] Login with valid credentials → Works
   - [ ] Login with invalid credentials → Shows error
   - [ ] Network error → Shows error
   - [ ] Long wait → Shows loading indicator

4. **Security**
   - [ ] HTTPS everywhere
   - [ ] No credentials logged
   - [ ] Session timeout configured
   - [ ] No hard-coded secrets

---

## 💬 Support

If you run into issues:

1. **App shows "Invalid username or password"** but credentials are correct

   - Check if backend is running
   - Verify endpoint URL is correct
   - Test endpoint with Postman

2. **Network timeout error**

   - Backend is not responding
   - Check firewall/network connectivity
   - Backend might be slow (check server logs)

3. **CORS error** (Web only)

   - Add CORS headers to backend
   - Set `Access-Control-Allow-Origin: *`

4. **App crashes**
   - Check Flutter console for errors
   - Verify response JSON format matches expected

---

## 📞 Summary

Your Flutter app is ready to connect to **any backend**:

1. ✅ Implement `POST /auth/login` in your backend
2. ✅ Update `baseUrl` in `lib/main.dart`
3. ✅ Run the app
4. ✅ Test with your credentials
5. ✅ That's it! 🎉

**No more changes needed. The app seamlessly integrates with your backend!**
