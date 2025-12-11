import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Backend URL - change this to your server IP for physical device
  static const String baseUrl = 'http://16.171.32.31:8000';

  // Check connection to backend
  Future<Map<String, dynamic>> checkConnection() async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 5);
      final request = await client.getUrl(Uri.parse('$baseUrl/health'));
      final response = await request.close().timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        return {'connected': true, 'message': 'Connected to server'};
      } else {
        return {'connected': false, 'message': 'Server error ${response.statusCode}'};
      }
    } catch (e) {
      return {'connected': false, 'message': 'Cannot reach server'};
    } finally {
      client?.close();
    }
  }

  // Login using dart:io HttpClient
  Future<Map<String, dynamic>> login(String username, String password) async {
    HttpClient? client;
    try {
      print('=== FLUTTER LOGIN ATTEMPT ===');
      print('URL: $baseUrl/api/auth/login');
      print('Username: "$username"');
      
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 15);
      
      // Create POST request
      final uri = Uri.parse('$baseUrl/api/auth/login');
      final request = await client.postUrl(uri);
      
      // Set headers
      request.headers.contentType = ContentType.json;
      request.headers.set('Accept', 'application/json');
      
      // Create and write body
      final body = jsonEncode({
        'username': username.trim(),
        'password': password.trim(),
      });
      print('Body: $body');
      request.write(body);
      
      // Get response
      final response = await request.close().timeout(const Duration(seconds: 15));
      final responseBody = await response.transform(utf8.decoder).join();
      
      print('Status: ${response.statusCode}');
      print('Response: $responseBody');

      if (response.statusCode == 200) {
        final data = jsonDecode(responseBody);
        
        // Save token and user info
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', data['token'] ?? '');
        await prefs.setString('username', data['user']['username'] ?? '');
        await prefs.setString('department', data['user']['department'] ?? '');
        
        print('SUCCESS: Logged in as ${data['user']['username']}');
        return {'success': true, 'data': data};
      } else {
        String errorMsg = 'Login failed';
        try {
          final errorData = jsonDecode(responseBody);
          errorMsg = errorData['detail'] ?? responseBody;
        } catch (_) {
          errorMsg = responseBody.isNotEmpty ? responseBody : 'Unknown error';
        }
        print('FAILED: $errorMsg');
        return {'success': false, 'error': errorMsg};
      }
    } on TimeoutException {
      print('ERROR: Timeout');
      return {'success': false, 'error': 'Connection timeout'};
    } on SocketException catch (e) {
      print('ERROR: Socket - $e');
      return {'success': false, 'error': 'Cannot connect to server'};
    } catch (e) {
      print('ERROR: $e');
      return {'success': false, 'error': 'Error: $e'};
    } finally {
      client?.close();
    }
  }

  // Get item by UID from QR code
  Future<Map<String, dynamic>> getItemByUid(String uid) async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final request = await client.getUrl(Uri.parse('$baseUrl/api/items/$uid'));
      request.headers.set('Content-Type', 'application/json');
      request.headers.set('Authorization', 'Bearer $token');
      
      final response = await request.close();
      final responseBody = await response.transform(utf8.decoder).join();

      if (response.statusCode == 200) {
        final data = jsonDecode(responseBody);
        return {'success': true, 'item': data};
      } else if (response.statusCode == 404) {
        return {'success': false, 'error': 'Item not found'};
      } else {
        return {'success': false, 'error': 'Failed to fetch item'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    } finally {
      client?.close();
    }
  }

  // Get all items
  Future<Map<String, dynamic>> getAllItems() async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final request = await client.getUrl(Uri.parse('$baseUrl/api/items'));
      request.headers.set('Content-Type', 'application/json');
      request.headers.set('Authorization', 'Bearer $token');
      
      final response = await request.close();
      final responseBody = await response.transform(utf8.decoder).join();

      if (response.statusCode == 200) {
        final data = jsonDecode(responseBody);
        return {'success': true, 'items': data};
      } else {
        return {'success': false, 'error': 'Failed to fetch items'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    } finally {
      client?.close();
    }
  }

  // Update item status
  Future<Map<String, dynamic>> updateItemStatus(
      String uid, String status) async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final request = await client.putUrl(Uri.parse('$baseUrl/api/items/$uid'));
      request.headers.contentType = ContentType.json;
      request.headers.set('Authorization', 'Bearer $token');
      request.write(jsonEncode({'current_status': status}));
      
      final response = await request.close();
      final responseBody = await response.transform(utf8.decoder).join();

      if (response.statusCode == 200) {
        final data = jsonDecode(responseBody);
        return {'success': true, 'item': data};
      } else {
        return {'success': false, 'error': 'Failed to update item'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    } finally {
      client?.close();
    }
  }

  // Logout
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    return token != null && token.isNotEmpty;
  }

  // Get current user info
  Future<Map<String, String?>> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'username': prefs.getString('username'),
      'department': prefs.getString('department'),
    };
  }

  // ============================================================================
  // AI INSPECTION PIPELINE
  // ============================================================================

  /// Inspect a component using the multi-model AI pipeline
  /// 1. YOLO detects component type
  /// 2. ResNet classifies condition/defects
  /// 
  /// Returns inspection result with component type, condition, defects, recommendations
  Future<Map<String, dynamic>> inspectComponent(String base64Image, {String? componentType}) async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 30);
      
      final uri = Uri.parse('$baseUrl/api/inspect-component');
      final request = await client.postUrl(uri);
      
      request.headers.contentType = ContentType.json;
      request.headers.set('Accept', 'application/json');
      
      final body = jsonEncode({
        'image_base64': base64Image,
        if (componentType != null) 'component_type': componentType,
      });
      request.write(body);
      
      final response = await request.close().timeout(const Duration(seconds: 30));
      final responseBody = await response.transform(utf8.decoder).join();
      
      if (response.statusCode == 200) {
        final data = jsonDecode(responseBody);
        return {
          'success': data['success'] ?? false,
          'component_type': data['component_type'],
          'component_class': data['component_class'],
          'condition': data['condition'],
          'defects': data['defects'] ?? [],
          'recommendations': data['recommendations'] ?? [],
          'detection_confidence': data['detection_confidence'],
          'error': data['error'],
        };
      } else {
        return {
          'success': false,
          'error': 'Server error: ${response.statusCode}',
        };
      }
    } on TimeoutException {
      return {'success': false, 'error': 'Request timeout - please try again'};
    } on SocketException catch (e) {
      return {'success': false, 'error': 'Cannot connect to server: $e'};
    } catch (e) {
      return {'success': false, 'error': 'Inspection error: $e'};
    } finally {
      client?.close();
    }
  }

  /// Get pipeline status - check which models are loaded
  Future<Map<String, dynamic>> getPipelineStatus() async {
    HttpClient? client;
    try {
      client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      
      final request = await client.getUrl(Uri.parse('$baseUrl/api/pipeline-status'));
      final response = await request.close();
      final responseBody = await response.transform(utf8.decoder).join();
      
      if (response.statusCode == 200) {
        return jsonDecode(responseBody);
      } else {
        return {'available': false, 'error': 'Server error'};
      }
    } catch (e) {
      return {'available': false, 'error': 'Connection error: $e'};
    } finally {
      client?.close();
    }
  }
}
