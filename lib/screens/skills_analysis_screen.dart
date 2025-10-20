import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../controllers/skills_analysis_controller.dart';
import '../widgets/skills_display_widget.dart';
import '../widgets/job_input.dart';
import '../modules/cv/cv_selection_module.dart';
import '../core/theme/app_theme.dart';

/// Screen for performing and displaying skills analysis results
class SkillsAnalysisScreen extends StatefulWidget {
  const SkillsAnalysisScreen({super.key});

  @override
  State<SkillsAnalysisScreen> createState() => _SkillsAnalysisScreenState();
}

class _SkillsAnalysisScreenState extends State<SkillsAnalysisScreen> {
  late SkillsAnalysisController _controller;
  final TextEditingController _jdController = TextEditingController();
  final TextEditingController _jdUrlController = TextEditingController();
  String? _selectedCvFilename;

  @override
  void initState() {
    super.initState();
    _controller = SkillsAnalysisController();
    _controller.setNotificationCallback(_showSnackBar);

    // Listen to JD controller changes to update button state
    _jdController.addListener(() {
      setState(() {
        // This will trigger a rebuild and update the button state
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _jdController.dispose();
    _jdUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<SkillsAnalysisController>.value(
      value: _controller,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Skills Analysis'),
          backgroundColor: Colors.blue.shade600,
          foregroundColor: Colors.white,
          actions: [
            // Clear results action
            Consumer<SkillsAnalysisController>(
              builder: (context, controller, child) {
                if (controller.hasResults || controller.hasError) {
                  return IconButton(
                    onPressed: () {
                      controller.clearResults();
                      _jdController.clear();
                      _jdUrlController.clear();
                      setState(() {
                        _selectedCvFilename = null;
                      });
                    },
                    icon: const Icon(Icons.refresh),
                    tooltip: 'Clear and Reset',
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Instructions
              _buildInstructionsCard(),
              const SizedBox(height: 16),

              // CV Selection
              CVSelectionModule(
                selectedCVFilename: _selectedCvFilename,
                onCVSelected: (filename) {
                  setState(() {
                    _selectedCvFilename = filename;
                  });
                  _controller
                      .clearResults(); // Clear previous results when CV changes
                },
              ),
              const SizedBox(height: 16),

              // Job Description Input
              JobInput(
                jdController: _jdController,
                jdUrlController: _jdUrlController,
                onExtract: () {
                  // Job input widget handles extraction internally
                },
              ),
              const SizedBox(height: 16),

              // Analysis Button
              _buildAnalysisButton(),
              const SizedBox(height: 16),

              // Run ATS Test Again Button (appears after first analysis)
              Consumer<SkillsAnalysisController>(
                builder: (context, controller, child) {
                  if (controller.hasResults && _canPerformRerunAnalysis()) {
                    return _buildRerunAnalysisButton();
                  }
                  return const SizedBox.shrink();
                },
              ),
              const SizedBox(height: 16),

              // CV Context Display (shows which CV is being used)
              Consumer<SkillsAnalysisController>(
                builder: (context, controller, child) {
                  if (controller.currentCvFilename != null) {
                    return _buildCVContextCard(controller);
                  }
                  return const SizedBox.shrink();
                },
              ),
              const SizedBox(height: 24),

              // Skills Display Results
              Consumer<SkillsAnalysisController>(
                builder: (context, controller, child) {
                  return SkillsDisplayWidget(controller: controller);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInstructionsCard() {
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
                  Icons.info_outline,
                  color: Colors.blue.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'How Skills Analysis Works',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              '1. Select a CV file from your uploads\n'
              '2. Enter or extract a job description\n'
              '3. Click "Analyze Skills" to compare CV and JD skills side-by-side\n'
              '4. View technical skills, soft skills, and domain keywords\n'
              '5. Expand detailed AI analysis for comprehensive insights',
              style: TextStyle(
                fontSize: 14,
                color: Colors.blue.shade600,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisButton() {
    return StatefulBuilder(
      builder: (context, setState) {
        return Consumer<SkillsAnalysisController>(
          builder: (context, controller, child) {
            final canAnalyze = _canPerformAnalysis();
            final buttonText = controller.isLoading
                ? 'Analyzing...'
                : controller.hasResults
                    ? 'Re-analyze Skills'
                    : 'Analyze Skills';

            print(
                '🔍 Button state: canAnalyze=$canAnalyze, isLoading=${controller.isLoading}, hasResults=${controller.hasResults}');

            return SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: canAnalyze && !controller.isLoading
                    ? _performAnalysis
                    : null,
                icon: controller.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Icon(
                        controller.hasResults ? Icons.refresh : Icons.analytics,
                        size: 20,
                      ),
                label: Text(
                  buttonText,
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.w600),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: canAnalyze
                      ? (controller.hasResults
                          ? Colors.orange
                          : AppTheme.primaryNeon)
                      : Colors.grey,
                  foregroundColor: canAnalyze ? Colors.black : Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: canAnalyze ? 2 : 0,
                ),
              ),
            );
          },
        );
      },
    );
  }

  bool _canPerformAnalysis() {
    final hasCv =
        _selectedCvFilename != null && _selectedCvFilename!.isNotEmpty;
    final hasJd = _jdController.text.trim().isNotEmpty &&
        _jdController.text.trim().length >= 10;
    final canAnalyze = hasCv && hasJd;

    print(
        '🔍 Button check: hasCv=$hasCv, hasJd=$hasJd, canAnalyze=$canAnalyze');
    print('   CV: $_selectedCvFilename');
    print('   JD length: ${_jdController.text.trim().length}');

    return canAnalyze;
  }

  bool _canPerformRerunAnalysis() {
    // For rerun analysis, we need JD URL and company name
    final hasJdUrl = _jdUrlController.text.trim().isNotEmpty;
    final hasCompany = _extractCompanyFromJD() != null;
    return hasJdUrl && hasCompany;
  }

  String? _extractCompanyFromJD() {
    // Simple company extraction from JD text
    final jdText = _jdController.text.trim();
    if (jdText.isEmpty) return null;

    // Look for common company indicators
    final lines = jdText.split('\n');
    for (final line in lines) {
      final lowerLine = line.toLowerCase();
      if (lowerLine.contains('company:') ||
          lowerLine.contains('organization:') ||
          lowerLine.contains('employer:')) {
        return line.split(':').last.trim();
      }
    }

    // Fallback: use first line if it looks like a company name
    if (lines.isNotEmpty && lines.first.length < 50) {
      return lines.first.trim();
    }

    return null;
  }

  Widget _buildRerunAnalysisButton() {
    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.refresh,
                  color: Colors.orange.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Run ATS Test Again',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Use the latest tailored CV for improved analysis results',
              style: TextStyle(
                fontSize: 14,
                color: Colors.orange.shade600,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _canPerformRerunAnalysis() && !_controller.isLoading
                    ? _performRerunAnalysis
                    : null,
                icon: const Icon(Icons.psychology, size: 18),
                label: const Text(
                  'Run ATS Test Again',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _performAnalysis() async {
    if (!_canPerformAnalysis()) {
      String message = 'Cannot perform analysis:\n';
      if (_selectedCvFilename == null || _selectedCvFilename!.isEmpty) {
        message += '• Please select a CV file\n';
      }
      if (_jdController.text.trim().isEmpty) {
        message += '• Please enter a job description\n';
      } else if (_jdController.text.trim().length < 50) {
        message += '• Job description is too short (minimum 50 characters)\n';
      }

      _showSnackBar(message.trim(), isError: true);
      return;
    }

    try {
      // Perform standard analysis
      await _controller.performAnalysis(
        cvFilename: _selectedCvFilename!,
        jdText: _jdController.text.trim(),
      );

      // Notifications are now handled by the controller
      // No need to show duplicate notifications here
    } catch (e) {
      _showSnackBar('Error performing analysis: $e', isError: true);
    }
  }

  Future<void> _performRerunAnalysis() async {
    if (!_canPerformRerunAnalysis()) {
      String message = 'Cannot perform rerun analysis:\n';
      if (_jdUrlController.text.trim().isEmpty) {
        message += '• Please enter a job description URL\n';
      }
      if (_extractCompanyFromJD() == null) {
        message += '• Could not extract company name from job description\n';
      }

      _showSnackBar(message.trim(), isError: true);
      return;
    }

    try {
      // Use the company name from the backend's preliminary analysis result if available
      String company;
      if (_controller.result?.preextractedCompanyName != null && 
          _controller.result!.preextractedCompanyName!.isNotEmpty) {
        company = _controller.result!.preextractedCompanyName!;
        print('🔄 [RERUN] Using backend-extracted company name: $company');
      } else {
        // Fallback to frontend extraction if backend company name is not available
        company = _extractCompanyFromJD()!;
        print('🔄 [RERUN] Using frontend-extracted company name: $company');
      }

      // Perform context-aware rerun analysis
      await _controller.performContextAwareAnalysis(
        jdUrl: _jdUrlController.text.trim(),
        company: company,
        isRerun: true, // This is the key parameter for rerun
        includeTailoring: true,
      );

      _showSnackBar(
          'Rerun analysis completed! Using latest tailored CV for improved results.');
    } catch (e) {
      _showSnackBar('Error performing rerun analysis: $e', isError: true);
    }
  }

  Widget _buildCVContextCard(SkillsAnalysisController controller) {
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
                  'CV Being Used for Analysis',
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
              controller.currentCvFilename ?? 'Unknown',
              Colors.blue,
            ),

            // Analysis Status
            _buildContextItem(
              'Analysis Status',
              controller.isLoading
                  ? 'Analyzing...'
                  : controller.hasResults
                      ? 'Analysis Complete'
                      : controller.hasError
                          ? 'Analysis Failed'
                          : 'Ready to Analyze',
              controller.isLoading
                  ? Colors.orange
                  : controller.hasResults
                      ? Colors.green
                      : controller.hasError
                          ? Colors.red
                          : Colors.grey,
            ),

            // Execution Duration (if available)
            if (controller.executionDuration.inSeconds > 0)
              _buildContextItem(
                'Analysis Time',
                '${controller.executionDuration.inSeconds}s',
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

  void _showSnackBar(String message, {bool isError = false}) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: isError ? Colors.red : Colors.green,
          duration: Duration(seconds: isError ? 4 : 3),
          action: SnackBarAction(
            label: 'Dismiss',
            textColor: Colors.white,
            onPressed: () {
              ScaffoldMessenger.of(context).hideCurrentSnackBar();
            },
          ),
        ),
      );
    }
  }
}
