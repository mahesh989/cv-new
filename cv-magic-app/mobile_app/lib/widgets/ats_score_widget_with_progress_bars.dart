import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';
import '../models/skills_analysis_model.dart';

/// Enhanced ATS Score Widget with categorized progress bars
class ATSScoreWidgetWithProgressBars extends StatelessWidget {
  final SkillsAnalysisController controller;

  const ATSScoreWidgetWithProgressBars({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    // Only show if we have ATS results
    if (!controller.hasATSResult) {
      return const SizedBox.shrink();
    }

    final atsResult = controller.atsResult!;
    final hasComponentAnalysis = controller.hasComponentAnalysis;

    return Card(
      margin: const EdgeInsets.all(16),
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ATS Score Header
            Row(
              children: [
                const Icon(Icons.assessment, color: Colors.orange, size: 28),
                const SizedBox(width: 12),
                Text(
                  'ATS Score Analysis',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange[800],
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Score Display
            _buildFallbackScoreDisplay(atsResult),

            // Status and Recommendation
            const SizedBox(height: 16),
            Center(
              child: Column(
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _getScoreColor(atsResult.finalATSScore)
                          .withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                          color: _getScoreColor(atsResult.finalATSScore)
                              .withOpacity(0.3)),
                    ),
                    child: Text(
                      atsResult.categoryStatus,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: _getScoreColor(atsResult.finalATSScore),
                      ),
                    ),
                  ),
                  if (atsResult.recommendation.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Text(
                      atsResult.recommendation,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[700],
                        fontStyle: FontStyle.italic,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),

            // Additional Component Analysis Scores (if available)
            if (hasComponentAnalysis) ...[
              const SizedBox(height: 20),
              Text(
                'Additional Component Scores',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 12),
              _buildAdditionalScores(),
            ],

            // Categorized Progress Bars - Main Feature
            const SizedBox(height: 24),
            _buildCategorizedProgressBars(atsResult),
          ],
        ),
      ),
    );
  }

  Widget _buildFallbackScoreDisplay(ATSResult atsResult) {
    // Fallback to original style if no component analysis
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.orange[50]!,
            Colors.orange[100]!,
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange[300]!),
      ),
      child: Column(
        children: [
          Text(
            '${atsResult.finalATSScore.toStringAsFixed(1)}/100',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.bold,
              color: _getScoreColor(atsResult.finalATSScore),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAdditionalScores() {
    return Column(
      children: [
        _buildScoreRow(
            'Industry Fit', controller.industryFitScore, Icons.business),
        _buildScoreRow(
            'Role Seniority', controller.roleSeniorityScore, Icons.trending_up),
        _buildScoreRow('Technical Depth', controller.technicalDepthScore,
            Icons.engineering),
      ],
    );
  }

  Widget _buildScoreRow(String label, double score, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            ),
          ),
          SizedBox(
            width: 60,
            child: Text(
              score.toStringAsFixed(1),
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  /// Build categorized progress bars with CORRECT values from ATS breakdown
  Widget _buildCategorizedProgressBars(ATSResult atsResult) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Main title
        Row(
          children: [
            Icon(Icons.bar_chart, color: Colors.blue[700], size: 24),
            const SizedBox(width: 8),
            Text(
              'Detailed ATS Breakdown',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.blue[700],
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // Category 1: Skills Matching (Max: 40 points)
        _buildCategory1ProgressBars(atsResult.breakdown.category1),
        const SizedBox(height: 24),

        // Category 2: Experience & Competency (Max: 60 points)
        _buildCategory2ProgressBars(atsResult.breakdown.category2),
        const SizedBox(height: 24),

        // Category 3: Bonus Points
        _buildCategory3BonusSection(atsResult.breakdown),
        const SizedBox(height: 20),

        // Final Score Summary
        _buildFinalScoreSummary(atsResult),
      ],
    );
  }

  Widget _buildCategory1ProgressBars(ATSCategory1 category1) {
    // Convert percentage rates back to actual point values
    final techScore =
        (category1.technicalSkillsMatchRate / 100) * 20; // Max: 20 points
    final domainScore =
        (category1.domainKeywordsMatchRate / 100) * 5; // Max: 5 points
    final softScore =
        (category1.softSkillsMatchRate / 100) * 15; // Max: 15 points
    final totalScore = category1.score; // Total for category (0-40)

    return _buildCategorySection(
      title: 'Category 1: Skills Matching',
      totalScore: totalScore,
      maxScore: 40,
      color: const Color(0xFF4A90E2),
      items: [
        _ProgressBarItem(
            label: 'Technical Skills',
            value: techScore,
            maxValue: 20,
            percentage: category1.technicalSkillsMatchRate),
        _ProgressBarItem(
            label: 'Domain Keywords',
            value: domainScore,
            maxValue: 5,
            percentage: category1.domainKeywordsMatchRate),
        _ProgressBarItem(
            label: 'Soft Skills',
            value: softScore,
            maxValue: 15,
            percentage: category1.softSkillsMatchRate),
      ],
    );
  }

  Widget _buildCategory2ProgressBars(ATSCategory2 category2) {
    // Convert percentage rates back to actual point values
    final coreScore =
        (category2.coreCompetencyAvg / 100) * 25; // Max: 25 points
    final expScore =
        (category2.experienceSeniorityAvg / 100) * 20; // Max: 20 points
    final potentialScore =
        (category2.potentialAbilityAvg / 100) * 10; // Max: 10 points
    final companyScore = (category2.companyFitAvg / 100) * 5; // Max: 5 points
    final totalScore = category2.score; // Total for category (0-60)

    return _buildCategorySection(
      title: 'Category 2: Experience & Competency',
      totalScore: totalScore,
      maxScore: 60,
      color: const Color(0xFFE67E22),
      items: [
        _ProgressBarItem(
            label: 'Core Competency',
            value: coreScore,
            maxValue: 25,
            percentage: category2.coreCompetencyAvg),
        _ProgressBarItem(
            label: 'Experience & Seniority',
            value: expScore,
            maxValue: 20,
            percentage: category2.experienceSeniorityAvg),
        _ProgressBarItem(
            label: 'Potential & Ability',
            value: potentialScore,
            maxValue: 10,
            percentage: category2.potentialAbilityAvg),
        _ProgressBarItem(
            label: 'Company Fit',
            value: companyScore,
            maxValue: 5,
            percentage: category2.companyFitAvg),
      ],
    );
  }

  Widget _buildCategory3BonusSection(ATSBreakdown breakdown) {
    final bonusPoints = breakdown.bonusPoints;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: bonusPoints >= 0
              ? [Colors.green[50]!, Colors.green[100]!]
              : [Colors.red[50]!, Colors.red[100]!],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: bonusPoints >= 0 ? Colors.green[300]! : Colors.red[300]!,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: (bonusPoints >= 0 ? Colors.green : Colors.red)
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  bonusPoints >= 0 ? Icons.trending_up : Icons.trending_down,
                  color: bonusPoints >= 0 ? Colors.green[700] : Colors.red[700],
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Category 3: Bonus Points',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color:
                        bonusPoints >= 0 ? Colors.green[700] : Colors.red[700],
                  ),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: bonusPoints >= 0 ? Colors.green[600] : Colors.red[600],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${bonusPoints >= 0 ? '+' : ''}${bonusPoints.toStringAsFixed(1)}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            bonusPoints >= 0
                ? 'Bonus points awarded for exceptional keyword matches'
                : 'Points deducted for missing critical keywords',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[700],
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategorySection({
    required String title,
    required double totalScore,
    required int maxScore,
    required Color color,
    required List<_ProgressBarItem> items,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Category header with total score
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.assessment,
                  color: color,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${totalScore.toStringAsFixed(1)}/$maxScore',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Individual progress bars
          ...items.map((item) => _buildProgressBar(item, color)).toList(),
        ],
      ),
    );
  }

  Widget _buildProgressBar(_ProgressBarItem item, Color color) {
    final percentage =
        item.maxValue > 0 ? (item.value / item.maxValue) * 100 : 0;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Label and score display
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  item.label,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                '${item.value.toStringAsFixed(1)}/${item.maxValue.toInt()}',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),

          // Progress bar
          Container(
            height: 16,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Stack(
              children: [
                // Filled portion
                FractionallySizedBox(
                  widthFactor: (percentage / 100).clamp(0.0, 1.0),
                  child: Container(
                    height: 16,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [color, color.withOpacity(0.7)],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),

          // Percentage display
          Text(
            '${item.percentage.toStringAsFixed(1)}%',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinalScoreSummary(ATSResult atsResult) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF667EEA).withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.analytics, color: Colors.white, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Final ATS Score',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'Category 1 (${atsResult.breakdown.category1.score.toStringAsFixed(1)}) + Category 2 (${atsResult.breakdown.category2.score.toStringAsFixed(1)}) + Bonus (${atsResult.breakdown.bonusPoints >= 0 ? '+' : ''}${atsResult.breakdown.bonusPoints.toStringAsFixed(1)})',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              atsResult.finalATSScore.toStringAsFixed(1),
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF667EEA),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) {
      return Colors.green;
    } else if (score >= 60) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}

/// Helper class for progress bar data
class _ProgressBarItem {
  final String label;
  final double value;
  final int maxValue;
  final double percentage;

  _ProgressBarItem({
    required this.label,
    required this.value,
    required this.maxValue,
    required this.percentage,
  });
}
