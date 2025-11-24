import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/utils/ui_helpers.dart';
import 'package:ganithamithura/models/models.dart';
import 'package:ganithamithura/widgets/common/buttons_and_cards.dart';
import 'package:ganithamithura/screens/number/video_lesson/video_lesson_screen.dart';
import 'package:ganithamithura/services/api/api_service.dart';
import 'package:ganithamithura/services/bucket_manager.dart';

/// LevelSelectionScreen - Display 5 levels with only Level 1 enabled
class LevelSelectionScreen extends StatefulWidget {
  const LevelSelectionScreen({super.key});
  
  @override
  State<LevelSelectionScreen> createState() => _LevelSelectionScreenState();
}

class _LevelSelectionScreenState extends State<LevelSelectionScreen> {
  late List<LearningLevel> _levels;
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _initializeLevels();
  }
  
  Future<void> _initializeLevels() async {
    // TODO: Phase 2 - Load level progress from storage
    setState(() {
      _levels = [
        LearningLevel(
          levelNumber: 1,
          title: 'Level 1',
          description: 'Numbers 1-10',
          minNumber: 1,
          maxNumber: 10,
          isUnlocked: true,
          totalActivities: 50, // 10 numbers × 5 activities
          completedActivities: 0,
        ),
        LearningLevel(
          levelNumber: 2,
          title: 'Level 2',
          description: 'Numbers 11-20',
          minNumber: 11,
          maxNumber: 20,
          isUnlocked: false,
        ),
        LearningLevel(
          levelNumber: 3,
          title: 'Level 3',
          description: 'Numbers 21-50',
          minNumber: 21,
          maxNumber: 50,
          isUnlocked: false,
        ),
        LearningLevel(
          levelNumber: 4,
          title: 'Level 4',
          description: 'Numbers 51-100',
          minNumber: 51,
          maxNumber: 100,
          isUnlocked: false,
        ),
        LearningLevel(
          levelNumber: 5,
          title: 'Level 5',
          description: 'Advanced Numbers',
          minNumber: 100,
          maxNumber: 1000,
          isUnlocked: false,
        ),
      ];
      _isLoading = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(AppColors.backgroundColor),
      appBar: AppBar(
        title: const Text('Select Level'),
        backgroundColor: Color(AppColors.numberColor),
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(AppConstants.standardPadding),
                child: ListView.builder(
                  itemCount: _levels.length,
                  itemBuilder: (context, index) {
                    final level = _levels[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: LevelCard(
                        levelNumber: level.levelNumber,
                        title: level.title,
                        description: level.description,
                        isUnlocked: level.isUnlocked,
                        progress: level.progress,
                        onTap: level.isUnlocked
                            ? () => _startLevel(level)
                            : null,
                      ),
                    );
                  },
                ),
              ),
            ),
    );
  }
  
  void _startLevel(LearningLevel level) async {
    // Show loading with a small delay to ensure overlay is ready
    await Future.delayed(const Duration(milliseconds: 100));
    
    Get.dialog(
      Material(
        color: Colors.transparent,
        child: const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        ),
      ),
      barrierDismissible: false,
    );
    
    try {
      // Fetch activities for this level
      final activities = await ApiService.instance.getActivitiesForLevel(level.levelNumber);
      
      if (activities.isEmpty) {
        Get.back();
        await UIHelpers.showSafeSnackbar(
          title: 'Error',
          message: 'No activities found for this level',
          backgroundColor: Color(AppColors.errorColor),
        );
        return;
      }
      
      // Get learning sequence for first number
      final bucketManager = BucketManager.instance;
      final firstNumber = level.minNumber;
      final numberActivities = bucketManager.getLearningSequenceForNumber(
        activities,
        firstNumber,
      );
      
      Get.back(); // Close loading
      
      // Navigate to first activity (video lesson)
      if (numberActivities.isNotEmpty) {
        await Future.delayed(const Duration(milliseconds: 100));
        Get.to(() => VideoLessonScreen(
          activity: numberActivities.first,
          allActivities: activities,
          currentNumber: firstNumber,
          level: level,
        ));
      }
    } catch (e) {
      Get.back();
      await UIHelpers.showSafeSnackbar(
        title: 'Error',
        message: 'Failed to load activities: $e',
        backgroundColor: Color(AppColors.errorColor),
      );
    }
  }
}
