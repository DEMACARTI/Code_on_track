import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/qr_scan_service.dart';
import '../theme/app_theme.dart';

class QRScanSimulatePage extends StatefulWidget {
  final QRScanService qrService;
  final void Function(ScannedItem) onSimulated;
  final ScannedItem? initialItem;

  const QRScanSimulatePage({
    Key? key,
    required this.qrService,
    required this.onSimulated,
    this.initialItem,
  }) : super(key: key);

  @override
  State<QRScanSimulatePage> createState() => _QRScanSimulatePageState();
}

class _QRScanSimulatePageState extends State<QRScanSimulatePage> {
  final TextEditingController _feedbackController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  File? _photo;
  String _predictedStatus = 'operational';

  Future<void> _pick(ImageSource s) async {
    try {
      final x = await _picker.pickImage(source: s, imageQuality: 80);
      if (x != null) setState(() => _photo = File(x.path));
    } catch (_) {}
  }

  // LLM functionality removed: app now uses manual feedback and simulated status.

  Future<void> _submit() async {
    final feedback = _feedbackController.text.trim();
    final ok = await widget.qrService.uploadInspection(
      qrId: widget.initialItem?.id ?? 'QR_TEST',
      status: _predictedStatus,
      remark: feedback,
      photoPath: _photo?.path,
    );
    if (ok) {
      final item = ScannedItem(
        id: widget.initialItem?.id ?? 'QR_TEST',
        name: widget.initialItem?.name ?? 'Simulated',
        status: _predictedStatus,
        location: 'Demo',
        details: feedback,
        lastUpdated: DateTime.now(),
      );
      widget.onSimulated(item);
      if (mounted) Navigator.of(context).pop();
    } else {
      if (mounted)
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Upload failed')));
    }
  }

  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Simulate Scan & Feedback')),
      body: Container(
        decoration: appBackgroundDecoration,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: ListView(
            shrinkWrap: true,
            padding: EdgeInsets.zero,
            children: [
              Card(
                child: ListTile(
                  title: Text(widget.initialItem?.name ?? 'Simulated Item'),
                  subtitle: Text(
                    'Status: ${_predictedStatus.replaceAll('_', ' ')}',
                  ),
                  trailing: const Icon(Icons.bug_report),
                ),
              ),
              const SizedBox(height: 8),
              // Item details pre-filled from scanned item
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Item Details',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      Text('ID: ${widget.initialItem?.id ?? '-'}'),
                      Text('Location: ${widget.initialItem?.location ?? '-'}'),
                      Text('Material: ${widget.initialItem?.material ?? '-'}'),
                      Text('Lot No.: ${widget.initialItem?.lotNo ?? '-'}'),
                      Text('Vendor ID: ${widget.initialItem?.vendorId ?? '-'}'),
                      Text('Batch: ${widget.initialItem?.batch ?? '-'}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Photo attach controls are now inside the feedback card below.
              if (_photo != null)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text('Photo attached'),
                  ),
                ),
              const SizedBox(height: 12),
              const SizedBox(height: 12),
              // Status selector and final feedback (saved to DB)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Select Status',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: widget.initialItem?.status ?? _predictedStatus,
                        items: const [
                          DropdownMenuItem(
                            value: 'operational',
                            child: Text('Operational'),
                          ),
                          DropdownMenuItem(
                            value: 'to_be_replaced',
                            child: Text('To be replaced'),
                          ),
                          DropdownMenuItem(
                            value: 'fully_damaged',
                            child: Text('To be repaired'),
                          ),
                        ],
                        onChanged: (v) {
                          if (v != null) setState(() => _predictedStatus = v);
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Final feedback section (to be saved to DB)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Final Feedback',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      LayoutBuilder(
                        builder: (ctx, bc) {
                          final screenH = MediaQuery.of(ctx).size.height;
                          final maxH = (screenH * 0.5).clamp(140.0, 600.0);
                          return ConstrainedBox(
                            constraints: BoxConstraints(
                              minHeight: 120,
                              maxHeight: maxH,
                            ),
                            child: TextField(
                              controller: _feedbackController,
                              expands: true,
                              maxLines: null,
                              decoration: const InputDecoration(
                                hintText:
                                    'Write final feedback to save in database...',
                                border: InputBorder.none,
                                contentPadding: EdgeInsets.all(8.0),
                              ),
                              keyboardType: TextInputType.multiline,
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 8),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            children: [
                              IconButton(
                                tooltip: 'Attach Photo (Camera)',
                                onPressed: () => _pick(ImageSource.camera),
                                icon: const Icon(Icons.camera_alt),
                              ),
                              IconButton(
                                tooltip: 'Attach Photo (Gallery)',
                                onPressed: () => _pick(ImageSource.gallery),
                                icon: const Icon(Icons.photo),
                              ),
                              if (_photo != null)
                                Expanded(child: Text('Photo attached')),
                            ],
                          ),
                          const SizedBox(height: 8),
                          ElevatedButton(
                            onPressed: _submit,
                            child: const Text('Submit Feedback'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // single submit button kept above; no duplicate below
            ],
          ),
        ),
      ),
    );
  }
}
