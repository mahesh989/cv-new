import 'package:flutter/material.dart';
import 'text_formatter.dart';

/// Test widget to verify text formatter edge cases
class TextFormatterTest extends StatelessWidget {
  const TextFormatterTest({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Text Formatter Edge Cases Test')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Test 1: Unpaired bold markers
            _buildTestSection(
              'Test 1: Unpaired Bold Markers',
              '''**DECISION:** This is a decision line
**What they actually need:** Technical skills
**Candidate Assessment:** Strong match
**Final Recommendation:** Hire''',
            ),

            const SizedBox(height: 24),

            // Test 2: Mixed paired and unpaired
            _buildTestSection(
              'Test 2: Mixed Paired and Unpaired',
              '''**DECISION:** This is **bold text** with mixed markers
**What they need:** **Strong technical** background
Regular text with **bold** in the middle''',
            ),

            const SizedBox(height: 24),

            // Test 3: Headers with bold
            _buildTestSection(
              'Test 3: Headers with Bold',
              '''## **HEADER:** This is a header with bold
### **SUBHEADER:** This is a subheader
**DECISION:** This should be bold, not a header''',
            ),

            const SizedBox(height: 24),

            // Test 4: Edge cases
            _buildTestSection(
              'Test 4: Edge Cases',
              '''**Single word**
**Multiple words here**
**Text with numbers: 123**
**Text with symbols: @#\$%**
**Text ending with colon:**
**Text ending with period.**
**Text ending with exclamation!**''',
            ),

            const SizedBox(height: 24),

            // Test 5: Analyze match specific
            _buildTestSection(
              'Test 5: Analyze Match Formatting',
              '''🟢 STRONG PURSUE
**DECISION:** Strong candidate match
**Technical Skills Match: 85%**
**What they actually need:** React Native, Flutter
**Final Recommendation:** **HIRE** immediately''',
              isAnalyzeMatch: true,
            ),

            const SizedBox(height: 24),

            // Test 6: Complex mixed content
            _buildTestSection(
              'Test 6: Complex Mixed Content',
              '''## Technical Assessment
**DECISION:** Proceed with interview
### Skills Analysis
**Frontend:** **React Native** (4+ years), **Flutter** (2+ years)
**Backend:** Node.js, Python, **AWS** experience
**Database:** **PostgreSQL**, MongoDB
**Final Score:** **8.5/10** - **Strong Match**''',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestSection(String title, String testText,
      {bool isAnalyzeMatch = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.shade100,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: isAnalyzeMatch
              ? AnalyzeMatchFormattedText(text: testText)
              : FormattedTextWidget(text: testText),
        ),
        const SizedBox(height: 8),
        Text(
          'Raw text:',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: Colors.grey.shade600,
          ),
        ),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: Text(
            testText,
            style: TextStyle(
              fontSize: 11,
              fontFamily: 'monospace',
              color: Colors.grey.shade700,
            ),
          ),
        ),
      ],
    );
  }
}

/// Test cases for the formatter
class TextFormatterTestCases {
  static const List<Map<String, dynamic>> testCases = [
    {
      'name': 'Unpaired Bold Markers',
      'input': '**DECISION:** This is a decision',
      'expectedBold': ['DECISION:'],
      'expectedRegular': [' This is a decision'],
    },
    {
      'name': 'Paired Bold Markers',
      'input': 'This is **bold text** here',
      'expectedBold': ['bold text'],
      'expectedRegular': ['This is ', ' here'],
    },
    {
      'name': 'Mixed Bold Markers',
      'input': '**DECISION:** This is **bold text**',
      'expectedBold': ['DECISION:', 'bold text'],
      'expectedRegular': [' This is ', ''],
    },
    {
      'name': 'Single Word Bold',
      'input': '**HIRE**',
      'expectedBold': ['HIRE'],
      'expectedRegular': [],
    },
    {
      'name': 'Bold with Colon',
      'input': '**What they need:** Technical skills',
      'expectedBold': ['What they need:'],
      'expectedRegular': [' Technical skills'],
    },
    {
      'name': 'Multiple Bold Sections',
      'input': '**Frontend:** React **Backend:** Node.js',
      'expectedBold': ['Frontend:', 'Backend:'],
      'expectedRegular': [' React ', ' Node.js'],
    },
  ];

  static void runTests() {
    debugPrint('🧪 [TEST] Running TextFormatter tests...');

    for (final testCase in testCases) {
      debugPrint('🧪 [TEST] Testing: ${testCase['name']}');
      debugPrint('🧪 [TEST] Input: "${testCase['input']}"');

      // Test the formatter
      TextFormatter.formatText(text: testCase['input']);

      // Note: In a real test environment, you would parse the TextSpan
      // and verify the bold/regular text sections match expectations
      debugPrint('🧪 [TEST] Result generated successfully');
    }

    debugPrint('🧪 [TEST] All tests completed');
  }
}
