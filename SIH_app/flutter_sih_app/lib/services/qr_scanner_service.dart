import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'api_service.dart';

class QRScannerService {
  final ApiService _apiService = ApiService();
  final MobileScannerController controller = MobileScannerController();

  // Scan QR code and get item details
  Future<Map<String, dynamic>> scanAndFetchItem(String qrData) async {
    try {
      // Parse QR code data
      String uid;
      
      // Check if QR data is JSON or plain UID
      if (qrData.startsWith('{')) {
        // JSON format
        final data = parseQRData(qrData);
        uid = data['uid'] ?? '';
      } else if (qrData.startsWith('http')) {
        // URL format: http://localhost:8000/scan/IRF-XXX-XXX
        uid = qrData.split('/').last;
      } else {
        // Plain UID
        uid = qrData;
      }

      if (uid.isEmpty) {
        return {'success': false, 'error': 'Invalid QR code'};
      }

      // Fetch item details from database
      return await _apiService.getItemByUid(uid);
    } catch (e) {
      return {'success': false, 'error': 'Failed to process QR code: $e'};
    }
  }

  // Parse JSON QR data
  Map<String, dynamic> parseQRData(String jsonString) {
    try {
      return Map<String, dynamic>.from(
        Map.castFrom(
          jsonDecode(jsonString),
        ),
      );
    } catch (e) {
      return {};
    }
  }

  // Show QR scanner dialog
  Future<String?> showQRScanner(BuildContext context) async {
    String? scannedData;

    await showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Container(
          height: 400,
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Scan QR Code',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: MobileScanner(
                    controller: controller,
                    onDetect: (capture) {
                      final barcodes = capture.barcodes;
                      for (final barcode in barcodes) {
                        if (barcode.rawValue != null) {
                          scannedData = barcode.rawValue;
                          Navigator.pop(context);
                          break;
                        }
                      }
                    },
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Position QR code within the frame',
                style: TextStyle(color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );

    return scannedData;
  }

  // Toggle flashlight
  void toggleFlash() {
    controller.toggleTorch();
  }

  // Switch camera
  void switchCamera() {
    controller.switchCamera();
  }

  // Dispose controller
  void dispose() {
    controller.dispose();
  }
}
