import 'package:flutter/material.dart';
import '../models/skills_analysis_model.dart';

/// Modular ATS Score Display Card - matches preextracted table quality
class ATSScoreDisplayCard extends StatelessWidget {
  final ATSResult? atsResult;
  final bool isLoading;

  const ATSScoreDisplayCard({
    super.key,
    this.atsResult,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    debugPrint('🎨 [ATS_CARD] Building ATSScoreDisplayCard');
    debugPrint('   isLoading: $isLoading');
    debugPrint('   atsResult: ${atsResult != null}');
    if (atsResult != null) {
      debugPrint('   finalATSScore: ${atsResult!.finalATSScore}');
    }

    if (isLoading) {
      return _buildLoadingState();
    }

    if (atsResult == null) {
      debugPrint('   → Returning empty (no atsResult)');
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getScoreColor(atsResult!.finalATSScore).withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 2,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          _buildHeader(),

          const Divider(height: 1),

          // Main Score Display
          _buildMainScoreSection(),

          const Divider(height: 1),

          // Status & Recommendation
          _buildStatusSection(),

          const Divider(height: 1),

          // Skills Match Breakdown (Category 1)
          _buildCategory1Breakdown(),

          const Divider(height: 1),

          // Component Analysis Scores (Category 2)
          _buildCategory2Breakdown(),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200, width: 2),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(
                Colors.orange.shade600,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Text(
            'Calculating ATS score...',
            style: TextStyle(
              fontSize: 16,
              color: Colors.orange.shade700,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            _getScoreColor(atsResult!.finalATSScore).withOpacity(0.1),
            _getScoreColor(atsResult!.finalATSScore).withOpacity(0.05),
          ],
        ),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(10),
          topRight: Radius.circular(10),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: _getScoreColor(atsResult!.finalATSScore),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.assessment,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '🎯 ATS Score Analysis',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Applicant Tracking System',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMainScoreSection() {
    final breakdown = atsResult!.breakdown;
    final baseScore = breakdown.baseScore;
    final bonusPoints = breakdown.bonusPoints;
    final boostApplied = breakdown.boostApplied;

    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          // Final Score - Large Display
          Expanded(
            child: Column(
              children: [
                const Text(
                  'Final Score',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      atsResult!.finalATSScore.toStringAsFixed(1),
                      style: TextStyle(
                        fontSize: 40,
                        fontWeight: FontWeight.bold,
                        color: _getScoreColor(atsResult!.finalATSScore),
                      ),
                    ),
                    const Padding(
                      padding: EdgeInsets.only(bottom: 6),
                      child: Text(
                        '/100',
                        style: TextStyle(
                          fontSize: 20,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          Container(
            height: 60,
            width: 1,
            color: Colors.grey.shade300,
          ),

          // Base Score, Bonus & Boost
          Expanded(
            child: Column(
              children: [
                _buildScorePill('Base', baseScore, Colors.blue),
                const SizedBox(height: 8),
                _buildScorePill('Bonus', bonusPoints, Colors.green),
                if (boostApplied > 0) ...[
                  const SizedBox(height: 8),
                  _buildBoostPill(boostApplied),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScorePill(String label, double value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '$label: ',
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Text(
            value >= 0 ? '+${value.toStringAsFixed(1)}' : value.toStringAsFixed(1),
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBoostPill(double boostValue) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.bolt,
          size: 16,
          color: Colors.purple.shade700,
        ),
        const SizedBox(width: 4),
        Text(
          'Boost: ',
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.purple.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.purple.shade200),
          ),
          child: Text(
            '+${boostValue.toStringAsFixed(1)}',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Colors.purple.shade700,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getScoreColor(atsResult!.finalATSScore).withOpacity(0.05),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status Badge
          Row(
            children: [
              Icon(
                _getStatusIcon(),
                color: _getScoreColor(atsResult!.finalATSScore),
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  atsResult!.categoryStatus,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: _getScoreColor(atsResult!.finalATSScore),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Recommendation
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.lightbulb_outline,
                  size: 18,
                  color: Colors.orange,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '💡 ${atsResult!.recommendation}',
                    style: const TextStyle(
                      fontSize: 13,
                      color: Colors.black87,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategory1Breakdown() {
    final category1 = atsResult!.breakdown.category1;

    final technicalPoints = category1.technicalPoints;
    final softPoints = category1.softPoints;
    final domainPoints = category1.domainPoints;
    final totalScore = category1.score;
    final maxPoints = category1.maxPoints.toInt();

    final technicalRate = category1.technicalSkillsMatchRate;
    final softRate = category1.softSkillsMatchRate;
    final domainRate = category1.domainKeywordsMatchRate;

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Skills Match Breakdown',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          // Technical Skills
          _buildSkillsMatchRow(
            'Technical',
            technicalPoints,
            40,
            technicalRate,
            Colors.blue,
          ),
          const SizedBox(height: 10),

          // Soft Skills
          _buildSkillsMatchRow(
            'Soft',
            softPoints,
            15,
            softRate,
            Colors.purple,
          ),
          const SizedBox(height: 10),

          // Domain Keywords
          _buildSkillsMatchRow(
            'Domain',
            domainPoints,
            10,
            domainRate,
            Colors.orange,
          ),

          const SizedBox(height: 12),
          const Divider(),
          const SizedBox(height: 8),

          // Total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Total:',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '${totalScore.toStringAsFixed(1)} / $maxPoints',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: _getScoreColor((totalScore / maxPoints) * 100),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSkillsMatchRow(
    String label,
    double points,
    int maxPoints,
    double matchRate,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '${matchRate.toStringAsFixed(0)}% (${points.toStringAsFixed(1)})',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Stack(
          children: [
            // Background bar
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            // Progress bar
            FractionallySizedBox(
              widthFactor: (matchRate / 100).clamp(0.0, 1.0),
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCategory2Breakdown() {
    final category2 = atsResult!.breakdown.category2;

    final totalScore = category2.score;
    final maxPoints = category2.maxPoints.toInt();

    final technical = category2.technicalSkillsComponent;
    final experience = category2.experienceFitComponent;

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Component Analysis Scores',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          // Technical Skills Component
          _buildComponentRow(
            'Technical',
            technical.score,
            technical.maxPoints.toInt(),
            technical.average,
            Colors.blue,
          ),
          const SizedBox(height: 10),

          // Experience Fit Component
          _buildComponentRow(
            'Experience',
            experience.score,
            experience.maxPoints.toInt(),
            experience.average,
            Colors.green,
          ),

          const SizedBox(height: 12),
          const Divider(),
          const SizedBox(height: 8),

          // Total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Total:',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '${totalScore.toStringAsFixed(1)} / $maxPoints',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: _getScoreColor((totalScore / maxPoints) * 100),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildComponentRow(
    String label,
    double score,
    int maxPoints,
    double average,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '${score.toStringAsFixed(1)}/$maxPoints (Avg: ${average.toStringAsFixed(1)})',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Stack(
          children: [
            // Background bar
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            // Progress bar with safety clamp
            FractionallySizedBox(
              widthFactor: maxPoints > 0
                  ? (score / maxPoints).clamp(0.0, 1.0)
                  : 0.0,
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 75) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  IconData _getStatusIcon() {
    final score = atsResult!.finalATSScore;
    if (score >= 75) return Icons.check_circle;
    if (score >= 60) return Icons.warning_amber;
    return Icons.cancel;
  }
}

