import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Computer IP address for API connection
  static const String baseUrl = 'http://10.12.76.248:8000';
  
  // Authentication endpoints
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Save token and user info
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', data['token'] ?? '');
        await prefs.setString('username', data['user']['username'] ?? '');
        await prefs.setString('department', data['user']['department'] ?? '');
        
        return {'success': true, 'data': data};
      } else {
        return {
          'success': false,
          'error': 'Login failed: ${response.body}'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  // Get item by UID from QR code
  Future<Map<String, dynamic>> getItemByUid(String uid) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final response = await http.get(
        Uri.parse('$baseUrl/api/items/$uid'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'item': data};
      } else if (response.statusCode == 404) {
        return {'success': false, 'error': 'Item not found'};
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch item: ${response.body}'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  // Get all items
  Future<Map<String, dynamic>> getAllItems() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final response = await http.get(
        Uri.parse('$baseUrl/api/items'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'items': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to fetch items: ${response.body}'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  // Update item status
  Future<Map<String, dynamic>> updateItemStatus(
      String uid, String status) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final response = await http.put(
        Uri.parse('$baseUrl/api/items/$uid'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'current_status': status}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {'success': true, 'item': data};
      } else {
        return {
          'success': false,
          'error': 'Failed to update item: ${response.body}'
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
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
}
