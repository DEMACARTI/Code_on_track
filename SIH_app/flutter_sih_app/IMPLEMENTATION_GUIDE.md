# SIH App - Multi-Role Login & Dashboard System

## 📋 Project Overview

This Flutter application implements a secure multi-role authentication system with three distinct user roles, each with their own specialized dashboard interface:

1. **Inspection Management** - For tracking equipment and facility inspections

---

## 🏗️ Project Structure

```
lib/
├── main.dart                          # App entry point and route configuration
├── models/
│   └── user_model.dart               # User data model and authentication logic
└── pages/
    ├── login_page.dart               # Login interface (shared by all users)
    ├── dashboard_router.dart         # Routes users to their role-specific dashboard
  └── inspection_interface.dart     # Inspection management dashboard
```

---

## 🔐 User Credentials

The app comes with three pre-configured test users:

| Role       | Username    | Password  | Email                  |
| ---------- | ----------- | --------- | ---------------------- |
| Inspection | `insp_user` | `insp123` | inspection@example.com |

> **Note:** These are for testing only. In production, use proper authentication with secure password hashing and backend validation.

---

## 📱 Features

### Login Page (`login_page.dart`)

- Clean, modern UI with gradient background
- Username and password input validation
- Password visibility toggle
- Loading state during authentication
- Error message display
- Test credentials information displayed for easy testing

### Inspection Interface (`inspection_interface.dart`)

**Color Theme:** Green

**Features:**

- Dashboard with inspection statistics
- Status tracking (Passed, Failed, Pending, In Progress)
- Location-based inspection management
- Inspection type selection (Visual, Technical, Safety)
- Equipment ID tracking
- Notes and documentation support
- Create new inspection form

---

## 🔄 How the App Works

### 1. **Login Flow**

```
User Opens App
    ↓
Login Page Displays
    ↓
User Enters Credentials
    ↓
System Validates Against UserDatabase
    ↓
If Valid → Route to Role-Specific Dashboard
If Invalid → Show Error Message
```

### 2. **Dashboard Routing**

```
After Successful Login
    ↓
DashboardRouter Checks User Role
    ↓
Routes to Appropriate Interface:
└── UserRole.inspection → InspectionInterface
```

### 3. **Logout**

Users can logout from any dashboard interface using the menu button in the AppBar, which returns them to the login page.

---

## 📝 Implementation Details

### User Authentication (`user_model.dart`)

```dart
// User model
enum UserRole { inspection }

class User {
  final String username;
  final String email;
  final UserRole role;
  final String password;
}

// Authentication
class UserDatabase {
  static User? authenticate(String username, String password);
}
```

### Route Configuration (`main.dart`)

```dart
routes: {
  '/login': (context) => const LoginPage(),
  '/dashboard': (context) {
    final user = ModalRoute.of(context)?.settings.arguments as User?;
    return user != null ? DashboardRouter(user: user) : const LoginPage();
  },
}
```

---

## 🚀 Getting Started

### Prerequisites

- Flutter SDK (3.9.2 or higher)
- Dart SDK
- Any IDE (VS Code, Android Studio, IntelliJ IDEA)

### Installation

1. **Clone or download the project**

```bash
cd flutter_sih_app
```

2. **Get dependencies**

```bash
flutter pub get
```

3. **Run the app**

```bash
flutter run
```

### Testing the App

1. Launch the app
2. Use any of the test credentials provided
3. Explore the role-specific features
4. Use the logout button to return to login

---

## 🎨 UI Customization

Inspection interface uses a green color scheme:

- **Inspection:** Green (`Colors.green.shade700`)

To customize:

- Modify color values in the respective interface files
- Update AppBar background colors
- Change BottomNavigationBar colors
- Adjust card and button styling

---

## 🔒 Security Considerations

**Current Implementation (Testing Only):**

- Plain text password storage
- Mock database in-memory

**For Production, Add:**

1. ✅ Password hashing (bcrypt, argon2)
2. ✅ JWT token-based authentication
3. ✅ Secure backend API integration
4. ✅ Local secure storage (flutter_secure_storage)
5. ✅ HTTPS for all communications
6. ✅ Role-based access control (RBAC)
7. ✅ Session management
8. ✅ Password reset mechanism

---

## 🎯 Future Enhancements

### Phase 2

- [ ] Backend API integration
- [ ] Real-time data updates
- [ ] Cloud storage for documents
- [ ] Offline functionality
- [ ] Dark mode support

### Phase 3

- [ ] Advanced analytics
- [ ] Report generation
- [ ] Export functionality (PDF, Excel)
- [ ] Multi-language support
- [ ] Push notifications

### Phase 4

- [ ] Advanced user management
- [ ] Role-based permissions
- [ ] Audit logging
- [ ] Data synchronization
- [ ] Mobile app distribution

---

## 📚 Dependencies

Current dependencies (from pubspec.yaml):

```yaml
dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
```

### Recommended Future Dependencies

- `provider` - State management
- `http` or `dio` - API requests
- `flutter_secure_storage` - Secure data storage
- `get_it` - Service locator
- `firebase_auth` - Firebase authentication
- `charts_flutter` - Data visualization

---

## 🤝 Contributing

To add new features:

1. Create new files in appropriate directories
2. Follow the existing code structure
3. Ensure proper error handling
4. Add validation where necessary
5. Update this README with changes

---

## 📞 Support

For issues or questions:

1. Check the existing code comments
2. Review the Flutter documentation
3. Test with provided test credentials
4. Verify imports and file paths

---

## 📄 License

This project is part of the SIH (Smart Infrastructure Hub) initiative.

---

## 👤 Author

Created for the SIH Project

Last Updated: November 2024

---

## ✅ Quick Checklist

- [x] Login page with validation
- [x] Three user roles
- [x] Role-specific dashboards
- [x] Navigation between screens
- [x] Logout functionality
- [x] Error handling
- [x] Mock authentication database
- [x] Clean, modular code structure
- [ ] Backend integration (Future)
- [ ] Real data (Future)

---

Happy Coding! 🚀
