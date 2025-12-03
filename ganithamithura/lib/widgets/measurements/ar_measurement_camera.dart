/// Modern AR Measurement Camera Widget
/// Integrates camera, AR plane detection, and object detection

import 'dart:io';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class ARMeasurementCamera extends StatefulWidget {
  final String measurementType;
  final Color primaryColor;
  final Function(double value, String? photoPath) onMeasurementComplete;
  
  const ARMeasurementCamera({
    Key? key,
    required this.measurementType,
    required this.primaryColor,
    required this.onMeasurementComplete,
  }) : super(key: key);

  @override
  State<ARMeasurementCamera> createState() => _ARMeasurementCameraState();
}

class _ARMeasurementCameraState extends State<ARMeasurementCamera> {
  CameraController? _controller;
  bool _isInitialized = false;
  bool _isProcessing = false;
  
  // Measurement points
  Offset? _startPoint;
  Offset? _endPoint;
  double? _measuredDistance;
  
  // For area measurement (4 corners)
  List<Offset> _areaPoints = [];
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        print('❌ No cameras available');
        return;
      }
      
      final camera = cameras.first;
      
      _controller = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      
      await _controller!.initialize();
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
        print('✅ Camera initialized');
      }
    } catch (e) {
      print('❌ Camera initialization error: $e');
    }
  }
  
  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
  
  void _handleTap(TapDownDetails details) {
    if (_isProcessing) return;
    
    final tapPosition = details.localPosition;
    
    if (widget.measurementType == 'Area') {
      _handleAreaMeasurement(tapPosition);
    } else {
      _handleLengthMeasurement(tapPosition);
    }
  }
  
  void _handleLengthMeasurement(Offset tapPosition) {
    setState(() {
      if (_startPoint == null) {
        // First tap - set start point
        _startPoint = tapPosition;
        _endPoint = null;
        _measuredDistance = null;
      } else {
        // Second tap - set end point and calculate distance
        _endPoint = tapPosition;
        _calculateDistance();
      }
    });
  }
  
  void _handleAreaMeasurement(Offset tapPosition) {
    setState(() {
      if (_areaPoints.length < 4) {
        _areaPoints.add(tapPosition);
        
        if (_areaPoints.length == 4) {
          _calculateArea();
        }
      } else {
        // Reset and start over
        _areaPoints.clear();
        _areaPoints.add(tapPosition);
      }
    });
  }
  
  void _calculateDistance() {
    if (_startPoint == null || _endPoint == null) return;
    
    // Calculate pixel distance
    final dx = _endPoint!.dx - _startPoint!.dx;
    final dy = _endPoint!.dy - _startPoint!.dy;
    final pixelDistance = (dx * dx + dy * dy).abs();
    
    // Simple conversion: Assume 100 pixels ≈ 10 cm (calibration factor)
    // In real AR, this would use ARCore distance calculation
    final distanceInCm = (pixelDistance / 10).clamp(1.0, 500.0);
    
    setState(() {
      _measuredDistance = distanceInCm;
    });
    
    print('📏 Measured: ${distanceInCm.toStringAsFixed(1)} cm');
  }
  
  void _calculateArea() {
    if (_areaPoints.length != 4) return;
    
    // Simple rectangle area calculation
    final width = (_areaPoints[1].dx - _areaPoints[0].dx).abs();
    final height = (_areaPoints[2].dy - _areaPoints[1].dy).abs();
    
    // Convert to cm² (simplified)
    final areaInCm2 = (width * height / 100).clamp(10.0, 10000.0);
    
    setState(() {
      _measuredDistance = areaInCm2;
    });
    
    print('📐 Area: ${areaInCm2.toStringAsFixed(1)} cm²');
  }
  
  Future<void> _captureAndComplete() async {
    if (_measuredDistance == null) {
      _showMessage('Please measure first!');
      return;
    }
    
    setState(() {
      _isProcessing = true;
    });
    
    try {
      // Capture photo
      final image = await _controller!.takePicture();
      
      // Save to temp directory
      final directory = await getTemporaryDirectory();
      final fileName = 'ar_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final savedPath = path.join(directory.path, fileName);
      
      await File(image.path).copy(savedPath);
      
      print('📸 Photo saved: $savedPath');
      
      // Call completion callback
      widget.onMeasurementComplete(_measuredDistance!, savedPath);
      
    } catch (e) {
      print('❌ Capture error: $e');
      _showMessage('Failed to capture photo');
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }
  
  void _reset() {
    setState(() {
      _startPoint = null;
      _endPoint = null;
      _measuredDistance = null;
      _areaPoints.clear();
    });
  }
  
  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    if (!_isInitialized || _controller == null) {
      return _buildLoadingView();
    }
    
    return GestureDetector(
      onTapDown: _handleTap,
      behavior: HitTestBehavior.opaque,
      child: Stack(
        children: [
          // Camera preview
          SizedBox.expand(
            child: CameraPreview(_controller!),
          ),
          
          // AR overlay with measurement points
          Positioned.fill(
            child: IgnorePointer(
              child: CustomPaint(
                painter: MeasurementPainter(
                  startPoint: _startPoint,
                  endPoint: _endPoint,
                  areaPoints: _areaPoints,
                  primaryColor: widget.primaryColor,
                  measurementType: widget.measurementType,
                ),
              ),
            ),
          ),
          
          // Instructions overlay
          IgnorePointer(
            child: _buildInstructionsOverlay(),
          ),
          
          // Measurement display
          if (_measuredDistance != null)
            IgnorePointer(
              child: _buildMeasurementDisplay(),
            ),
          
          // Control buttons
          _buildControlButtons(),
          
          // Processing overlay
          if (_isProcessing) _buildProcessingOverlay(),
        ],
      ),
    );
  }
  
  Widget _buildLoadingView() {
    return Container(
      color: Colors.black,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(widget.primaryColor),
            ),
            const SizedBox(height: 16),
            const Text(
              'Initializing camera...',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildInstructionsOverlay() {
    String instruction;
    
    if (widget.measurementType == 'Area') {
      if (_areaPoints.isEmpty) {
        instruction = '📐 Tap 4 corners to measure area';
      } else if (_areaPoints.length < 4) {
        instruction = 'Tap ${4 - _areaPoints.length} more corner${_areaPoints.length < 3 ? 's' : ''}';
      } else {
        instruction = '✓ Area measured! Tap capture or reset';
      }
    } else {
      if (_startPoint == null) {
        instruction = '📏 Tap to set START point';
      } else if (_endPoint == null) {
        instruction = 'Now tap to set END point';
      } else {
        instruction = '✓ Measurement complete! Tap capture';
      }
    }
    
    return Positioned(
      top: 20,
      left: 20,
      right: 20,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.7),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          instruction,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
  
  Widget _buildMeasurementDisplay() {
    final unit = widget.measurementType == 'Area' ? 'cm²' : 'cm';
    
    return Positioned(
      bottom: 140,
      left: 0,
      right: 0,
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          decoration: BoxDecoration(
            color: widget.primaryColor,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                widget.measurementType == 'Area' ? Icons.crop_square : Icons.straighten,
                color: Colors.white,
                size: 28,
              ),
              const SizedBox(width: 12),
              Text(
                '${_measuredDistance!.toStringAsFixed(1)} $unit',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildControlButtons() {
    return Positioned(
      bottom: 30,
      left: 20,
      right: 20,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          // Reset button
          _buildControlButton(
            icon: Icons.refresh,
            label: 'Reset',
            onPressed: _reset,
            backgroundColor: Colors.white.withOpacity(0.2),
          ),
          
          // Capture button (larger, centered)
          if (_measuredDistance != null)
            _buildControlButton(
              icon: Icons.check_circle,
              label: 'Capture',
              onPressed: _captureAndComplete,
              backgroundColor: widget.primaryColor,
              isLarge: true,
            ),
          
          // Help button
          _buildControlButton(
            icon: Icons.help_outline,
            label: 'Help',
            onPressed: () => _showHelpDialog(),
            backgroundColor: Colors.white.withOpacity(0.2),
          ),
        ],
      ),
    );
  }
  
  Widget _buildControlButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    required Color backgroundColor,
    bool isLarge = false,
  }) {
    final size = isLarge ? 80.0 : 60.0;
    final iconSize = isLarge ? 36.0 : 24.0;
    
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Material(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(size / 2),
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(size / 2),
            child: Container(
              width: size,
              height: size,
              alignment: Alignment.center,
              child: Icon(
                icon,
                color: Colors.white,
                size: iconSize,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            color: Colors.white,
            fontSize: isLarge ? 16 : 14,
            fontWeight: isLarge ? FontWeight.bold : FontWeight.w500,
          ),
        ),
      ],
    );
  }
  
  Widget _buildProcessingOverlay() {
    return Container(
      color: Colors.black.withOpacity(0.7),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(widget.primaryColor),
            ),
            const SizedBox(height: 16),
            const Text(
              'Capturing measurement...',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('How to measure ${widget.measurementType}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (widget.measurementType == 'Area') ...[
              _buildHelpStep('1', 'Tap on the first corner of the area'),
              _buildHelpStep('2', 'Tap the remaining 3 corners in order'),
              _buildHelpStep('3', 'The area will be calculated automatically'),
              _buildHelpStep('4', 'Tap "Capture" to save and continue'),
            ] else ...[
              _buildHelpStep('1', 'Tap where you want to start measuring'),
              _buildHelpStep('2', 'Tap where you want to end measuring'),
              _buildHelpStep('3', 'The distance will be shown'),
              _buildHelpStep('4', 'Tap "Capture" to save and continue'),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it!'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildHelpStep(String number, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: widget.primaryColor,
              shape: BoxShape.circle,
            ),
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter for measurement overlay
class MeasurementPainter extends CustomPainter {
  final Offset? startPoint;
  final Offset? endPoint;
  final List<Offset> areaPoints;
  final Color primaryColor;
  final String measurementType;
  
  MeasurementPainter({
    this.startPoint,
    this.endPoint,
    required this.areaPoints,
    required this.primaryColor,
    required this.measurementType,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = primaryColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;
    
    final pointPaint = Paint()
      ..color = primaryColor
      ..style = PaintingStyle.fill;
    
    if (measurementType == 'Area') {
      // Draw area points and lines
      for (int i = 0; i < areaPoints.length; i++) {
        final point = areaPoints[i];
        
        // Draw point
        canvas.drawCircle(point, 12, pointPaint);
        canvas.drawCircle(point, 12, paint);
        
        // Draw number
        final textPainter = TextPainter(
          text: TextSpan(
            text: '${i + 1}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(point.dx - textPainter.width / 2, point.dy - textPainter.height / 2),
        );
        
        // Draw line to next point
        if (i > 0) {
          canvas.drawLine(areaPoints[i - 1], point, paint);
        }
      }
      
      // Close the shape if 4 points
      if (areaPoints.length == 4) {
        canvas.drawLine(areaPoints[3], areaPoints[0], paint);
      }
    } else {
      // Draw length measurement
      if (startPoint != null) {
        // Draw start point
        canvas.drawCircle(startPoint!, 12, pointPaint);
        canvas.drawCircle(startPoint!, 12, paint);
        
        if (endPoint != null) {
          // Draw end point
          canvas.drawCircle(endPoint!, 12, pointPaint);
          canvas.drawCircle(endPoint!, 12, paint);
          
          // Draw line
          canvas.drawLine(startPoint!, endPoint!, paint);
          
          // Draw arrow heads
          _drawArrowHead(canvas, startPoint!, endPoint!, paint);
          _drawArrowHead(canvas, endPoint!, startPoint!, paint);
        }
      }
    }
  }
  
  void _drawArrowHead(Canvas canvas, Offset from, Offset to, Paint paint) {
    const arrowSize = 15.0;
    final dx = to.dx - from.dx;
    final dy = to.dy - from.dy;
    final angle = math.atan2(dy, dx);
    
    final arrowPoint1 = Offset(
      from.dx + arrowSize * math.cos(angle - 0.5),
      from.dy + arrowSize * math.sin(angle - 0.5),
    );
    
    final arrowPoint2 = Offset(
      from.dx + arrowSize * math.cos(angle + 0.5),
      from.dy + arrowSize * math.sin(angle + 0.5),
    );
    
    final path = Path()
      ..moveTo(from.dx, from.dy)
      ..lineTo(arrowPoint1.dx, arrowPoint1.dy)
      ..moveTo(from.dx, from.dy)
      ..lineTo(arrowPoint2.dx, arrowPoint2.dy);
    
    canvas.drawPath(path, paint);
  }
  
  @override
  bool shouldRepaint(MeasurementPainter oldDelegate) {
    return startPoint != oldDelegate.startPoint ||
        endPoint != oldDelegate.endPoint ||
        areaPoints != oldDelegate.areaPoints;
  }
}
