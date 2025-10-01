import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/foundation.dart';
import 'package:cv_agent_mobile/core/config/environment_config.dart';
import 'package:cv_agent_mobile/core/config/app_config.dart';

void main() {
  group('Environment Configuration Tests', () {
    testWidgets('EnvironmentConfig should return correct URLs',
        (WidgetTester tester) async {
      // Test that EnvironmentConfig returns the expected URLs
      expect(EnvironmentConfig.baseUrl, isA<String>());
      expect(EnvironmentConfig.apiBaseUrl, isA<String>());

      // In test environment, it should behave like development mode
      expect(EnvironmentConfig.baseUrl, contains('localhost'));
      expect(EnvironmentConfig.apiBaseUrl, contains('/api'));
    });

    testWidgets('AppConfig should return correct URLs',
        (WidgetTester tester) async {
      // Test that AppConfig returns the expected URLs
      expect(AppConfig.baseUrl, isA<String>());
      expect(AppConfig.apiBaseUrl, isA<String>());

      // In test environment, it should behave like development mode
      expect(AppConfig.baseUrl, contains('localhost'));
      expect(AppConfig.apiBaseUrl, contains('/api'));
    });

    test('EnvironmentConfig properties should be accessible', () {
      // Test all getter properties
      expect(EnvironmentConfig.isDevelopment, isA<bool>());
      expect(EnvironmentConfig.isProduction, isA<bool>());
      expect(EnvironmentConfig.logLevel, isA<String>());
      expect(EnvironmentConfig.apiTimeout, isA<Duration>());

      // Verify logical consistency
      expect(EnvironmentConfig.isDevelopment,
          equals(!EnvironmentConfig.isProduction));
    });

    test('URLs should be properly formatted', () {
      final baseUrl = EnvironmentConfig.baseUrl;
      final apiUrl = EnvironmentConfig.apiBaseUrl;

      // Base URL should not end with slash
      expect(baseUrl, isNot(endsWith('/')));

      // API URL should end with /api
      expect(apiUrl, endsWith('/api'));

      // API URL should start with base URL
      expect(apiUrl, startsWith(baseUrl));
    });

    test('AppConfig constants should be valid', () {
      // Test app constants
      expect(AppConfig.appName, equals('CV Magic'));
      expect(AppConfig.appVersion, equals('1.0.0'));
      expect(AppConfig.youtubeVideoId, isA<String>());

      // Test animation durations
      expect(AppConfig.defaultAnimationDuration, isA<Duration>());
      expect(AppConfig.fastAnimationDuration, isA<Duration>());
      expect(AppConfig.slowAnimationDuration, isA<Duration>());

      // Test spacing constants
      expect(AppConfig.defaultPadding, isA<double>());
      expect(AppConfig.smallPadding, isA<double>());
      expect(AppConfig.largePadding, isA<double>());

      // Test border radius
      expect(AppConfig.defaultBorderRadius, isA<double>());
      expect(AppConfig.smallBorderRadius, isA<double>());
      expect(AppConfig.largeBorderRadius, isA<double>());

      // Test feature flags
      expect(AppConfig.enableVideoPlayer, isA<bool>());
      expect(AppConfig.enableAnimations, isA<bool>());
      expect(AppConfig.enableHapticFeedback, isA<bool>());
    });

    test('URLs should be consistent between configs', () {
      // Both configs should return the same base URL
      expect(EnvironmentConfig.baseUrl, equals(AppConfig.baseUrl));

      // Both configs should return the same API URL
      expect(EnvironmentConfig.apiBaseUrl, equals(AppConfig.apiBaseUrl));
    });

    test('Development mode should use localhost', () {
      // In test environment (which behaves like debug mode)
      expect(EnvironmentConfig.baseUrl, contains('localhost'));
      expect(EnvironmentConfig.baseUrl, contains('8000'));
      expect(EnvironmentConfig.isDevelopment, isTrue);
    });
  });

  group('Configuration Integration Tests', () {
    test('All services should be able to access configuration', () {
      // Test that we can import and use the configuration
      final baseUrl = EnvironmentConfig.baseUrl;
      final apiUrl = EnvironmentConfig.apiBaseUrl;

      // URLs should be valid
      expect(baseUrl, isNotEmpty);
      expect(apiUrl, isNotEmpty);

      // Should be able to construct full API endpoints
      final testEndpoint = '$apiUrl/test';
      expect(testEndpoint, contains('/api/test'));
    });

    test('Configuration should handle different environments', () {
      // Test that configuration is environment-aware
      if (kDebugMode) {
        expect(EnvironmentConfig.isDevelopment, isTrue);
        expect(EnvironmentConfig.baseUrl, contains('localhost'));
      } else {
        expect(EnvironmentConfig.isProduction, isTrue);
        // In production, it should not contain localhost
        expect(EnvironmentConfig.baseUrl, isNot(contains('localhost')));
      }
    });
  });

  group('Error Handling Tests', () {
    test('Configuration should not throw exceptions', () {
      // All configuration access should be safe
      expect(() => EnvironmentConfig.baseUrl, returnsNormally);
      expect(() => EnvironmentConfig.apiBaseUrl, returnsNormally);
      expect(() => AppConfig.baseUrl, returnsNormally);
      expect(() => AppConfig.apiBaseUrl, returnsNormally);
    });

    test('URLs should be valid HTTP/HTTPS URLs', () {
      final baseUrl = EnvironmentConfig.baseUrl;
      final apiUrl = EnvironmentConfig.apiBaseUrl;

      // Should start with http:// or https://
      expect(baseUrl, anyOf(startsWith('http://'), startsWith('https://')));
      expect(apiUrl, anyOf(startsWith('http://'), startsWith('https://')));
    });
  });
}
