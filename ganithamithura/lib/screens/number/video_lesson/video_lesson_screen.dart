import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/models/models.dart';
import 'package:ganithamithura/widgets/common/buttons_and_cards.dart';
import 'package:ganithamithura/services/learning_flow_manager.dart';

/// VideoLessonScreen - Display video lesson with Continue button
class VideoLessonScreen extends StatefulWidget {
  final Activity activity;
  final List<Activity> allActivities;
  final int currentNumber;
  final LearningLevel level;
  
  const VideoLessonScreen({
    super.key,
    required this.activity,
    required this.allActivities,
    required this.currentNumber,
    required this.level,
  });
  
  @override
  State<VideoLessonScreen> createState() => _VideoLessonScreenState();
}

class _VideoLessonScreenState extends State<VideoLessonScreen> {
  bool _videoCompleted = false;
  
  @override
  void initState() {
    super.initState();
    // Simulate video completion after 5 seconds (placeholder)
    Future.delayed(const Duration(seconds: 5), () {
      if (mounted) {
        setState(() {
          _videoCompleted = true;
        });
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Learn Number ${widget.currentNumber}'),
        backgroundColor: Color(AppColors.numberColor),
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Video player area
            Expanded(
              child: Center(
                child: _buildVideoPlaceholder(),
              ),
            ),
            
            // Controls
            Container(
              color: Colors.black87,
              padding: const EdgeInsets.all(AppConstants.standardPadding),
              child: Column(
                children: [
                  // Number display
                  // NumberDisplay(
                  //   number: widget.currentNumber,
                  //   word: NumberWords.getWord(widget.currentNumber),
                  // ),
                  const SizedBox(height: 24),
                  
                  // Continue button
                  ActionButton(
                    text: 'Continue',
                    icon: Icons.arrow_forward,
                    isEnabled: _videoCompleted,
                    onPressed: _onContinue,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildVideoPlaceholder() {
    return Container(
      margin: const EdgeInsets.all(AppConstants.standardPadding),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(AppConstants.buttonBorderRadius),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // TODO: Phase 2 - Integrate actual video player
          // Use video_player or chewie package
          Icon(
            _videoCompleted ? Icons.check_circle : Icons.play_circle_outline,
            size: 100,
            color: _videoCompleted 
                ? Color(AppColors.successColor)
                : Colors.white,
          ),
          const SizedBox(height: 24),
          Text(
            _videoCompleted 
                ? 'Video Completed!' 
                : 'Playing video...',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Learn about number ${widget.currentNumber}',
            style: TextStyle(
              color: Colors.grey[400],
              fontSize: 16,
            ),
          ),
          if (!_videoCompleted) ...[
            const SizedBox(height: 24),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ],
      ),
    );
  }
  
  void _onContinue() async {
    debugPrint('🎬 Video continue button pressed');
    debugPrint('  Current activity: ${widget.activity.id} (${widget.activity.type})');
    debugPrint('  Current number: ${widget.currentNumber}');
    debugPrint('  Level: ${widget.level.levelNumber}');
    
    // Use LearningFlowManager to handle progression
    final learningFlowManager = LearningFlowManager.instance;
    
    try {
      await learningFlowManager.moveToNextActivity(
        currentActivity: widget.activity,
        currentNumber: widget.currentNumber,
        level: widget.level,
        isTutorial: true, // Tutorial mode uses easy questions
      );
      debugPrint('  ✅ moveToNextActivity completed');
    } catch (e) {
      debugPrint('  ❌ Error in moveToNextActivity: $e');
      Get.snackbar(
        'Error',
        'Failed to load next activity: $e',
        backgroundColor: Color(AppColors.errorColor),
        colorText: Colors.white,
      );
    }
  }
}