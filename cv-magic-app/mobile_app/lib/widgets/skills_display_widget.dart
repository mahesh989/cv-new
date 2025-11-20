import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../controllers/skills_analysis_controller.dart';
import '../utils/preextracted_parser.dart';
import 'analyze_match_card.dart';
import 'ats_score_widget.dart';
import 'skills_analysis/ai_powered_skills_analysis.dart';

/// Widget for displaying comprehensive skills analysis results
/// Shows all analysis components progressively as they become available
class SkillsDisplayWidget extends StatelessWidget {
  final SkillsAnalysisController controller;

  const SkillsDisplayWidget({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<SkillsAnalysisController>(
      builder: (context, controller, child) {
        if (!controller.hasResults) {
          return const SizedBox.shrink();
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Analyze Match Results
            if (controller.hasAnalyzeMatch && controller.analyzeMatch != null) ...[
              _buildAnalyzeMatchSection(controller),
              const SizedBox(height: 16),
            ] else if (controller.showAnalyzeMatch && !controller.hasAnalyzeMatch) ...[
              _buildLoadingCard('Generating analyze match results...'),
              const SizedBox(height: 16),
            ],

            // Pre-extracted Skills Comparison (AI-Powered Summary Table)
            if (controller.result != null && controller.result!.hasPreextractedComparison) ...[
              _buildPreextractedComparisonSection(controller),
              const SizedBox(height: 16),
            ],

            // ATS Score Results
            if (controller.hasATSResult) ...[
              ATSScoreWidget(controller: controller),
              const SizedBox(height: 16),
            ] else if (controller.showATSLoading) ...[
              _buildLoadingCard('Calculating ATS score...'),
              const SizedBox(height: 16),
            ],

            // AI Recommendations
            if (controller.showAIRecommendationResults && controller.result?.aiRecommendation != null) ...[
              _buildAIRecommendationsSection(controller),
              const SizedBox(height: 16),
            ] else if (controller.showAIRecommendationLoading) ...[
              _buildLoadingCard('Generating AI recommendations...'),
              const SizedBox(height: 16),
            ],
          ],
        );
      },
    );
  }

  Widget _buildAnalyzeMatchSection(SkillsAnalysisController controller) {
    final matchData = controller.result?.toJson()['analyze_match'] as Map<String, dynamic>? ?? {};
    
    return AnalyzeMatchCard(
      matchData: matchData,
      companyName: controller.analyzeMatchCompanyName,
    );
  }

  Widget _buildPreextractedComparisonSection(SkillsAnalysisController controller) {
    final result = controller.result;
    if (result == null || !result.hasPreextractedComparison) {
      return const SizedBox.shrink();
    }

    try {
      // Parse the raw text output into structured data
      final parsedData = PreextractedParser.parse(result.preextractedRawOutput!);
      
      return Card(
        margin: const EdgeInsets.symmetric(vertical: 8.0),
        elevation: 4,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            gradient: LinearGradient(
              colors: [
                Colors.purple.shade50,
                Colors.purple.shade100,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: AIPoweredSkillsAnalysis(data: parsedData),
          ),
        ),
      );
    } catch (e) {
      debugPrint('❌ [SKILLS_DISPLAY] Error parsing preextracted comparison: $e');
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Error parsing skills comparison: $e',
            style: const TextStyle(color: Colors.red),
          ),
        ),
      );
    }
  }

  Widget _buildAIRecommendationsSection(SkillsAnalysisController controller) {
    final recommendation = controller.result?.aiRecommendation;
    if (recommendation == null || recommendation.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.lightbulb, color: Colors.amber, size: 24),
                const SizedBox(width: 8),
                Text(
                  'AI Recommendations',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber[800],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              recommendation.content,
              style: const TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingCard(String message) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[700],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

