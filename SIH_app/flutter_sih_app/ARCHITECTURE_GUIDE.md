# SIH App - Visual Architecture Guide (Updated for QR Scanner)

## 🎯 Application Flow Diagram - NEW SYSTEM

```
┌─────────────────────────────────────────────────────────────────┐
│                        App Initialization                        │
│                      (main.dart - main())                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   MyApp Widget   │
                    │  (Injection)     │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌─────────────┐  ┌──────────┐
        │  Auth    │  │  QRService  │  │ MockData │
        │ Service  │  │  Injection  │  │   Init   │
        └────┬─────┘  └──────┬──────┘  └──────────┘
             │               │
             └───────┬───────┘
                     │
                     ▼
            ┌──────────────────┐
            │   LoginPage      │
            │  (home route)    │
            └────────┬─────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐      ┌──────────────┐
    │Invalid User │      │Valid: User   │
    │Show Error   │      │inspection_   │
    │Re-show Login│      │team          │
    └─────────────┘      └──────┬───────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   QRScanDashboard    │
                    │   (NEW!)             │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
  ┌──────────────┐      ┌─────────────┐    ┌──────────────┐
  │📷 Camera     │      │🔗 QR Service│    │📊 Status Box │
  │Real-time     │      │Backend call │    │Color-coded   │
  │Detection     │      │Validation   │    │Results       │
  └──────┬───────┘      └──────┬──────┘    └──────────────┘
         │                     │
         └─────────┬───────────┘
                   │
         ┌─────────▼──────────┐
         │ Item Found?        │
         └──────┬──────┬──────┘
               Yes     No
                │       │
                ▼       ▼
          ┌────────┐  ┌──────────┐
          │Show    │  │Show Error│
          │Details │  │Not Found │
          └────┬───┘  └────┬─────┘
               │           │
               │    ┌──────┘
               │    │
               └────┼─────────────┐
                    │             │
                    ▼             ▼
            ┌─────────────┐  ┌──────────┐
            │ Auto-resume │  │Logout    │
            │ Scanning    │  │Menu      │
            └─────┬───────┘  └────┬─────┘
                  │               │
                  │               ▼
                  │          ┌────────────┐
                  │          │ LoginPage  │
                  │          │ (Again)    │
                  │          └────────────┘
                  │
                  └─ [Repeat Scan Cycle]
```

---

## 📂 File Structure Explanation - NEW SYSTEM

### Core Configuration Files

#### `main.dart`

- **Purpose:** Application entry point and dependency injection
- **Key Components:**
  - `main()` function - Launches the app
  - `MyApp` widget - Service injection & theme
  - `MockAuthService` - Test credentials injection
  - `MockQRScanService` - Test QR data injection
  - Route definitions for `/login` and `/dashboard`
- **New Feature:** Injects both Auth and QR services
- **Easy Switch:** One-line change from Mock to Production

```dart
// Testing (current):
final authService = MockAuthService();
final qrService = MockQRScanService();

// Production (uncomment):
// final authService = RestAuthService(baseUrl: '...');
// final qrService = RestQRScanService(baseUrl: '...');
```

### Data Models

#### `models/user_model.dart`

- **Purpose:** User data structure
- **Changes from old system:**
  - ❌ Removed: `UserRole` enum (only one role now)
  - ❌ Removed: `UserDatabase` (backend handles it)
  - ✅ Kept: `User` class (username, email)
- **Usage:** Passed to dashboard after login

### Services - NEW ARCHITECTURE

#### `services/auth_service.dart`

**Abstract Layer:**

```dart
abstract class AuthService {
  Future<User?> authenticate(String username, String password);
}
```

**Two Implementations:**

1. **RestAuthService** (Production)

   - Makes HTTP POST to backend `/auth/login`
   - Customizable headers & endpoints
   - Proper error handling
   - 10-second timeout

2. **MockAuthService** (Testing)
   - Local credentials: `inspection_team` / `insp@123`
   - Simulates network delay
   - Perfect for development

#### `services/qr_scan_service.dart` (NEW!)

**Abstract Layer:**

```dart
abstract class QRScanService {
  Future<ScannedItem?> scanQRCode(String qrData);
}
```

**Components:**

```dart
class ScannedItem {
  final String id;
  final String name;
  final String status;      // "operational", "needs_maintenance", "non_operational"
  final String location;
  final String? details;
  final DateTime? lastUpdated;
}
```

**Two Implementations:**

1. **RestQRScanService** (Production)

   - HTTP POST to backend `/qr/scan`
   - Sends: `{ "qr_code": "QR001" }`
   - Receives: `ScannedItem` data
   - Customizable response parsing

2. **MockQRScanService** (Testing)
   - 3 test QR codes included
   - Local data validation
   - Fast for demos

### Pages - SIMPLIFIED SYSTEM

#### `pages/login_page.dart` (UPDATED)

```
┌─────────────────────────────────┐
│      Login Page Layout          │
├─────────────────────────────────┤
│  [🔐 Icon] SIH Dashboard        │
│      Smart Infrastructure       │
│          Inspection             │
├─────────────────────────────────┤
│      ┌───────────────────┐      │
│      │ Username Field    │      │
│      ├───────────────────┤      │
│      │ Password Field    │      │
│      │ [Eye Icon]        │      │
│      ├───────────────────┤      │
│      │ [LOGIN] Button    │      │
│      │ (Loading state)   │      │
│      └───────────────────┘      │
│                                 │
│  [Error Message if needed]      │
│                                 │
│  ℹ️ One login role:             │
│     inspection_team / insp@123  │
│                                 │
└─────────────────────────────────┘
```

**Changes:**

- ✅ Single role (inspection team)
- ✅ Clean, focused login
- ❌ Removed test credentials display box
- ✅ Uses named route navigation

#### `pages/qr_scan_dashboard.dart` (NEW!)

```
┌──────────────────────────────────────┐
│  🔍 QR Scanner - Inspection      👤  │ ← AppBar with user info
├──────────────────────────────────────┤
│                                      │
│          📷 Camera View              │
│          (60% of screen)             │
│                                      │
│      Real-time QR Detection         │
│      [Auto-scanning...]             │
│                                      │
├──────────────────────────────────────┤
│  Status & Details (40% of screen)    │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ 🟢 Item Operational          │   │ ← Color-coded status
│  │ Item found in database       │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ ID: QR001                    │   │
│  │ Fire Extinguisher - Lobby    │   │ ← Item Details Card
│  │ 📍 Main Lobby  [OPERATIONAL] │   │
│  │ Fire extinguisher checked    │   │
│  │ Last: 2025-11-12 10:30       │   │
│  └──────────────────────────────┘   │
│                                      │
├──────────────────────────────────────┤
│         [▶ Pause Camera] FAB         │ ← Play/Pause button
└──────────────────────────────────────┘
```

**Features:**

- 📷 Real-time camera scanning
- 🔗 Backend validation
- 🎨 Color-coded status
- 📋 Item information
- ⏸️ Pause/Resume

---

## 🔄 Authentication Flow - NEW

### Step 1: User Submission

```
User enters credentials
         ↓
  Validate non-empty
         ↓
   Send to backend
```

### Step 2: Backend Verification

```
RestAuthService.authenticate()
         ↓
    POST /auth/login
         ↓
   Backend validates
         ↓
   User found?
      /      \
    Yes       No
     ↓        ↓
  Return   Return
   User     null
```

### Step 3: Navigation

```
user != null?
   /         \
 Yes          No
  ↓           ↓
Route     Show error
to        message
QR Scan   & retry
Dashboard
```

---

## 🔍 QR Scanning Flow - NEW

### Step 1: QR Detection

```
Camera continuously scanning
         ↓
   QR code detected?
         ↓
    Extract QR data
         ↓
   Pause camera
```

### Step 2: Backend Validation

```
QRScanService.scanQRCode(qrData)
         ↓
    POST /qr/scan
         ↓
   Backend lookup
         ↓
   QR found?
      /      \
    Yes       No
     ↓        ↓
  Parse    Return
  JSON     null
```

### Step 3: Display Results

```
Item found?
   /       \
 Yes        No
  ↓         ↓
Display   Show
Details   Error
  ↓         ↓
  └─┬─────┬─┘
    │     │
    ▼     ▼
Auto-resume scanning
(after 2 seconds)
```

---

## 📊 Service Dependency Injection

```
main.dart
   │
   ├─ MockAuthService()
   │   └─ Returns: User(username, email)
   │
   ├─ MockQRScanService()
   │   └─ Returns: ScannedItem(id, name, status, ...)
   │
   ├─ LoginPage(authService: ...)
   │   └─ Receives injected AuthService
   │
   └─ QRScanDashboard(qrService: ...)
       └─ Receives injected QRScanService
```

---

## 🎨 State Management

### Simple Widget State

**LoginPage (\_LoginPageState)**

- `_usernameController` - Text input
- `_passwordController` - Text input
- `_isLoading` - Loading indicator
- `_obscurePassword` - Password visibility
- `_errorMessage` - Error display

**QRScanDashboard (\_QRScanDashboardState)**

- `cameraController` - Mobile scanner
- `scannedItem` - Current item found
- `isScanning` - Scan in progress
- `errorMessage` - Error display
- `cameraRunning` - Camera state

---

## � Backend Integration Points

### Authentication

```
POST /auth/login
Response: { "username": "...", "email": "..." }
```

### QR Scanning

```
POST /qr/scan
Response: {
  "id": "...",
  "name": "...",
  "status": "operational",
  "location": "...",
  "details": "...",
  "last_updated": "..."
}
```

---

## 📱 Navigation Structure - SIMPLIFIED

```
MyApp
├─ /login
│  └─ LoginPage
│     └─ Authenticate
│
├─ /dashboard
│  └─ QRScanDashboard
│     └─ Scan QR codes
│
└─ onUnknownRoute
   └─ Redirect to /login
```

---

## ✅ BEFORE vs AFTER Comparison

| Aspect               | Before (Old)                          | After (New)              |
| -------------------- | ------------------------------------- | ------------------------ |
| **Roles**            | 1 (Inspection only) | 1 (Inspection only)      |
| **Dashboards**       | 3 different interfaces                | 1 QR scanner dashboard   |
| **Primary Function** | Role-based management                 | QR scanning & validation |
| **Database**         | Mock with 3 user roles                | Backend API validation   |
| **Backend Ready**    | Basic login                           | Full REST API            |
| **Complexity**       | Multi-role routing                    | Single-flow scanning     |
| **Files**            | 8+ interface files                    | 2 core interface files   |
| **Services**         | Auth only                             | Auth + QR Scanning       |
| **Test Data**        | 3 user credentials                    | 3 QR codes               |
| **UI Focus**         | Dashboard stats                       | Camera + Status display  |

---

## 🎯 Key Architecture Improvements

✅ **Simpler** - Single role, single flow
✅ **Cleaner** - Removed multi-role complexity
✅ **Focused** - QR scanning is primary function
✅ **Extensible** - Service abstraction for customization
✅ **Production-Ready** - REST API integration built-in
✅ **Testable** - Mock services for development
✅ **Maintainable** - Clear separation of concerns

---

## 📚 Related Files

- `lib/main.dart` - Dependency injection
- `lib/pages/login_page.dart` - Authentication UI
- `lib/pages/qr_scan_dashboard.dart` - Scanner UI
- `lib/services/auth_service.dart` - Auth services
- `lib/services/qr_scan_service.dart` - QR services
- `lib/models/user_model.dart` - Data models

---

**This is the new, streamlined architecture for your QR scanning inspection app!** 🎉

## 🎨 Color Scheme

| Component  | Inventory    | Inspection    | Monitoring     |
| ---------- | ------------ | ------------- | -------------- |
| Primary    | Blue 700     | Green 700     | Purple 700     |
| AppBar     | Blue 700     | Green 700     | Purple 700     |
| BottomNav  | Blue 700     | Green 700     | Purple 700     |
| Gradient   | Blue 600-800 | Green 600-800 | Purple 600-800 |
| Stat Cards | Varies       | Varies        | Varies         |

---

## 📊 Navigation Tree

```
LoginPage (/)
│       ├── Dashboard Tab
│       │   └── StatCards + Overview
│       │   └── ItemsList
│       └── Add Item Tab
│           └── Form
├── Inspection Role
│   └── InspectionInterface (/dashboard)
│       ├── Dashboard Tab
│       │   └── Stats + Overview
│       ├── Inspections Tab
│       │   └── InspectionsList
│       └── New Inspection Tab
│           └── Form
        ├── Dashboard Tab
        │   └── Metrics + Status
        ├── Metrics Tab
        │   └── HistoricalData
        └── Alerts Tab
            └── AlertsList
```

---

## 🔄 State Management

Current: StatefulWidget (local state)

### Current Implementation

```dart
  int _selectedIndex = 0;  // Tracks bottom nav selection

  // IndexedStack shows different widgets based on _selectedIndex
}
```

### Future Enhancements

- Provider package for global state
- GetIt for service locator
- Riverpod for reactive programming

---

## 🛡️ Error Handling

### Login Errors

```
Invalid Credentials
    ↓
└─ Show SnackBar
└─ Display error message in form
└─ Clear password field (optional)
└─ Allow retry
```

### Navigation Errors

```
Route not found
    ↓
Fallback to LoginPage
```

---

## 📱 Responsive Design

### Current Breakpoints

- Mobile: All screens (No specific responsive design)
- Tablet: Supported via default Flutter scaling

### Future Improvements

- MediaQuery for responsive layouts
- Adaptive widgets for tablet/desktop
- Split view for landscape mode

---

## 🧪 Testing the App


```
1. Launch app → LoginPage
2. Enter: insp_user / insp123
3. Tap LOGIN
4. Verify: InspectionInterface displays (Green theme)
5. Check statistics and status updates
6. Logout and return
```


```
1. Enter: invalid_user / wrongpass
2. Tap LOGIN
3. Verify: Error message displays
4. Clear and retry with correct credentials
```

---

## 📚 Key Dart Concepts Used

1. **Enums** - `UserRole` for role classification
2. **Classes** - `User`, `UserDatabase` data models
3. **Static Methods** - `UserDatabase.authenticate()`
4. **StatefulWidget** - Interactive UI components
5. **IndexedStack** - Efficient tab/page switching
6. **Navigation** - Named routes and arguments
7. **Form Validation** - TextFormField with validators
8. **Async/Await** - Login simulation delay

---

## 🚀 Performance Considerations

- **Mock Database:** In-memory (instant)
- **Navigation:** Efficient with `pushNamedAndRemoveUntil`
- **UI Updates:** Local setState only
- **Asset Loading:** Minimal (no large assets)

---

## ✨ UI/UX Highlights

✅ Gradient backgrounds for visual appeal
✅ Smooth transitions and animations
✅ Clear error messages
✅ Loading state feedback
✅ Intuitive navigation
✅ Color-coded role identification
✅ Responsive card layouts
✅ Professional typography

---

This guide provides a complete visual overview of the app architecture and flow!
