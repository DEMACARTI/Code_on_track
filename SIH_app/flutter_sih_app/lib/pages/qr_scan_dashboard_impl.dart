import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'qr_scan_simulate.dart';
import '../theme/app_theme.dart';

import '../models/user_model.dart';
import '../services/qr_scan_service.dart';

/// Simplified QR scan dashboard: scanner overlay, manual input and quick-fill
/// buttons have been removed per request. Use the Feedback button to open
/// the simulate/feedback page.
class QRScanDashboard extends StatefulWidget {
  final User user;
  final QRScanService qrService;

  const QRScanDashboard({Key? key, required this.user, required this.qrService})
    : super(key: key);

  @override
  State<QRScanDashboard> createState() => _QRScanDashboardState();
}

class _QRScanDashboardState extends State<QRScanDashboard> {
  // Scanner and manual input state
  final TextEditingController _manualScanController = TextEditingController();
  final MobileScannerController _cameraController = MobileScannerController();
  final ImagePicker _picker = ImagePicker();

  bool _boxOpen = false;
  bool _torchOn = false;

  void _openScannerBox() => setState(() => _boxOpen = true);
  void _closeScannerBox() => setState(() => _boxOpen = false);

  void _openSimulatePage([ScannedItem? item]) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => QRScanSimulatePage(
          qrService: widget.qrService,
          initialItem: item,
          onSimulated: (updated) {},
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
    try {
      final found = await widget.qrService.scanQRCode(data);
      if (found != null) {
        _openSimulatePage(found);
      } else {
        if (mounted)
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('QR not found')));
      }
    } catch (_) {
      if (mounted)
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Error processing scan')));
    }
  }

  Future<void> _handleManualScan() async {
    final id = _manualScanController.text.trim();
    if (id.isEmpty) return;
    await _processScannedData(id);
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    try {
      final raw = (capture.barcodes.isNotEmpty)
          ? (capture.barcodes.first.rawValue ?? '')
          : '';
      if (raw.isNotEmpty) await _processScannedData(raw);
    } catch (_) {}
  }

  Future<void> _pickFromGalleryAndScan() async {
    final XFile? file = await _picker.pickImage(source: ImageSource.gallery);
    if (file == null) return;
    try {
      final svc = widget.qrService;
      if (svc is RestQRScanService) {
        final result = await svc.scanQRCodeFromImage(file.path);
        if (result != null) return _processScannedData(result.id);
      } else if (svc is MockQRScanService) {
        final result = await svc.scanQRCodeFromImage(file.path);
        if (result != null) return _processScannedData(result.id);
      }
    } catch (_) {}
    if (mounted)
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Picked image (not decoded)')),
      );
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
        title: const Text('QR Scan Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Feedback',
            icon: const Icon(Icons.feedback),
            onPressed: () => _openSimulatePage(),
          ),
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
            Expanded(
              flex: 6,
              child: Center(
                child: Card(
                  margin: const EdgeInsets.all(24),
                  child: SizedBox(
                    width: double.infinity,
                    height: 300,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: _boxOpen
                          ? Stack(
                              children: [
                                Positioned.fill(
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: MobileScanner(
                                      controller: _cameraController,
                                      fit: BoxFit.cover,
                                      onDetect: (capture) async {
                                        await _onDetect(capture);
                                      },
                                    ),
                                  ),
                                ),
                                Positioned(
                                  left: 8,
                                  top: 8,
                                  child: IconButton(
                                    icon: const Icon(
                                      Icons.close,
                                      color: Colors.white,
                                    ),
                                    onPressed: _closeScannerBox,
                                  ),
                                ),
                                Positioned(
                                  right: 8,
                                  top: 8,
                                  child: Row(
                                    children: [
                                      IconButton(
                                        icon: const Icon(
                                          Icons.photo,
                                          color: Colors.white,
                                        ),
                                        onPressed: _pickFromGalleryAndScan,
                                      ),
                                      IconButton(
                                        icon: Icon(
                                          _torchOn
                                              ? Icons.flash_on
                                              : Icons.flash_off,
                                          color: Colors.white,
                                        ),
                                        onPressed: _toggleTorch,
                                      ),
                                      IconButton(
                                        icon: const Icon(
                                          Icons.flip_camera_android,
                                          color: Colors.white,
                                        ),
                                        onPressed: _flipCamera,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            )
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(
                                  Icons.qr_code_scanner,
                                  size: 56,
                                  color: Colors.green,
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  'Scanner closed',
                                  style: TextStyle(fontSize: 16),
                                ),
                                const SizedBox(height: 12),
                                ElevatedButton.icon(
                                  onPressed: _openScannerBox,
                                  icon: const Icon(Icons.camera_alt),
                                  label: const Text('Open Scanner'),
                                ),
                              ],
                            ),
                    ),
                  ),
                ),
              ),
            ),

            // Manual entry row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _manualScanController,
                      decoration: const InputDecoration(
                        hintText: 'Enter ID manually',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _handleManualScan,
                    child: const Text('Scan'),
                  ),
                ],
              ),
            ),

            const Divider(height: 1),
            const SizedBox(height: 8),

            // (camera opens embedded in the top card; no separate full-screen overlay)
          ],
        ),
      ),
    );
  }
}
