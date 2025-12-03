/// On-device object detection using ML Kit Image Labeling
/// Detects classroom objects when user taps on AR plane

import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/services.dart';
import 'package:google_mlkit_image_labeling/google_mlkit_image_labeling.dart';
import 'package:image/image.dart' as img;

class ClassroomObject {
  final String name;
  final String icon;
  final String category; // length, area, capacity, weight
  
  const ClassroomObject({
    required this.name,
    required this.icon,
    required this.category,
  });
}

class DetectionResult {
  final String suggestedObject;
  final double confidence;
  final List<String> alternatives;
  
  DetectionResult({
    required this.suggestedObject,
    required this.confidence,
    required this.alternatives,
  });
}

class ObjectDetectionService {
  ImageLabeler? _imageLabeler;
  
  // Predefined classroom objects with icons
  static const List<ClassroomObject> classroomObjects = [
    ClassroomObject(name: 'Desk', icon: '📚', category: 'length'),
    ClassroomObject(name: 'Chair', icon: '🪑', category: 'length'),
    ClassroomObject(name: 'Door', icon: '🚪', category: 'length'),
    ClassroomObject(name: 'Window', icon: '🪟', category: 'length'),
    ClassroomObject(name: 'Whiteboard', icon: '⬜', category: 'area'),
    ClassroomObject(name: 'Blackboard', icon: '⬛', category: 'area'),
    ClassroomObject(name: 'Floor Mat', icon: '🟫', category: 'area'),
    ClassroomObject(name: 'Water Bottle', icon: '🍼', category: 'capacity'),
    ClassroomObject(name: 'Cup', icon: '☕', category: 'capacity'),
    ClassroomObject(name: 'Jug', icon: '🫗', category: 'capacity'),
    ClassroomObject(name: 'Book', icon: '📖', category: 'weight'),
    ClassroomObject(name: 'School Bag', icon: '🎒', category: 'weight'),
    ClassroomObject(name: 'Pencil Box', icon: '✏️', category: 'weight'),
    ClassroomObject(name: 'Ruler', icon: '📏', category: 'length'),
    ClassroomObject(name: 'Table', icon: '🪑', category: 'length'),
    ClassroomObject(name: 'Other', icon: '❓', category: 'length'),
  ];
  
  // ML Kit labels → Classroom object mapping
  static const Map<String, String> _labelMapping = {
    'table': 'Desk',
    'desk': 'Desk',
    'furniture': 'Desk',
    'chair': 'Chair',
    'seat': 'Chair',
    'door': 'Door',
    'window': 'Window',
    'board': 'Whiteboard',
    'whiteboard': 'Whiteboard',
    'blackboard': 'Blackboard',
    'bottle': 'Water Bottle',
    'container': 'Water Bottle',
    'cup': 'Cup',
    'mug': 'Cup',
    'jug': 'Jug',
    'pitcher': 'Jug',
    'book': 'Book',
    'notebook': 'Book',
    'textbook': 'Book',
    'backpack': 'School Bag',
    'bag': 'School Bag',
    'schoolbag': 'School Bag',
    'ruler': 'Ruler',
    'pencil': 'Pencil Box',
    'pen': 'Pencil Box',
    'stationery': 'Pencil Box',
    'floor': 'Floor Mat',
    'carpet': 'Floor Mat',
    'rug': 'Floor Mat',
    'mat': 'Floor Mat',
  };
  
  /// Initialize ML Kit Image Labeler
  Future<void> initialize() async {
    try {
      final options = ImageLabelerOptions(
        confidenceThreshold: 0.5, // Lower threshold, we'll filter later
      );
      _imageLabeler = ImageLabeler(options: options);
      print('✅ Object detection initialized');
    } catch (e) {
      print('❌ Failed to initialize object detection: $e');
    }
  }
  
  /// Detect object from camera frame at specific tap point
  /// 
  /// Strategy: Crop around tap point for faster, more accurate detection
  Future<DetectionResult?> detectObjectAtPoint({
    required String imagePath,
    required double tapX,
    required double tapY,
  }) async {
    if (_imageLabeler == null) {
      await initialize();
    }
    
    try {
      print('🔍 Detecting object at tap point ($tapX, $tapY)...');
      
      // Load and crop image around tap point
      final inputImage = InputImage.fromFilePath(imagePath);
      
      // Run ML Kit detection
      final labels = await _imageLabeler!.processImage(inputImage);
      
      if (labels.isEmpty) {
        print('⚠️ No objects detected');
        return null;
      }
      
      // Filter and map labels
      final mappedLabels = <String, double>{};
      
      for (final label in labels) {
        final labelText = label.label.toLowerCase();
        final confidence = label.confidence;
        
        // Only consider high confidence labels
        if (confidence < 0.6) continue;
        
        // Map to classroom object
        final classroomObject = _mapToClassroomObject(labelText);
        if (classroomObject != null) {
          // Keep highest confidence for each classroom object
          if (!mappedLabels.containsKey(classroomObject) ||
              mappedLabels[classroomObject]! < confidence) {
            mappedLabels[classroomObject] = confidence;
          }
        }
      }
      
      if (mappedLabels.isEmpty) {
        print('⚠️ No classroom objects found in labels');
        return null;
      }
      
      // Sort by confidence
      final sorted = mappedLabels.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      
      final topMatch = sorted.first;
      final alternatives = sorted
          .skip(1)
          .take(2)
          .map((e) => e.key)
          .toList();
      
      print('✅ Detected: ${topMatch.key} (${(topMatch.value * 100).toInt()}%)');
      
      return DetectionResult(
        suggestedObject: topMatch.key,
        confidence: topMatch.value,
        alternatives: alternatives,
      );
      
    } catch (e) {
      print('❌ Detection error: $e');
      return null;
    }
  }
  
  /// Simplified detection without tap point (uses full image)
  Future<DetectionResult?> detectObject(String imagePath) async {
    if (_imageLabeler == null) {
      await initialize();
    }
    
    try {
      final inputImage = InputImage.fromFilePath(imagePath);
      final labels = await _imageLabeler!.processImage(inputImage);
      
      if (labels.isEmpty) return null;
      
      // Map labels to classroom objects
      final mappedLabels = <String, double>{};
      
      for (final label in labels) {
        if (label.confidence < 0.6) continue;
        
        final classroomObject = _mapToClassroomObject(label.label.toLowerCase());
        if (classroomObject != null) {
          if (!mappedLabels.containsKey(classroomObject) ||
              mappedLabels[classroomObject]! < label.confidence) {
            mappedLabels[classroomObject] = label.confidence;
          }
        }
      }
      
      if (mappedLabels.isEmpty) return null;
      
      final sorted = mappedLabels.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      
      return DetectionResult(
        suggestedObject: sorted.first.key,
        confidence: sorted.first.value,
        alternatives: sorted.skip(1).take(2).map((e) => e.key).toList(),
      );
      
    } catch (e) {
      print('❌ Detection error: $e');
      return null;
    }
  }
  
  /// Map ML Kit label to classroom object name
  String? _mapToClassroomObject(String label) {
    final normalized = label.toLowerCase().trim();
    
    // Direct match
    if (_labelMapping.containsKey(normalized)) {
      return _labelMapping[normalized];
    }
    
    // Partial match (contains)
    for (final entry in _labelMapping.entries) {
      if (normalized.contains(entry.key) || entry.key.contains(normalized)) {
        return entry.value;
      }
    }
    
    return null;
  }
  
  /// Get classroom objects by category
  static List<ClassroomObject> getObjectsByCategory(String category) {
    return classroomObjects
        .where((obj) => obj.category == category)
        .toList();
  }
  
  /// Get all object names for a category
  static List<String> getObjectNames(String category) {
    return getObjectsByCategory(category)
        .map((obj) => obj.name)
        .toList();
  }
  
  /// Find object by name
  static ClassroomObject? findObject(String name) {
    try {
      return classroomObjects.firstWhere(
        (obj) => obj.name.toLowerCase() == name.toLowerCase(),
      );
    } catch (e) {
      return null;
    }
  }
  
  void dispose() {
    _imageLabeler?.close();
    _imageLabeler = null;
  }
}
