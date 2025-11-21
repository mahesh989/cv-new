///
/// Organized CV Magic Page
///
/// This page uses modular components for better code organization:
/// - CVUploadModule for file uploads
/// - CVSelectionModule for CV selection
/// - CVPreviewModule for CV preview
///

import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:async';
import '../modules/cv/cv_upload_module.dart';
import '../modules/cv/cv_selection_module.dart';
import '../modules/cv/cv_preview_module.dart';
import '../widgets/job_input.dart';
import '../services/api_service.dart';
import '../controllers/context_aware_analysis_controller.dart';
import '../widgets/skills_comparison_card.dart';
import '../widgets/analyze_match_card.dart';
import '../widgets/preextracted_skills_comparison_card.dart';
import '../utils/preextracted_parser.dart';
import '../widgets/ats_score_display_card.dart';
import '../widgets/ai_recommendation_display_card.dart';
class CVMagicOrganizedPage extends StatefulWidget {
  final VoidCallback? onNavigateToCVGeneration;
  final bool Function()? shouldClearResults;
  final VoidCallback? onResultsCleared;

  const CVMagicOrganizedPage({
    super.key,
    this.onNavigateToCVGeneration,
    this.shouldClearResults,
    this.onResultsCleared,
  });

  @override
  State<CVMagicOrganizedPage> createState() => _CVMagicOrganizedPageState();
}

class _CVMagicOrganizedPageState extends State<CVMagicOrganizedPage>
    with AutomaticKeepAliveClientMixin {
  // State variables
  String? selectedCVFilename;
  bool isLoading = false;
  int cvRefreshToken = 0;
  // Removed company selection used for JDAnalysisWidget (backend-only focus)

  // Job description controllers
  final TextEditingController jdController = TextEditingController();
  final TextEditingController jdUrlController = TextEditingController();

  // Job metadata from "Analyze & Save Job"
  String? savedCompanyName;
  String? savedCompanySlug;
  String? savedJobTitle;

  // Context-aware analysis controller (supports analyze match pause)
  late final ContextAwareAnalysisController _skillsController;

  // Timer for checking clear flag
  Timer? _clearCheckTimer;

  @override
  void initState() {
    super.initState();
    _skillsController = ContextAwareAnalysisController();

    // Set notification callback for real-time progress updates
    _skillsController.setNotificationCallback(_showSnackBar);

    // Note: ResultsClearingService registration removed since ContextAwareAnalysisController
    // has direct access to clearResults() method

    // Start periodic timer to check if we need to clear results
    _clearCheckTimer =
        Timer.periodic(const Duration(milliseconds: 500), (timer) {
      if (mounted) {
        _checkAndClearResults();
      }
    });

    // Add listener to jdController to debug changes and trigger rebuilds
    jdController.addListener(() {
      print(
          '🔍 [DEBUG] CV Magic: jdController changed - length: ${jdController.text.length}');

      // Force a rebuild of the widget to update button state
      if (mounted) {
        setState(() {
          // This rebuild will update the AnimatedBuilder and button state
        });
      }
    });

    // Clear saved company info when JD URL changes (user working on different job)
    jdUrlController.addListener(() {
      if (mounted && savedCompanySlug != null) {
        setState(() {
          savedCompanyName = null;
          savedCompanySlug = null;
          savedJobTitle = null;
        });
        print('🧹 Cleared saved company (URL changed)');
      }
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Check if results need to be cleared when dependencies change
    _checkAndClearResults();
  }

  /// Check if we need to clear results and do so if needed
  void _checkAndClearResults() {
    final shouldClear = widget.shouldClearResults?.call();

    if (shouldClear == true) {
      debugPrint('🧹 [CV_MAGIC] Clearing results due to Run ATS Again');
      clearAnalysisResults();
      widget.onResultsCleared?.call();
      debugPrint('🧹 [CV_MAGIC] Results cleared successfully');
    }
    // No logging when shouldClear is false to avoid console spam
  }

  /// Public method to trigger clear check when needed (called from parent)
  void triggerClearCheck() {
    if (mounted) {
      _checkAndClearResults();
    }
  }

  @override
  void dispose() {
    _clearCheckTimer?.cancel();
    // Note: ResultsClearingService unregistration removed
    _skillsController.dispose();
    jdController.dispose();
    jdUrlController.dispose();
    super.dispose();
  }

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin

    // Remove the continuous check from build method to prevent infinite loops

    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic - Organized'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        actions: [
          // Clear All button - show when CV is selected or there are results
          if (selectedCVFilename != null ||
              _skillsController.hasResults ||
              _skillsController.hasError)
            Container(
              margin: const EdgeInsets.only(right: 8),
              child: IconButton(
                onPressed: () {
                  _showClearConfirmationDialog();
                },
                icon: const Icon(Icons.clear),
                tooltip: 'Clear All Results',
                style: IconButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  shape: const CircleBorder(),
                  padding: const EdgeInsets.all(8),
                ),
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // CV Upload Module
            CVUploadModule(
              onFilePicked: _onFilePicked,
              isLoading: isLoading,
            ),
            const SizedBox(height: 16),

            // CV Selection Module
            CVSelectionModule(
              selectedCVFilename: selectedCVFilename,
              onCVSelected: _onCVSelected,
              refreshToken: cvRefreshToken,
            ),
            const SizedBox(height: 16),

            // CV Preview Module
            CVPreviewModule(
              selectedCVFilename: selectedCVFilename,
            ),
            const SizedBox(height: 16),

            // CV Context Display (shows which CV is being used for analysis)
            if (selectedCVFilename != null) _buildCVContextCard(),
            if (selectedCVFilename != null) const SizedBox(height: 16),

            // Job Description Input
            JobInput(
              jdController: jdController,
              jdUrlController: jdUrlController,
              onExtract:
                  () {}, // Not used anymore, analysis is handled in JobInput widget
              onJobSaved: (jobData) {
                setState(() {
                  savedCompanyName = jobData['company_name'];
                  savedCompanySlug = jobData['company_slug'];
                  savedJobTitle = jobData['job_title'];
                });
                print('✅ Saved: $savedCompanySlug ($savedCompanyName)');
              },
            ),
            const SizedBox(height: 16),

            // Skills Comparison Card (shown BEFORE analyze match decision)
            // Simple side-by-side display of CV vs JD skills from initial analysis
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                // Debug logging
                debugPrint('🔍 [SKILLS_CARD] AnimatedBuilder called');
                debugPrint('   hasInitialResults: ${_skillsController.hasInitialResults}');
                debugPrint('   initialResult != null: ${_skillsController.initialResult != null}');
                debugPrint('   initialResult?.results != null: ${_skillsController.initialResult?.results != null}');
                
                // Show skills comparison if we have initial analysis results
                if (_skillsController.hasInitialResults && 
                    _skillsController.initialResult?.results != null) {
                  debugPrint('✅ [SKILLS_CARD] Showing SkillsComparisonCard');
                  final results = _skillsController.initialResult!.results!;
                  debugPrint('   cvSkills: ${results.cvSkills}');
                  debugPrint('   jdSkills: ${results.jdSkills}');
                  
                  return Column(
                    children: [
                      SkillsComparisonCard(
                        cvSkills: results.cvSkills,
                        jdSkills: results.jdSkills,
                      ),
                      const SizedBox(height: 16),
                    ],
                  );
                }
                debugPrint('❌ [SKILLS_CARD] Not showing (conditions not met)');
                return const SizedBox.shrink();
              },
            ),

            // Analyze Match Decision Widget (appears after initial analysis)
            // Stays visible after user makes decision, only buttons change
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                // Show if we have analyze match decision from initial analysis
                final hasDecision = _skillsController.hasAnalyzeMatchDecision;
                if (!hasDecision) return const SizedBox.shrink();

                return Column(
                  children: [
                    _buildAnalyzeMatchDecisionCard(),
                    const SizedBox(height: 16),
                  ],
                );
              },
            ),

            // Analyze Match Card (shown AFTER user clicks Proceed when data is ready)
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                debugPrint('🔍 [ANALYZE_MATCH_CARD] AnimatedBuilder called');
                debugPrint('   hasAnalyzeMatch: ${_skillsController.hasAnalyzeMatch}');
                debugPrint('   analyzeMatch != null: ${_skillsController.analyzeMatch != null}');
                debugPrint('   showAnalyzeMatch: ${_skillsController.showAnalyzeMatch}');
                debugPrint('   analyzeMatchRawAnalysis != null: ${_skillsController.analyzeMatchRawAnalysis != null}');
                debugPrint('   analyzeMatchRawAnalysis length: ${_skillsController.analyzeMatchRawAnalysis?.length ?? 0}');
                if (_skillsController.analyzeMatch != null) {
                  debugPrint('   analyzeMatch.rawAnalysis length: ${_skillsController.analyzeMatch!.rawAnalysis.length}');
                  debugPrint('   analyzeMatch.isEmpty: ${_skillsController.analyzeMatch!.isEmpty}');
                }
                
                // Show when we have analyze match data
                if (_skillsController.hasAnalyzeMatch &&
                    _skillsController.analyzeMatch != null) {
                  
                  debugPrint('✅ [ANALYZE_MATCH_CARD] Showing AnalyzeMatchCard');
                  
                  // Get full cv_jd_matching data from result
                  final matchData = _skillsController.result?.toJson()['analyze_match'] as Map<String, dynamic>? ?? {};
                  debugPrint('   matchData keys: ${matchData.keys.toList()}');
                  
                  return Column(
                    children: [
                      AnalyzeMatchCard(
                        matchData: matchData,
                        companyName: _skillsController.analyzeMatchCompanyName,
                      ),
                      const SizedBox(height: 16),
                    ],
                  );
                }
                
                // Show loading state if showAnalyzeMatch flag is true but data not ready yet
                if (_skillsController.showAnalyzeMatch && !_skillsController.hasAnalyzeMatch) {
                  debugPrint('⏳ [ANALYZE_MATCH_CARD] Showing loading state');
                  return Column(
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Row(
                            children: [
                              const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Generating analyze match results...',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                  );
                }
                
                debugPrint('❌ [ANALYZE_MATCH_CARD] Not showing (conditions not met)');
                return const SizedBox.shrink();
              },
            ),

            // Pre-extracted Skills Comparison (AI-Powered Summary Table)
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                debugPrint('🔍 [PREEXTRACTED_COMPARISON] AnimatedBuilder called');
                final result = _skillsController.result;
                debugPrint('   result != null: ${result != null}');
                debugPrint('   hasPreextractedComparison: ${result?.hasPreextractedComparison ?? false}');
                debugPrint('   preextractedRawOutput != null: ${result?.preextractedRawOutput != null}');
                if (result?.preextractedRawOutput != null) {
                  debugPrint('   preextractedRawOutput length: ${result!.preextractedRawOutput!.length}');
                }
                
                // Show when we have preextracted comparison data
                if (result != null && result.hasPreextractedComparison) {
                  debugPrint('✅ [PREEXTRACTED_COMPARISON] Showing PreextractedSkillsComparisonCard');
                  
                  try {
                    // Parse the raw text output into structured data
                    final parsedData = PreextractedParser.parse(result.preextractedRawOutput!);
                    debugPrint('   Parsed categories: ${parsedData.categories.length}');
                    debugPrint('   Overall match rate: ${parsedData.overall.matchRatePercent}%');
                    
                    return Column(
                      children: [
                        PreextractedSkillsComparisonCard(
                          data: parsedData,
                          companyName: _skillsController.currentCompany,
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  } catch (e) {
                    debugPrint('❌ [PREEXTRACTED_COMPARISON] Parse error: $e');
                    return Column(
                      children: [
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Text(
                              'Error parsing skills comparison: $e',
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                }
                
                debugPrint('❌ [PREEXTRACTED_COMPARISON] Not showing (no data)');
                return const SizedBox.shrink();
              },
            ),

            // ATS Score Display
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                debugPrint('🔍 [ATS_SECTION] AnimatedBuilder called');
                final showATSLoading = _skillsController.showATSLoading;
                final showATSResults = _skillsController.showATSResults;
                final hasATSResult = _skillsController.hasATSResult;
                final atsResult = _skillsController.atsResult;
                
                debugPrint('   showATSLoading: $showATSLoading');
                debugPrint('   showATSResults: $showATSResults');
                debugPrint('   hasATSResult: $hasATSResult');
                debugPrint('   atsResult != null: ${atsResult != null}');
                
                if (atsResult != null) {
                  debugPrint('   ✅ ATS Score: ${atsResult.finalATSScore}');
                  debugPrint('   ✅ Category Status: ${atsResult.categoryStatus}');
                }
                
                // Show ATS section if loading or results are available
                if (showATSLoading || showATSResults) {
                  debugPrint('✅ [ATS_SECTION] Showing ATS section');
                  
                  // Show loading state
                  if (showATSLoading && !showATSResults) {
                    debugPrint('   → Rendering ATS loading state');
                    return Column(
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                          child: const ATSScoreDisplayCard(isLoading: true),
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                  
                  // Show actual ATS results
                  if (showATSResults && hasATSResult && atsResult != null) {
                    debugPrint('   ✅ Rendering ATS card with score: ${atsResult.finalATSScore}');
                    return Column(
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                          child: ATSScoreDisplayCard(
                            atsResult: atsResult,
                            isLoading: false,
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                }
                
                debugPrint('❌ [ATS_SECTION] Not showing (no data or conditions not met)');
                return const SizedBox.shrink();
              },
            ),

            // AI Recommendations Display
            AnimatedBuilder(
              animation: _skillsController,
              builder: (context, _) {
                debugPrint('🔍 [AI_SECTION] AnimatedBuilder called');
                final showAILoading = _skillsController.showAIRecommendationLoading;
                final showAIResults = _skillsController.showAIRecommendationResults;
                final aiRecommendation = _skillsController.aiRecommendation;
                
                debugPrint('   showAIRecommendationLoading: $showAILoading');
                debugPrint('   showAIRecommendationResults: $showAIResults');
                debugPrint('   aiRecommendation != null: ${aiRecommendation != null}');
                
                if (aiRecommendation != null) {
                  debugPrint('   ✅ AI Recommendation content length: ${aiRecommendation.content.length}');
                  debugPrint('   ✅ hasContent: ${aiRecommendation.hasContent}');
                  debugPrint('   ✅ isEmpty: ${aiRecommendation.isEmpty}');
                }
                
                // Show AI section if loading or results are available
                if (showAILoading || showAIResults) {
                  debugPrint('✅ [AI_SECTION] Showing AI recommendations section');
                  
                  // Show loading state
                  if (showAILoading && !showAIResults) {
                    debugPrint('   → Rendering AI loading state');
                    return Column(
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                          child: const AIRecommendationDisplayCard(isLoading: true),
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                  
                  // Show actual AI recommendations
                  if (showAIResults && aiRecommendation != null && aiRecommendation.hasContent) {
                    debugPrint('   ✅ Rendering AI recommendation card with content length: ${aiRecommendation.content.length}');
                    return Column(
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
                          child: AIRecommendationDisplayCard(
                            aiRecommendation: aiRecommendation,
                            isLoading: false,
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                }
                
                debugPrint('❌ [AI_SECTION] Not showing (no data or conditions not met)');
                return const SizedBox.shrink();
              },
            ),

            // Skills Analysis Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.psychology_outlined,
                          color: Colors.purple,
                          size: 24,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Skills Analysis',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.purple,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Compare your CV skills against job requirements',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: AnimatedBuilder(
                        animation:
                            Listenable.merge([_skillsController, jdController]),
                        builder: (context, _) {
                          final canAnalyze = selectedCVFilename != null &&
                              jdController.text.trim().isNotEmpty;
                          final isAnalyzing = _skillsController.isLoading;
                          final isCancelled = _skillsController.isCancelled;

                          // Comprehensive debug logging
                          print('=== BUTTON STATE CHECK ===');
                          print(
                              '🔍 [DEBUG] Button state - canAnalyze: $canAnalyze, isAnalyzing: $isAnalyzing');
                          print(
                              '🔍 [DEBUG] selectedCVFilename: $selectedCVFilename');
                          print(
                              '🔍 [DEBUG] selectedCVFilename != null: ${selectedCVFilename != null}');
                          print(
                              '🔍 [DEBUG] jdController.text.length: ${jdController.text.length}');
                          print(
                              '🔍 [DEBUG] jdController.text.trim().length: ${jdController.text.trim().length}');
                          print(
                              '🔍 [DEBUG] jdController.text.trim().isEmpty: ${jdController.text.trim().isEmpty}');
                          print(
                              '🔍 [DEBUG] jdController.text.trim().isNotEmpty: ${jdController.text.trim().isNotEmpty}');
                          print(
                              '🔍 [DEBUG] _skillsController.isLoading: ${_skillsController.isLoading}');
                          print('=== END BUTTON CHECK ===');

                          return Row(
                            children: [
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: (canAnalyze && !isAnalyzing)
                                      ? _analyzeSkills
                                      : null,
                                  icon: isAnalyzing
                                      ? const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : isCancelled
                                          ? const Icon(Icons.refresh)
                                          : const Icon(Icons.psychology),
                                  label: Text(isAnalyzing
                                      ? 'Analyzing Skills...'
                                      : isCancelled
                                          ? 'Restart Analysis'
                                          : 'Analyze Skills'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: isCancelled
                                        ? Colors.orange
                                        : canAnalyze
                                            ? Colors.purple
                                            : Colors.grey,
                                    foregroundColor:
                                        canAnalyze ? Colors.white : Colors.grey,
                                    padding: const EdgeInsets.symmetric(
                                        vertical: 12),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                  ),
                                ),
                              ),
                              if (isAnalyzing) ...[
                                const SizedBox(width: 12),
                                ElevatedButton.icon(
                                  onPressed: _cancelAnalysis,
                                  icon: const Icon(Icons.stop, size: 18),
                                  label: const Text('Cancel'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.red,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                        vertical: 12, horizontal: 16),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                  ),
                                ),
                              ],
                              if (isCancelled) ...[
                                const SizedBox(width: 12),
                                ElevatedButton.icon(
                                  onPressed: _resetEverything,
                                  icon: const Icon(Icons.clear_all, size: 18),
                                  label: const Text('Reset'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.grey.shade600,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                        vertical: 12, horizontal: 16),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          );
                        },
                      ),
                    ),
                    if (selectedCVFilename == null ||
                        jdController.text.trim().isEmpty) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.purple.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: Colors.purple.withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.info_outline,
                              color: Colors.purple,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                selectedCVFilename == null
                                    ? 'Please select a CV first'
                                    : 'Please enter a job description first',
                                style: TextStyle(
                                  color: Colors.purple[700],
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            // Skills display moved ABOVE analyze match decision for better UX
            // (See lines 233-249 above)
            // JD Analysis UI section removed for backend-only focus

            // Loading indicator for upload
            if (isLoading)
              const Padding(
                padding: EdgeInsets.only(bottom: 8),
                child: LinearProgressIndicator(),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _onFilePicked(PlatformFile file) async {
    setState(() {
      isLoading = true;
    });

    try {
      // Check if a CV with same name exists and inform user about replacement
      final exists = await APIService.cvExists(file.name);
      if (exists) {
        _showSnackBar('Replacing existing CV: ${file.name}');
      }

      await APIService.uploadCV(file);
      // Increment token to trigger CVSelectionModule reload
      setState(() {
        cvRefreshToken++;
      });
      // Fetch list, but do not auto-select; user will choose the CV
      await APIService.fetchUploadedCVs();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('CV uploaded successfully: ${file.name}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void _onCVSelected(String? filename) {
    print('🔍 [DEBUG] _onCVSelected called with: $filename');
    
    setState(() {
      selectedCVFilename = filename;
    });
    
    // Persist selection by saving original CV artifacts
    if (filename != null && filename.isNotEmpty) {
      print('🔍 [DEBUG] Calling APIService.saveCVForAnalysis for: $filename');
      APIService.saveCVForAnalysis(filename).then((response) {
        print('✅ [DEBUG] API call succeeded. Response: $response');
        _showSnackBar('Saved original CV files for "$filename"');
      }).catchError((e) {
        print('❌ [DEBUG] API call failed: $e');
        print('❌ [DEBUG] Error type: ${e.runtimeType}');
        print('❌ [DEBUG] Error details: ${e.toString()}');
        _showSnackBar('Failed to save original CV: $e', isError: true);
      });
    } else {
      print('⚠️ [DEBUG] filename is null or empty, skipping save');
    }
  }

  /// Analyze skills by comparing CV with Job Description
  Future<void> _analyzeSkills() async {
    print('🔍 [DEBUG] _analyzeSkills called');
    print('🔍 [DEBUG] selectedCVFilename: $selectedCVFilename');
    print('🔍 [DEBUG] jdController.text: "${jdController.text}"');
    print(
        '🔍 [DEBUG] jdController.text.trim().isEmpty: ${jdController.text.trim().isEmpty}');
    print(
        '🔍 [DEBUG] _skillsController.isLoading: ${_skillsController.isLoading}');

    // Prevent multiple simultaneous calls
    if (_skillsController.isLoading) {
      print('⚠️ [DEBUG] Analysis already in progress, ignoring duplicate call');
      return;
    }

    if (selectedCVFilename == null || jdController.text.trim().isEmpty) {
      print('❌ [DEBUG] Cannot analyze - missing CV or JD');
      _showSnackBar('Please select a CV and enter a job description first',
          isError: true);
      return;
    }

    print('✅ [DEBUG] Starting context-aware analysis...');

    // Use saved company info if available (from "Analyze & Save Job")
    final jdUrl = jdUrlController.text.trim();
    String company;

    if (savedCompanySlug?.isNotEmpty ?? false) {
      // Primary: Use saved company from state
      company = savedCompanySlug!;
      print('✅ [PRIMARY] Using saved company: $company');
    } else {
      // Fallback: Extract from URL (backend will correct if needed)
      company = _extractCompanyFromUrl(jdUrl);
      print('⚠️ [FALLBACK] Extracted from URL: $company (backend will lookup)');
    }

    if (jdUrl.isEmpty) {
      _showSnackBar('Please provide a job description URL', isError: true);
      return;
    }

    if (company.isEmpty) {
      _showSnackBar('Could not determine company name', isError: true);
      return;
    }

    try {
      await _skillsController.performContextAwareAnalysis(
        jdUrl: jdUrl,
        company: company,
        isRerun: false, // TODO: Detect if this is a rerun
        includeTailoring: true,
      );

      // Check if waiting for user decision
      if (_skillsController.waitingForUserDecision) {
        print('⏸️ [DEBUG] Waiting for user decision after analyze match');
        return; // Stop here, widget will be shown
      }

      if (_skillsController.hasResults) {
        _showSnackBar('Skills analysis completed successfully!');
      } else if (_skillsController.hasError) {
        _showSnackBar(
            'Skills analysis failed: ${_skillsController.errorMessage}',
            isError: true);
      } else if (_skillsController.isCancelled) {
        _showSnackBar('Analysis was cancelled');
      }
    } catch (e) {
      print('❌ [DEBUG] Error in _analyzeSkills: $e');
      _showSnackBar('Error performing skills analysis: $e', isError: true);
    }
  }

  /// Cancel the current analysis
  void _cancelAnalysis() {
    print('🛑 [DEBUG] _cancelAnalysis called');
    _skillsController.cancelAnalysis();
    _showSnackBar('🛑 Analysis cancelled');
  }

  /// Reset everything - CV, JD, and all analysis results
  void _resetEverything() {
    print('🗑️ [DEBUG] _resetEverything called');

    // First, cancel any ongoing analysis to stop backend processing
    if (_skillsController.isLoading) {
      print('🛑 [DEBUG] Stopping ongoing analysis before reset');
      _skillsController.cancelAnalysis();
    }

    // Clear all state
    setState(() {
      selectedCVFilename = null;
      jdController.clear();
      jdUrlController.clear();
    });

    // Clear analysis results
    _skillsController.clearResults();

    // Show confirmation message
    _showSnackBar('🗑️ Everything has been reset. Ready for a fresh start!');

    print('🗑️ [DEBUG] Everything reset successfully');
  }

  void _showSnackBar(String message, {bool isError = false}) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: isError ? Colors.red : Colors.green,
          duration: Duration(seconds: isError ? 4 : 3),
        ),
      );
    }
  }

  void _navigateToCVGeneration() {
    debugPrint('🚀 CV Magic: Navigate to CV Generation tab requested');

    if (widget.onNavigateToCVGeneration != null) {
      // Use the callback to navigate to CV Generation tab
      widget.onNavigateToCVGeneration!();
      _showSnackBar('🚀 Navigating to CV Generation tab...');
    } else {
      // Fallback message if callback not provided
      _showSnackBar('🚀 Please switch to CV Generation tab manually');
      debugPrint('No navigation callback provided');
    }
  }

  Widget _buildCVContextCard() {
    return Card(
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.description,
                  color: Colors.blue.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'CV Selected for Analysis',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // CV Filename
            _buildContextItem(
              'CV File',
              selectedCVFilename ?? 'Unknown',
              Colors.blue,
            ),

            // Analysis Status
            _buildContextItem(
              'Analysis Status',
              _skillsController.isLoading
                  ? 'Analyzing...'
                  : _skillsController.hasResults
                      ? 'Analysis Complete'
                      : _skillsController.hasError
                          ? 'Analysis Failed'
                          : 'Ready to Analyze',
              _skillsController.isLoading
                  ? Colors.orange
                  : _skillsController.hasResults
                      ? Colors.green
                      : _skillsController.hasError
                          ? Colors.red
                          : Colors.grey,
            ),

            // Execution Duration (if available)
            if (_skillsController.executionDuration.inSeconds > 0)
              _buildContextItem(
                'Analysis Time',
                '${_skillsController.executionDuration.inSeconds}s',
                Colors.grey,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildContextItem(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 14,
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Company selector removed (backend-only focus)

  /// Show confirmation dialog before clearing all results
  void _showClearConfirmationDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Clear All Results'),
          content: const Text(
            'This will clear all analysis results, JD URL, and JD text but keep your selected CV and CV preview. Are you sure?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                clearAnalysisResults();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: const Text('Clear All'),
            ),
          ],
        );
      },
    );
  }

  /// Clear all analysis results and reset the controller
  /// Preserves selected CV and CV preview, but clears JD inputs
  void clearAnalysisResults() {
    debugPrint('🧹 [CV_MAGIC] Clearing analysis results in CV Magic tab');
    debugPrint('🧹 [CV_MAGIC] Preserving selected CV: $selectedCVFilename');
    debugPrint('🧹 [CV_MAGIC] Clearing JD URL: ${jdUrlController.text}');
    debugPrint(
        '🧹 [CV_MAGIC] Clearing JD text length: ${jdController.text.length}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller has results before clear: ${_skillsController.hasResults}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller state before clear: ${_skillsController.state}');

    // Clear the skills analysis results
    _skillsController.clearResults();

    // CLEAR JD inputs as requested
    jdController.clear(); // ✅ Clear the JD text
    jdUrlController.clear(); // ✅ Clear the JD URL

    debugPrint(
        '🧹 [CV_MAGIC] Controller has results after clear: ${_skillsController.hasResults}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller state after clear: ${_skillsController.state}');
    debugPrint('🧹 [CV_MAGIC] Selected CV preserved: $selectedCVFilename');
    debugPrint('🧹 [CV_MAGIC] JD URL cleared: ${jdUrlController.text}');
    debugPrint(
        '🧹 [CV_MAGIC] JD text cleared: ${jdController.text.length} characters');

    // Clear any other state if needed
    setState(() {
      // Reset any local state variables if needed
      debugPrint('🧹 [CV_MAGIC] setState called to refresh UI');
    });

    // Show confirmation message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
            '✅ All analysis results, JD URL, and JD text cleared. CV preview preserved.'),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }

  /// Clear only analysis results while preserving CV, JD URL, and JD text
  /// This is used by "Run ATS Again" button to preserve user inputs
  void clearAnalysisResultsOnly() {
    debugPrint(
        '🧹 [CV_MAGIC] Clearing analysis results only (preserving JD inputs)');
    debugPrint('🧹 [CV_MAGIC] Preserving selected CV: $selectedCVFilename');
    debugPrint('🧹 [CV_MAGIC] Preserving JD URL: ${jdUrlController.text}');
    debugPrint(
        '🧹 [CV_MAGIC] Preserving JD text length: ${jdController.text.length}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller has results before clear: ${_skillsController.hasResults}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller state before clear: ${_skillsController.state}');

    // Clear only the skills analysis results
    _skillsController.clearResults();

    debugPrint(
        '🧹 [CV_MAGIC] Controller has results after clear: ${_skillsController.hasResults}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller state after clear: ${_skillsController.state}');
    debugPrint('🧹 [CV_MAGIC] Selected CV preserved: $selectedCVFilename');
    debugPrint('🧹 [CV_MAGIC] JD URL preserved: ${jdUrlController.text}');
    debugPrint(
        '🧹 [CV_MAGIC] JD text preserved: ${jdController.text.length} characters');

    // Clear any other state if needed
    setState(() {
      // Reset any local state variables if needed
      debugPrint('🧹 [CV_MAGIC] setState called to refresh UI');
    });

    // Show confirmation message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
            '🔄 Analysis results cleared. CV, JD URL, and JD text preserved for fresh analysis.'),
        backgroundColor: Colors.blue,
        duration: Duration(seconds: 3),
      ),
    );
  }

  /// Extract company name from job URL
  String _extractCompanyFromUrl(String url) {
    try {
      final uri = Uri.parse(url);
      final host = uri.host;

      // Basic extraction logic - enhance as needed
      if (host.contains('seek')) {
        final segments = uri.pathSegments;
        if (segments.length > 2) {
          return segments[2].replaceAll('-', '_');
        }
      } else if (host.contains('linkedin')) {
        // LinkedIn company extraction
        final segments = uri.pathSegments;
        if (segments.contains('company')) {
          final companyIndex = segments.indexOf('company') + 1;
          if (companyIndex < segments.length) {
            return segments[companyIndex].replaceAll('-', '_');
          }
        }
      }

      // Fallback: use host as company name
      return host.replaceAll('.', '_').replaceAll('-', '_');
    } catch (e) {
      return 'unknown_company';
    }
  }

  /// Build analyze match decision card
  Widget _buildAnalyzeMatchDecisionCard() {
    final decision = _skillsController.analyzeMatchDecision;

    // If no decision data, show fallback
    if (decision == null) {
      return Card(
        margin: const EdgeInsets.symmetric(vertical: 16.0),
        elevation: 4,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              const Icon(Icons.info_outline, size: 48, color: Colors.orange),
              const SizedBox(height: 16),
              const Text(
                'Initial Analysis Complete',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('Waiting for analyze match decision...'),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        _skillsController.continueFullAnalysis(
                            includeTailoring: true);
                      },
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('Proceed with Full Analysis'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        _skillsController.skipFullAnalysis();
                      },
                      icon: const Icon(Icons.skip_next),
                      label: const Text('Skip Full Analysis'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }

    // Determine colors based on decision
    Color cardColor;
    Color iconColor;
    Color buttonColor;
    IconData icon;
    String title;

    if (decision.isProceed) {
      cardColor = Colors.green.shade50;
      iconColor = Colors.green.shade700;
      buttonColor = Colors.green;
      icon = Icons.check_circle;
      title = 'Strong Match - Proceed Recommended';
    } else if (decision.isMaybe) {
      cardColor = Colors.orange.shade50;
      iconColor = Colors.orange.shade700;
      buttonColor = Colors.orange;
      icon = Icons.warning;
      title = 'Conditional Match - Consider Proceeding';
    } else {
      cardColor = Colors.red.shade50;
      iconColor = Colors.red.shade700;
      buttonColor = Colors.red;
      icon = Icons.cancel;
      title = 'Not Recommended - Consider Skipping';
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 16.0),
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: cardColor,
          border: Border.all(color: iconColor.withOpacity(0.3), width: 2),
        ),
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: iconColor,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: Colors.white, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Analyze Match Decision',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: iconColor,
                        ),
                      ),
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 14,
                          color: iconColor.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Match Score
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: iconColor.withOpacity(0.2)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildScoreItem(
                      'Match Score', '${decision.matchScore}%', iconColor),
                  _buildScoreItem(
                      'Confidence', '${decision.confidence}%', iconColor),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Primary Reason
            if (decision.primaryReason.isNotEmpty) ...[
              Text(
                'Primary Reason:',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade700,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  decision.primaryReason,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade800,
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Critical Missing (if any)
            if (decision.criticalMissing.isNotEmpty) ...[
              Text(
                'Critical Missing Skills:',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.red.shade700,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: decision.criticalMissing.map((skill) {
                  return Chip(
                    label: Text(skill),
                    backgroundColor: Colors.red.shade100,
                    labelStyle:
                        TextStyle(color: Colors.red.shade900, fontSize: 12),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],

            // Action Buttons (conditionally shown based on state)
            if (_skillsController.waitingForUserDecision) ...[
              // Show Proceed/Skip buttons when waiting for decision
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        _skillsController.continueFullAnalysis(
                            includeTailoring: true);
                      },
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('Proceed with Full Analysis'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: buttonColor,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        _skillsController.skipFullAnalysis();
                      },
                      icon: const Icon(Icons.skip_next),
                      label: const Text('Skip Full Analysis'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.grey.shade700,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: BorderSide(color: Colors.grey.shade400),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ] else if (!_skillsController.hasResults) ...[
              // Show "Analyze Another Job" button if user skipped (has initial but no full results)
              ElevatedButton.icon(
                onPressed: () {
                  // Clear current results but keep CV/JD
                  clearAnalysisResults();
                },
                icon: const Icon(Icons.refresh),
                label: const Text('Analyze Another Job'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ] else ...[
              // User proceeded - no buttons shown, analysis complete or in progress
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.blue.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Full analysis in progress...',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // Info text
            const SizedBox(height: 12),
            Text(
              'Note: Full analysis includes component analysis, ATS optimization, AI recommendations, and CV tailoring. This consumes more AI credits.',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }
}
