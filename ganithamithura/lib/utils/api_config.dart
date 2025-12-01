/// API Configuration - Automatically detects emulator vs physical device
/// and uses the appropriate backend URL

import 'dart:io';

class ApiConfig {
  // Your Mac's local network IP
  static const String _localNetworkIp = '192.168.8.145';
  
  // Emulator uses special IP to reach host
  static const String _emulatorIp = '10.0.2.2';
  
  /// Get the base URL for measurement service (port 8001)
  static String get measurementServiceUrl {
    return 'http://${_getBaseIp()}:8001/api/v1/measurements';
  }
  
  /// Get the base URL for RAG service (port 8000)
  static String get ragServiceUrl {
    return 'http://${_getBaseIp()}:8000/api/v1/contextual';
  }
  
  /// Get health check URL for measurement service
  static String get measurementHealthUrl {
    return 'http://${_getBaseIp()}:8001/health';
  }
  
  /// Get health check URL for RAG service
  static String get ragHealthUrl {
    return 'http://${_getBaseIp()}:8000/health';
  }
  
  /// Determine if running on emulator
  static bool get isEmulator {
    // Check common emulator indicators
    if (Platform.isAndroid) {
      // Android emulators typically have these characteristics
      return Platform.environment.containsKey('ANDROID_EMULATOR') ||
             _isAndroidEmulator();
    }
    return false;
  }
  
  /// Get the appropriate base IP based on device type
  static String _getBaseIp() {
    if (Platform.isAndroid) {
      // For Android with USB forwarding (adb reverse), use localhost
      // This works for both emulator (via 10.0.2.2) and physical device (via adb reverse)
      // We'll use localhost since it's more universal with adb reverse
      print('📱 Android device - using localhost (via USB forwarding)');
      return 'localhost';
    } else {
      print('📱 Non-Android device - using localhost');
      return 'localhost';
    }
  }
  
  /// Check Android-specific emulator indicators
  static bool _isAndroidEmulator() {
    // This will be refined based on actual device characteristics
    // For now, we can check if we can detect emulator patterns
    try {
      // Common emulator indicators
      final brand = Platform.environment['BRAND'] ?? '';
      final device = Platform.environment['DEVICE'] ?? '';
      final model = Platform.environment['MODEL'] ?? '';
      
      return brand.toLowerCase().contains('generic') ||
             device.toLowerCase().contains('emulator') ||
             model.toLowerCase().contains('sdk') ||
             model.toLowerCase().contains('emulator');
    } catch (e) {
      // If we can't determine, default to physical device (use local network IP)
      return false;
    }
  }
  
  /// Print current configuration for debugging
  static void printConfig() {
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    print('📡 API Configuration:');
    print('   Device Type: ${isEmulator ? "Emulator" : "Physical Device"}');
    print('   Base IP: ${_getBaseIp()}');
    print('   Measurement Service: $measurementServiceUrl');
    print('   RAG Service: $ragServiceUrl');
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  }
}
