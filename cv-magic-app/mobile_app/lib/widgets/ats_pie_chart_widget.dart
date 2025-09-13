import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

/// Custom pie chart widget for displaying ATS component scores
class ATSPieChartWidget extends StatelessWidget {
  final double skillsRelevanceScore;
  final double experienceAlignmentScore;
  final double overallScore;

  const ATSPieChartWidget({
    super.key,
    required this.skillsRelevanceScore,
    required this.experienceAlignmentScore,
    required this.overallScore,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 250,
      child: Row(
        children: [
          // Pie Chart
          Expanded(
            flex: 3,
            child: PieChart(
              PieChartData(
                pieTouchData: PieTouchData(
                  touchCallback: (FlTouchEvent event, pieTouchResponse) {},
                  enabled: true,
                ),
                startDegreeOffset: -90,
                borderData: FlBorderData(show: false),
                sectionsSpace: 4,
                centerSpaceRadius: 40,
                sections: _buildPieChartSections(),
              ),
            ),
          ),
          
          // Legend and Overall Score
          Expanded(
            flex: 2,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Overall ATS Score in center-like display
                Container(
                  padding: const EdgeInsets.all(16),
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
                        '${overallScore.toStringAsFixed(1)}',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: _getScoreColor(overallScore),
                        ),
                      ),
                      Text(
                        'Overall Score',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                
                // Legend
                _buildLegendItem(
                  'Skills Relevance', 
                  skillsRelevanceScore, 
                  Colors.green,
                ),
                const SizedBox(height: 8),
                _buildLegendItem(
                  'Experience Alignment', 
                  experienceAlignmentScore, 
                  Colors.orange,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<PieChartSectionData> _buildPieChartSections() {
    return [
      PieChartSectionData(
        color: Colors.green,
        value: skillsRelevanceScore,
        title: '${skillsRelevanceScore.toStringAsFixed(1)}%',
        radius: 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      PieChartSectionData(
        color: Colors.orange,
        value: experienceAlignmentScore,
        radius: 60,
        title: '${experienceAlignmentScore.toStringAsFixed(1)}%',
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Fill remaining space with light gray for visual completion
      PieChartSectionData(
        color: Colors.grey[300]!,
        value: 100 - skillsRelevanceScore - experienceAlignmentScore,
        title: '',
        radius: 50,
        titleStyle: const TextStyle(fontSize: 0),
      ),
    ];
  }

  Widget _buildLegendItem(String label, double score, Color color) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${score.toStringAsFixed(1)}',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ],
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