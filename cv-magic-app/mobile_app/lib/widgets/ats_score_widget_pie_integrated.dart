import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../controllers/skills_analysis_controller.dart';
import '../models/skills_analysis_model.dart';

/// Widget to display ATS score and component analysis results with pie chart
class ATSScoreWidgetWithPieChart extends StatelessWidget {
  final SkillsAnalysisController controller;

  const ATSScoreWidgetWithPieChart({
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
            
            // Pie Chart Display - Replacing linear score display
            if (hasComponentAnalysis) 
              _buildPieChartSection()
            else
              _buildFallbackScoreDisplay(atsResult),
            
            // Status and Recommendation
            const SizedBox(height: 16),
            Center(
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: _getScoreColor(atsResult.finalATSScore).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _getScoreColor(atsResult.finalATSScore).withOpacity(0.3)),
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
              _buildAdditionalScores(context),
            ],
            
            // ATS Breakdown
            const SizedBox(height: 20),
            _buildATSBreakdown(context, atsResult),
          ],
        ),
      ),
    );
  }

  Widget _buildPieChartSection() {
    final atsResult = controller.atsResult!;
    
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
                        '${atsResult.finalATSScore.toStringAsFixed(1)}',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: _getScoreColor(atsResult.finalATSScore),
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
                  controller.skillsRelevanceScore, 
                  Colors.green,
                ),
                const SizedBox(height: 8),
                _buildLegendItem(
                  'Experience Alignment', 
                  controller.experienceAlignmentScore, 
                  Colors.orange,
                ),
              ],
            ),
          ),
        ],
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

  List<PieChartSectionData> _buildPieChartSections() {
    final skillsScore = controller.skillsRelevanceScore;
    final experienceScore = controller.experienceAlignmentScore;
    final remainingScore = 100 - skillsScore - experienceScore;
    
    return [
      PieChartSectionData(
        color: Colors.green,
        value: skillsScore,
        title: '${skillsScore.toStringAsFixed(1)}%',
        radius: 60,
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      PieChartSectionData(
        color: Colors.orange,
        value: experienceScore,
        radius: 60,
        title: '${experienceScore.toStringAsFixed(1)}%',
        titleStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      // Fill remaining space with light gray for visual completion
      if (remainingScore > 0)
        PieChartSectionData(
          color: Colors.grey[300]!,
          value: remainingScore,
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

  Widget _buildAdditionalScores(BuildContext context) {
    return Column(
      children: [
        _buildScoreRow('Industry Fit', controller.industryFitScore, Icons.business),
        _buildScoreRow('Role Seniority', controller.roleSeniorityScore, Icons.trending_up),
        _buildScoreRow('Technical Depth', controller.technicalDepthScore, Icons.engineering),
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

  Widget _buildATSBreakdown(BuildContext context, ATSResult atsResult) {
    return ExpansionTile(
      title: const Text(
        'Detailed ATS Breakdown',
        style: TextStyle(fontWeight: FontWeight.bold),
      ),
      leading: const Icon(Icons.analytics, color: Colors.blue),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Category 1: Skills Matching
              _buildBreakdownSection(
                'Skills Matching',
                atsResult.breakdown.category1.score,
                [
                  'Technical Skills: ${atsResult.breakdown.category1.technicalSkillsMatchRate.toStringAsFixed(1)}%',
                  'Soft Skills: ${atsResult.breakdown.category1.softSkillsMatchRate.toStringAsFixed(1)}%',
                  'Domain Keywords: ${atsResult.breakdown.category1.domainKeywordsMatchRate.toStringAsFixed(1)}%',
                ],
              ),
              const SizedBox(height: 16),
              
              // Category 2: Experience & Competency
              _buildBreakdownSection(
                'Experience & Competency',
                atsResult.breakdown.category2.score,
                [
                  'Core Competency: ${atsResult.breakdown.category2.coreCompetencyAvg.toStringAsFixed(1)}%',
                  'Experience/Seniority: ${atsResult.breakdown.category2.experienceSeniorityAvg.toStringAsFixed(1)}%',
                  'Potential/Ability: ${atsResult.breakdown.category2.potentialAbilityAvg.toStringAsFixed(1)}%',
                  'Company Fit: ${atsResult.breakdown.category2.companyFitAvg.toStringAsFixed(1)}%',
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Final Calculations
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Base ATS Score:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  Text(
                    '${atsResult.breakdown.ats1Score.toStringAsFixed(1)}',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Bonus Points:',
                    style: TextStyle(
                      fontWeight: FontWeight.w500,
                      color: atsResult.breakdown.bonusPoints >= 0 ? Colors.green : Colors.red,
                    ),
                  ),
                  Text(
                    '${atsResult.breakdown.bonusPoints >= 0 ? '+' : ''}${atsResult.breakdown.bonusPoints.toStringAsFixed(1)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: atsResult.breakdown.bonusPoints >= 0 ? Colors.green : Colors.red,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBreakdownSection(String title, double score, List<String> details) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '${score.toStringAsFixed(1)}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: _getScoreColor(score),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...details.map((detail) => Padding(
          padding: const EdgeInsets.only(left: 16, bottom: 4),
          child: Row(
            children: [
              const Icon(Icons.circle, size: 6, color: Colors.grey),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  detail,
                  style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                ),
              ),
            ],
          ),
        )),
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