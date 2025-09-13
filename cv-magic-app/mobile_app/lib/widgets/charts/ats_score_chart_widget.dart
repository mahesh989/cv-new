import 'package:flutter/material.dart';
import '../../models/skills_analysis_model.dart';
import 'chart_data_models.dart';
import 'category1_chart_widget.dart';
import 'category2_chart_widget.dart';
import 'category3_bonus_widget.dart';

/// Main widget for displaying the complete ATS Score breakdown with all categories
class ATSScoreChartWidget extends StatelessWidget {
  final ATSResult atsResult;

  const ATSScoreChartWidget({
    super.key,
    required this.atsResult,
  });

  @override
  Widget build(BuildContext context) {
    // Convert data using the converter utility
    final category1Data = ATSChartDataConverter.convertCategory1Data(atsResult.breakdown.category1);
    final category2Data = ATSChartDataConverter.convertCategory2Data(atsResult.breakdown.category2);
    final category3Data = ATSChartDataConverter.convertCategory3Data(atsResult.breakdown);
    final overallScores = ATSChartDataConverter.getOverallScores(atsResult);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Main Title and Overall ATS Score
          _buildMainHeader(context),
          const SizedBox(height: 16),
          
          // Category 1: Direct Match Rates
          Category1ChartWidget(
            data: category1Data,
            totalScore: overallScores['category1_score'].toStringAsFixed(1),
            maxScore: overallScores['category1_max'].toString(),
          ),
          
          // Category 2: Component Analysis
          Category2ChartWidget(
            data: category2Data,
            totalScore: overallScores['category2_score'].toStringAsFixed(1),
            maxScore: overallScores['category2_max'].toString(),
          ),
          
          // Category 3: Bonus Points
          Category3BonusWidget(
            data: category3Data,
            totalBonusPoints: '+${overallScores['bonus_points'].toStringAsFixed(1)}',
          ),
          
          // Final Score Summary
          _buildFinalScoreSummary(overallScores),
        ],
      ),
    );
  }

  Widget _buildMainHeader(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
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
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.analytics,
              color: Colors.white,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'ATS Score Analysis',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Comprehensive CV-JD Match Assessment',
                  style: TextStyle(
                    fontSize: 14,
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
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  spreadRadius: 1,
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                const Text(
                  'Final Score',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF34495E),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  atsResult.finalATSScore.toStringAsFixed(1),
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF667EEA),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinalScoreSummary(Map<String, dynamic> scores) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE9ECEF), width: 2),
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
          const Text(
            'Score Breakdown Summary',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2C3E50),
            ),
          ),
          const SizedBox(height: 16),
          
          // Category breakdowns
          _buildScoreLine(
            'Category 1 (Direct Match)',
            scores['category1_score'].toStringAsFixed(1),
            scores['category1_max'].toString(),
            const Color(0xFF4A90E2),
          ),
          const SizedBox(height: 8),
          _buildScoreLine(
            'Category 2 (Component Analysis)',
            scores['category2_score'].toStringAsFixed(1),
            scores['category2_max'].toString(),
            const Color(0xFFE67E22),
          ),
          const SizedBox(height: 8),
          _buildScoreLine(
            'Category 3 (Bonus Points)',
            '+${scores['bonus_points'].toStringAsFixed(1)}',
            '',
            const Color(0xFF8E44AD),
          ),
          const SizedBox(height: 12),
          
          // Divider
          const Divider(thickness: 2, color: Color(0xFFE9ECEF)),
          const SizedBox(height: 12),
          
          // Final total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Final ATS Score',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2C3E50),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  scores['final_ats_score'].toStringAsFixed(1),
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildScoreLine(String label, String score, String maxScore, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: Color(0xFF34495E),
          ),
        ),
        Text(
          maxScore.isNotEmpty ? '$score/$maxScore' : score,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}