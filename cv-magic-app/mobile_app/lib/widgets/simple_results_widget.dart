import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';

/// Simple widget to display analysis results without progress bars
class SimpleResultsWidget extends StatelessWidget {
  final SkillsAnalysisController controller;

  const SimpleResultsWidget({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (context, _) {
        // Show loading state
        if (controller.isLoading) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  const Icon(
                    Icons.psychology,
                    size: 48,
                    color: Colors.purple,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Analyzing your CV...',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.purple,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'This may take a few moments',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
                  ),
                ],
              ),
            ),
          );
        }

        // Show error state
        if (controller.hasError) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 48,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Analysis Failed',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    controller.errorMessage ?? 'Unknown error occurred',
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          );
        }

        // Show results
        if (controller.hasResults) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.check_circle,
                        size: 24,
                        color: Colors.green,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Analysis Complete',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildResultsContent(),
                ],
              ),
            ),
          );
        }

        // Default empty state
        return const SizedBox.shrink();
      },
    );
  }

  Widget _buildResultsContent() {
    final results = controller.analysisResults;
    if (results == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Skills Analysis Results
        if (results['cv_skills'] != null || results['jd_skills'] != null) ...[
          _buildSkillsSection('CV Skills', results['cv_skills']),
          const SizedBox(height: 16),
          _buildSkillsSection('Job Requirements', results['jd_skills']),
          const SizedBox(height: 16),
        ],

        // Match Analysis
        if (results['match_analysis'] != null) ...[
          _buildMatchAnalysis(results['match_analysis']),
          const SizedBox(height: 16),
        ],

        // ATS Score
        if (results['ats_score'] != null) ...[
          _buildATSScore(results['ats_score']),
          const SizedBox(height: 16),
        ],

        // Recommendations
        if (results['recommendations'] != null) ...[
          _buildRecommendations(results['recommendations']),
        ],
      ],
    );
  }

  Widget _buildSkillsSection(String title, dynamic skillsData) {
    if (skillsData == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.purple,
          ),
        ),
        const SizedBox(height: 8),
        if (skillsData is Map<String, dynamic>) ...[
          if (skillsData['technical_skills'] != null)
            _buildSkillCategory(
                'Technical Skills', skillsData['technical_skills']),
          if (skillsData['soft_skills'] != null)
            _buildSkillCategory('Soft Skills', skillsData['soft_skills']),
          if (skillsData['domain_keywords'] != null)
            _buildSkillCategory(
                'Domain Keywords', skillsData['domain_keywords']),
        ],
      ],
    );
  }

  Widget _buildSkillCategory(String category, dynamic skills) {
    if (skills == null) return const SizedBox.shrink();

    final skillsList = skills is List ? skills.cast<String>() : <String>[];
    if (skillsList.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(left: 16, top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$category (${skillsList.length})',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 4),
          Wrap(
            spacing: 4,
            runSpacing: 4,
            children: skillsList
                .take(10)
                .map((skill) => Chip(
                      label: Text(
                        skill,
                        style: const TextStyle(fontSize: 12),
                      ),
                      backgroundColor: Colors.purple.withOpacity(0.1),
                      labelStyle: const TextStyle(color: Colors.purple),
                    ))
                .toList(),
          ),
          if (skillsList.length > 10) ...[
            const SizedBox(height: 4),
            Text(
              '... and ${skillsList.length - 10} more',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMatchAnalysis(dynamic matchData) {
    if (matchData == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Match Analysis',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue.withOpacity(0.3)),
          ),
          child: Text(
            matchData.toString(),
            style: const TextStyle(fontSize: 14),
          ),
        ),
      ],
    );
  }

  Widget _buildATSScore(dynamic atsData) {
    if (atsData == null) return const SizedBox.shrink();

    double score = 0.0;
    String category = 'Unknown';

    if (atsData is Map<String, dynamic>) {
      score = (atsData['overall_ats_score'] ?? 0.0).toDouble();
      category = atsData['score_category'] ?? 'Unknown';
    } else if (atsData is num) {
      score = atsData.toDouble();
      category = _getScoreCategory(score);
    }

    Color scoreColor = _getScoreColor(score);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'ATS Score',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.orange,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: scoreColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: scoreColor.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Text(
                '${score.toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: scoreColor,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                category,
                style: TextStyle(
                  fontSize: 14,
                  color: scoreColor,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendations(dynamic recommendations) {
    if (recommendations == null) return const SizedBox.shrink();

    String recommendationsText = '';
    if (recommendations is String) {
      recommendationsText = recommendations;
    } else if (recommendations is List) {
      recommendationsText = recommendations.join('\n\n');
    } else if (recommendations is Map<String, dynamic>) {
      recommendationsText = recommendations.toString();
    }

    if (recommendationsText.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recommendations',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.green.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.green.withOpacity(0.3)),
          ),
          child: SelectableText(
            recommendationsText,
            style: const TextStyle(fontSize: 14),
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  String _getScoreCategory(double score) {
    if (score >= 90) return 'Excellent Match';
    if (score >= 80) return 'Good Match';
    if (score >= 70) return 'Fair Match';
    if (score >= 60) return 'Below Average';
    return 'Poor Match';
  }
}
