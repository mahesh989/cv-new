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
    return Consumer<SkillsAnalysisController>(
      builder: (context, controller, child) {
        final canAnalyze = _canPerformAnalysis();
        final buttonText = controller.isLoading
            ? 'Analyzing...'
            : controller.hasResults
                ? 'Re-analyze Skills'
                : 'Analyze Skills';

        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed:
                canAnalyze && !controller.isLoading ? _performAnalysis : null,
            icon: controller.isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Icon(
                    controller.hasResults ? Icons.refresh : Icons.analytics,
                    size: 20,
                  ),
            label: Text(
              buttonText,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
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
  }

  bool _canPerformAnalysis() {
    return _selectedCvFilename != null &&
        _selectedCvFilename!.isNotEmpty &&
        _jdController.text.trim().isNotEmpty &&
        _jdController.text.trim().length >= 50;
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
