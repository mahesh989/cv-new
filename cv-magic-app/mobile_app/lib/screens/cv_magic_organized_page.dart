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
import '../modules/cv/cv_upload_module.dart';
import '../modules/cv/cv_selection_module.dart';
import '../modules/cv/cv_preview_module.dart';
import '../widgets/job_input.dart';
import '../services/api_service.dart';
import '../controllers/skills_analysis_controller.dart';
import '../widgets/skills_display_widget.dart';

class CVMagicOrganizedPage extends StatefulWidget {
  const CVMagicOrganizedPage({super.key});

  @override
  State<CVMagicOrganizedPage> createState() => _CVMagicOrganizedPageState();
}

class _CVMagicOrganizedPageState extends State<CVMagicOrganizedPage> with AutomaticKeepAliveClientMixin {
  // State variables
  String? selectedCVFilename;
  bool isLoading = false;
  // Removed company selection used for JDAnalysisWidget (backend-only focus)

  // Job description controllers
  final TextEditingController jdController = TextEditingController();
  final TextEditingController jdUrlController = TextEditingController();

  // Skills analysis controller
  late final SkillsAnalysisController _skillsController;

  @override
  void initState() {
    super.initState();
    _skillsController = SkillsAnalysisController();

    // Set notification callback for real-time progress updates
    _skillsController.setNotificationCallback(_showSnackBar);

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
  void dispose() {
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic - Organized'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
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
                        animation: Listenable.merge([_skillsController, jdController]),
                        builder: (context, _) {
                          final canAnalyze = selectedCVFilename != null &&
                              jdController.text.trim().isNotEmpty;
                          final isAnalyzing = _skillsController.isLoading;

                          // Comprehensive debug logging
                          print('=== BUTTON STATE CHECK ===');
                          print('🔍 [DEBUG] Button state - canAnalyze: $canAnalyze, isAnalyzing: $isAnalyzing');
                          print('🔍 [DEBUG] selectedCVFilename: $selectedCVFilename');
                          print('🔍 [DEBUG] selectedCVFilename != null: ${selectedCVFilename != null}');
                          print('🔍 [DEBUG] jdController.text.length: ${jdController.text.length}');
                          print('🔍 [DEBUG] jdController.text.trim().length: ${jdController.text.trim().length}');
                          print('🔍 [DEBUG] jdController.text.trim().isEmpty: ${jdController.text.trim().isEmpty}');
                          print('🔍 [DEBUG] jdController.text.trim().isNotEmpty: ${jdController.text.trim().isNotEmpty}');
                          print('🔍 [DEBUG] _skillsController.isLoading: ${_skillsController.isLoading}');
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
              jobDescription: jdController.text.trim().isNotEmpty ? jdController.text.trim() : null,
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
    
    // Show feedback to user
    _showSnackBar('🚀 Please switch to CV Generation tab manually for now');
    
    // TODO: Implement proper tab switching via parent widget or state management
    // For now, users need to manually tap the CV Generation tab
    debugPrint('TODO: Implement navigation to CV Generation tab (index 2)');
  }

  Future<void> _refreshCVList() async {
    // This would trigger a refresh of the CV selection module
    // For now, we'll just update the state
    setState(() {});
  }

  // Company selector removed (backend-only focus)
}
