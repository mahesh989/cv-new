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
