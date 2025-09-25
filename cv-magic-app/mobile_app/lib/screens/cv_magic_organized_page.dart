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
import '../controllers/skills_analysis_controller.dart';
import '../widgets/skills_display_widget.dart';

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
  // Removed company selection used for JDAnalysisWidget (backend-only focus)

  // Job description controllers
  final TextEditingController jdController = TextEditingController();
  final TextEditingController jdUrlController = TextEditingController();

  // Skills analysis controller
  late final SkillsAnalysisController _skillsController;

  // Timer for checking clear flag
  Timer? _clearCheckTimer;

  @override
  void initState() {
    super.initState();
    _skillsController = SkillsAnalysisController();

    // Set notification callback for real-time progress updates
    _skillsController.setNotificationCallback(_showSnackBar);

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
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Check if results need to be cleared when dependencies change
    _checkAndClearResults();
  }

  /// Check if we need to clear results and do so if needed
  void _checkAndClearResults() {
    debugPrint('🧹 [CV_MAGIC] _checkAndClearResults called');
    final shouldClear = widget.shouldClearResults?.call();
    debugPrint('🧹 [CV_MAGIC] shouldClearResults returned: $shouldClear');

    if (shouldClear == true) {
      debugPrint('🧹 [CV_MAGIC] Clearing results due to Run ATS Again');
      debugPrint('🧹 [CV_MAGIC] About to call clearAnalysisResults()');
      clearAnalysisResults();
      debugPrint(
          '🧹 [CV_MAGIC] clearAnalysisResults() completed, calling onResultsCleared');
      widget.onResultsCleared?.call();
      debugPrint('🧹 [CV_MAGIC] onResultsCleared callback completed');
    } else {
      debugPrint(
          '🧹 [CV_MAGIC] shouldClearResults returned false, no clearing needed');
    }
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
            ),
            const SizedBox(height: 16),

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

                          return ElevatedButton.icon(
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
                                : const Icon(Icons.psychology),
                            label: Text(isAnalyzing
                                ? 'Analyzing Skills...'
                                : 'Analyze Skills'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  canAnalyze ? Colors.purple : Colors.grey,
                              foregroundColor:
                                  canAnalyze ? Colors.white : Colors.grey,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
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
            const SizedBox(height: 16),

            // Skills Display with Side-by-Side Layout and Expandable Analysis
            SkillsDisplayWidget(
              controller: _skillsController,
              cvFilename: selectedCVFilename,
              jobDescription: jdController.text.trim().isNotEmpty
                  ? jdController.text.trim()
                  : null,
              onNavigateToCVGeneration: _navigateToCVGeneration,
            ),
            // JD Analysis UI section removed for backend-only focus

            // Loading indicator
            if (isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
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
      await APIService.uploadCV(file);
      await _refreshCVList();

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
    setState(() {
      selectedCVFilename = filename;
    });
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

    print('✅ [DEBUG] Starting skills analysis...');
    try {
      await _skillsController.performAnalysis(
        cvFilename: selectedCVFilename!,
        jdText: jdController.text.trim(),
      );

      if (_skillsController.hasResults) {
        _showSnackBar('Skills analysis completed successfully!');
      } else if (_skillsController.hasError) {
        _showSnackBar(
            'Skills analysis failed: ${_skillsController.errorMessage}',
            isError: true);
      }
    } catch (e) {
      print('❌ [DEBUG] Error in _analyzeSkills: $e');
      _showSnackBar('Error performing skills analysis: $e', isError: true);
    }
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

  Future<void> _refreshCVList() async {
    // This would trigger a refresh of the CV selection module
    // For now, we'll just update the state
    setState(() {});
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
            'This will clear all analysis results but keep your selected CV and CV preview. Are you sure?',
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
  /// Preserves selected CV, CV preview, and JD inputs as requested
  void clearAnalysisResults() {
    debugPrint('🧹 [CV_MAGIC] Clearing analysis results in CV Magic tab');
    debugPrint('🧹 [CV_MAGIC] Preserving selected CV: $selectedCVFilename');
    debugPrint('🧹 [CV_MAGIC] Preserving JD URL: ${jdUrlController.text}');
    debugPrint(
        '🧹 [CV_MAGIC] Preserving JD text length: ${jdController.text.length}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller has results before clear: ${_skillsController.hasResults}');
    debugPrint(
        '🧹 [CV_MAGIC] Controller state before clear: ${_skillsController.state}');

    // Clear the skills analysis results
    _skillsController.clearResults();

    // PRESERVE JD inputs - DO NOT clear them during re-runs
    // jdController.clear();  // ❌ REMOVED: This was clearing the JD text
    // jdUrlController.clear(); // ❌ REMOVED: This was clearing the JD URL

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
            '✅ All analysis results cleared. CV preview and JD inputs preserved.'),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }
}
