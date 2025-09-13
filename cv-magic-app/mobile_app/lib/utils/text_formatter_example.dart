import 'package:flutter/material.dart';
import 'text_formatter.dart';

/// Example usage of the TextFormatter utility
/// This file demonstrates how to use the formatter in different scenarios
class TextFormatterExample extends StatelessWidget {
  const TextFormatterExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Text Formatter Examples')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Example 1: Basic formatted text
            const Text('Example 1: Basic Formatted Text',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const FormattedTextWidget(
              text: '''## Main Header
### Sub Header
This is **bold text** and regular text.
- Bullet point 1
- Bullet point 2
1. Numbered item 1
2. Numbered item 2''',
            ),

            const SizedBox(height: 24),

            // Example 2: Analyze match formatting
            const Text('Example 2: Analyze Match Formatting',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const AnalyzeMatchFormattedText(
              text: '''🟢 STRONG PURSUE
## Candidate Assessment
### Technical Skills Match: 85%
**Strong technical background** in required technologies.
- React Native: 4+ years
- Flutter: 2+ years
- Backend APIs: 3+ years''',
            ),

            const SizedBox(height: 24),

            // Example 3: Skills analysis formatting
            const Text('Example 3: Skills Analysis Formatting',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const SkillsAnalysisFormattedText(
              text: '''## Technical Skills Analysis
### Frontend Technologies
**React Native** - Advanced level
**Flutter** - Intermediate level
- JavaScript/TypeScript
- Dart programming
- UI/UX design principles''',
              baseColor: Colors.blue,
            ),

            const SizedBox(height: 24),

            // Example 4: Custom formatting
            const Text('Example 4: Custom Formatting',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const FormattedTextWidget(
              text: '''## Custom Styling
This text has **custom formatting** with different colors and sizes.
- Custom bullet points
- Different font sizes
- Custom colors''',
              baseColor: Colors.green,
              fontSize: 14,
              textColor: Colors.purple,
            ),
          ],
        ),
      ),
    );
  }
}

/// Usage examples for different scenarios:

/// 1. For basic text formatting:
/// FormattedTextWidget(text: "Your markdown text here")

/// 2. For analyze match results:
/// AnalyzeMatchFormattedText(text: analyzeMatchResult)

/// 3. For skills analysis:
/// SkillsAnalysisFormattedText(text: analysisText, baseColor: Colors.blue)

/// 4. For custom formatting:
/// FormattedTextWidget(
///   text: "Your text",
///   baseColor: Colors.red,
///   fontSize: 16,
///   textColor: Colors.white,
///   isAnalyzeMatch: false,
/// )

/// 5. For programmatic formatting (without widget):
/// TextFormatter.formatText(
///   text: "Your text",
///   baseColor: Colors.blue,
///   baseFontSize: 14,
///   isAnalyzeMatch: true,
/// )
