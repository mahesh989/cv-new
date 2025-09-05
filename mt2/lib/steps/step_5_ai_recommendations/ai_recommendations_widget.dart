import 'package:flutter/material.dart';
import '../base/analysis_step_widget.dart';
import 'ai_recommendations_controller.dart';

/// Widget for displaying Step 5: AI Recommendations results
class AIRecommendationsWidget extends AnalysisStepWidget {
  const AIRecommendationsWidget({
    super.key,
    required AIRecommendationsController controller,
    super.showHeader = true,
    super.showProgress = true,
    super.showErrors = true,
  }) : super(controller: controller);

  @override
  Widget buildStepContent(BuildContext context) {
    final recommendationsController = controller as AIRecommendationsController;

    return Container(
      decoration: BoxDecoration(
        color: Colors.amber[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI Recommendations Section
          if (recommendationsController.recommendations != null) ...[
            _buildRecommendationsSection(recommendationsController),
          ],
        ],
      ),
    );
  }

  /// Build the AI recommendations section
  Widget _buildRecommendationsSection(AIRecommendationsController controller) {
    final recommendations = controller.recommendations ?? '';

    return buildResultContainer(
      title: '💡 AI Recommendations - CV Tailoring Strategy',
      color: Colors.amber,
      icon: Icons.lightbulb_outline,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Recommendations content
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber[200]!),
            ),
            child: _buildFormattedText(recommendations),
          ),
          const SizedBox(height: 12),

          // Metadata row
          Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.amber[700], size: 16),
              const SizedBox(width: 8),
              Text(
                'Claude AI CV Tailoring Recommendations',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.amber[700],
                  fontSize: 14,
                ),
              ),
              const Spacer(),
              Text(
                '${recommendations.length} characters',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build formatted text that handles markdown-style formatting
  Widget _buildFormattedText(String text) {
    final spans = <TextSpan>[];
    final lines = text.split('\n');

    for (final line in lines) {
      if (line.trim().isEmpty) {
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Handle headers (##)
      if (line.startsWith('##')) {
        final headerText = line.replaceFirst('##', '').trim();
        spans.add(TextSpan(
          text: '$headerText\n',
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.amber,
            fontFamily: 'monospace',
          ),
        ));
        continue;
      }

      // Handle bold text (**text**)
      if (line.contains('**')) {
        final regex = RegExp(r'\*\*(.*?)\*\*');
        int lastIndex = 0;
        final lineSpans = <TextSpan>[];

        for (final match in regex.allMatches(line)) {
          // Add text before the match
          if (match.start > lastIndex) {
            lineSpans.add(TextSpan(
              text: line.substring(lastIndex, match.start),
              style: const TextStyle(
                fontSize: 14,
                height: 1.6,
                fontFamily: 'monospace',
              ),
            ));
          }
          // Add the bold text (without the ** markers)
          lineSpans.add(TextSpan(
            text: match.group(1),
            style: const TextStyle(
              fontSize: 14,
              height: 1.6,
              fontFamily: 'monospace',
              fontWeight: FontWeight.bold,
            ),
          ));
          lastIndex = match.end;
        }
        // Add remaining text after the last match
        if (lastIndex < line.length) {
          lineSpans.add(TextSpan(
            text: line.substring(lastIndex),
            style: const TextStyle(
              fontSize: 14,
              height: 1.6,
              fontFamily: 'monospace',
            ),
          ));
        }
        spans.addAll(lineSpans);
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Regular text
      spans.add(TextSpan(
        text: '$line\n',
        style: const TextStyle(
          fontSize: 14,
          height: 1.6,
          fontFamily: 'monospace',
        ),
      ));
    }

    return SelectableText.rich(
      TextSpan(children: spans),
    );
  }
}
