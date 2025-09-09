import 'package:flutter/material.dart';
import '../models/skills_analysis_model.dart';

/// Widget for displaying analyze match results with recruiter-style assessment
class AnalyzeMatchWidget extends StatefulWidget {
  final AnalyzeMatchResult? analyzeMatch;
  final bool isLoading;

  const AnalyzeMatchWidget({
    super.key,
    this.analyzeMatch,
    this.isLoading = false,
  });

  @override
  State<AnalyzeMatchWidget> createState() => _AnalyzeMatchWidgetState();
}

class _AnalyzeMatchWidgetState extends State<AnalyzeMatchWidget> {
  @override
  Widget build(BuildContext context) {
    debugPrint('🔍 [ANALYZE_MATCH_WIDGET] Building widget');
    debugPrint('   isLoading: ${widget.isLoading}');
    debugPrint('   analyzeMatch: ${widget.analyzeMatch != null}');
    if (widget.analyzeMatch != null) {
      debugPrint('   isEmpty: ${widget.analyzeMatch!.isEmpty}');
      debugPrint('   hasError: ${widget.analyzeMatch!.hasError}');
      debugPrint(
          '   rawAnalysis length: ${widget.analyzeMatch!.rawAnalysis.length}');
    }

    if (widget.isLoading) {
      debugPrint('🔍 [ANALYZE_MATCH_WIDGET] Showing loading state');
      return _buildLoadingState();
    }

    if (widget.analyzeMatch == null || widget.analyzeMatch!.isEmpty) {
      debugPrint('🔍 [ANALYZE_MATCH_WIDGET] Showing empty state');
      return _buildEmptyState();
    }

    if (widget.analyzeMatch!.hasError) {
      debugPrint('🔍 [ANALYZE_MATCH_WIDGET] Showing error state');
      return _buildErrorState();
    }

    debugPrint('🔍 [ANALYZE_MATCH_WIDGET] Showing content state');
    return _buildAnalyzeMatchContent();
  }

  Widget _buildLoadingState() {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [
              Colors.orange.shade50,
              Colors.orange.shade100,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade600,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.analytics,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Analyze Match',
                          style:
                              Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.orange.shade800,
                                  ),
                        ),
                        Text(
                          'Recruiter Assessment',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Colors.orange.shade600,
                                  ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        valueColor:
                            AlwaysStoppedAnimation<Color>(Colors.orange),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Generating recruiter-style hiring assessment...',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.orange.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.analytics, color: Colors.grey.shade400),
                const SizedBox(width: 8),
                Text(
                  'Analyze Match',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade600,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'No analyze match results available',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.error_outline, color: Colors.red.shade600),
                const SizedBox(width: 8),
                Text(
                  'Analyze Match Error',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              widget.analyzeMatch?.error ?? 'Unknown error occurred',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.red.shade600,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyzeMatchContent() {
    final analyzeMatch = widget.analyzeMatch!;

    return Card(
      margin: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Header (non-expandable)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Icon(
                  Icons.analytics,
                  color: _getDecisionColor(analyzeMatch.rawAnalysis),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Analyze Match',
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                              color:
                                  _getDecisionColor(analyzeMatch.rawAnalysis),
                            ),
                      ),
                      Text(
                        _getDecisionSummary(analyzeMatch.rawAnalysis),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey.shade600,
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Content (always visible)
          Padding(
            padding: const EdgeInsets.fromLTRB(16.0, 0, 16.0, 16.0),
            child: _FormattedAnalyzeMatchText(
              text: analyzeMatch.rawAnalysis,
            ),
          ),
        ],
      ),
    );
  }

  Color _getDecisionColor(String analysis) {
    if (analysis.contains('🟢 STRONG PURSUE')) {
      return Colors.green.shade600;
    } else if (analysis.contains('🟡 STRATEGIC PURSUE')) {
      return Colors.orange.shade600;
    } else if (analysis.contains('🟠 CALCULATED RISK')) {
      return Colors.deepOrange.shade600;
    } else if (analysis.contains('🔴 REALISTIC REJECT')) {
      return Colors.red.shade600;
    }
    return Colors.blue.shade600;
  }

  String _getDecisionSummary(String analysis) {
    if (analysis.contains('🟢 STRONG PURSUE')) {
      return 'Strong candidate match (80%+ probability)';
    } else if (analysis.contains('🟡 STRATEGIC PURSUE')) {
      return 'Strategic candidate match (40-70% probability)';
    } else if (analysis.contains('🟠 CALCULATED RISK')) {
      return 'Calculated risk candidate (15-40% probability)';
    } else if (analysis.contains('🔴 REALISTIC REJECT')) {
      return 'Low match probability (<15%)';
    }
    return 'Recruiter assessment available';
  }
}

/// Custom widget to format analyze match text with proper styling
class _FormattedAnalyzeMatchText extends StatelessWidget {
  final String text;

  const _FormattedAnalyzeMatchText({
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return SelectableText.rich(
      _buildFormattedText(),
      style: TextStyle(
        fontSize: 13,
        color: Colors.grey.shade700,
        height: 1.4,
      ),
    );
  }

  TextSpan _buildFormattedText() {
    final lines = text.split('\n');
    final List<TextSpan> spans = [];

    for (final line in lines) {
      if (line.trim().isEmpty) {
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Handle decision indicators with emojis
      if (line.contains('🟢 STRONG PURSUE') ||
          line.contains('🟡 STRATEGIC PURSUE') ||
          line.contains('🟠 CALCULATED RISK') ||
          line.contains('🔴 REALISTIC REJECT')) {
        spans.add(TextSpan(
          text: line + '\n',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: _getDecisionColor(line),
          ),
        ));
      }
      // Handle main headers (##)
      else if (line.startsWith('## ')) {
        spans.add(TextSpan(
          text: '${line.substring(3)}\n',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ));
        spans.add(const TextSpan(text: '\n'));
      }
      // Handle sub headers (###)
      else if (line.startsWith('### ')) {
        spans.add(TextSpan(
          text: '${line.substring(4)}\n',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.grey.shade800,
          ),
        ));
      }
      // Handle numbered lists
      else if (RegExp(r'^\d+\.\s').hasMatch(line)) {
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey.shade700,
            height: 1.5,
          ),
        ));
      }
      // Handle bullet points
      else if (line.startsWith('- ')) {
        spans.add(TextSpan(
          text: '• ${line.substring(2)}\n',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey.shade700,
            height: 1.5,
          ),
        ));
      }
      // Handle probability indicators
      else if (line.contains('%')) {
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Colors.blue.shade700,
          ),
        ));
      }
      // Handle bold text (**text**) - this should come last
      else if (line.contains('**')) {
        spans.add(_parseBoldText(line));
      }
      // Regular text
      else {
        spans.add(TextSpan(
          text: '$line\n',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey.shade700,
            height: 1.4,
          ),
        ));
      }
    }

    return TextSpan(children: spans);
  }

  TextSpan _parseBoldText(String line) {
    final List<TextSpan> spans = [];
    final parts = line.split('**');

    for (int i = 0; i < parts.length; i++) {
      if (i % 2 == 0) {
        // Regular text
        if (parts[i].isNotEmpty) {
          spans.add(TextSpan(
            text: parts[i],
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey.shade700,
            ),
          ));
        }
      } else {
        // Bold text
        spans.add(TextSpan(
          text: parts[i],
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.bold,
            color: Colors.grey.shade800,
          ),
        ));
      }
    }

    spans.add(const TextSpan(text: '\n'));
    return TextSpan(children: spans);
  }

  Color _getDecisionColor(String line) {
    if (line.contains('🟢')) return Colors.green.shade600;
    if (line.contains('🟡')) return Colors.orange.shade600;
    if (line.contains('🟠')) return Colors.deepOrange.shade600;
    if (line.contains('🔴')) return Colors.red.shade600;
    return Colors.blue.shade600;
  }
}
