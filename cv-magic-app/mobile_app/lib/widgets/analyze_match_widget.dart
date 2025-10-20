import 'package:flutter/material.dart';
import '../models/skills_analysis_model.dart';
import '../utils/text_formatter.dart';

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
    final decisionColor = _getDecisionColor(analyzeMatch.rawAnalysis);

    return Card(
      margin: const EdgeInsets.all(16.0),
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              decisionColor.withOpacity(0.1),
              decisionColor.withOpacity(0.05),
            ],
          ),
        ),
        child: Column(
          children: [
            // Header with beautiful gradient background
            Container(
              padding: const EdgeInsets.all(20.0),
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    decisionColor.withOpacity(0.15),
                    decisionColor.withOpacity(0.08),
                  ],
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: decisionColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      _getDecisionIcon(analyzeMatch.rawAnalysis),
                      color: decisionColor,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Analyze Match',
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: decisionColor,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _getDecisionSummary(analyzeMatch.rawAnalysis),
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: decisionColor.withOpacity(0.8),
                                fontWeight: FontWeight.w500,
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
              padding: const EdgeInsets.fromLTRB(20.0, 16.0, 20.0, 20.0),
              child: AnalyzeMatchFormattedText(
                text: analyzeMatch.rawAnalysis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getDecisionColor(String analysis) {
    // New LITMUS_TEST_PROMPT format
    if (analysis.contains('DECISION: PROCEED')) {
      return const Color(0xFF10B981); // Emerald green
    } else if (analysis.contains('DECISION: MAYBE')) {
      return const Color(0xFFF59E0B); // Amber
    } else if (analysis.contains('DECISION: DONT_PROCEED')) {
      return const Color(0xFFEF4444); // Red
    }
    
    // Legacy format support
    if (analysis.contains('🟢 STRONG PURSUE')) {
      return const Color(0xFF10B981); // Emerald green
    } else if (analysis.contains('🟡 STRATEGIC PURSUE')) {
      return const Color(0xFFF59E0B); // Amber
    } else if (analysis.contains('🟠 CALCULATED RISK')) {
      return const Color(0xFFEA580C); // Orange
    } else if (analysis.contains('🔴 REALISTIC REJECT')) {
      return const Color(0xFFEF4444); // Red
    }
    
    return const Color(0xFF3B82F6); // Blue
  }

  String _getDecisionSummary(String analysis) {
    // New LITMUS_TEST_PROMPT format
    if (analysis.contains('DECISION: PROCEED')) {
      return '✅ Strong Match - Proceed with confidence!';
    } else if (analysis.contains('DECISION: MAYBE')) {
      return '⚠️ Conditional Match - Worth considering';
    } else if (analysis.contains('DECISION: DONT_PROCEED')) {
      return '❌ Not Recommended - Skip this opportunity';
    }
    
    // Legacy format support
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

  IconData _getDecisionIcon(String analysis) {
    // New LITMUS_TEST_PROMPT format
    if (analysis.contains('DECISION: PROCEED')) {
      return Icons.check_circle_rounded; // Green checkmark
    } else if (analysis.contains('DECISION: MAYBE')) {
      return Icons.help_center_rounded; // Question mark in circle
    } else if (analysis.contains('DECISION: DONT_PROCEED')) {
      return Icons.cancel_rounded; // Red X
    }
    
    // Legacy format support
    if (analysis.contains('🟢 STRONG PURSUE')) {
      return Icons.check_circle_rounded;
    } else if (analysis.contains('🟡 STRATEGIC PURSUE')) {
      return Icons.help_center_rounded;
    } else if (analysis.contains('🟠 CALCULATED RISK')) {
      return Icons.warning_rounded;
    } else if (analysis.contains('🔴 REALISTIC REJECT')) {
      return Icons.cancel_rounded;
    }
    
    return Icons.analytics_rounded; // Default analytics icon
  }
}
