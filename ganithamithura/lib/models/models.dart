import 'package:ganithamithura/utils/constants.dart';

/// Activity Model - Represents a learning activity
class Activity {
  final String id;
  final String type; // trace, read, say, object_detection, video, show
  final int number; // The number this activity teaches
  final String title;
  final String? description;
  final Map<String, dynamic>? metadata; // Activity-specific data
  final int level;
  final int order; // Order within the number sequence
  final List<ActivityQuestion>? questions; // Array of questions with difficulty
  
  Activity({
    required this.id,
    required this.type,
    required this.number,
    required this.title,
    this.description,
    this.metadata,
    required this.level,
    required this.order,
    this.questions,
  });
  
  factory Activity.fromJson(Map<String, dynamic> json) {
    List<ActivityQuestion>? questionsList;
    if (json['questions'] != null) {
      questionsList = (json['questions'] as List)
          .map((q) => ActivityQuestion.fromJson(q))
          .toList();
    }
    
    return Activity(
      id: json['id'] as String,
      type: json['type'] as String,
      number: json['number'] as int,
      title: json['title'] as String,
      description: json['description'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      level: json['level'] as int,
      order: json['order'] as int,
      questions: questionsList,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'number': number,
      'title': title,
      'description': description,
      'metadata': metadata,
      'level': level,
      'order': order,
      'questions': questions?.map((q) => q.toJson()).toList(),
    };
  }
  
  // Get questions by difficulty
  List<ActivityQuestion> getQuestionsByDifficulty(String difficulty) {
    if (questions == null) return [];
    return questions!.where((q) => q.difficulty == difficulty).toList();
  }
  
  // Get easy question for tutorial
  ActivityQuestion? getEasyQuestion() {
    if (questions == null || questions!.isEmpty) return null;
    try {
      return questions!.firstWhere((q) => q.difficulty == 'easy');
    } catch (e) {
      return questions!.first;
    }
  }
  
  // Get non-easy questions for progress test
  List<ActivityQuestion> getTestQuestions() {
    if (questions == null) return [];
    return questions!.where((q) => q.difficulty != 'easy').toList();
  }
  
  bool get isVideoLesson => type == AppConstants.activityTypeVideo;
  bool get isTraceActivity => type == AppConstants.activityTypeTrace;
  bool get isReadActivity => type == AppConstants.activityTypeRead;
  bool get isSayActivity => type == AppConstants.activityTypeSay;
  bool get isObjectDetection => type == AppConstants.activityTypeObjectDetection || type == 'show';
}

/// Activity Question Model - Represents a single question within an activity
class ActivityQuestion {
  final String id;
  final String difficulty; // easy, medium, hard
  final int points;
  final String? question;
  final String? instruction;
  final dynamic correctAnswer;
  final List<String>? options;
  final String? answer;
  final String? image;
  final String? templateImage;
  final String? helpImage;
  final String? pronounce;
  final List<String>? alternatives;
  final int? maxObjects;
  final String? type; // For read activity
  
  ActivityQuestion({
    required this.id,
    required this.difficulty,
    required this.points,
    this.question,
    this.instruction,
    this.correctAnswer,
    this.options,
    this.answer,
    this.image,
    this.templateImage,
    this.helpImage,
    this.pronounce,
    this.alternatives,
    this.maxObjects,
    this.type,
  });
  
  factory ActivityQuestion.fromJson(Map<String, dynamic> json) {
    return ActivityQuestion(
      id: json['id'] as String,
      difficulty: json['difficulty'] as String,
      points: json['points'] as int,
      question: json['question'] as String?,
      instruction: json['instruction'] as String?,
      correctAnswer: json['correct_answer'],
      options: json['options'] != null 
          ? List<String>.from(json['options']) 
          : null,
      answer: json['answer'] as String?,
      image: json['image'] as String?,
      templateImage: json['template_image'] as String?,
      helpImage: json['help_image'] as String?,
      pronounce: json['pronounce'] as String?,
      alternatives: json['alternatives'] != null 
          ? List<String>.from(json['alternatives']) 
          : null,
      maxObjects: json['max_objects'] as int?,
      type: json['type'] as String?,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'difficulty': difficulty,
      'points': points,
      'question': question,
      'instruction': instruction,
      'correct_answer': correctAnswer,
      'options': options,
      'answer': answer,
      'image': image,
      'template_image': templateImage,
      'help_image': helpImage,
      'pronounce': pronounce,
      'alternatives': alternatives,
      'max_objects': maxObjects,
      'type': type,
    };
  }
}

/// Level Model - Represents a learning level
class LearningLevel {
  final int levelNumber;
  final String title;
  final String description;
  final int minNumber;
  final int maxNumber;
  final bool isUnlocked;
  final int totalActivities;
  final int completedActivities;
  
  LearningLevel({
    required this.levelNumber,
    required this.title,
    required this.description,
    required this.minNumber,
    required this.maxNumber,
    required this.isUnlocked,
    this.totalActivities = 0,
    this.completedActivities = 0,
  });
  
  double get progress => totalActivities > 0 
      ? completedActivities / totalActivities 
      : 0.0;
  
  bool get isCompleted => completedActivities == totalActivities && totalActivities > 0;
  
  factory LearningLevel.fromJson(Map<String, dynamic> json) {
    return LearningLevel(
      levelNumber: json['levelNumber'] as int,
      title: json['title'] as String,
      description: json['description'] as String,
      minNumber: json['minNumber'] as int,
      maxNumber: json['maxNumber'] as int,
      isUnlocked: json['isUnlocked'] as bool,
      totalActivities: json['totalActivities'] as int? ?? 0,
      completedActivities: json['completedActivities'] as int? ?? 0,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'levelNumber': levelNumber,
      'title': title,
      'description': description,
      'minNumber': minNumber,
      'maxNumber': maxNumber,
      'isUnlocked': isUnlocked,
      'totalActivities': totalActivities,
      'completedActivities': completedActivities,
    };
  }
}

/// Progress Model - Tracks user's progress
class Progress {
  final String activityId;
  final int score;
  final bool isCompleted;
  final DateTime completedAt;
  final int attempts;
  final Map<String, dynamic>? additionalData;
  
  Progress({
    required this.activityId,
    required this.score,
    required this.isCompleted,
    required this.completedAt,
    this.attempts = 1,
    this.additionalData,
  });
  
  factory Progress.fromJson(Map<String, dynamic> json) {
    return Progress(
      activityId: json['activityId'] as String,
      score: json['score'] as int,
      isCompleted: json['isCompleted'] as bool,
      completedAt: DateTime.parse(json['completedAt'] as String),
      attempts: json['attempts'] as int? ?? 1,
      additionalData: json['additionalData'] as Map<String, dynamic>?,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'activityId': activityId,
      'score': score,
      'isCompleted': isCompleted,
      'completedAt': completedAt.toIso8601String(),
      'attempts': attempts,
      'additionalData': additionalData,
    };
  }
}

/// Test Result Model
class TestResult {
  final String testType; // 'beginner', 'intermediate', 'advanced'
  final int totalQuestions;
  final int correctAnswers;
  final DateTime completedAt;
  final List<String> activityIds;
  final Map<String, bool> activityResults; // activityId -> wasCorrect
  
  TestResult({
    required this.testType,
    required this.totalQuestions,
    required this.correctAnswers,
    required this.completedAt,
    required this.activityIds,
    required this.activityResults,
  });
  
  double get percentage => totalQuestions > 0 
      ? (correctAnswers / totalQuestions) * 100 
      : 0.0;
  
  bool get isPassed => percentage >= 70.0;
  
  factory TestResult.fromJson(Map<String, dynamic> json) {
    return TestResult(
      testType: json['testType'] as String,
      totalQuestions: json['totalQuestions'] as int,
      correctAnswers: json['correctAnswers'] as int,
      completedAt: DateTime.parse(json['completedAt'] as String),
      activityIds: List<String>.from(json['activityIds'] as List),
      activityResults: Map<String, bool>.from(json['activityResults'] as Map),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'testType': testType,
      'totalQuestions': totalQuestions,
      'correctAnswers': correctAnswers,
      'completedAt': completedAt.toIso8601String(),
      'activityIds': activityIds,
      'activityResults': activityResults,
    };
  }
}
