import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';
import 'analyze_match_widget.dart';
import 'skills_analysis/ai_powered_skills_analysis.dart';
import 'ats_score_display_card.dart';
import 'ai_recommendation_display_card.dart';
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
        // ✅ CRITICAL: These logs MUST appear in Chrome DevTools
        // If you don't see these, check console filter settings!
        print('🔄 [WIDGET] ===== SKILLS_DISPLAY REBUILD =====');
        print('   controller.hasError: ${controller.hasError}');
        print('   controller.hasResults: ${controller.hasResults}');
        print('   controller.isLoading: ${controller.isLoading}');
        print('   controller.state: ${controller.state}');
        print('   showATSResults: ${controller.showATSResults}');
        print('   showATSLoading: ${controller.showATSLoading}');
        print('   hasATSResult: ${controller.hasATSResult}');
        
        // ✅ UNMISSABLE LOG - This should ALWAYS appear
        debugPrint('🚨🚨🚨 SKILLS_DISPLAY_WIDGET BUILD METHOD EXECUTED 🚨🚨🚨');
        debugPrint('🚨🚨🚨 If you see this, the widget IS building 🚨🚨🚨');

        // Main content based on state
        if (controller.hasError) {
          print('🔍 [SKILLS_DISPLAY] Building error state');
          return _buildErrorState();
        } else if (controller.isCancelled) {
          print('🔍 [SKILLS_DISPLAY] Building cancelled state');
          return _buildCancelledState();
        } else if (!controller.hasResults && !controller.isLoading) {
          print(
            '🔍 [SKILLS_DISPLAY] Building empty state (no results, not loading)',
          );
          return const SizedBox.shrink(); // Remove placeholder - show nothing
        } else {
          print('🔍 [SKILLS_DISPLAY] Building results content');
          print('   ✅ About to call _buildResultsContent()');
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
    // ✅ CRITICAL: This log MUST appear if method is called
    // ✅ UNMISSABLE - If you don't see this, the method is NOT being called!
    debugPrint('🚨🚨🚨 [WIDGET] _buildResultsContent CALLED! 🚨🚨🚨');
    debugPrint('🚨🚨🚨 IF YOU SEE THIS, _buildResultsContent() IS EXECUTING! 🚨🚨🚨');
    print('🚨🚨🚨 [WIDGET] _buildResultsContent CALLED! 🚨🚨🚨');
    print('🏗️ [WIDGET] _buildResultsContent called');
    print('   controller.hasResults: ${controller.hasResults}');
    print('   controller.isLoading: ${controller.isLoading}');
    print('   controller.result: ${controller.result != null}');
    print('   controller.showATSResults: ${controller.showATSResults}');
    print('   controller.showATSLoading: ${controller.showATSLoading}');
    print('   controller.hasATSResult: ${controller.hasATSResult}');
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
          // ✅ CRITICAL: Verify Column children list is being built
          Builder(
            builder: (context) {
              print('🏗️ [WIDGET] Column children list is being built');
              print('   Total children will be evaluated now');
              return const SizedBox.shrink();
            },
          ),
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

          // Enhanced ATS Score Widget - Show with progressive loading
          // ✅ CRITICAL: Diagnostic logging - this should ALWAYS execute
          Builder(
            builder: (context) {
              final showATS =
                  controller.showATSLoading || controller.showATSResults;
              
              // ✅ UNMISSABLE LOGS - These MUST appear in console
              debugPrint('🚨🚨🚨 [ATS_DIAGNOSTIC] ===== ATS CONDITION CHECK ===== 🚨🚨🚨');
              debugPrint('🚨🚨🚨 THIS BUILDER IS EXECUTING - CHECK CONSOLE FILTER! 🚨🚨🚨');
              print('🚨🚨🚨 [ATS_DIAGNOSTIC] ===== ATS CONDITION CHECK ===== 🚨🚨🚨');
              print('   showATSLoading: ${controller.showATSLoading}');
              print('   showATSResults: ${controller.showATSResults}');
              print(
                  '   Condition (showATSLoading || showATSResults): $showATS');
              print('   hasATSResult: ${controller.hasATSResult}');
              print('   atsResult != null: ${controller.atsResult != null}');
              if (controller.atsResult != null) {
                print(
                    '   ✅ atsResult.finalATSScore: ${controller.atsResult!.finalATSScore}');
              }
              print('🚨🚨🚨 [ATS_DIAGNOSTIC] ===== END CHECK ===== 🚨🚨🚨');
              
              // Also use debugPrint for redundancy
              debugPrint('   [ATS_DIAGNOSTIC] showATSLoading: ${controller.showATSLoading}');
              debugPrint('   [ATS_DIAGNOSTIC] showATSResults: ${controller.showATSResults}');
              debugPrint('   [ATS_DIAGNOSTIC] hasATSResult: ${controller.hasATSResult}');
              
              return const SizedBox.shrink();
            },
          ),
          // ✅ ATS Section - This should render if condition is true
          if (controller.showATSLoading || controller.showATSResults) ...[
            Builder(
              builder: (context) {
                print(
                    '🚨 [ATS_DIAGNOSTIC] ATS SECTION CONDITION IS TRUE - ENTERING SECTION');
                return const SizedBox.shrink();
              },
            ),
            Builder(
              builder: (context) {
                // ✅ CRITICAL: This log should appear if ATS section is in widget tree
                print(
                    '🚨🚨🚨 [ATS_SECTION] ATS SECTION BUILDER CALLED! 🚨🚨🚨');
                print('🎨 [ATS_SECTION] Building ATS section');
                print('   showATSLoading: ${controller.showATSLoading}');
                print('   showATSResults: ${controller.showATSResults}');
                print('   hasATSResult: ${controller.hasATSResult}');
                print('   atsResult != null: ${controller.atsResult != null}');

                if (controller.atsResult != null) {
                  print('   ✅ [ATS_DEBUG] ATS_RESULT EXISTS IN CONTROLLER!');
                  print(
                      '   finalATSScore: ${controller.atsResult!.finalATSScore}');
                  print(
                      '   categoryStatus: ${controller.atsResult!.categoryStatus}');
                  print(
                      '   breakdown baseScore: ${controller.atsResult!.breakdown.baseScore}');
                  print(
                      '   breakdown bonusPoints: ${controller.atsResult!.breakdown.bonusPoints}');
                  print(
                      '   breakdown boostApplied: ${controller.atsResult!.breakdown.boostApplied}');
                } else {
                  print('   ❌ [ATS_DEBUG] ATS_RESULT IS NULL IN CONTROLLER!');
                }

                // Show loading state
                if (controller.showATSLoading && !controller.showATSResults) {
                  print('   → Rendering loading state');
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                    child: const ATSScoreDisplayCard(isLoading: true),
                  );
                }

                // Show actual ATS results
                if (controller.showATSResults && controller.hasATSResult) {
                  print(
                      '   ✅ Rendering ATS card with score: ${controller.atsResult?.finalATSScore}');
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                    child: ATSScoreDisplayCard(
                      atsResult: controller.atsResult,
                      isLoading: false,
                    ),
                  );
                }

                print('   ❌ Neither loading nor results - returning empty');
                print('      showATSResults: ${controller.showATSResults}');
                print('      hasATSResult: ${controller.hasATSResult}');
                print('      atsResult: ${controller.atsResult != null}');
                return const SizedBox.shrink();
              },
            ),
          ] else ...[
            Builder(
              builder: (context) {
                print('🔍 [ATS_DEBUG] ATS SECTION NOT IN BUILD TREE');
                print('   showATSLoading: ${controller.showATSLoading}');
                print('   showATSResults: ${controller.showATSResults}');
                print(
                    '   Condition (showATSLoading || showATSResults): ${controller.showATSLoading || controller.showATSResults}');
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

          // AI Recommendations - Enhanced with modular widget
          // ✅ CRITICAL: Diagnostic logging - this should ALWAYS execute
          Builder(
            builder: (context) {
              final showAI =
                  controller.showAIRecommendationLoading ||
                  controller.showAIRecommendationResults;
              
              // ✅ UNMISSABLE LOGS - These MUST appear in console
              debugPrint('🚨🚨🚨 [AI_DIAGNOSTIC] ===== AI CONDITION CHECK ===== 🚨🚨🚨');
              debugPrint('🚨🚨🚨 THIS BUILDER IS EXECUTING - CHECK CONSOLE FILTER! 🚨🚨🚨');
              print('🚨🚨🚨 [AI_DIAGNOSTIC] ===== AI CONDITION CHECK ===== 🚨🚨🚨');
              print('   showAIRecommendationLoading: ${controller.showAIRecommendationLoading}');
              print('   showAIRecommendationResults: ${controller.showAIRecommendationResults}');
              print('   Condition (showAIRecommendationLoading || showAIRecommendationResults): $showAI');
              print('   hasAIRecommendation: ${controller.result?.aiRecommendation != null}');
              print('   aiRecommendation != null: ${controller.result?.aiRecommendation != null}');
              if (controller.result?.aiRecommendation != null) {
                print('   ✅ aiRecommendation.content length: ${controller.result!.aiRecommendation!.content.length}');
                print('   ✅ aiRecommendation.hasContent: ${controller.result!.aiRecommendation!.hasContent}');
                print('   ✅ aiRecommendation.isEmpty: ${controller.result!.aiRecommendation!.isEmpty}');
              }
              print('🚨🚨🚨 [AI_DIAGNOSTIC] ===== END CHECK ===== 🚨🚨🚨');
              
              // Also use debugPrint for redundancy
              debugPrint('   [AI_DIAGNOSTIC] showAIRecommendationLoading: ${controller.showAIRecommendationLoading}');
              debugPrint('   [AI_DIAGNOSTIC] showAIRecommendationResults: ${controller.showAIRecommendationResults}');
              debugPrint('   [AI_DIAGNOSTIC] hasAIRecommendation: ${controller.result?.aiRecommendation != null}');
              
              return const SizedBox.shrink();
            },
          ),
          // ✅ AI Recommendations Section - This should render if condition is true
          if (controller.showAIRecommendationLoading ||
              controller.showAIRecommendationResults) ...[
            Builder(
              builder: (context) {
                print('🚨 [AI_DIAGNOSTIC] AI SECTION CONDITION IS TRUE - ENTERING SECTION');
                return const SizedBox.shrink();
              },
            ),
            Builder(
              builder: (context) {
                // ✅ CRITICAL: This log should appear if AI section is in widget tree
                print('🚨🚨🚨 [AI_SECTION] AI SECTION BUILDER CALLED! 🚨🚨🚨');
                print('🎨 [AI_SECTION] Building AI recommendations section');
                print('   showAIRecommendationLoading: ${controller.showAIRecommendationLoading}');
                print('   showAIRecommendationResults: ${controller.showAIRecommendationResults}');
                print('   aiRecommendation != null: ${controller.result?.aiRecommendation != null}');

                if (controller.result?.aiRecommendation != null) {
                  print('   ✅ [AI_DEBUG] AI_RECOMMENDATION EXISTS IN CONTROLLER!');
                  print('   content length: ${controller.result!.aiRecommendation!.content.length}');
                  print('   hasContent: ${controller.result!.aiRecommendation!.hasContent}');
                  print('   isEmpty: ${controller.result!.aiRecommendation!.isEmpty}');
                  print('   generatedAt: ${controller.result!.aiRecommendation!.generatedAt}');
                } else {
                  print('   ❌ [AI_DEBUG] AI_RECOMMENDATION IS NULL IN CONTROLLER!');
                }

                // Show loading state
                if (controller.showAIRecommendationLoading &&
                    !controller.showAIRecommendationResults) {
                  print('   → Rendering loading state');
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                    child: const AIRecommendationDisplayCard(isLoading: true),
                  );
                }

                // Show actual AI recommendations
                if (controller.showAIRecommendationResults &&
                    controller.result?.aiRecommendation != null &&
                    controller.result!.aiRecommendation!.hasContent) {
                  print('   ✅ Rendering AI recommendation card with content length: ${controller.result!.aiRecommendation!.content.length}');
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                    child: AIRecommendationDisplayCard(
                      aiRecommendation: controller.result!.aiRecommendation,
                      isLoading: false,
                    ),
                  );
                }

                print('   ❌ Neither loading nor results - returning empty');
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
