import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cv_agent_mobile/core/config/environment_config.dart';
import 'package:cv_agent_mobile/core/config/app_config.dart';

/// Test widget to verify configuration works in Flutter context
class ConfigTestWidget extends StatelessWidget {
  const ConfigTestWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          children: [
            Text('Base URL: ${EnvironmentConfig.baseUrl}'),
            Text('API URL: ${EnvironmentConfig.apiBaseUrl}'),
            Text('App Name: ${AppConfig.appName}'),
            Text('Is Development: ${EnvironmentConfig.isDevelopment}'),
            Text('Log Level: ${EnvironmentConfig.logLevel}'),
          ],
        ),
      ),
    );
  }
}

void main() {
  group('Configuration Widget Tests', () {
    testWidgets('ConfigTestWidget should display configuration values',
        (WidgetTester tester) async {
      // Build the test widget
      await tester.pumpWidget(const ConfigTestWidget());

      // Verify that configuration values are displayed
      expect(find.textContaining('Base URL:'), findsOneWidget);
      expect(find.textContaining('API URL:'), findsOneWidget);
      expect(find.textContaining('App Name: CV Magic'), findsOneWidget);
      expect(find.textContaining('Is Development:'), findsOneWidget);
      expect(find.textContaining('Log Level:'), findsOneWidget);

      // Verify that URLs contain expected values
      final baseUrlText = find.textContaining('Base URL:');
      final apiUrlText = find.textContaining('API URL:');

      expect(baseUrlText, findsOneWidget);
      expect(apiUrlText, findsOneWidget);
    });

    testWidgets('Configuration should be accessible in widget context',
        (WidgetTester tester) async {
      // Test that we can access configuration in a widget
      Widget testWidget = Builder(
        builder: (context) {
          final baseUrl = EnvironmentConfig.baseUrl;
          final apiUrl = EnvironmentConfig.apiBaseUrl;

          return Text('$baseUrl | $apiUrl');
        },
      );

      await tester.pumpWidget(MaterialApp(home: testWidget));

      // Should find the combined URL text
      expect(find.textContaining('localhost'), findsOneWidget);
      expect(find.textContaining('/api'), findsOneWidget);
    });

    testWidgets('Configuration should work with different build modes',
        (WidgetTester tester) async {
      // Test that configuration adapts to different modes
      await tester.pumpWidget(const ConfigTestWidget());

      // In test environment, should show development values
      expect(find.textContaining('localhost'), findsOneWidget);
      expect(find.textContaining('Is Development: true'), findsOneWidget);
    });
  });
}
