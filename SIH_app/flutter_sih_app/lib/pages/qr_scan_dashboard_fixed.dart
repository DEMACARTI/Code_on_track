import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import '../theme/app_theme.dart';

import '../services/qr_scan_service.dart';

/// Clean replacement dashboard. If `qr_scan_dashboard.dart` remains corrupted,
/// import and use this file instead for testing.
class QRScanDashboardFixed extends StatefulWidget {
  final QRScanService qrService;

  const QRScanDashboardFixed({Key? key, required this.qrService})
    : super(key: key);

  @override
  State<QRScanDashboardFixed> createState() => _QRScanDashboardFixedState();
}

class _QRScanDashboardFixedState extends State<QRScanDashboardFixed>
    with SingleTickerProviderStateMixin {
  late final MobileScannerController _cameraController;
  late final AnimationController _scanLineController;
  final TextEditingController _manualScanController = TextEditingController();
  final TextEditingController _remarkController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  bool _isSimulate = false;
  ScannedItem? _currentItem;
  final List<ScannedItem> _recent = [];
  String? _attachedPhotoPath;

  @override
  void initState() {
    super.initState();
    _cameraController = MobileScannerController();
    _scanLineController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..repeat();
    _startCameraSafe();
  }

  Future<void> _startCameraSafe() async {
    try {
      await _cameraController.start();
    } catch (_) {}
  }

  @override
  void dispose() {
    _scanLineController.dispose();
    _cameraController.dispose();
    _manualScanController.dispose();
    _remarkController.dispose();
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
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('QR not recognized')));
      return;
    }
    setState(() {
      _currentItem = item;
      _recent.insert(0, item);
    });
  }

  Future<void> _handleManualScan() async {
    final text = _manualScanController.text.trim();
    if (text.isEmpty) return;
    await _processScannedCode(text);
    _manualScanController.clear();
  }

  Future<void> _pickImage() async {
    final XFile? file = await _picker.pickImage(source: ImageSource.gallery);
    if (file == null) return;
    setState(() => _attachedPhotoPath = file.path);
  }

  Future<void> _takePhoto() async {
    final XFile? file = await _picker.pickImage(source: ImageSource.camera);
    if (file == null) return;
    setState(() => _attachedPhotoPath = file.path);
  }

  String _deriveStatusFromRemark(String remark) {
    final r = remark.toLowerCase();
    if (r.contains('fail') || r.contains('broken') || r.contains('damaged'))
      return 'fail';
    if (r.contains('pass') || r.contains('ok') || r.contains('good'))
      return 'pass';
    return 'unknown';
  }

  Future<void> _submitRemark() async {
    final remark = _remarkController.text.trim();
    if (_currentItem == null || remark.isEmpty) return;
    final status = _deriveStatusFromRemark(remark);

    final success = await widget.qrService.uploadInspection(
      qrId: _currentItem!.id,
      status: status,
      remark: remark,
      photoPath: _attachedPhotoPath,
    );
    if (success) {
      final updated = ScannedItem(
        id: _currentItem!.id,
        name: _currentItem!.name,
        status: status,
        location: _currentItem!.location,
        details: remark,
        lastUpdated: DateTime.now(),
      );
      setState(() {
        _currentItem = updated;
        if (_recent.isNotEmpty && _recent.first.id == updated.id)
          _recent[0] = updated;
        _remarkController.clear();
        _attachedPhotoPath = null;
      });
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Upload failed')));
    }
  }

  Widget _buildScannerOverlay(BoxConstraints bc) {
    final width = bc.maxWidth * 0.78;
    final height = width * 0.7;
    return Center(
      child: SizedBox(
        width: width,
        height: height,
        child: Stack(
          children: [
            // Simple rounded border for accessibility (no custom painter)
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.greenAccent, width: 3),
              ),
            ),
            // Animated scan line
            Positioned.fill(
              child: AnimatedBuilder(
                animation: _scanLineController,
                builder: (context, _) {
                  final t = _scanLineController.value;
                  return Align(
                    alignment: Alignment(0, (t * 2.0) - 1.0),
                    child: Container(
                      width: width - 24,
                      height: 2,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.greenAccent.withOpacity(0.0),
                            Colors.greenAccent.withOpacity(0.95),
                            Colors.greenAccent.withOpacity(0.0),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('QR Scan Dashboard (Fixed)')),
      body: Container(
        decoration: appBackgroundDecoration,
        child: Column(
          children: [
            Expanded(
              flex: 6,
              child: Stack(
                children: [
                  MobileScanner(
                    controller: _cameraController,
                    onDetect: _onDetect,
                  ),
                  LayoutBuilder(
                    builder: (context, bc) => _buildScannerOverlay(bc),
                  ),
                ],
              ),
            ),
            if (!_isSimulate)
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
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
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Row(
                children: [
                  IconButton(
                    onPressed: _takePhoto,
                    icon: const Icon(Icons.camera_alt_outlined),
                  ),
                  IconButton(
                    onPressed: _pickImage,
                    icon: const Icon(Icons.photo),
                  ),
                  Expanded(
                    child: TextField(
                      controller: _remarkController,
                      onSubmitted: (_) => _submitRemark(),
                      decoration: const InputDecoration(
                        hintText: 'Add remark and press send',
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: _submitRemark,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _isSimulate = !_isSimulate;
                        if (_isSimulate) {
                          _currentItem = ScannedItem(
                            id: 'QR_TEST',
                            name: 'Simulated',
                            status: 'simulated',
                            location: 'N/A',
                          );
                        } else {
                          _currentItem = null;
                        }
                      });
                    },
                    child: Text(
                      _isSimulate ? 'Disable Simulate' : 'Simulate/Test',
                    ),
                  ),
                  const SizedBox(width: 12),
                  if (_currentItem != null)
                    Expanded(
                      child: Text(
                        'Current: ${_currentItem!.id} — ${_currentItem!.status}',
                      ),
                    ),
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
