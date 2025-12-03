import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:ganithamithura/models/unit_models.dart';

/// API Service for Unit-based Learning
/// Base URL should be configured in production
class UnitApiService {
  // TODO: Move to config file
  static const String baseUrl = 'http://localhost:8000/api';
  
  // Singleton pattern
  static final UnitApiService _instance = UnitApiService._internal();
  factory UnitApiService() => _instance;
  UnitApiService._internal();
  
  // Current student ID (should be set on login/app start)
  String? _currentStudentId;
  
  void setStudentId(String studentId) {
    _currentStudentId = studentId;
  }
  
  String get studentId => _currentStudentId ?? 'student_default';
  
  /// GET /api/units?grade=3
  /// Fetch all units for a specific grade
  Future<List<Unit>> getUnits(int grade) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/units?grade=$grade'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Unit.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load units: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock data for MVP if API fails
      return _getMockUnits(grade);
    }
  }
  
  /// GET /api/units/{unitId}/progress
  /// Fetch student progress for a specific unit
  Future<StudentUnitProgress?> getUnitProgress(String unitId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/units/$unitId/progress?studentId=$studentId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return StudentUnitProgress.fromJson(json.decode(response.body));
      }
      return null;
    } catch (e) {
      // Return mock progress for MVP
      return _getMockProgress(unitId);
    }
  }
  
  /// POST /api/questions/next
  /// Get next question for practice
  Future<Question> getNextQuestion(String unitId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/questions/next'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'studentId': studentId,
          'unitId': unitId,
        }),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return Question.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to get question: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock question for MVP
      return _getMockQuestion(unitId);
    }
  }
  
  /// POST /api/questions/answer
  /// Submit answer and get feedback
  Future<AnswerResponse> submitAnswer({
    required String questionId,
    required int selectedIndex,
    required String unitId,
    required int timeTaken,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/questions/answer'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'questionId': questionId,
          'selectedIndex': selectedIndex,
          'studentId': studentId,
          'unitId': unitId,
          'timeTaken': timeTaken,
        }),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return AnswerResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to submit answer: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock response for MVP
      return _getMockAnswerResponse(selectedIndex);
    }
  }
  
  /// POST /api/chat
  /// Send chat message and get AI response
  Future<ChatResponse> sendChatMessage({
    required String unitId,
    required String message,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'studentId': studentId,
          'unitId': unitId,
          'message': message,
        }),
      ).timeout(const Duration(seconds: 15));
      
      if (response.statusCode == 200) {
        return ChatResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to send message: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock response for MVP
      return _getMockChatResponse(message);
    }
  }
  
  // ========== MOCK DATA FOR MVP ==========
  
  List<Unit> _getMockUnits(int grade) {
    return [
      Unit(
        id: 'unit_length_$grade',
        name: 'Length – cm and m',
        topic: 'Length',
        grade: grade,
        description: 'Learn to measure length using centimeters and meters',
        iconName: 'straighten',
      ),
      Unit(
        id: 'unit_area_$grade',
        name: 'Area – cm² and m²',
        topic: 'Area',
        grade: grade,
        description: 'Understand how to calculate area of shapes',
        iconName: 'crop_square',
      ),
      Unit(
        id: 'unit_capacity_$grade',
        name: 'Capacity – ml and l',
        topic: 'Capacity',
        grade: grade,
        description: 'Learn about volume and capacity measurements',
        iconName: 'local_drink',
      ),
      Unit(
        id: 'unit_weight_$grade',
        name: 'Weight – g and kg',
        topic: 'Weight',
        grade: grade,
        description: 'Understand weight measurements in grams and kilograms',
        iconName: 'fitness_center',
      ),
    ];
  }
  
  StudentUnitProgress _getMockProgress(String unitId) {
    return StudentUnitProgress(
      unitId: unitId,
      questionsAnswered: 12,
      correctAnswers: 9,
      accuracy: 75.0,
      stars: 3,
    );
  }
  
  Question _getMockQuestion(String unitId) {
    final questions = [
      Question(
        questionId: 'q1_${DateTime.now().millisecondsSinceEpoch}',
        questionText: 'How many centimeters are in 1 meter?',
        options: ['10 cm', '100 cm', '1000 cm', '50 cm'],
        correctIndex: 1,
        difficulty: 'easy',
        explanation: '1 meter equals 100 centimeters. Remember: 1m = 100cm',
      ),
      Question(
        questionId: 'q2_${DateTime.now().millisecondsSinceEpoch}',
        questionText: 'If a pencil is 15 cm long, how many mm is that?',
        options: ['150 mm', '15 mm', '1500 mm', '1.5 mm'],
        correctIndex: 0,
        difficulty: 'medium',
        explanation: '1 cm = 10 mm, so 15 cm = 15 × 10 = 150 mm',
      ),
      Question(
        questionId: 'q3_${DateTime.now().millisecondsSinceEpoch}',
        questionText: 'Which is longer: 2 meters or 150 centimeters?',
        options: ['2 meters', '150 centimeters', 'They are equal', 'Cannot compare'],
        correctIndex: 0,
        difficulty: 'easy',
        explanation: '2 meters = 200 cm, which is longer than 150 cm',
      ),
    ];
    
    return questions[DateTime.now().second % questions.length];
  }
  
  AnswerResponse _getMockAnswerResponse(int selectedIndex) {
    final isCorrect = selectedIndex == 1; // Mock: option B is correct
    return AnswerResponse(
      isCorrect: isCorrect,
      correctIndex: 1,
      explanation: isCorrect 
          ? 'Great job! That\'s correct!' 
          : '1 meter equals 100 centimeters. Remember: 1m = 100cm',
    );
  }
  
  ChatResponse _getMockChatResponse(String message) {
    return ChatResponse(
      reply: 'Great question! In measurement, we use different units for different sizes. '
             'For example, we use centimeters (cm) for small things like pencils, '
             'and meters (m) for bigger things like the height of a door. '
             'Remember: 100 cm = 1 m. Would you like to practice some questions?',
    );
  }
}
