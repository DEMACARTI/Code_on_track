import 'package:flutter/material.dart';
import 'models/user_model.dart';
import 'pages/login_page.dart';
import 'pages/qr_scan_dashboard_impl.dart';
import 'theme/app_theme.dart';
import 'services/auth_service.dart';
import 'services/qr_scan_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // ============================================================
    // BACKEND CONFIGURATION
    // ============================================================
    // Production: Use RestAuthService and RestQRScanService
    // Render cloud deployment - works on any device with internet
    const String backendBaseUrl = 'http://16.171.32.31:8000';
    final authService = RestAuthService(baseUrl: backendBaseUrl);
    final qrService = RestQRScanService(baseUrl: backendBaseUrl);

    // For testing with mock data: Uncomment below
    // final authService = MockAuthService();
    // final qrService = MockQRScanService();

    return MaterialApp(
      title: 'Rail_Chinh',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      // Apply the login background gradient app-wide behind routes
      builder: (context, child) =>
          Container(decoration: appBackgroundDecoration, child: child),
      home: LoginPage(authService: authService),
      routes: {
        '/login': (context) => LoginPage(authService: authService),
        '/dashboard': (context) {
          final user = ModalRoute.of(context)?.settings.arguments as User?;
          if (user != null) {
            return QRScanDashboard(user: user, qrService: qrService);
          }
          return LoginPage(authService: authService);
        },
      },
      onUnknownRoute: (settings) {
        return MaterialPageRoute(
          builder: (context) => LoginPage(authService: authService),
        );
      },
    );
  }
}
