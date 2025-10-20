import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';
import 'analyze_match_widget.dart';
import 'skills_analysis/ai_powered_skills_analysis.dart';
import 'ats_score_widget_with_progress_bars.dart';
import 'ai_recommendations_widget.dart';
import '../utils/preextracted_parser.dart';

/// Widget for displaying side-by-side CV and JD skills comparison
class SkillsDisplayWidget extends StatelessWidget {
  final SkillsAnalysisController controller;
  final String? cvFilename;
  final String? jobDescription;
  final VoidCallback? onNavigateToCVGeneration;

  const SkillsDisplayWidget({
    super.key,
    required this.controller,
    this.cvFilename,
    this.jobDescription,
    this.onNavigateToCVGeneration,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        debugPrint('🔍 [SKILLS_DISPLAY] AnimatedBuilder rebuild triggered');
        debugPrint('   controller.hasError: ${controller.hasError}');
        debugPrint('   controller.hasResults: ${controller.hasResults}');
        debugPrint('   controller.isLoading: ${controller.isLoading}');
        debugPrint('   controller.state: ${controller.state}');

        // Main content based on state
        if (controller.hasError) {
          debugPrint('🔍 [SKILLS_DISPLAY] Building error state');
          return _buildErrorState();
        } else if (controller.isCancelled) {
          debugPrint('🔍 [SKILLS_DISPLAY] Building cancelled state');
          return _buildCancelledState();
        } else if (!controller.hasResults && !controller.isLoading) {
          debugPrint(
            '🔍 [SKILLS_DISPLAY] Building empty state (no results, not loading)',
          );
          return const SizedBox.shrink(); // Remove placeholder - show nothing
        } else {
          debugPrint('🔍 [SKILLS_DISPLAY] Building results content');
          return _buildResultsContent();
        }
      },
    );
  }

  Widget _buildErrorState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade600, size: 48),
          const SizedBox(height: 12),
          Text(
            'Analysis Failed',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.red.shade700,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            controller.errorMessage ?? 'Unknown error occurred',
            style: TextStyle(fontSize: 14, color: Colors.red.shade600),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildCancelledState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Icon(Icons.stop_circle_outlined,
              color: Colors.orange.shade600, size: 48),
          const SizedBox(height: 12),
          Text(
            'Analysis Cancelled',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.orange.shade700,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'The analysis was stopped by the user. Click "Restart Analysis" to begin again.',
            style: TextStyle(fontSize: 14, color: Colors.orange.shade600),
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
        '   CV comprehensive analysis length: ${controller.cvComprehensiveAnalysis?.length ?? 0}',
      );
      debugPrint(
        '   JD comprehensive analysis length: ${controller.jdComprehensiveAnalysis?.length ?? 0}',
      );
      debugPrint('   CV total skills: ${controller.cvTotalSkills}');
      debugPrint('   JD total skills: ${controller.jdTotalSkills}');
    }

    // Show nothing when loading with no results - remove loading placeholder
    if (controller.isLoading && controller.result == null) {
      return const SizedBox.shrink();
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
          // Inline minimal CV warning with actionable suggestions
          if (controller.result?.warnings != null &&
              (controller.result!.warnings!.any(
                (w) =>
                    (w is Map && (w['type'] == 'cv_minimal')) ||
                    (w is String && w.contains('cv_minimal')),
              )))
            Padding(
              padding: const EdgeInsets.all(16),
              child: _buildCvMinimalSuggestions(),
            ),
          // Header with execution info - show as soon as any results are available
          if (controller.result != null &&
              (controller.cvTotalSkills > 0 ||
                  controller.jdTotalSkills > 0 ||
                  controller.hasAnalyzeMatch ||
                  controller.result?.hasPreextractedComparison == true))
            _buildResultsHeader(),

          // Progressive loading indicator - show when analysis is still running but we have partial results
          if (controller.isLoading && controller.result != null) ...[
            Padding(
              padding: const EdgeInsets.all(16),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          Colors.orange.shade600,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'Analysis continuing... More results will appear below',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.orange.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],

          // Side by side comparison - show as soon as skills data is available
          if (controller.result != null &&
              (controller.cvTotalSkills > 0 ||
                  controller.jdTotalSkills > 0)) ...[
            Builder(
              builder: (context) {
                debugPrint(
                  '🔍 [SKILLS_DISPLAY] Rendering side-by-side comparison',
                );
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
                  '🔍 [SKILLS_DISPLAY] Rendering AnalyzeMatchWidget (progressive)',
                );
                debugPrint(
                  '   showAnalyzeMatch: ${controller.showAnalyzeMatch}',
                );
                debugPrint('   hasAnalyzeMatch: ${controller.hasAnalyzeMatch}');
                debugPrint('   isLoading: ${controller.isLoading}');
                debugPrint(
                  '   analyzeMatch: ${controller.analyzeMatch != null}',
                );

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

          // Enhanced ATS Score Widget with Pie Chart and Progress Bars - Show with progressive loading (moved before AI-Powered Skills Analysis)
          if (controller.showATSLoading || controller.showATSResults) ...[
            Builder(
              builder: (context) {
                debugPrint(
                  '🔍 [SKILLS_DISPLAY] Rendering ATS section (progressive)',
                );
                debugPrint('   showATSLoading: ${controller.showATSLoading}');
                debugPrint('   showATSResults: ${controller.showATSResults}');
                debugPrint('   hasATSResult: ${controller.hasATSResult}');

                // Show loading state if ATS should show but results aren't available yet
                if (controller.showATSLoading && !controller.showATSResults) {
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.orange.shade600,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Generating enhanced ATS analysis...',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.orange.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                // Show actual ATS results when available
                if (controller.showATSResults && controller.hasATSResult) {
                  return ATSScoreWidgetWithProgressBars(controller: controller);
                }

                return const SizedBox.shrink();
              },
            ),
          ],

          // AI-Powered Skills Analysis - Show based on progressive state (moved after ATS)
          if (controller.showPreextractedComparison ||
              controller.result?.hasPreextractedComparison == true) ...[
            Builder(
              builder: (context) {
                debugPrint(
                  '🔍 [SKILLS_DISPLAY] Rendering AIPoweredSkillsAnalysis',
                );
                debugPrint(
                  '   showPreextractedComparison: ${controller.showPreextractedComparison}',
                );
                debugPrint(
                  '   hasPreextractedComparison: ${controller.result?.hasPreextractedComparison}',
                );
                debugPrint(
                  '   preextractedRawOutput length: ${controller.result?.preextractedRawOutput?.length ?? 0}',
                );

                // Show loading state if comparison should show but isn't available yet
                if (controller.showPreextractedComparison &&
                    controller.result?.hasPreextractedComparison != true) {
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.orange.shade600,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Generating skills comparison analysis...',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.orange.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
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

          // AI Recommendations - Strict rendering (no fallback)
          if (controller.showAIRecommendationLoading ||
              controller.showAIRecommendationResults) ...[
            Builder(
              builder: (context) {
                debugPrint(
                    '🔍 [SKILLS_DISPLAY] ===== AI RECOMMENDATIONS SECTION =====');
                debugPrint(
                    '   showAIRecommendationLoading: ${controller.showAIRecommendationLoading}');
                debugPrint(
                    '   showAIRecommendationResults: ${controller.showAIRecommendationResults}');
                debugPrint(
                    '   hasAIRecommendation: ${controller.result?.aiRecommendation != null}');
                debugPrint(
                    '   AI Recommendation content length: ${controller.result?.aiRecommendation?.content.length ?? 0}');
                debugPrint(
                    '   AI Recommendation isEmpty: ${controller.result?.aiRecommendation?.isEmpty ?? true}');

                if (controller.showAIRecommendationLoading) {
                  debugPrint('🎯 [SKILLS_DISPLAY] Showing AI loading state');
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Center(
                      child: Column(
                        children: [
                          const CircularProgressIndicator(),
                          const SizedBox(height: 8),
                          Text(
                            'Loading AI recommendations...',
                            style: TextStyle(
                                color: Colors.grey[600], fontSize: 14),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                if (controller.showAIRecommendationResults) {
                  final ai = controller.result?.aiRecommendation;
                  if (ai == null) {
                    debugPrint(
                        '❌ [SKILLS_DISPLAY] AI recommendation is null but results flag is true');
                    // Error state when controller says results should show but model missing
                    return Padding(
                      padding: const EdgeInsets.all(16),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.error_outline,
                                color: Colors.red.shade700),
                            const SizedBox(width: 12),
                            const Expanded(
                              child: Text(
                                'AI recommendation file not found. Please run analysis again.',
                                style: TextStyle(fontSize: 14),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }

                  // ignore: avoid_print
                  print(
                      '🎨 [AI_WIDGET] Building with isLoading: false, hasRecommendation: true, isEmpty: ${ai.isEmpty}');
                  debugPrint(
                      '✅ [SKILLS_DISPLAY] Building AIRecommendationsWidget with content length: ${ai.content.length}');
                  return AIRecommendationsWidget(
                    aiRecommendation: ai,
                    isLoading: false,
                    onGenerateCV: onNavigateToCVGeneration,
                  );
                }

                debugPrint(
                    '❌ [SKILLS_DISPLAY] No AI state matched - returning empty');
                return const SizedBox.shrink();
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCvMinimalSuggestions() {
    try {
      final suggestions = controller.result?.suggestions?['cv_enrichment']
              as Map<String, dynamic>? ??
          {};
      final addTech = List<String>.from(suggestions['add_technical'] ?? []);
      final addEvidence = List<String>.from(suggestions['add_evidence'] ?? []);
      final addDomain = List<String>.from(suggestions['add_domain'] ?? []);

      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFFFFF8E1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFFFFECB3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(
                  Icons.warning_amber_rounded,
                  color: Color(0xFFFFA000),
                  size: 20,
                ),
                SizedBox(width: 8),
                Text(
                  'Your CV looks minimal — suggestions to enrich it',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
              ],
            ),
            if (addTech.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Add technical focus:',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: addTech.map((s) => Chip(label: Text(s))).toList(),
              ),
            ],
            if (addEvidence.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Strengthen evidence:',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              ...addEvidence.map((e) => Text('• $e')).toList(),
            ],
            if (addDomain.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Add domain terms:',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: addDomain.map((s) => Chip(label: Text(s))).toList(),
              ),
            ],
          ],
        ),
      );
    } catch (_) {
      return const SizedBox.shrink();
    }
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
          Icon(Icons.analytics, color: Colors.blue.shade700, size: 20),
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
          _buildSkillSection('🤝 Soft Skills', softSkills, baseColor.shade200),
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
    // Create a sorted copy for display to avoid mutating source lists
    final List<String> sortedSkills = List<String>.from(skills)
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

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
            children: sortedSkills
                .map(
                  (skill) => Chip(
                    label: Text(skill, style: const TextStyle(fontSize: 12)),
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
