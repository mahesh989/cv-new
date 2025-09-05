// Basic Flutter widget test for CV Agent Mobile App.

import 'package:flutter_test/flutter_test.dart';

import 'package:cv_agent_mobile/main.dart';

void main() {
  testWidgets('CV Agent app launches', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const CVAgentApp());

    // Wait for the loading screen to complete
    await tester.pump(const Duration(seconds: 2));

    // Verify that the app shows the auth screen or loading screen
    expect(find.text('CV Agent'), findsOneWidget);
  });
}
