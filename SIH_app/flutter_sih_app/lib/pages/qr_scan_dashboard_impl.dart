import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'qr_scan_simulate.dart';
import '../theme/app_theme.dart';

import '../models/user_model.dart';
import '../services/qr_scan_service.dart';

/// Clean, focused QR scan dashboard implementation.
class QRScanDashboard extends StatefulWidget {
  final User user;
  final QRScanService qrService;

  const QRScanDashboard({Key? key, required this.user, required this.qrService})
    : super(key: key);

  @override
  State<QRScanDashboard> createState() => _QRScanDashboardState();
}

class _QRScanDashboardState extends State<QRScanDashboard>
    with SingleTickerProviderStateMixin {
  late final MobileScannerController _cameraController;
  late final AnimationController _scanLineController;
  final TextEditingController _manualScanController = TextEditingController();

  final ImagePicker _picker = ImagePicker();

  final List<ScannedItem> _recent = [];
  bool _boxOpen = false;
  bool _torchOn = false;

  @override
  void initState() {
    super.initState();
    _cameraController = MobileScannerController();
    _scanLineController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..repeat();
    // Camera will start when user opens the scanner box.
  }

  // Camera start/stop handled when opening/closing the scanner box.

  Future<void> _openScannerBox() async {
    setState(() => _boxOpen = true);
    try {
      await _cameraController.start();
    } catch (_) {}
  }

  Future<void> _closeScannerBox() async {
    setState(() => _boxOpen = false);
    try {
      await _cameraController.stop();
    } catch (_) {}
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

  Future<void> _pickFromGalleryAndScan() async {
    try {
      final XFile? file = await _picker.pickImage(source: ImageSource.gallery);
      if (file == null) return;

      // Prefer a service-provided image scan method if available
      try {
        final dynamic svc = widget.qrService;
        final dynamic out = await (svc as dynamic).scanQRCodeFromImage?.call(
          file.path,
        );
        if (out is ScannedItem) {
          setState(() {
            if (!_recent.any((s) => s.id == out.id)) _recent.insert(0, out);
          });
          await _closeScannerBox();
          return;
        }
      } catch (_) {}

      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not decode QR from image')),
        );
    } catch (_) {}
  }

  @override
  void dispose() {
    _scanLineController.dispose();
    _cameraController.dispose();
    _manualScanController.dispose();
    super.dispose();
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (capture.barcodes.isEmpty) return;
    final code = capture.barcodes.first.rawValue ?? '';
    if (code.isEmpty) return;
    await _processScannedCode(code);
  }

  Future<void> _processScannedCode(String code) async {
    final item = await widget.qrService.scanQRCode(code);
    if (item == null) {
      if (mounted)
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('QR not recognized')));
      return;
    }
    setState(() {
      _recent.insert(0, item);
    });
  }

  Future<void> _handleManualScan() async {
    final text = _manualScanController.text.trim();
    if (text.isEmpty) return;
    await _processScannedCode(text);
    _manualScanController.clear();
  }
  // Feedback and LLM handling moved to the simulate page.

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('QR Scan Dashboard')),
      body: Container(
        decoration: appBackgroundDecoration,
        child: Column(
          children: [
            Expanded(
              flex: 6,
              child: Stack(
                children: [
                  // Placeholder area with Open Scanner button
                  Center(
                    child: Card(
                      margin: const EdgeInsets.all(24),
                      child: SizedBox(
                        width: double.infinity,
                        height: 260,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.qr_code_scanner,
                              size: 48,
                              color: Colors.green,
                            ),
                            const SizedBox(height: 12),
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

                  // Full-screen scanner box overlay
                  if (_boxOpen)
                    Positioned.fill(
                      child: Container(
                        color: Colors.black.withOpacity(0.6),
                        child: SafeArea(
                          child: Stack(
                            children: [
                              // Close button top-left
                              Positioned(
                                left: 12,
                                top: 12,
                                child: IconButton(
                                  icon: const Icon(
                                    Icons.close,
                                    color: Colors.white,
                                  ),
                                  onPressed: _closeScannerBox,
                                ),
                              ),
                              // Torch + Flip + Gallery top-right
                              Positioned(
                                right: 12,
                                top: 12,
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

                              // Centered scanner window
                              Center(
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: Container(
                                    width: 340,
                                    height: 240,
                                    color: Colors.black,
                                    child: MobileScanner(
                                      controller: _cameraController,
                                      onDetect: (capture) async {
                                        await _onDetect(capture);
                                        // Optionally close after successful scan
                                        await _closeScannerBox();
                                      },
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
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
            // Inline remark/photo UI removed; feedback moved to simulate page
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  ElevatedButton(
                    onPressed: () async {
                      // stop camera while navigating to simulate page
                      try {
                        await _cameraController.stop();
                      } catch (_) {}
                      await Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (ctx) => QRScanSimulatePage(
                            qrService: widget.qrService,
                            onSimulated: (it) {
                              setState(() {
                                if (!_recent.any((s) => s.id == it.id))
                                  _recent.insert(0, it);
                              });
                            },
                          ),
                        ),
                      );
                      // restart camera when coming back
                      try {
                        await _cameraController.start();
                      } catch (_) {}
                    },
                    child: const Text('Simulate/Test'),
                  ),
                  const SizedBox(width: 12),
                  const Spacer(),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              flex: 3,
              child: ListView.builder(
                itemCount: _recent.length,
                itemBuilder: (context, i) {
                  final it = _recent[i];
                  return ListTile(
                    title: Text(it.id),
                    subtitle: Text(it.status),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
