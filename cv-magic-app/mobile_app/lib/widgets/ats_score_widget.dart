import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';
import '../models/skills_analysis_model.dart';

/// Widget to display ATS score and component analysis results
class ATSScoreWidget extends StatelessWidget {
  final SkillsAnalysisController controller;

  const ATSScoreWidget({
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
            
            // ATS Score Display
            Container(
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
                  const SizedBox(height: 8),
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
            
            // Component Analysis Scores (if available)
            if (hasComponentAnalysis) ...[
              const SizedBox(height: 20),
              Text(
                'Detailed Component Scores',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildComponentScores(context),
            ],
            
            // ATS Breakdown
            const SizedBox(height: 20),
            _buildATSBreakdown(context, atsResult),
          ],
        ),
      ),
    );
  }

  Widget _buildComponentScores(BuildContext context) {
    return Column(
      children: [
        _buildScoreRow('Skills Relevance', controller.skillsRelevanceScore, Icons.code),
        _buildScoreRow('Experience Alignment', controller.experienceAlignmentScore, Icons.work),
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
    debugPrint('🎨 [ATS_WIDGET] Building ATS breakdown');
    debugPrint('   Final Score: ${atsResult.finalATSScore}');
    debugPrint('   Version: ${atsResult.scoringVersion}');
    debugPrint('   Category1 Score: ${atsResult.breakdown.category1.score}/${atsResult.breakdown.category1.maxPoints}');
    debugPrint('   Category2 Score: ${atsResult.breakdown.category2.score}/${atsResult.breakdown.category2.maxPoints}');
    debugPrint('   Base Score: ${atsResult.breakdown.baseScore}');
    debugPrint('   Bonus: ${atsResult.breakdown.bonusPoints}');
    debugPrint('   Boost: ${atsResult.breakdown.boostApplied}');
    
    final breakdown = atsResult.breakdown;
    
    return ExpansionTile(
      title: const Text(
        'Detailed ATS Breakdown (v2 - 65/35 Split)',
        style: TextStyle(fontWeight: FontWeight.bold),
      ),
      leading: const Icon(Icons.analytics, color: Colors.blue),
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Category 1: Keyword Matching (65 points)
              _buildCategory1Section(
                'Category 1: Keyword Matching (${breakdown.category1.maxPoints.toInt()} points)',
                breakdown.category1.score,
                _buildCategory1Details(breakdown.category1),
              ),
              const SizedBox(height: 16),
              
              // Category 2: AI Component Analysis (35 points)
              _buildCategory2Section(breakdown.category2),
              
              const SizedBox(height: 16),
              
              // Final Calculations
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Base Score:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  Text(
                    '${breakdown.baseScore.toStringAsFixed(1)}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              if (breakdown.boostApplied > 0) ...[
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Boost Applied:',
                      style: TextStyle(
                        fontWeight: FontWeight.w500,
                        color: Colors.orange,
                      ),
                    ),
                    Text(
                      '+${breakdown.boostApplied.toStringAsFixed(1)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange,
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Bonus Points:',
                    style: TextStyle(
                      fontWeight: FontWeight.w500,
                      color: breakdown.bonusPoints >= 0 ? Colors.green : Colors.red,
                    ),
                  ),
                  Text(
                    '${breakdown.bonusPoints >= 0 ? '+' : ''}${breakdown.bonusPoints.toStringAsFixed(1)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: breakdown.bonusPoints >= 0 ? Colors.green : Colors.red,
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

  List<Widget> _buildCategory1Details(ATSCategory1 category1) {
    debugPrint('🎨 [ATS_WIDGET] Building Category1 details');
    debugPrint('   Tech: ${category1.technicalSkillsMatchRate}% → ${category1.technicalPoints}/40');
    debugPrint('   Domain: ${category1.domainKeywordsMatchRate}% → ${category1.domainPoints}/10');
    debugPrint('   Soft: ${category1.softSkillsMatchRate}% → ${category1.softPoints}/15');
    
    return [
      _buildDetailRow('Technical Skills', 
        '${category1.technicalSkillsMatchRate.toStringAsFixed(1)}% → ${category1.technicalPoints.toStringAsFixed(1)}/40'),
      _buildDetailRow('Domain Keywords', 
        '${category1.domainKeywordsMatchRate.toStringAsFixed(1)}% → ${category1.domainPoints.toStringAsFixed(1)}/10'),
      _buildDetailRow('Soft Skills', 
        '${category1.softSkillsMatchRate.toStringAsFixed(1)}% → ${category1.softPoints.toStringAsFixed(1)}/15'),
    ];
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 4),
      child: Row(
        children: [
          const Icon(Icons.circle, size: 6, color: Colors.grey),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '$label: $value',
              style: TextStyle(fontSize: 14, color: Colors.grey[700]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategory2Section(ATSCategory2 category2) {
    debugPrint('🎨 [ATS_WIDGET] Building Category2 section');
    debugPrint('   Score: ${category2.score}/${category2.maxPoints}');
    debugPrint('   Tech Component: ${category2.technicalSkillsComponent.score}/22 (avg: ${category2.technicalSkillsComponent.average}%)');
    debugPrint('   Exp Component: ${category2.experienceFitComponent.score}/13 (avg: ${category2.experienceFitComponent.average}%)');
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                'Category 2: AI Component Analysis (${category2.maxPoints.toInt()} points)',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            Text(
              '${category2.score.toStringAsFixed(1)}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: _getScoreColor(category2.score),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        _buildDetailRow(
          'Technical & Skills Component',
          '${category2.technicalSkillsComponent.score.toStringAsFixed(1)}/22 (avg: ${category2.technicalSkillsComponent.average.toStringAsFixed(1)}%)',
        ),
        _buildDetailRow(
          'Experience & Fit Component',
          '${category2.experienceFitComponent.score.toStringAsFixed(1)}/13 (avg: ${category2.experienceFitComponent.average.toStringAsFixed(1)}%)',
        ),
      ],
    );
  }

  Widget _buildCategory1Section(String title, double score, List<Widget> details) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
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
        ...details,
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
