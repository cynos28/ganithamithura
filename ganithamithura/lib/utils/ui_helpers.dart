import 'package:flutter/material.dart';
import 'package:get/get.dart';

/// Helper utilities for safe UI operations
class UIHelpers {
  /// Safely show a snackbar with a delay to ensure overlay is available
  static Future<void> showSafeSnackbar({
    required String title,
    required String message,
    required Color backgroundColor,
    Color colorText = Colors.white,
    Duration duration = const Duration(seconds: 2),
    int delayMilliseconds = 100,
  }) async {
    await Future.delayed(Duration(milliseconds: delayMilliseconds));
    
    // Check if Get context is available
    if (Get.context != null) {
      Get.snackbar(
        title,
        message,
        backgroundColor: backgroundColor,
        colorText: colorText,
        duration: duration,
      );
    }
  }

  /// Safely show a dialog with a delay to ensure overlay is available
  static Future<void> showSafeDialog({
    required Widget dialog,
    bool barrierDismissible = true,
    int delayMilliseconds = 100,
  }) async {
    await Future.delayed(Duration(milliseconds: delayMilliseconds));
    
    // Check if Get context is available
    if (Get.context != null) {
      Get.dialog(
        dialog,
        barrierDismissible: barrierDismissible,
      );
    }
  }
}
