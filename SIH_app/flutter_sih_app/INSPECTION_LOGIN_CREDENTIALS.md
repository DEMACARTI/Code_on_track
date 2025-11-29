# 🔐 Inspection Login Credentials

## ✅ Debug Stamp Removed

The "DEBUG" banner in the top-right corner has been removed for a clean, professional look.

---

## 🔑 Test Credentials

Your app is now using **MockAuthService** for testing with these inspection team credentials:

### Available Test Users

| Username          | Password   | Email                            |
| ----------------- | ---------- | -------------------------------- |
| `inspection_team` | `insp@123` | inspection_team@inspection.local |
| `inspector_01`    | `insp@123` | inspector_01@inspection.local    |
| `inspector_02`    | `insp@123` | inspector_02@inspection.local    |

---

## 🚀 Quick Test

1. **Run the app:**

   ```bash
   flutter run -d macos
   ```

2. **Enter credentials:**

   - Username: `inspection_team`
   - Password: `insp@123`

3. **Click LOGIN** → Dashboard opens ✓

---

## 📋 All Test Users

You can use any of these:

**User 1:**

```
Username: inspection_team
Password: insp@123
```

**User 2:**

```
Username: inspector_01
Password: insp@123
```

**User 3:**

```
Username: inspector_02
Password: insp@123
```

---

## 🔄 Switch to Production Backend

When ready to connect your backend, edit `lib/main.dart`:

```dart
// Change from:
final authService = MockAuthService();

// To:
const String backendBaseUrl = 'https://your-api-endpoint.com';
final authService = RestAuthService(baseUrl: backendBaseUrl);
```

---

## ✨ Summary

✅ Debug stamp removed
✅ Clean, professional UI
✅ Test credentials ready
✅ Easy backend switching

**Use any of the inspection credentials above to test!** 🎉
