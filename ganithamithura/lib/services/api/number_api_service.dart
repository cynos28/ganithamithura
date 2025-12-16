import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:ganithamithura/models/models.dart';
import 'package:ganithamithura/utils/constants.dart';

/// NumApiService - Handles all backend API calls
class NumApiService {
  static NumApiService? _instance;
  final String numBaseUrl;
  
  NumApiService._({required this.numBaseUrl});
  
  static NumApiService get instance {
    _instance ??= NumApiService._(numBaseUrl: AppConstants.numBaseUrl);
    return _instance!;
  }
  
  /// Helper method to create headers
  Map<String, String> _getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }
  
  // ==================== Activity Endpoints ====================
  
  /// GET /activities/level/{level}/number/{number} - Fetch activities for a specific number
  /// Returns activities in proper sequence: video -> trace -> show -> say -> read
  /// Optional: difficulty filter to get only easy questions for tutorial
  Future<List<Activity>> getActivitiesForNumber(int level, int number, {String? difficulty}) async {
    try {
      var uri = Uri.parse('$numBaseUrl/activities/level/$level/number/$number');
      
      // Add difficulty filter if provided
      if (difficulty != null) {
        uri = uri.replace(queryParameters: {'difficulty': difficulty});
      }
      
      final response = await http.get(
        uri,
        headers: _getHeaders(),
      ).timeout(
        Duration(seconds: AppConstants.apiTimeout),
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final activitiesList = jsonData['activities'] as List;
        return activitiesList
            .map((json) => Activity.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load activities: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching activities for number: $e');
    }
  }
  
  /// GET /levels/{level}/activities - Fetch all activities for a level
  Future<List<Activity>> getActivitiesForLevel(int level) async {
    try {
      final url = Uri.parse('$numBaseUrl/levels/$level/activities');
      final response = await http.get(
        url,
        headers: _getHeaders(),
      ).timeout(
        Duration(seconds: AppConstants.apiTimeout),
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final activitiesList = jsonData['activities'] as List;
        return activitiesList
            .map((json) => Activity.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load activities: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching activities: $e');
    }
  }
  
  /// POST /activity/score - Submit activity score
  Future<Map<String, dynamic>> submitActivityScore({
    required String activityId,
    required int score,
    required bool isCompleted,
    Map<String, dynamic>? additionalData,
  }) async {
    try {
      final url = Uri.parse('$numBaseUrl/activity/score');
      final body = {
        'activity_id': activityId,
        'score': score,
        'is_completed': isCompleted,
        'completed_at': DateTime.now().toIso8601String(),
        'additional_data': additionalData,
      };
      
      final response = await http.post(
        url,
        headers: _getHeaders(),
        body: jsonEncode(body),
      ).timeout(
        Duration(seconds: AppConstants.apiTimeout),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to submit score: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error submitting score: $e');
    }
  }
  
  // ==================== Test Endpoints ====================
  
  /// GET /test/beginner - Get beginner test activities (5 random)
  Future<List<Activity>> getBeginnerTestActivities() async {
    try {
      final url = Uri.parse('$numBaseUrl/test/beginner');
      final response = await http.get(
        url,
        headers: _getHeaders(),
      ).timeout(
        Duration(seconds: AppConstants.apiTimeout),
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final activitiesList = jsonData['activities'] as List;
        return activitiesList
            .map((json) => Activity.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load test activities: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching test activities: $e');
    }
  }
  
  /// TODO: Phase 2 - Add intermediate and advanced test endpoints
  // Future<List<Activity>> getIntermediateTestActivities() async { }
  // Future<List<Activity>> getAdvancedTestActivities() async { }
  
  // ==================== Progress Endpoints ====================
  
  /// TODO: Phase 2 - Add progress sync endpoints
  // Future<void> syncProgress(List<Progress> progressList) async { }
  // Future<Map<String, dynamic>> getUserProgress() async { }
  
  // ==================== Utility Methods ====================
  
  /// Health check endpoint
  Future<bool> healthCheck() async {
    try {
      final url = Uri.parse('$numBaseUrl/health');
      final response = await http.get(url).timeout(
        const Duration(seconds: 5),
      );
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  // ==================== Object Detection Endpoints ====================
  
  /// POST /detect/objects - Detect objects in image using YOLO
  Future<ObjectDetectionResult> detectObjects({
    required Uint8List imageBytes,
    String? targetObject,
    int? expectedCount,
    double confidenceThreshold = 0.5,
  }) async {
    try {
      final url = Uri.parse('$numBaseUrl/detect/objects');
      
      // Convert image to base64
      final base64Image = base64Encode(imageBytes);
      
      final body = {
        'image_base64': base64Image,
        'target_object': targetObject,
        'expected_count': expectedCount,
        'confidence_threshold': confidenceThreshold,
      };
      
      print('🔍 Detecting objects...');
      print('   Target: $targetObject');
      print('   Expected: $expectedCount');
      print('   Image size: ${imageBytes.length} bytes');
      
      final response = await http.post(
        url,
        headers: _getHeaders(),
        body: jsonEncode(body),
      ).timeout(
        const Duration(seconds: 30), // Longer timeout for detection
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final result = ObjectDetectionResult.fromJson(jsonData);
        
        print('✅ Detection complete');
        print('   Total detected: ${result.totalCount}');
        print('   Target detected: ${result.targetCount}');
        
        return result;
      } else {
        throw Exception('Detection failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('❌ Detection error: $e');
      throw Exception('Error detecting objects: $e');
    }
  }
  
  /// GET /detect/available-classes - Get list of detectable object classes
  Future<List<String>> getAvailableClasses() async {
    try {
      final url = Uri.parse('$numBaseUrl/detect/available-classes');
      
      final response = await http.get(
        url,
        headers: _getHeaders(),
      ).timeout(
        const Duration(seconds: 10),
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final classes = List<String>.from(jsonData['classes']);
        
        print('📋 Available classes: ${classes.length}');
        return classes;
      } else {
        throw Exception('Failed to get classes: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error getting classes: $e');
      throw Exception('Error retrieving available classes: $e');
    }
  }  
  // ==================== Digit Recognition Endpoints ====================
  
  /// POST /recognize/digit - Recognize handwritten digit from image
  Future<DigitRecognitionResult> recognizeDigit({
    required Uint8List imageBytes,
    int? expectedDigit,
    double confidenceThreshold = 0.7,
  }) async {
    try {
      final url = Uri.parse('$numBaseUrl/recognize/digit');
      
      // Convert image to base64
      final base64Image = base64Encode(imageBytes);
      
      final body = {
        'image': base64Image,
        if (expectedDigit != null) 'expected_digit': expectedDigit,
        'confidence_threshold': confidenceThreshold,
      };
      
      print('🔍 Recognizing digit...');
      if (expectedDigit != null) {
        print('   Expected: $expectedDigit');
      }
      print('   Image size: ${imageBytes.length} bytes');
      
      final response = await http.post(
        url,
        headers: _getHeaders(),
        body: jsonEncode(body),
      ).timeout(
        const Duration(seconds: 15),
      );
      
      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final result = DigitRecognitionResult.fromJson(jsonData);
        
        print('✅ Recognition complete');
        print('   Predicted: ${result.predictedDigit}');
        print('   Confidence: ${(result.confidence * 100).toStringAsFixed(1)}%');
        if (result.isCorrect != null) {
          print('   Correct: ${result.isCorrect}');
        }
        
        return result;
      } else {
        throw Exception('Recognition failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('❌ Recognition error: $e');
      throw Exception('Error recognizing digit: $e');
    }
  }}

// ==================== Object Detection Models ====================

/// Object Detection Result Model
class ObjectDetectionResult {
  final int totalCount;
  final int? targetCount;
  final String? targetObject;
  final List<Detection> detections;
  final Map<String, int> classCounts;
  final ValidationResult? validation;
  
  ObjectDetectionResult({
    required this.totalCount,
    this.targetCount,
    this.targetObject,
    required this.detections,
    required this.classCounts,
    this.validation,
  });
  
  factory ObjectDetectionResult.fromJson(Map<String, dynamic> json) {
    return ObjectDetectionResult(
      totalCount: json['total_count'] as int,
      targetCount: json['target_count'] as int?,
      targetObject: json['target_object'] as String?,
      detections: (json['detections'] as List)
          .map((d) => Detection.fromJson(d))
          .toList(),
      classCounts: Map<String, int>.from(json['class_counts']),
      validation: json['validation'] != null
          ? ValidationResult.fromJson(json['validation'])
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'total_count': totalCount,
      'target_count': targetCount,
      'target_object': targetObject,
      'detections': detections.map((d) => d.toJson()).toList(),
      'class_counts': classCounts,
      'validation': validation?.toJson(),
    };
  }
}

/// Individual Detection Model
class Detection {
  final String className;
  final double confidence;
  final BoundingBox bbox;
  final int number;
  
  Detection({
    required this.className,
    required this.confidence,
    required this.bbox,
    required this.number,
  });
  
  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      className: json['class'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      bbox: BoundingBox.fromJson(json['bbox']),
      number: json['number'] as int,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'class': className,
      'confidence': confidence,
      'bbox': bbox.toJson(),
      'number': number,
    };
  }
}

/// Bounding Box Model
class BoundingBox {
  final int x1;
  final int y1;
  final int x2;
  final int y2;
  
  BoundingBox({
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
  });
  
  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x1: json['x1'] as int,
      y1: json['y1'] as int,
      x2: json['x2'] as int,
      y2: json['y2'] as int,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'x1': x1,
      'y1': y1,
      'x2': x2,
      'y2': y2,
    };
  }
  
  double get width => (x2 - x1).toDouble();
  double get height => (y2 - y1).toDouble();
  double get centerX => x1 + (width / 2);
  double get centerY => y1 + (height / 2);
}

/// Validation Result Model
class ValidationResult {
  final bool isCorrect;
  final int detectedCount;
  final int expectedCount;
  final int difference;
  final String feedback;
  final int points;
  
  ValidationResult({
    required this.isCorrect,
    required this.detectedCount,
    required this.expectedCount,
    required this.difference,
    required this.feedback,
    required this.points,
  });
  
  factory ValidationResult.fromJson(Map<String, dynamic> json) {
    return ValidationResult(
      isCorrect: json['is_correct'] as bool,
      detectedCount: json['detected_count'] as int,
      expectedCount: json['expected_count'] as int,
      difference: json['difference'] as int,
      feedback: json['feedback'] as String,
      points: json['points'] as int,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'is_correct': isCorrect,
      'detected_count': detectedCount,
      'expected_count': expectedCount,
      'difference': difference,
      'feedback': feedback,
      'points': points,
    };
  }
}

/// Digit Recognition Result Model
class DigitRecognitionResult {
  final int predictedDigit;
  final double confidence;
  final List<double> probabilities;
  final List<TopPrediction> top3Predictions;
  final bool? isCorrect;
  final int? expected;
  final String? feedback;
  
  DigitRecognitionResult({
    required this.predictedDigit,
    required this.confidence,
    required this.probabilities,
    required this.top3Predictions,
    this.isCorrect,
    this.expected,
    this.feedback,
  });
  
  factory DigitRecognitionResult.fromJson(Map<String, dynamic> json) {
    return DigitRecognitionResult(
      predictedDigit: json['predicted_digit'] as int,
      confidence: (json['confidence'] as num).toDouble(),
      probabilities: (json['probabilities'] as List)
          .map((e) => (e as num).toDouble())
          .toList(),
      top3Predictions: (json['top_3_predictions'] as List)
          .map((e) => TopPrediction.fromJson(e))
          .toList(),
      isCorrect: json['is_correct'] as bool?,
      expected: json['expected'] as int?,
      feedback: json['feedback'] as String?,
    );
  }
}

/// Top Prediction Model
class TopPrediction {
  final int digit;
  final double confidence;
  
  TopPrediction({
    required this.digit,
    required this.confidence,
  });
  
  factory TopPrediction.fromJson(Map<String, dynamic> json) {
    return TopPrediction(
      digit: json['digit'] as int,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}

