import 'package:flutter/foundation.dart';

class EnvironmentConfig {
  // Environment-based configuration
  static const String _developmentBaseUrl = 'http://localhost:8000';
  static const String _productionBaseUrl = 'https://your-production-url.com';

  // Get base URL based on environment
  static String get baseUrl {
    if (kDebugMode) {
      return _developmentBaseUrl;
    } else {
      return _productionBaseUrl;
    }
  }

  // API endpoints
  static String get apiBaseUrl => '$baseUrl/api';

  // Other environment-specific settings
  static bool get isDevelopment => kDebugMode;
  static bool get isProduction => !kDebugMode;

  // Logging level
  static String get logLevel => kDebugMode ? 'DEBUG' : 'INFO';

  // Timeout settings
  static Duration get apiTimeout => kDebugMode
      ? Duration(seconds: 30) // Longer timeout for development
      : Duration(seconds: 10); // Shorter timeout for production
}
