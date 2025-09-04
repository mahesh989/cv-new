import 'package:flutter/material.dart';
import '../base/analysis_step_widget.dart';
import 'ai_analysis_controller.dart';

/// Widget for displaying Step 2: AI Analysis results
class AIAnalysisWidget extends AnalysisStepWidget {
  const AIAnalysisWidget({
    super.key,
    required AIAnalysisController controller,
    super.showHeader = true,
    super.showProgress = true,
    super.showErrors = true,
  }) : super(controller: controller);

  @override
  Widget buildStepContent(BuildContext context) {
    final aiController = controller as AIAnalysisController;

    return Container(
      decoration: BoxDecoration(
        color: Colors.purple[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI Analysis Result Section
          if (aiController.analysisResult != null) ...[
            _buildAnalysisResultSection(
              '🤖 AI Match Analysis',
              aiController.analysisResult!,
              Colors.purple,
            ),
          ],
        ],
      ),
    );
  }

  /// Build the AI analysis result section
  Widget _buildAnalysisResultSection(
      String title, String analysisResult, Color color) {
    return buildResultContainer(
      title: title,
      color: color,
      icon: Icons.psychology,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Analysis content
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: color.withValues(alpha: 0.3)),
            ),
            child: _buildFormattedText(analysisResult),
          ),
          const SizedBox(height: 12),

          // Analysis metadata
          Row(
            children: [
              Icon(Icons.info_outline, color: color, size: 16),
              const SizedBox(width: 8),
              Text(
                'Analysis completed',
                style: TextStyle(
                  fontSize: 12,
                  color: color,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const Spacer(),
              Text(
                '${analysisResult.length} characters',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
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
    final regex = RegExp(r'\*\*(.*?)\*\*');
    int lastIndex = 0;

    for (final match in regex.allMatches(text)) {
      // Add text before the match
      if (match.start > lastIndex) {
        spans.add(TextSpan(
          text: text.substring(lastIndex, match.start),
          style: const TextStyle(
            fontSize: 14,
            height: 1.6,
            fontFamily: 'monospace',
          ),
        ));
      }

      // Add the bold text (without the ** markers)
      spans.add(TextSpan(
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
    if (lastIndex < text.length) {
      spans.add(TextSpan(
        text: text.substring(lastIndex),
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
