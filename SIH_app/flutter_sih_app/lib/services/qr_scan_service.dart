import 'dart:convert';
import 'package:http/http.dart' as http;

/// Model for QR scanned item details from backend
class ScannedItem {
  final String id;
  final String name;
  final String status;
  final String location;
  final String? details;
  final DateTime? lastUpdated;

  ScannedItem({
    required this.id,
    required this.name,
    required this.status,
    required this.location,
    this.details,
    this.lastUpdated,
  });

  factory ScannedItem.fromJson(Map<String, dynamic> json) {
    return ScannedItem(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? 'Unknown',
      status: json['status'] as String? ?? 'unknown',
      location: json['location'] as String? ?? 'N/A',
      details: json['details'] as String?,
      lastUpdated: json['last_updated'] != null
          ? DateTime.tryParse(json['last_updated'] as String)
          : null,
    );
  }
}

/// Service to handle QR code scanning and backend validation
abstract class QRScanService {
  /// Scan QR code data and validate with backend
  /// Returns ScannedItem if found, null if not found or error
  Future<ScannedItem?> scanQRCode(String qrData);

  /// Upload inspection result with remark and optional photo
  /// Returns true if upload successful, false otherwise
  Future<bool> uploadInspection({
    required String qrId,
    required String status,
    required String remark,
    String? photoPath,
  });
}

/// REST-backed QR scan service
class RestQRScanService implements QRScanService {
  final String baseUrl;
  final http.Client httpClient;
  final String endpoint;

  RestQRScanService({
    required this.baseUrl,
    http.Client? client,
    this.endpoint = '/qr/scan',
  }) : httpClient = client ?? http.Client();

  @override
  Future<ScannedItem?> scanQRCode(String qrData) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      final resp = await httpClient
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'qr_code': qrData}),
          )
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        return ScannedItem.fromJson(data);
      } else if (resp.statusCode == 404) {
        return null;
      }
    } catch (e) {
      // Network or parsing error
    }
    return null;
  }

  @override
  Future<bool> uploadInspection({
    required String qrId,
    required String status,
    required String remark,
    String? photoPath,
  }) async {
    final uri = Uri.parse('$baseUrl/qr/inspection');
    var request = http.MultipartRequest('POST', uri);
    request.fields['qr_id'] = qrId;
    request.fields['status'] = status;
    request.fields['remark'] = remark;
    if (photoPath != null) {
      request.files.add(await http.MultipartFile.fromPath('photo', photoPath));
    }
    try {
      final streamed = await request.send();
      if (streamed.statusCode == 200) {
        return true;
      }
    } catch (e) {
      // Upload error
    }
    return false;
  }

  /// Upload an image and let backend decode the QR from the image.
  /// This method is optional and may not be available on all implementations.
  Future<ScannedItem?> scanQRCodeFromImage(String imagePath) async {
    final uri = Uri.parse('$baseUrl/qr/scan-image');
    var request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('image', imagePath));
    try {
      final streamed = await request.send();
      final resp = await http.Response.fromStream(streamed);
      if (streamed.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        return ScannedItem.fromJson(data);
      } else if (streamed.statusCode == 404) {
        return null;
      }
    } catch (e) {
      // network or parsing error
    }
    return null;
  }
}

/// Mock QR scan service for testing
class MockQRScanService implements QRScanService {
  final Map<String, Map<String, dynamic>> _mockDatabase = {
    'QR001': {
      'id': 'QR001',
      'name': 'Fire Extinguisher - Lobby',
      'status': 'operational',
      'location': 'Main Lobby',
      'details': 'Fire extinguisher checked and operational',
      'last_updated': DateTime.now().toString(),
    },
    'QR002': {
      'id': 'QR002',
      'name': 'Emergency Light - Corridor A',
      'status': 'operational',
      'location': 'Corridor A',
      'details': 'Emergency lighting system functional',
      'last_updated': DateTime.now().toString(),
    },
    'QR003': {
      'id': 'QR003',
      'name': 'Safety Equipment - Storage',
      'status': 'needs_maintenance',
      'location': 'Storage Room',
      'details': 'Equipment requires maintenance',
      'last_updated': DateTime.now().toString(),
    },
  };

  @override
  Future<ScannedItem?> scanQRCode(String qrData) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 600));

    final itemData = _mockDatabase[qrData];
    if (itemData != null) {
      return ScannedItem.fromJson(itemData);
    }

    return null; // QR code not found
  }

  @override
  Future<bool> uploadInspection({
    required String qrId,
    required String status,
    required String remark,
    String? photoPath,
  }) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));
    // Always succeed for mock
    return true;
  }

  /// For mock service, optionally support image scanning (simple stub)
  Future<ScannedItem?> scanQRCodeFromImage(String imagePath) async {
    await Future.delayed(const Duration(milliseconds: 300));
    // Basic heuristic for mock: if filename contains a known ID, return it.
    final lower = imagePath.toLowerCase();
    for (final k in _mockDatabase.keys) {
      if (lower.contains(k.toLowerCase())) {
        return ScannedItem.fromJson(_mockDatabase[k]!);
      }
    }
    return null;
  }
}
