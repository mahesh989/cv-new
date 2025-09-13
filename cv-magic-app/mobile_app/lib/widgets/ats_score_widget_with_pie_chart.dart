import 'package:flutter/material.dart';
import 'ats_pie_chart_widget.dart';
import '../controllers/skills_analysis_controller.dart';
import '../models/skills_analysis_model.dart';

/// Widget to display ATS score and component analysis results with pie chart
class ATSScoreWithPieChartWidget extends StatelessWidget {
  // For demo purposes - using direct properties instead of controller
  final double finalATSScore;
  final String categoryStatus;
  final String recommendation;
  final double skillsRelevanceScore;
  final double experienceAlignmentScore;
  final bool hasComponentAnalysis;

  const ATSScoreWithPieChartWidget({
    super.key,
    required this.finalATSScore,
    required this.categoryStatus,
    required this.recommendation,
    required this.skillsRelevanceScore,
    required this.experienceAlignmentScore,
    this.hasComponentAnalysis = true,
  });

  @override
  Widget build(BuildContext context) {
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
            
            // Pie Chart Display - Replacing linear score display
            ATSPieChartWidget(
              skillsRelevanceScore: skillsRelevanceScore,
              experienceAlignmentScore: experienceAlignmentScore,
              overallScore: finalATSScore,
            ),
            
            // Status and Recommendation
            const SizedBox(height: 16),
            Center(
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _getScoreColor(finalATSScore).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _getScoreColor(finalATSScore).withOpacity(0.3)),
                    ),
                    child: Text(
                      categoryStatus,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: _getScoreColor(finalATSScore),
                      ),
                    ),
                  ),
                  if (recommendation.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    Text(
                      recommendation,
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
            
            // Component Analysis Scores (if available)
            if (hasComponentAnalysis) ...[
              const SizedBox(height: 20),
              Text(
                'Additional Component Scores',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildAdditionalScores(context),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAdditionalScores(BuildContext context) {
    // Demo additional scores - in real implementation, these would come from the controller
    final additionalScores = [
      {'label': 'Industry Fit', 'score': 75.0, 'icon': Icons.business},
      {'label': 'Role Seniority', 'score': 68.0, 'icon': Icons.trending_up},
      {'label': 'Technical Depth', 'score': 82.0, 'icon': Icons.engineering},
    ];
    
    return Column(
      children: additionalScores.map((scoreData) => 
        _buildScoreRow(
          scoreData['label'] as String, 
          scoreData['score'] as double, 
          scoreData['icon'] as IconData
        )
      ).toList(),
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
          Container(
            width: 60,
            child: Text(
              '${score.toStringAsFixed(1)}',
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
