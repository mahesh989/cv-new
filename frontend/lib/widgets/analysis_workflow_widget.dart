import 'package:flutter/material.dart';
import 'analysis_workflow_controller.dart';
import '../widgets/ats/enhanced_ats_result_widget.dart';
import '../widgets/ats/enhanced_ats_score_widget.dart';

class AnalysisWorkflowWidget extends StatelessWidget {
  final AnalysisWorkflowController controller;
  final String cvFilename;
  final String jdText;
  final String currentPrompt;

  const AnalysisWorkflowWidget({
    super.key,
    required this.controller,
    required this.cvFilename,
    required this.jdText,
    required this.currentPrompt,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (context, _) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Main action button
            _buildActionButton(),

            // Progress indicators
            if (controller.isPreliminaryRunning ||
                controller.isAIAnalysisRunning ||
                controller.isSkillComparisonRunning ||
                controller.isEnhancedATSRunning ||
                controller.isAIRecommendationsRunning) ...[
              const SizedBox(height: 16),
              _buildProgressIndicator(),
            ],

            // Progressive results display
            if (controller.preliminaryResults != null) ...[
              const SizedBox(height: 24),
              _buildPreliminaryResults(),
            ],

            if (controller.aiAnalysisResult.isNotEmpty) ...[
              const SizedBox(height: 24),
              _buildAIAnalysisResults(),
            ],

            if (controller.hasSkillComparisonResults) ...[
              const SizedBox(height: 24),
              _buildSkillComparisonResults(),
            ],

            // Enhanced ATS Score Results (4th step)
            if (controller.hasEnhancedATSResults) ...[
              const SizedBox(height: 24),
              _buildEnhancedATSResults(),
            ],

            // AI Recommendations Results (5th step)
            if (controller.hasAIRecommendations) ...[
              const SizedBox(height: 24),
              _buildAIRecommendationsResults(),
            ],
          ],
        );
      },
    );
  }

  Widget _buildActionButton() {
    final isAnyRunning = controller.isPreliminaryRunning ||
        controller.isAIAnalysisRunning ||
        controller.isSkillComparisonRunning;

    return ElevatedButton.icon(
      onPressed: isAnyRunning ? null : () => _executeAnalysis(),
      icon: isAnyRunning
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.auto_awesome_mosaic),
      label: Text(
        isAnyRunning
            ? 'Running Full Analysis...'
            : 'Complete Analysis (5 Steps)',
      ),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16),
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Analysis Progress:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          if (controller.isPreliminaryRunning)
            _buildProgressStep('1. CV & JD Claude Analysis', true),
          if (controller.isAIAnalysisRunning)
            _buildProgressStep(
                '2. AI Match Analysis', !controller.isPreliminaryRunning),
          if (controller.isSkillComparisonRunning)
            _buildProgressStep(
                '3. Skill Comparison', !controller.isAIAnalysisRunning),
          if (controller.isEnhancedATSRunning)
            _buildProgressStep(
                '4. Enhanced ATS Score', !controller.isSkillComparisonRunning),
          if (controller.isAIRecommendationsRunning)
            _buildProgressStep(
                '5. AI Recommendations', !controller.isEnhancedATSRunning),
        ],
      ),
    );
  }

  Widget _buildProgressStep(String label, bool isCompleted) {
    return Row(
      children: [
        Icon(
          isCompleted ? Icons.check_circle : Icons.hourglass_top,
          color: isCompleted ? Colors.green : Colors.blue,
          size: 16,
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            color: isCompleted ? Colors.green : Colors.blue[700]!,
            fontWeight: isCompleted ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }

  Widget _buildPreliminaryResults() {
    final results = controller.preliminaryResults;
    if (results == null) return const SizedBox();

    final cvSkills = results['cv_skills'] ?? {};
    final jdSkills = results['jd_skills'] ?? {};

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50]!,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📊 CV & JD Claude Analysis Results',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.blue[800]!,
            ),
          ),
          const SizedBox(height: 16),

          // Side by side comparison
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // CV Skills
              Expanded(
                child: _buildSkillsColumn('CV Skills', cvSkills, Colors.blue),
              ),
              const SizedBox(width: 16),
              // JD Skills
              Expanded(
                child: _buildSkillsColumn('JD Skills', jdSkills, Colors.green),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSkillsColumn(
      String title, Map<String, dynamic> skills, MaterialColor color) {
    final technical = (skills['technical_skills'] as List<dynamic>?)
            ?.whereType<String>()
            .toList() ??
        [];
    final soft = (skills['soft_skills'] as List<dynamic>?)
            ?.whereType<String>()
            .toList() ??
        [];
    final domain = (skills['domain_keywords'] as List<dynamic>?)
            ?.whereType<String>()
            .toList() ??
        [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color[100],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: color[300]!),
          ),
          child: Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color[800]!,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 12),
        if (technical.isNotEmpty)
          _buildSkillCategory('🔧 Technical Skills', technical),
        if (soft.isNotEmpty) _buildSkillCategory('🤝 Soft Skills', soft),
        if (domain.isNotEmpty)
          _buildSkillCategory('🎯 Domain Keywords', domain),
      ],
    );
  }

  Widget _buildSkillCategory(String title, List<String> skills) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$title (${skills.length})',
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: skills
              .map((skill) => Chip(
                    label: Text(skill, style: const TextStyle(fontSize: 12)),
                    backgroundColor: Colors.grey[100],
                  ))
              .toList(),
        ),
        const SizedBox(height: 12),
      ],
    );
  }

  Widget _buildAIAnalysisResults() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.purple[50]!,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🤖 AI Match Analysis Results',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.purple[800]!,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.purple[200]!),
            ),
            child: SelectableText(
              controller.aiAnalysisResult,
              style: const TextStyle(fontSize: 14, height: 1.6),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSkillComparisonResults() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green[50]!,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🎯 Skill Comparison Results',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.green[800]!,
            ),
          ),
          const SizedBox(height: 16),
          EnhancedATSResultWidget(skillComparison: controller.skillComparison),
        ],
      ),
    );
  }

  Widget _buildEnhancedATSResults() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange[50]!,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🏆 Enhanced ATS Score Results',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.orange[800]!,
            ),
          ),
          const SizedBox(height: 16),
          EnhancedATSScoreWidget(atsResults: controller.enhancedATSResults!),
        ],
      ),
    );
  }

  Widget _buildAIRecommendationsResults() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amber[50]!,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline,
                  color: Colors.amber[700]!, size: 24),
              const SizedBox(width: 8),
              Text(
                '💡 AI Recommendations - CV Tailoring Strategy',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber[700]!,
                ),
              ),
              const Spacer(),
              if (controller.isAIRecommendationsRunning)
                SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor:
                        AlwaysStoppedAnimation<Color>(Colors.amber[700]!),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.amber[50]!,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.amber[200]!),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.auto_awesome,
                        color: Colors.amber[700]!, size: 16),
                    const SizedBox(width: 8),
                    Text(
                      'Claude AI CV Tailoring Recommendations',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Colors.amber[700]!,
                        fontSize: 14,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '${controller.aiRecommendationsResult.length} characters',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.amber[200]!),
                  ),
                  child: SelectableText(
                    controller.aiRecommendationsResult,
                    style: const TextStyle(
                      fontSize: 14,
                      height: 1.6,
                      fontFamily: 'monospace',
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

  Future<void> _executeAnalysis() async {
    try {
      await controller.executeFullAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
        currentPrompt: currentPrompt,
      );
    } catch (e) {
      // Error handling is done in the controller
    }
  }
}
