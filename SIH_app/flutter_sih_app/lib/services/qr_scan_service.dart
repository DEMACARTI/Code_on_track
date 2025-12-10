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
  // Optional metadata fields from backend
  final String? material;
  final String? lotNo;
  final String? vendorId;
  final String? batch;

  ScannedItem({
    required this.id,
    required this.name,
    required this.status,
    required this.location,
    this.details,
    this.lastUpdated,
    this.material,
    this.lotNo,
    this.vendorId,
    this.batch,
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
      material: json['material'] as String?,
      lotNo: json['lot_no'] as String? ?? json['lotNo'] as String?,
      vendorId: json['vendor_id'] as String? ?? json['vendorId'] as String?,
      batch: json['batch'] as String?,
    );
  }
}

/// Service to handle QR code scanning and backend validation
abstract class QRScanService {
  /// Get the base URL for the backend API
  String get baseUrl;

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

  RestQRScanService({
    required this.baseUrl,
    http.Client? client,
  }) : httpClient = client ?? http.Client();

  @override
  Future<ScannedItem?> scanQRCode(String qrData) async {
    try {
      // Extract UID from QR data (could be JSON, URL, or plain UID)
      String uid = qrData;
      
      // If QR data is JSON, extract UID
      if (qrData.trim().startsWith('{')) {
        final jsonData = jsonDecode(qrData);
        uid = jsonData['uid'] ?? qrData;
      } 
      // If QR data is URL, extract UID from path
      else if (qrData.startsWith('http')) {
        uid = Uri.parse(qrData).pathSegments.last;
      }

      // Call backend API to get item details
      final uri = Uri.parse('$baseUrl/api/items/$uid');
      final resp = await httpClient
          .get(
            uri,
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        
        // Map backend response to ScannedItem
        return ScannedItem(
          id: data['uid'] ?? uid,
          name: '${data['component_type']} - ${data['lot_number']}',
          status: data['current_status'] ?? 'unknown',
          location: 'Warehouse', // Default location
          details: 'Vendor: ${data['vendor_id']}, Warranty: ${data['warranty_years']} years',
          lastUpdated: data['created_at'] != null 
              ? DateTime.tryParse(data['created_at'])
              : null,
          material: data['component_type'],
          lotNo: data['lot_number'],
          vendorId: data['vendor_id']?.toString(),
          batch: data['lot_number'],
        );
      } else if (resp.statusCode == 404) {
        return null;
      }
    } catch (e) {
      print('Error scanning QR: $e');
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
    try {
      final resp = await httpClient
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'qr_id': qrId,
              'status': status,
              'remark': remark,
            }),
          )
          .timeout(const Duration(seconds: 10));
      
      print('Inspection upload response: ${resp.statusCode} - ${resp.body}');
      
      if (resp.statusCode == 200) {
        return true;
      }
    } catch (e) {
      print('Inspection upload error: $e');
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
  @override
  String get baseUrl => 'http://localhost:8000'; // Mock base URL

  final Map<String, Map<String, dynamic>> _mockDatabase = {
    'QR001': {
      'id': 'QR001',
      'name': 'Fire Extinguisher - Lobby',
      'status': 'operational',
      'location': 'Main Lobby',
      'details': 'Fire extinguisher checked and operational',
      'material': 'Extinguisher Model X',
      'lot_no': 'L-001',
      'vendor_id': 'VEND-100',
      'batch': 'BATCH-A1',
      'last_updated': DateTime.now().toString(),
    },
    'QR002': {
      'id': 'QR002',
      'name': 'Emergency Light - Corridor A',
      'status': 'operational',
      'location': 'Corridor A',
      'details': 'Emergency lighting system functional',
      'material': 'EmergencyLight-Z',
      'lot_no': 'L-221',
      'vendor_id': 'VEND-203',
      'batch': 'BATCH-C3',
      'last_updated': DateTime.now().toString(),
    },
    'QR003': {
      'id': 'QR003',
      'name': 'Safety Equipment - Storage',
      'status': 'needs_maintenance',
      'location': 'Storage Room',
      'details': 'Equipment requires maintenance',
      'material': 'SafetyKit-9',
      'lot_no': 'L-900',
      'vendor_id': 'VEND-330',
      'batch': 'BATCH-X',
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
