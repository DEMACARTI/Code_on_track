import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

/// Abstract authentication service. Implement this for your backend.
abstract class AuthService {
  /// Authenticate with backend and return a User on success, or null on failure.
  Future<User?> authenticate(String username, String password);
}

/// REST-backed implementation. Configure `baseUrl` to your API endpoint.
///
/// **INTEGRATION GUIDE:**
/// 1. Set baseUrl to your backend API root (e.g., 'https://api.yourcompany.com')
/// 2. Your backend should implement: POST /auth/login
/// 3. Request format: { "username": "...", "password": "..." }
/// 4. Success response (200): { "username": "...", "email": "..." }
/// 5. Failure response (any other status): Return null
///
/// **Optional customizations:**
/// - Override headers() method to add authorization
/// - Override parseResponse() to handle custom response formats
/// - Use endpoint parameter to change default '/auth/login'
class RestAuthService implements AuthService {
  final String baseUrl;
  final http.Client httpClient;
  final String endpoint;

  RestAuthService({
    required this.baseUrl,
    http.Client? client,
    this.endpoint = '/auth/login',
  }) : httpClient = client ?? http.Client();

  /// Get HTTP headers for requests. Override to customize (e.g., add auth tokens).
  Map<String, String> headers() {
    return {'Content-Type': 'application/json'};
  }

  /// Parse and validate authentication response. Override to handle custom formats.
  User? parseResponse(Map<String, dynamic> data) {
    final username = data['username'] as String?;
    final email = data['email'] as String?;

    if (username == null) {
      return null; // Invalid response
    }

    return User(username: username, email: email ?? '');
  }

  @override
  Future<User?> authenticate(String username, String password) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      final resp = await httpClient
          .post(
            uri,
            headers: headers(),
            body: jsonEncode({'username': username, 'password': password}),
          )
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        return parseResponse(data);
      }
    } catch (e) {
      // Network or parsing error - return null (fail silently)
      // For debugging, uncomment: debugPrint('Authentication error: $e');
    }

    return null;
  }
}

/// Mock service for local development/testing. Remove in production.
class MockAuthService implements AuthService {
  // Inspection team credentials for testing
  final Map<String, String> _credentials = {
    'inspection_team': 'insp@123',
    'inspector_01': 'insp@123',
    'inspector_02': 'insp@123',
  };

  @override
  Future<User?> authenticate(String username, String password) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 800));

    // Validate against inspection credentials
    final storedPassword = _credentials[username];
    if (storedPassword != null && storedPassword == password) {
      return User(username: username, email: '$username@inspection.local');
    }

    return null;
  }
}
