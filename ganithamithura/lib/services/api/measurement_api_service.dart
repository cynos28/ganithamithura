/// API client for measurement-service (port 8001)
/// Processes AR measurements and builds educational context

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/ar_measurement.dart';
import '../../utils/api_config.dart';

class MeasurementApiService {
  static String get baseUrl => ApiConfig.measurementServiceUrl;
  static const Duration timeout = Duration(seconds: 30);
  
  /// Process an AR measurement and get educational context
  /// 
  /// Takes raw AR measurement data and returns structured context
  /// including suggested grade, difficulty hints, and personalized prompts
  Future<MeasurementContext> processMeasurement({
    required MeasurementType measurementType,
    required double value,
    required MeasurementUnit unit,
    required String objectName,
    required String studentId,
    required int grade,
  }) async {
    try {
      final request = ARMeasurementRequest(
        measurementType: measurementType,
        value: value,
        unit: unit,
        objectName: objectName,
        studentId: studentId,
        grade: grade,
      );
      
      print('🔄 Processing AR measurement: ${request.toJson()}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/process'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      ).timeout(
        timeout,
        onTimeout: () {
          throw Exception(
            'Connection timeout: measurement-service did not respond within ${timeout.inSeconds}s. '
            'Please check if the service is running and accessible.'
          );
        },
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final context = MeasurementContext.fromJson(data);
        
        print('✅ Measurement context built: ${context.topicDisplay}');
        print('   Suggested grade: ${context.suggestedGrade}');
        print('   Prompt: ${context.personalizedPrompt}');
        
        return context;
      } else {
        throw Exception(
          'Failed to process measurement: ${response.statusCode} - ${response.body}'
        );
      }
    } catch (e) {
      print('❌ Error processing measurement: $e');
      rethrow;
    }
  }
  
  /// Quick measurement context for testing (without AR)
  Future<MeasurementContext> quickMeasurement({
    required String objectName,
    required double value,
    required MeasurementUnit unit,
    required MeasurementType type,
    int grade = 1,
  }) async {
    return processMeasurement(
      measurementType: type,
      value: value,
      unit: unit,
      objectName: objectName,
      studentId: 'student_123', // TODO: Get from auth service
      grade: grade,
    );
  }
  
  /// Check if measurement-service is available
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse(ApiConfig.measurementHealthUrl),
      ).timeout(const Duration(seconds: 3));
      
      return response.statusCode == 200;
    } catch (e) {
      print('❌ measurement-service not available: $e');
      return false;
    }
  }
}
