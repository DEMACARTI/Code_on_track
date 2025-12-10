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

  /// Classify defect from base64 encoded image
  Future<DefectClassificationResult?> classifyDefectFromBase64(String base64Image) async {
    try {
      final url = Uri.parse('$baseUrl/api/classify-defect-base64');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'image_base64': base64Image}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return DefectClassificationResult.fromJson(data);
      } else {
        print('Classification failed: ${response.statusCode} - ${response.body}');
        return null;
      }
    } catch (e) {
      print('Error calling classification API: $e');
      return null;
    }
  }

  /// Check if model is loaded on backend
  Future<ModelStatus> checkModelStatus() async {
    try {
      final url = Uri.parse('$baseUrl/api/model-status');
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

  DefectClassificationResult({
    required this.predictedClass,
    required this.confidence,
    required this.allProbabilities,
    required this.remark,
  });

  factory DefectClassificationResult.fromJson(Map<String, dynamic> json) {
    return DefectClassificationResult(
      predictedClass: json['predicted_class'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      allProbabilities: Map<String, double>.from(
        (json['all_probabilities'] ?? {}).map(
          (key, value) => MapEntry(key, (value as num).toDouble()),
        ),
      ),
      remark: json['remark'] ?? '',
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

  ModelStatus({
    required this.isLoaded,
    this.modelType,
    this.classes = const [],
    required this.status,
    required this.message,
  });

  factory ModelStatus.fromJson(Map<String, dynamic> json) {
    return ModelStatus(
      isLoaded: json['model_loaded'] ?? false,
      modelType: json['model_type'],
      classes: List<String>.from(json['classes'] ?? []),
      status: json['status'] ?? 'unknown',
      message: json['message'] ?? '',
    );
  }
}
