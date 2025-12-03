/// Completely redesigned AR Measurement Screen with Object Detection
/// Clean architecture, modern UI, integrated detection flow

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/widgets/measurements/ar_measurement_camera.dart';
import 'package:ganithamithura/widgets/measurements/object_confirmation_dialog.dart';
import 'package:ganithamithura/services/object_detection_service.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NewARMeasurementScreen extends StatefulWidget {
  const NewARMeasurementScreen({Key? key}) : super(key: key);

  @override
  State<NewARMeasurementScreen> createState() => _NewARMeasurementScreenState();
}

class _NewARMeasurementScreenState extends State<NewARMeasurementScreen> {
  final ObjectDetectionService _detectionService = ObjectDetectionService();
  
  // Get measurement type from arguments
  String get _measurementType {
    final args = Get.arguments as Map<String, dynamic>?;
    return args?['type'] ?? 'Length';
  }
  
  Color get _primaryColor {
    switch (_measurementType) {
      case 'Length':
        return Colors.blue;
      case 'Area':
        return Colors.green;
      case 'Capacity':
        return Colors.orange;
      case 'Weight':
        return Colors.purple;
      default:
        return Colors.blue;
    }
  }
  
  bool _isProcessingDetection = false;
  bool _isSubmittingMeasurement = false;

  @override
  void dispose() {
    _detectionService.dispose();
    super.dispose();
  }

  /// Called when camera measurement is complete
  Future<void> _onMeasurementComplete(double value, String? photoPath) async {
    print('📏 Measurement complete: $value, photo: $photoPath');
    
    if (photoPath == null) {
      _showError('No photo captured');
      return;
    }
    
    // Step 1: Detect object in the photo
    await _detectAndConfirmObject(value, photoPath);
  }
  
  /// Detect object and show confirmation dialog
  Future<void> _detectAndConfirmObject(double measurementValue, String photoPath) async {
    setState(() {
      _isProcessingDetection = true;
    });
    
    try {
      // Run object detection
      final detectionResult = await _detectionService.detectObject(photoPath);
      
      if (!mounted) return;
      
      setState(() {
        _isProcessingDetection = false;
      });
      
      // Show confirmation dialog
      await showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => ObjectConfirmationDialog(
          suggestedObject: detectionResult?.suggestedObject ?? 'Other',
          confidence: detectionResult?.confidence ?? 0.0,
          category: _measurementType.toLowerCase(),
          onConfirm: (confirmedObject) async {
            Navigator.of(context).pop();
            // Submit measurement with confirmed object
            await _submitMeasurement(
              value: measurementValue,
              photoPath: photoPath,
              objectName: confirmedObject,
              confidence: detectionResult?.confidence ?? 0.0,
              wasManuallySelected: false,
            );
          },
          onCancel: () {
            Navigator.of(context).pop();
            print('❌ User cancelled object confirmation');
          },
        ),
      );
      
    } catch (e) {
      print('❌ Detection error: $e');
      
      if (!mounted) return;
      
      setState(() {
        _isProcessingDetection = false;
      });
      
      // Fallback: Show manual selection
      await _showManualObjectSelection(measurementValue, photoPath);
    }
  }
  
  /// Fallback: Manual object selection if detection fails
  Future<void> _showManualObjectSelection(double measurementValue, String photoPath) async {
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => ObjectConfirmationDialog(
        suggestedObject: 'Other',
        confidence: 0.0,
        category: _measurementType.toLowerCase(),
        onConfirm: (selectedObject) async {
          Navigator.of(context).pop();
          await _submitMeasurement(
            value: measurementValue,
            photoPath: photoPath,
            objectName: selectedObject,
            confidence: 0.0,
            wasManuallySelected: true,
          );
        },
        onCancel: () {
          Navigator.of(context).pop();
          print('❌ User cancelled manual selection');
        },
      ),
    );
  }
  
  /// Submit measurement to backend and navigate to questions
  Future<void> _submitMeasurement({
    required double value,
    required String photoPath,
    required String objectName,
    required double confidence,
    required bool wasManuallySelected,
  }) async {
    setState(() {
      _isSubmittingMeasurement = true;
    });
    
    try {
      print('📤 Submitting measurement...');
      print('   Type: $_measurementType');
      print('   Value: $value');
      print('   Object: $objectName');
      print('   Confidence: $confidence');
      print('   Manual: $wasManuallySelected');
      
      // Determine base URL (check network config)
      final baseUrl = 'http://localhost:8001'; // Will use adb reverse
      
      // Prepare request
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/measurements'),
      );
      
      // Add fields
      request.fields['measurement_type'] = _measurementType;
      request.fields['value'] = value.toString();
      request.fields['unit'] = _getUnit();
      request.fields['object_name'] = objectName;
      request.fields['detection_confidence'] = confidence.toString();
      request.fields['manually_corrected'] = wasManuallySelected.toString();
      request.fields['session_id'] = DateTime.now().millisecondsSinceEpoch.toString();
      request.fields['measurement_method'] = 'ar_camera';
      
      // Add photo file
      request.files.add(
        await http.MultipartFile.fromPath('photo', photoPath),
      );
      
      // Send request
      final response = await request.send();
      final responseData = await response.stream.bytesToString();
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(responseData);
        print('✅ Measurement submitted successfully');
        print('   Measurement ID: ${data['measurement_id']}');
        
        // Navigate to questions screen
        _navigateToQuestions(data);
      } else {
        print('❌ Server error: ${response.statusCode}');
        print('   Response: $responseData');
        _showError('Failed to save measurement (${response.statusCode})');
      }
      
    } catch (e) {
      print('❌ Submission error: $e');
      _showError('Failed to submit measurement: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isSubmittingMeasurement = false;
        });
      }
    }
  }
  
  String _getUnit() {
    switch (_measurementType) {
      case 'Length':
        return 'cm';
      case 'Area':
        return 'cm²';
      case 'Capacity':
        return 'ml';
      case 'Weight':
        return 'g';
      default:
        return 'cm';
    }
  }
  
  void _navigateToQuestions(Map<String, dynamic> measurementData) {
    // Navigate to RAG questions screen
    Get.toNamed(
      '/measurement-questions',
      arguments: {
        'measurement_id': measurementData['measurement_id'],
        'measurement_type': _measurementType,
        'value': measurementData['value'],
        'object_name': measurementData['object_name'],
        'unit': measurementData['unit'],
      },
    );
  }
  
  void _showError(String message) {
    if (!mounted) return;
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 4),
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'OK',
          textColor: Colors.white,
          onPressed: () {},
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            // Main AR Camera Widget
            ARMeasurementCamera(
              measurementType: _measurementType,
              primaryColor: _primaryColor,
              onMeasurementComplete: _onMeasurementComplete,
            ),
            
            // Top bar with back button and title
            _buildTopBar(),
            
            // Detection processing overlay
            if (_isProcessingDetection) _buildDetectionOverlay(),
            
            // Submission processing overlay
            if (_isSubmittingMeasurement) _buildSubmissionOverlay(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildTopBar() {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black.withOpacity(0.6),
              Colors.transparent,
            ],
          ),
        ),
        child: Row(
          children: [
            // Back button
            IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => Get.back(),
            ),
            
            // Title
            Expanded(
              child: Text(
                'Measure $_measurementType',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            
            // Measurement type icon
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: _primaryColor.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                _getMeasurementIcon(),
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 8),
          ],
        ),
      ),
    );
  }
  
  IconData _getMeasurementIcon() {
    switch (_measurementType) {
      case 'Length':
        return Icons.straighten;
      case 'Area':
        return Icons.crop_square;
      case 'Capacity':
        return Icons.water_drop;
      case 'Weight':
        return Icons.monitor_weight;
      default:
        return Icons.straighten;
    }
  }
  
  Widget _buildDetectionOverlay() {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  strokeWidth: 6,
                  valueColor: AlwaysStoppedAnimation<Color>(_primaryColor),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'Detecting object...',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Using AI to identify what you measured',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildSubmissionOverlay() {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  strokeWidth: 6,
                  valueColor: AlwaysStoppedAnimation<Color>(_primaryColor),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'Saving measurement...',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Generating personalized questions for you',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
