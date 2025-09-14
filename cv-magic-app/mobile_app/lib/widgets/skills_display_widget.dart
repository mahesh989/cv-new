import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';
import 'analyze_match_widget.dart';
import 'skills_analysis/ai_powered_skills_analysis.dart';
import 'ats_score_widget_with_progress_bars.dart';
import '../utils/preextracted_parser.dart';
import 'progressive_analysis/progressive_loading_widget.dart';
import 'progressive_analysis/progressive_analysis_phase.dart';

/// Widget for displaying side-by-side CV and JD skills comparison
class SkillsDisplayWidget extends StatelessWidget {
  final SkillsAnalysisController controller;

  const SkillsDisplayWidget({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        // Main content based on state
        if (controller.hasError) {
          return _buildErrorState();
        } else if (!controller.hasResults && !controller.isLoading) {
          return _buildEmptyState();
        } else {
          return _buildResultsContent();
        }
      },
    );
  }

  Widget _buildErrorState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.error_outline,
            color: Colors.red.shade600,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            'Analysis Failed',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.red.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            controller.errorMessage ?? 'Unknown error occurred',
            style: TextStyle(
              fontSize: 14,
              color: Colors.red.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.analytics_outlined,
            color: Colors.grey.shade600,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            'No Analysis Results',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start analysis to see CV and JD skills comparison',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildResultsContent() {
    // Debug logging
    debugPrint('🔍 [SKILLS_DISPLAY] _buildResultsContent called');
    debugPrint('   controller.hasResults: ${controller.hasResults}');
    debugPrint('   controller.isLoading: ${controller.isLoading}');
    debugPrint('   controller.result: ${controller.result != null}');
    if (controller.result != null) {
      debugPrint(
          '   CV comprehensive analysis length: ${controller.cvComprehensiveAnalysis?.length ?? 0}');
      debugPrint(
          '   JD comprehensive analysis length: ${controller.jdComprehensiveAnalysis?.length ?? 0}');
      debugPrint('   CV total skills: ${controller.cvTotalSkills}');
      debugPrint('   JD total skills: ${controller.jdTotalSkills}');
    }

    // Show loading only if we have no results at all yet
    if (controller.isLoading && controller.result == null) {
      return Container(
        child: MainLoadingWidget(
          message: 'Starting analysis...',
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with execution info - show as soon as any results are available
          if (controller.result != null &&
              (controller.cvTotalSkills > 0 ||
                  controller.jdTotalSkills > 0 ||
                  controller.hasAnalyzeMatch ||
                  controller.result?.hasPreextractedComparison == true))
            _buildResultsHeader(),

          // Progressive loading indicators - show when analysis is still running but we have partial results
          if (controller.isLoading && controller.result != null) ...[
            // Show loading for analyze match phase
            if (controller.progressiveController
                .isPhaseLoading('analyze_match')) ...[
              ProgressiveLoadingWidget(
                message: ProgressiveAnalysisConfig.getPhaseById('analyze_match')
                        ?.loadingMessage ??
                    'Starting recruiter assessment analysis...',
              ),
            ],

            // Show loading for skills comparison phase
            if (controller.progressiveController
                .isPhaseLoading('skills_comparison')) ...[
              ProgressiveLoadingWidget(
                message:
                    ProgressiveAnalysisConfig.getPhaseById('skills_comparison')
                            ?.loadingMessage ??
                        'Generating skills comparison analysis...',
              ),
            ],

            // Show loading for ATS analysis phase
            if (controller.progressiveController
                .isPhaseLoading('ats_analysis')) ...[
              ProgressiveLoadingWidget(
                message: ProgressiveAnalysisConfig.getPhaseById('ats_analysis')
                        ?.loadingMessage ??
                    'Generating ATS score analysis...',
              ),
            ],
          ],

          // Side by side comparison - show as soon as skills data is available
          if (controller.result != null &&
              (controller.cvTotalSkills > 0 ||
                  controller.jdTotalSkills > 0)) ...[
            Builder(
              builder: (context) {
                debugPrint(
                    '🔍 [SKILLS_DISPLAY] Rendering side-by-side comparison');
                debugPrint('   CV Skills: ${controller.cvTotalSkills}');
                debugPrint('   JD Skills: ${controller.jdTotalSkills}');
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // CV Skills Column
                      Expanded(
                        child: _buildSkillsColumn(
                          'CV Skills (${controller.cvTotalSkills})',
                          controller.cvTechnicalSkills,
                          controller.cvSoftSkills,
                          controller.cvDomainKeywords,
                          controller.cvComprehensiveAnalysis,
                          Colors.blue,
                          'cv',
                        ),
                      ),
                      const SizedBox(width: 16),
                      // JD Skills Column
                      Expanded(
                        child: _buildSkillsColumn(
                          'JD Skills (${controller.jdTotalSkills})',
                          controller.jdTechnicalSkills,
                          controller.jdSoftSkills,
                          controller.jdDomainKeywords,
                          controller.jdComprehensiveAnalysis,
                          Colors.green,
                          'jd',
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],

          // Analyze Match Section - Show based on progressive state
          if (controller.showAnalyzeMatch || controller.hasAnalyzeMatch) ...[
            Builder(
              builder: (context) {
                debugPrint(
                    '🔍 [SKILLS_DISPLAY] Rendering AnalyzeMatchWidget (progressive)');
                debugPrint(
                    '   showAnalyzeMatch: ${controller.showAnalyzeMatch}');
                debugPrint('   hasAnalyzeMatch: ${controller.hasAnalyzeMatch}');
                debugPrint('   isLoading: ${controller.isLoading}');
                debugPrint(
                    '   analyzeMatch: ${controller.analyzeMatch != null}');

                // Show loading state if analyze match should show but isn't available yet
                // This happens when showAnalyzeMatch is true but the actual data isn't loaded yet
                final isAnalyzeMatchInProgress =
                    controller.showAnalyzeMatch && !controller.hasAnalyzeMatch;

                return AnalyzeMatchWidget(
                  analyzeMatch: controller.analyzeMatch,
                  isLoading: isAnalyzeMatchInProgress,
                );
              },
            ),
          ],

          // AI-Powered Skills Analysis - Show based on progressive state
          if (controller.showPreextractedComparison ||
              controller.result?.hasPreextractedComparison == true) ...[
            Builder(
              builder: (context) {
                debugPrint(
                    '🔍 [SKILLS_DISPLAY] Rendering AIPoweredSkillsAnalysis');
                debugPrint(
                    '   showPreextractedComparison: ${controller.showPreextractedComparison}');
                debugPrint(
                    '   hasPreextractedComparison: ${controller.result?.hasPreextractedComparison}');
                debugPrint(
                    '   preextractedRawOutput length: ${controller.result?.preextractedRawOutput?.length ?? 0}');

                // Show loading state if comparison should show but isn't available yet
                if (controller.showPreextractedComparison &&
                    controller.result?.hasPreextractedComparison != true) {
                  return ProgressiveLoadingWidget(
                    message: ProgressiveAnalysisConfig.getPhaseById(
                                'skills_comparison')
                            ?.loadingMessage ??
                        'Generating skills comparison analysis...',
                    margin: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                  );
                }

                return Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.green.shade200),
                    ),
                    child: Builder(
                      builder: (context) {
                        // Parse the raw output into structured data for table display
                        final parsedData = PreextractedParser.parse(
                          controller.result!.preextractedRawOutput!,
                        );

                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Use the proper table widget instead of plain text
                            AIPoweredSkillsAnalysis(data: parsedData),

                            // Show company info if available
                            if (controller.result!.preextractedCompanyName !=
                                null) ...[
                              const SizedBox(height: 16),
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade100,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  'Company: ${controller.result!.preextractedCompanyName}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.green.shade700,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ],
                        );
                      },
                    ),
                  ),
                );
              },
            ),
          ],

          // Enhanced ATS Score Widget with Pie Chart and Progress Bars - Show when available
          if (controller.hasATSResult) ...[
            Builder(
              builder: (context) {
                debugPrint(
                    '🔍 [SKILLS_DISPLAY] Rendering ATSScoreWidgetWithProgressBars');
                debugPrint('   hasATSResult: ${controller.hasATSResult}');
                debugPrint('   atsScore: ${controller.atsScore}');

                return ATSScoreWidgetWithProgressBars(
                  controller: controller,
                );
              },
            ),
          ],

          // AI Recommendations - Show when ATS result includes recommendations
          if (controller.hasATSResult &&
              controller.atsResult?.recommendations != null &&
              controller.atsResult!.recommendations.isNotEmpty) ...[
            Builder(
              builder: (context) {
                debugPrint('🔍 [SKILLS_DISPLAY] Rendering AI Recommendations');
                final recommendations = controller.atsResult!.recommendations;
                debugPrint(
                    '   recommendations count: ${recommendations.length}');

                return Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.amber.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.lightbulb_outline,
                              color: Colors.amber.shade700,
                              size: 24,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '💡 AI RECOMMENDATIONS',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.amber.shade700,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Personalized suggestions to improve your ATS score',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.amber.shade600,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Recommendations list
                        ...recommendations
                            .take(8)
                            .map((recommendation) => Padding(
                                  padding: const EdgeInsets.only(bottom: 8),
                                  child: Row(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        margin: const EdgeInsets.only(top: 4),
                                        width: 6,
                                        height: 6,
                                        decoration: BoxDecoration(
                                          color: Colors.amber.shade600,
                                          shape: BoxShape.circle,
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Text(
                                          recommendation,
                                          style: TextStyle(
                                            fontSize: 14,
                                            color: Colors.grey.shade700,
                                            height: 1.4,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ))
                            .toList(),

                        if (recommendations.length > 8) ...[
                          const SizedBox(height: 8),
                          Text(
                            '... and ${recommendations.length - 8} more recommendations available',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.amber.shade600,
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResultsHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade100,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(12),
          topRight: Radius.circular(12),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.analytics,
            color: Colors.blue.shade700,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            'Skills Analysis Results',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
          ),
          const Spacer(),
          if (controller.executionDuration.inSeconds > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.blue.shade200,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${controller.executionDuration.inSeconds}s',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue.shade700,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSkillsColumn(
    String title,
    List<String> technicalSkills,
    List<String> softSkills,
    List<String> domainKeywords,
    String? comprehensiveAnalysis,
    MaterialColor baseColor,
    String type,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: baseColor.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: baseColor.shade200),
          ),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: baseColor.shade700,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 16),

        // Technical Skills
        if (technicalSkills.isNotEmpty) ...[
          _buildSkillSection(
            '🔧 Technical Skills',
            technicalSkills,
            baseColor.shade100,
          ),
          const SizedBox(height: 12),
        ],

        // Soft Skills
        if (softSkills.isNotEmpty) ...[
          _buildSkillSection(
            '🤝 Soft Skills',
            softSkills,
            baseColor.shade200,
          ),
          const SizedBox(height: 12),
        ],

        // Domain Keywords
        if (domainKeywords.isNotEmpty) ...[
          _buildSkillSection(
            '📚 Domain Keywords',
            domainKeywords,
            baseColor.shade300,
          ),
          const SizedBox(height: 12),
        ],

        // Detailed AI analysis hidden from frontend per requirements
        // (comprehensiveAnalysis expandable sections removed)
      ],
    );
  }

  Widget _buildSkillSection(
    String title,
    List<String> skills,
    Color backgroundColor,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$title (${skills.length})',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: Wrap(
            spacing: 6,
            runSpacing: 6,
            children: skills
                .map(
                  (skill) => Chip(
                    label: Text(
                      skill,
                      style: const TextStyle(fontSize: 12),
                    ),
                    backgroundColor: Colors.white,
                    side: BorderSide(color: Colors.grey.shade400),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    visualDensity: VisualDensity.compact,
                  ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }

  // Note: _buildExpandableAnalysis and _buildFormattedText methods removed
  // as detailed AI analysis is now hidden from frontend per requirements
}
