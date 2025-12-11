import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

/// Service for AI-powered defect classification using VGG model
class DefectClassificationService {
  final String baseUrl;

  DefectClassificationService({required this.baseUrl});

  /// Classify defect from image file
  Future<DefectClassificationResult?> classifyDefectFromFile(File imageFile) async {
    try {
      // Read image as bytes and convert to base64
      final bytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(bytes);

      return await classifyDefectFromBase64(base64Image);
    } catch (e) {
      print('Error classifying from file: $e');
      return null;
    }
  }

  /// Classify defect from base64 encoded image using the new AI pipeline
  /// Uses YOLO for detection + ResNet for classification
  /// [expectedComponent] - From QR code, validates detected matches expected
  Future<DefectClassificationResult?> classifyDefectFromBase64(
    String base64Image, {
    String? expectedComponent,
  }) async {
    try {
      // Use new multi-model pipeline endpoint
      final url = Uri.parse('$baseUrl/api/inspect-component');
      
      // Build request body with optional expected_component
      final requestBody = <String, dynamic>{
        'image_base64': base64Image,
      };
      if (expectedComponent != null) {
        requestBody['expected_component'] = expectedComponent;
      }
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Check if wrong component detected (QR vs camera mismatch)
        if (data['wrong_component'] == true) {
          return DefectClassificationResult(
            predictedClass: 'Wrong Component',
            confidence: (data['detection_confidence'] ?? 0.0).toDouble(),
            allProbabilities: {},
            remark: data['error'] ?? 'Wrong component detected',
            componentType: data['component_type'],
            componentClass: data['component_class'],
            componentDetected: data['component_detected'],
            severity: null,
            defects: [],
            wrongComponent: true,
          );
        }
        
        // Check if pipeline returned success
        if (data['success'] == true) {
          return DefectClassificationResult(
            predictedClass: data['severity'] ?? data['condition'] ?? 'Unknown',
            confidence: (data['detection_confidence'] ?? 0.0).toDouble(),
            allProbabilities: {},
            remark: (data['recommendations'] as List?)?.join(' ') ?? '',
            componentType: data['component_type'],
            componentClass: data['component_class'],
            componentDetected: data['component_detected'],
            severity: data['severity'],
            defects: List<String>.from(data['defects'] ?? []),
            wrongComponent: false,
          );
        } else {
          // Pipeline returned an error (e.g., no component detected)
          print('Pipeline error: ${data['error']}');
          return DefectClassificationResult(
            predictedClass: 'Unknown',
            confidence: 0.0,
            allProbabilities: {},
            remark: data['error'] ?? 'Inspection failed',
            componentType: null,
            componentClass: null,
            componentDetected: null,
            severity: null,
            defects: [],
            wrongComponent: false,
          );
        }
      } else {
        print('Classification failed: ${response.statusCode} - ${response.body}');
        return null;
      }
    } catch (e) {
      print('Error calling classification API: $e');
      return null;
    }
  }

  /// Check if pipeline models are loaded on backend
  Future<ModelStatus> checkModelStatus() async {
    try {
      final url = Uri.parse('$baseUrl/api/pipeline-status');
      final response = await http.get(url).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ModelStatus.fromJson(data);
      } else {
        return ModelStatus(
          isLoaded: false,
          status: 'error',
          message: 'Failed to check model status',
        );
      }
    } catch (e) {
      print('Error checking model status: $e');
      return ModelStatus(
        isLoaded: false,
        status: 'error',
        message: 'Cannot connect to server',
      );
    }
  }
}

/// Result of defect classification
class DefectClassificationResult {
  final String predictedClass;
  final double confidence;
  final Map<String, double> allProbabilities;
  final String remark;
  final String? componentType;      // e.g., 'erc', 'sleeper'
  final String? componentClass;     // e.g., 'elastic_clip_good'
  final String? componentDetected;  // Human-readable: 'Elastic Rail Clip', 'Sleeper'
  final String? severity;           // 'Good', 'Fair', 'Bad'
  final List<String> defects;
  final bool wrongComponent;        // True if detected != expected from QR

  DefectClassificationResult({
    required this.predictedClass,
    required this.confidence,
    required this.allProbabilities,
    required this.remark,
    this.componentType,
    this.componentClass,
    this.componentDetected,
    this.severity,
    this.defects = const [],
    this.wrongComponent = false,
  });

  factory DefectClassificationResult.fromJson(Map<String, dynamic> json) {
    return DefectClassificationResult(
      predictedClass: json['predicted_class'] ?? json['severity'] ?? json['condition'] ?? '',
      confidence: (json['confidence'] ?? json['detection_confidence'] ?? 0.0).toDouble(),
      allProbabilities: Map<String, double>.from(
        (json['all_probabilities'] ?? {}).map(
          (key, value) => MapEntry(key, (value as num).toDouble()),
        ),
      ),
      remark: json['remark'] ?? '',
      componentType: json['component_type'],
      componentClass: json['component_class'],
      componentDetected: json['component_detected'],
      severity: json['severity'],
      defects: List<String>.from(json['defects'] ?? []),
      wrongComponent: json['wrong_component'] ?? false,
    );
  }


  /// Get confidence as percentage string
  String get confidencePercent => '${(confidence * 100).toStringAsFixed(1)}%';

  /// Get severity color based on predicted class
  String get severityColor {
    switch (predictedClass.toLowerCase()) {
      case 'broken':
        return '#FF0000'; // Red - Critical
      case 'crack':
        return '#FF6600'; // Orange - High
      case 'rust':
        return '#FF9900'; // Light Orange - Medium
      case 'damaged':
        return '#FFCC00'; // Yellow - Low
      case 'normal':
        return '#00CC00'; // Green - Good
      default:
        return '#808080'; // Gray - Unknown
    }
  }

  /// Get severity level
  String get severityLevel {
    switch (predictedClass.toLowerCase()) {
      case 'broken':
        return 'CRITICAL';
      case 'crack':
        return 'HIGH';
      case 'rust':
        return 'MEDIUM';
      case 'damaged':
        return 'LOW';
      case 'normal':
        return 'NONE';
      default:
        return 'UNKNOWN';
    }
  }

  /// Get icon emoji for class
  String get icon {
    switch (predictedClass.toLowerCase()) {
      case 'broken':
        return '⚠️';
      case 'crack':
        return '🔶';
      case 'rust':
        return '🔴';
      case 'damaged':
        return '🟡';
      case 'normal':
        return '✅';
      default:
        return '❓';
    }
  }
}

/// Model status information
class ModelStatus {
  final bool isLoaded;
  final String? modelType;
  final List<String> classes;
  final String status;
  final String message;
  final Map<String, bool> detectors;  // e.g., {'erc': true, 'sleeper': true}
  final Map<String, bool> classifiers;

  ModelStatus({
    required this.isLoaded,
    this.modelType,
    this.classes = const [],
    required this.status,
    required this.message,
    this.detectors = const {},
    this.classifiers = const {},
  });

  factory ModelStatus.fromJson(Map<String, dynamic> json) {
    // Handle new pipeline-status format
    final available = json['available'] ?? json['model_loaded'] ?? false;
    final initialized = json['initialized'] ?? false;
    
    return ModelStatus(
      isLoaded: available && initialized,
      modelType: 'YOLO + ResNet Pipeline',
      classes: List<String>.from(json['supported_components'] ?? json['classes'] ?? []),
      status: available ? 'ready' : 'not loaded',
      message: available ? 'Pipeline is ready' : (json['error'] ?? 'Pipeline not available'),
      detectors: Map<String, bool>.from(json['detectors'] ?? {}),
      classifiers: Map<String, bool>.from(json['classifiers'] ?? {}),
    );
  }
}
