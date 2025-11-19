/// Constants for the Ganithamithura Learning App - Phase 1
library;

class AppConstants {
  // API Configuration
  static const String baseUrl = 'http://localhost:8000';
  
  // Activity Types
  static const String activityTypeTrace = 'trace';
  static const String activityTypeRead = 'read';
  static const String activityTypeSay = 'say';
  static const String activityTypeObjectDetection = 'object_detection';
  static const String activityTypeVideo = 'video';
  
  // Scoring Thresholds
  static const double traceSuccessThreshold = 0.70; // 70% coverage
  static const double speechRecognitionThreshold = 0.80; // 80% similarity
  
  // Test Configuration
  static const int beginnerTestActivityCount = 5;
  static const int activitiesPerNumber = 5;
  static const int testBucketSize = 6; // Show 5 out of 6
  
  // Level Configuration
  static const int totalLevels = 5;
  static const int level1MinNumber = 1;
  static const int level1MaxNumber = 10;
  
  // TODO: Phase 2 - Define levels 2-5 number ranges
  // static const int level2MinNumber = 11;
  // static const int level2MaxNumber = 20;
  
  // Timeouts
  static const int videoLoadTimeout = 30; // seconds
  static const int apiTimeout = 10; // seconds
  
  // UI Constants
  static const double buttonBorderRadius = 16.0;
  static const double cardElevation = 4.0;
  static const double standardPadding = 16.0;
  
  // Animation Durations
  static const Duration shortAnimationDuration = Duration(milliseconds: 300);
  static const Duration mediumAnimationDuration = Duration(milliseconds: 600);
  static const Duration longAnimationDuration = Duration(milliseconds: 1000);
}

class StorageKeys {
  static const String completedActivities = 'completed_activities';
  static const String testScores = 'test_scores';
  static const String currentLevel = 'current_level';
  static const String progressData = 'progress_data';
  static const String lastActivityDate = 'last_activity_date';
}

class NumberWords {
  static const Map<int, String> numberToWord = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    // TODO: Phase 2 - Add numbers 11-100
  };
  
  static String getWord(int number) => numberToWord[number] ?? '';
  
  static int? getNumber(String word) {
    return numberToWord.entries
        .firstWhere(
          (entry) => entry.value.toLowerCase() == word.toLowerCase(),
          orElse: () => const MapEntry(0, ''),
        )
        .key;
  }
}

class AppColors {
  // Module Colors
  static const int measurementColor = 0xFF4CAF50; // Green
  static const int numberColor = 0xFF2196F3; // Blue
  static const int shapeColor = 0xFFFF9800; // Orange
  static const int symbolColor = 0xFF9C27B0; // Purple
  
  // Status Colors
  static const int successColor = 0xFF4CAF50;
  static const int errorColor = 0xFFF44336;
  static const int warningColor = 0xFFFFC107;
  static const int infoColor = 0xFF2196F3;
  
  // UI Colors
  static const int primaryColor = 0xFF6200EE;
  static const int secondaryColor = 0xFF03DAC6;
  static const int backgroundColor = 0xFFF5F5F5;
  static const int disabledColor = 0xFFBDBDBD;
}
