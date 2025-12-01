import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'item_details_page.dart';
import '../theme/app_theme.dart';

import '../models/user_model.dart';
import '../services/qr_scan_service.dart';

/// QR Scan Dashboard with camera scanner, manual input, and item details view
class QRScanDashboard extends StatefulWidget {
  final User user;
  final QRScanService qrService;

  const QRScanDashboard({Key? key, required this.user, required this.qrService})
    : super(key: key);

  @override
  State<QRScanDashboard> createState() => _QRScanDashboardState();
}

class _QRScanDashboardState extends State<QRScanDashboard> {
  final TextEditingController _manualScanController = TextEditingController();
  final MobileScannerController _cameraController = MobileScannerController();
  final ImagePicker _picker = ImagePicker();

  bool _boxOpen = false;
  bool _torchOn = false;
  bool _isProcessing = false;

  void _openScannerBox() => setState(() => _boxOpen = true);
  void _closeScannerBox() => setState(() => _boxOpen = false);

  void _openItemDetailsPage(ScannedItem item) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ItemDetailsPage(
          item: item,
          qrService: widget.qrService,
        ),
      ),
    );
  }

  void _logout() {
    Navigator.of(context).maybePop();
  }

  @override
  void dispose() {
    _cameraController.dispose();
    _manualScanController.dispose();
    super.dispose();
  }

  Future<void> _processScannedData(String data) async {
    if (_isProcessing) return;
    
    setState(() => _isProcessing = true);
    _closeScannerBox();
    
    // Show loading indicator
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Fetching item details...'),
              ],
            ),
          ),
        ),
      ),
    );
    
    try {
      final found = await widget.qrService.scanQRCode(data);
      
      // Close loading dialog
      if (mounted) Navigator.of(context).pop();
      
      if (found != null) {
        _openItemDetailsPage(found);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('❌ Item not found: $data'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      // Close loading dialog
      if (mounted) Navigator.of(context).pop();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _handleManualScan() async {
    final id = _manualScanController.text.trim();
    if (id.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a UID')),
      );
      return;
    }
    await _processScannedData(id);
    _manualScanController.clear();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_isProcessing) return;
    
    try {
      final raw = (capture.barcodes.isNotEmpty)
          ? (capture.barcodes.first.rawValue ?? '')
          : '';
      if (raw.isNotEmpty) {
        await _processScannedData(raw);
      }
    } catch (_) {}
  }

  Future<void> _pickFromGalleryAndScan() async {
    final XFile? file = await _picker.pickImage(source: ImageSource.gallery);
    if (file == null) return;
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Image scanning not yet supported')),
      );
    }
  }

  Future<void> _toggleTorch() async {
    try {
      await _cameraController.toggleTorch();
      setState(() => _torchOn = !_torchOn);
    } catch (_) {}
  }

  Future<void> _flipCamera() async {
    try {
      await _cameraController.switchCamera();
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome, ${widget.user.username}'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            tooltip: 'Logout',
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: Container(
        decoration: appBackgroundDecoration,
        child: Column(
          children: [
            // Scanner Card
            Expanded(
              flex: 5,
              child: Center(
                child: Card(
                  margin: const EdgeInsets.all(20),
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: SizedBox(
                    width: double.infinity,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: _boxOpen
                          ? Stack(
                              children: [
                                Positioned.fill(
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(12),
                                    child: MobileScanner(
                                      controller: _cameraController,
                                      fit: BoxFit.cover,
                                      onDetect: (capture) async {
                                        await _onDetect(capture);
                                      },
                                    ),
                                  ),
                                ),
                                // Scan frame overlay
                                Center(
                                  child: Container(
                                    width: 200,
                                    height: 200,
                                    decoration: BoxDecoration(
                                      border: Border.all(
                                        color: Colors.green,
                                        width: 3,
                                      ),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                ),
                                Positioned(
                                  left: 8,
                                  top: 8,
                                  child: CircleAvatar(
                                    backgroundColor: Colors.black54,
                                    child: IconButton(
                                      icon: const Icon(
                                        Icons.close,
                                        color: Colors.white,
                                      ),
                                      onPressed: _closeScannerBox,
                                    ),
                                  ),
                                ),
                                Positioned(
                                  right: 8,
                                  top: 8,
                                  child: Row(
                                    children: [
                                      CircleAvatar(
                                        backgroundColor: Colors.black54,
                                        child: IconButton(
                                          icon: Icon(
                                            _torchOn
                                                ? Icons.flash_on
                                                : Icons.flash_off,
                                            color: Colors.white,
                                          ),
                                          onPressed: _toggleTorch,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      CircleAvatar(
                                        backgroundColor: Colors.black54,
                                        child: IconButton(
                                          icon: const Icon(
                                            Icons.flip_camera_android,
                                            color: Colors.white,
                                          ),
                                          onPressed: _flipCamera,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const Positioned(
                                  bottom: 16,
                                  left: 0,
                                  right: 0,
                                  child: Text(
                                    'Position QR code within the frame',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 14,
                                      backgroundColor: Colors.black54,
                                    ),
                                  ),
                                ),
                              ],
                            )
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(24),
                                  decoration: BoxDecoration(
                                    color: Colors.green.shade50,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    Icons.qr_code_scanner,
                                    size: 80,
                                    color: Colors.green.shade700,
                                  ),
                                ),
                                const SizedBox(height: 24),
                                const Text(
                                  'Scan QR Code',
                                  style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'Tap the button below to start scanning',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                                const SizedBox(height: 24),
                                ElevatedButton.icon(
                                  onPressed: _openScannerBox,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green.shade700,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 32,
                                      vertical: 16,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                  icon: const Icon(Icons.camera_alt),
                                  label: const Text(
                                    'Open Scanner',
                                    style: TextStyle(fontSize: 16),
                                  ),
                                ),
                              ],
                            ),
                    ),
                  ),
                ),
              ),
            ),

            // Manual Entry Card
            Card(
              margin: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Manual Entry',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _manualScanController,
                            decoration: InputDecoration(
                              hintText: 'Enter UID (e.g., EC-LOT1234-xxx)',
                              prefixIcon: const Icon(Icons.edit),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                              contentPadding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 12,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton(
                          onPressed: _handleManualScan,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green.shade700,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 16,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: const Text('Search'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
