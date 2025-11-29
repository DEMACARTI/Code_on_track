import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/qr_scan_service.dart';
import '../theme/app_theme.dart';

class QRScanSimulatePage extends StatefulWidget {
  final QRScanService qrService;
  final void Function(ScannedItem) onSimulated;

  const QRScanSimulatePage({
    Key? key,
    required this.qrService,
    required this.onSimulated,
  }) : super(key: key);

  @override
  State<QRScanSimulatePage> createState() => _QRScanSimulatePageState();
}

class _QRScanSimulatePageState extends State<QRScanSimulatePage> {
  final TextEditingController _llmController = TextEditingController();
  final TextEditingController _feedbackController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  File? _photo;
  bool _loading = false;
  String? _llmResult;
  String _predictedStatus = 'operational';

  Future<void> _pick(ImageSource s) async {
    try {
      final x = await _picker.pickImage(source: s, imageQuality: 80);
      if (x != null) setState(() => _photo = File(x.path));
    } catch (_) {}
  }

  Future<void> _callLLM() async {
    final remark = _llmController.text.trim();
    if (remark.isEmpty && _photo == null) return;
    setState(() {
      _loading = true;
      _llmResult = null;
    });
    try {
      // Try backend LLM if available
      try {
        final res = await (widget.qrService as dynamic).rateInspectionWithLLM(
          qrId: 'QR_TEST',
          remark: remark,
          photoPath: _photo?.path,
        );
        if (res is Map && res['status'] != null) {
          setState(() {
            _predictedStatus = res['status'].toString();
            _llmResult = res['rating']?.toString() ?? res.toString();
          });
          return;
        } else if (res is String && res.isNotEmpty) {
          setState(() {
            _predictedStatus = res;
            _llmResult = res;
          });
          return;
        }
      } catch (_) {}

      // Local fallback heuristic
      await Future.delayed(const Duration(milliseconds: 600));
      final low = remark.toLowerCase();
      String newStatus = 'operational';
      if (low.contains('broken') ||
          low.contains('fail') ||
          low.contains('damaged') ||
          low.contains('not working'))
        newStatus = 'non_operational';
      else if (low.contains('maint') ||
          low.contains('service') ||
          low.contains('repair') ||
          low.contains('leak'))
        newStatus = 'needs_maintenance';
      setState(() {
        _predictedStatus = newStatus;
        _llmResult = 'Auto-rated: ${newStatus.replaceAll('_', ' ')}';
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    final feedback = _feedbackController.text.trim();
    final ok = await widget.qrService.uploadInspection(
      qrId: 'QR_TEST',
      status: _predictedStatus,
      remark: feedback,
      photoPath: _photo?.path,
    );
    if (ok) {
      final item = ScannedItem(
        id: 'QR_TEST',
        name: 'Simulated',
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
    _llmController.dispose();
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
          child: Column(
            children: [
              Card(
                child: ListTile(
                  title: const Text('Simulated Item'),
                  subtitle: Text(
                    'Status: ${_predictedStatus.replaceAll('_', ' ')}',
                  ),
                  trailing: const Icon(Icons.bug_report),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: () => _pick(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: () => _pick(ImageSource.gallery),
                    icon: const Icon(Icons.photo),
                    label: const Text('Gallery'),
                  ),
                  const SizedBox(width: 12),
                  if (_photo != null) const Text('Photo attached'),
                ],
              ),
              const SizedBox(height: 12),
              // LLM input section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'LLM Input',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _llmController,
                        minLines: 1,
                        maxLines: 4,
                        decoration: const InputDecoration(
                          hintText: 'Describe the issue for LLM...',
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          ElevatedButton(
                            onPressed: _loading ? null : _callLLM,
                            child: _loading
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Text('Send to LLM'),
                          ),
                          const SizedBox(width: 12),
                          if (_llmResult != null)
                            Expanded(
                              child: Text(
                                _llmResult!,
                                style: const TextStyle(color: Colors.black87),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 12),
              // Final feedback section (to be saved to DB)
              Expanded(
                child: Card(
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
                        Expanded(
                          child: TextField(
                            controller: _feedbackController,
                            maxLines: null,
                            decoration: const InputDecoration(
                              hintText:
                                  'Write final feedback to save in database...',
                            ),
                            keyboardType: TextInputType.multiline,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            ElevatedButton(
                              onPressed: _submit,
                              child: const Text('Submit Feedback'),
                            ),
                            const SizedBox(width: 12),
                            if (_photo != null) const Text('Photo attached'),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              if (_llmResult != null)
                Text(
                  _llmResult!,
                  style: const TextStyle(fontSize: 14, color: Colors.black87),
                ),
              const SizedBox(height: 8),
              Row(
                children: [
                  ElevatedButton(
                    onPressed: _loading ? null : _callLLM,
                    child: _loading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Send to LLM'),
                  ),
                  const SizedBox(width: 12),
                  ElevatedButton(
                    onPressed: _submit,
                    child: const Text('Submit'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
