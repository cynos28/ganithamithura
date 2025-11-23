/// Models for Unit-based Learning System

class Unit {
  final String id;
  final String name;
  final String topic; // Length, Area, Capacity, Weight
  final int grade;
  final String? description;
  final String? iconName;

  Unit({
    required this.id,
    required this.name,
    required this.topic,
    required this.grade,
    this.description,
    this.iconName,
  });

  factory Unit.fromJson(Map<String, dynamic> json) {
    return Unit(
      id: json['id'] ?? json['unitId'] ?? '',
      name: json['name'] ?? '',
      topic: json['topic'] ?? '',
      grade: json['grade'] ?? 0,
      description: json['description'],
      iconName: json['iconName'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'topic': topic,
      'grade': grade,
      'description': description,
      'iconName': iconName,
    };
  }
}

class StudentUnitProgress {
  final String unitId;
  final int questionsAnswered;
  final int correctAnswers;
  final double accuracy;
  final int stars;

  StudentUnitProgress({
    required this.unitId,
    required this.questionsAnswered,
    required this.correctAnswers,
    required this.accuracy,
    required this.stars,
  });

  factory StudentUnitProgress.fromJson(Map<String, dynamic> json) {
    return StudentUnitProgress(
      unitId: json['unitId'] ?? '',
      questionsAnswered: json['questionsAnswered'] ?? 0,
      correctAnswers: json['correctAnswers'] ?? 0,
      accuracy: (json['accuracy'] ?? 0).toDouble(),
      stars: json['stars'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'unitId': unitId,
      'questionsAnswered': questionsAnswered,
      'correctAnswers': correctAnswers,
      'accuracy': accuracy,
      'stars': stars,
    };
  }
}

class Question {
  final String questionId;
  final String questionText;
  final List<String> options;
  final int? correctIndex;
  final String difficulty; // easy, medium, hard
  final String explanation;

  Question({
    required this.questionId,
    required this.questionText,
    required this.options,
    this.correctIndex,
    required this.difficulty,
    required this.explanation,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      questionId: json['questionId'] ?? '',
      questionText: json['questionText'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      correctIndex: json['correctIndex'],
      difficulty: json['difficulty'] ?? 'easy',
      explanation: json['explanation'] ?? json['explanation_en'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'questionId': questionId,
      'questionText': questionText,
      'options': options,
      'correctIndex': correctIndex,
      'difficulty': difficulty,
      'explanation': explanation,
    };
  }
}

class AnswerResponse {
  final bool isCorrect;
  final int correctIndex;
  final String explanation;

  AnswerResponse({
    required this.isCorrect,
    required this.correctIndex,
    required this.explanation,
  });

  factory AnswerResponse.fromJson(Map<String, dynamic> json) {
    return AnswerResponse(
      isCorrect: json['isCorrect'] ?? false,
      correctIndex: json['correctIndex'] ?? 0,
      explanation: json['explanation'] ?? json['explanation_en'] ?? '',
    );
  }
}

class ChatMessage {
  final String message;
  final bool isUser;
  final DateTime timestamp;
  final String? reply;

  ChatMessage({
    required this.message,
    required this.isUser,
    required this.timestamp,
    this.reply,
  });
}

class ChatResponse {
  final String reply;

  ChatResponse({
    required this.reply,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      reply: json['reply'] ?? json['reply_en'] ?? '',
    );
  }
}
