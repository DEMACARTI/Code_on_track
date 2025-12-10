import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import '../services/qr_scan_service.dart';
import '../services/defect_classification_service.dart';
import '../theme/app_theme.dart';

/// Full-screen page to display scanned QR code item details
class ItemDetailsPage extends StatefulWidget {
  final ScannedItem item;
  final QRScanService qrService;

  const ItemDetailsPage({
    Key? key,
    required this.item,
    required this.qrService,
  }) : super(key: key);

  @override
  State<ItemDetailsPage> createState() => _ItemDetailsPageState();
}

class _ItemDetailsPageState extends State<ItemDetailsPage> {
  final TextEditingController _remarkController = TextEditingController();
  String _selectedStatus = 'operational';
  bool _isSubmitting = false;
  final ImagePicker _picker = ImagePicker();
  File? _capturedImage;
  DefectClassificationResult? _aiClassification;
  bool _isClassifying = false;

  // All valid status values
  static const List<String> _validStatuses = [
    'operational',
    'manufactured',
    'needs_maintenance',
    'damaged',
    'inspected',
    'rejected',
  ];

  @override
  void initState() {
    super.initState();
    // Use item status if valid, otherwise default to 'operational'
    _selectedStatus = _validStatuses.contains(widget.item.status)
        ? widget.item.status
        : 'operational';
  }

  @override
  void dispose() {
    _remarkController.dispose();
    super.dispose();
  }

  Future<void> _captureAndClassify() async {
    try {
      // Capture image from camera
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (photo == null) return;

      setState(() {
        _capturedImage = File(photo.path);
        _isClassifying = true;
        _aiClassification = null;
      });

      // Show classification dialog
      if (!mounted) return;
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
                  Text('Analyzing defect...'),
                ],
              ),
            ),
          ),
        ),
      );

      // Call AI classification service
      final classificationService = DefectClassificationService(
        baseUrl: widget.qrService.baseUrl,
      );

      final result = await classificationService.classifyDefectFromFile(_capturedImage!);

      // Close loading dialog
      if (mounted) Navigator.of(context).pop();

      if (result != null) {
        setState(() {
          _aiClassification = result;
          _remarkController.text = result.remark;
          _isClassifying = false;
        });

        // Update status based on AI classification
        _updateStatusFromAI(result.predictedClass);

        // Show success snackbar
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                '${result.icon} Detected: ${result.predictedClass} (${result.confidencePercent})',
              ),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      } else {
        setState(() => _isClassifying = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('❌ Classification failed. Please try again.'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      setState(() => _isClassifying = false);
      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog if open
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _updateStatusFromAI(String predictedClass) {
    // Auto-update status based on AI classification
    switch (predictedClass.toLowerCase()) {
      case 'broken':
        setState(() => _selectedStatus = 'rejected');
        break;
      case 'crack':
      case 'damaged':
        setState(() => _selectedStatus = 'damaged');
        break;
      case 'rust':
        setState(() => _selectedStatus = 'needs_maintenance');
        break;
      case 'normal':
        setState(() => _selectedStatus = 'operational');
        break;
    }
  }

  Future<void> _submitInspection() async {
    setState(() => _isSubmitting = true);
    
    try {
      final success = await widget.qrService.uploadInspection(
        qrId: widget.item.id,
        status: _selectedStatus,
        remark: _remarkController.text.trim(),
      );
      
      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Inspection submitted successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('❌ Failed to submit inspection'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'operational':
      case 'manufactured':
        return Colors.green;
      case 'to_be_replaced':
      case 'needs_maintenance':
        return Colors.orange;
      case 'fully_damaged':
      case 'damaged':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Item Details'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
      ),
      body: Container(
        decoration: appBackgroundDecoration,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Card with UID
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.green.shade600, Colors.green.shade800],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.qr_code_2,
                        size: 48,
                        color: Colors.white,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        widget.item.id,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          letterSpacing: 0.5,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: _getStatusColor(widget.item.status),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          widget.item.status.toUpperCase().replaceAll('_', ' '),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Details Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.info_outline, color: Colors.green.shade700),
                          const SizedBox(width: 8),
                          const Text(
                            'Component Information',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 24),
                      _buildDetailRow('Name', widget.item.name),
                      _buildDetailRow('Component Type', widget.item.material ?? '-'),
                      _buildDetailRow('Lot Number', widget.item.lotNo ?? '-'),
                      _buildDetailRow('Vendor ID', widget.item.vendorId ?? '-'),
                      _buildDetailRow('Location', widget.item.location),
                      _buildDetailRow('Details', widget.item.details ?? '-'),
                      if (widget.item.lastUpdated != null)
                        _buildDetailRow(
                          'Last Updated',
                          '${widget.item.lastUpdated!.day}/${widget.item.lastUpdated!.month}/${widget.item.lastUpdated!.year}',
                        ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Inspection Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.assignment, color: Colors.green.shade700),
                          const SizedBox(width: 8),
                          const Text(
                            'Inspection Report',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 24),
                      
                      const Text(
                        'Update Status',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: _selectedStatus,
                        decoration: InputDecoration(
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                        ),
                        items: const [
                          DropdownMenuItem(
                            value: 'operational',
                            child: Row(
                              children: [
                                Icon(Icons.check_circle, color: Colors.green, size: 20),
                                SizedBox(width: 8),
                                Text('Operational'),
                              ],
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'manufactured',
                            child: Row(
                              children: [
                                Icon(Icons.precision_manufacturing, color: Colors.blue, size: 20),
                                SizedBox(width: 8),
                                Text('Manufactured'),
                              ],
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'inspected',
                            child: Row(
                              children: [
                                Icon(Icons.verified, color: Colors.teal, size: 20),
                                SizedBox(width: 8),
                                Text('Inspected'),
                              ],
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'needs_maintenance',
                            child: Row(
                              children: [
                                Icon(Icons.build, color: Colors.orange, size: 20),
                                SizedBox(width: 8),
                                Text('Needs Maintenance'),
                              ],
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'damaged',
                            child: Row(
                              children: [
                                Icon(Icons.warning, color: Colors.red, size: 20),
                                SizedBox(width: 8),
                                Text('Damaged'),
                              ],
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'rejected',
                            child: Row(
                              children: [
                                Icon(Icons.cancel, color: Colors.red, size: 20),
                                SizedBox(width: 8),
                                Text('Rejected'),
                              ],
                            ),
                          ),
                        ],
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _selectedStatus = value);
                          }
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Inspection Remarks',
                            style: TextStyle(fontWeight: FontWeight.w600),
                          ),
                          ElevatedButton.icon(
                            onPressed: _isClassifying ? null : _captureAndClassify,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.blue.shade700,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 8,
                              ),
                            ),
                            icon: _isClassifying
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.camera_alt, size: 20),
                            label: Text(_isClassifying ? 'Analyzing...' : 'AI Scan'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      
                      // Show AI classification result if available
                      if (_aiClassification != null) ...[
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.blue.shade200),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    _aiClassification!.icon,
                                    style: const TextStyle(fontSize: 24),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'AI Detected: ${_aiClassification!.predictedClass}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.green.shade100,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      _aiClassification!.confidencePercent,
                                      style: TextStyle(
                                        color: Colors.green.shade800,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Severity: ${_aiClassification!.severityLevel}',
                                style: TextStyle(
                                  color: Colors.grey.shade700,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 8),
                      ],
                      
                      // Show captured image thumbnail if available
                      if (_capturedImage != null) ...[
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            _capturedImage!,
                            height: 150,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                        const SizedBox(height: 8),
                      ],
                      
                      TextField(
                        controller: _remarkController,
                        maxLines: 4,
                        decoration: InputDecoration(
                          hintText: 'Enter inspection notes or click AI Scan to auto-detect...',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 20),
                      
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _submitInspection,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green.shade700,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          icon: _isSubmitting
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Icon(Icons.send),
                          label: Text(
                            _isSubmitting ? 'Submitting...' : 'Submit Inspection',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 15,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
