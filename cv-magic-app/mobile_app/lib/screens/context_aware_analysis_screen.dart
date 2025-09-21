import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../controllers/context_aware_analysis_controller.dart';
import '../controllers/skills_analysis_controller.dart';
import '../widgets/skills_display_widget.dart';
import '../core/theme/app_theme.dart';
import '../services/context_aware_analysis_service.dart';

/// Screen for performing context-aware analysis with intelligent CV selection
class ContextAwareAnalysisScreen extends StatefulWidget {
  const ContextAwareAnalysisScreen({super.key});

  @override
  State<ContextAwareAnalysisScreen> createState() =>
      _ContextAwareAnalysisScreenState();
}

class _ContextAwareAnalysisScreenState
    extends State<ContextAwareAnalysisScreen> {
  late ContextAwareAnalysisController _controller;
  final TextEditingController _jdUrlController = TextEditingController();
  final TextEditingController _companyController = TextEditingController();
  bool _isRerun = false;
  bool _includeTailoring = true;

  @override
  void initState() {
    super.initState();
    _controller = ContextAwareAnalysisController();
    _controller.setNotificationCallback(_showSnackBar);

    // Listen to controller changes to update button state
    _jdUrlController.addListener(() {
      setState(() {
        // This will trigger a rebuild and update the button state
      });
    });

    _companyController.addListener(() {
      setState(() {
        // This will trigger a rebuild and update the button state
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _jdUrlController.dispose();
    _companyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<ContextAwareAnalysisController>.value(
      value: _controller,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Context-Aware Analysis'),
          backgroundColor: Colors.blue.shade600,
          foregroundColor: Colors.white,
          actions: [
            // Clear results action
            Consumer<ContextAwareAnalysisController>(
              builder: (context, controller, child) {
                if (controller.hasResults || controller.hasError) {
                  return IconButton(
                    onPressed: () {
                      controller.clearResults();
                      _jdUrlController.clear();
                      _companyController.clear();
                      setState(() {
                        _isRerun = false;
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

              // Analysis Input Section
              _buildAnalysisInputCard(),
              const SizedBox(height: 16),

              // Analysis Options
              _buildAnalysisOptionsCard(),
              const SizedBox(height: 16),

              // Analysis Button
              _buildAnalysisButton(),
              const SizedBox(height: 16),

              // CV Context Display
              Consumer<ContextAwareAnalysisController>(
                builder: (context, controller, child) {
                  if (controller.showCVContext && controller.hasCVContext) {
                    return _buildCVContextCard(controller);
                  }
                  return const SizedBox.shrink();
                },
              ),

              // Analysis Results
              Consumer<ContextAwareAnalysisController>(
                builder: (context, controller, child) {
                  if (controller.showAnalysisResults && controller.hasResults) {
                    return SkillsDisplayWidget(
                      controller: _createCompatibleController(controller),
                    );
                  }
                  return const SizedBox.shrink();
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
                  Icons.psychology,
                  color: Colors.blue.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Context-Aware Analysis',
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
              '🧠 Intelligent CV Selection:\n'
              '• Fresh analysis → Uses original CV\n'
              '• Rerun analysis → Uses latest tailored CV\n\n'
              '♻️ Smart JD Caching:\n'
              '• Reuses JD analysis for same URL\n'
              '• 44% faster processing on reruns\n\n'
              '📊 Rich Context Information:\n'
              '• Shows which CV version is used\n'
              '• Displays cache status and performance\n'
              '• Provides detailed analysis metadata',
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

  Widget _buildAnalysisInputCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis Input',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 16),

            // Job Description URL
            TextField(
              controller: _jdUrlController,
              decoration: InputDecoration(
                labelText: 'Job Description URL',
                hintText: 'https://company.com/job-description',
                prefixIcon: const Icon(Icons.link),
                border: const OutlineInputBorder(),
                helperText: 'Enter the URL of the job description to analyze',
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 16),

            // Company Name
            TextField(
              controller: _companyController,
              decoration: InputDecoration(
                labelText: 'Company Name',
                hintText: 'Company Name',
                prefixIcon: const Icon(Icons.business),
                border: const OutlineInputBorder(),
                helperText: 'Enter the company name for analysis context',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisOptionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis Options',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 16),

            // Rerun Analysis Toggle
            SwitchListTile(
              title: const Text('Rerun Analysis'),
              subtitle: Text(_isRerun
                  ? 'Uses latest tailored CV for improved results'
                  : 'Uses original CV for fresh analysis'),
              value: _isRerun,
              onChanged: (value) {
                setState(() {
                  _isRerun = value;
                });
              },
              secondary: Icon(
                _isRerun ? Icons.refresh : Icons.fiber_new,
                color: _isRerun ? Colors.orange : Colors.green,
              ),
            ),

            // Include Tailoring Toggle
            SwitchListTile(
              title: const Text('Include CV Tailoring'),
              subtitle: const Text('Generate tailored CV based on analysis'),
              value: _includeTailoring,
              onChanged: (value) {
                setState(() {
                  _includeTailoring = value;
                });
              },
              secondary: Icon(
                _includeTailoring ? Icons.auto_fix_high : Icons.auto_fix_off,
                color: _includeTailoring ? Colors.purple : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisButton() {
    return Consumer<ContextAwareAnalysisController>(
      builder: (context, controller, child) {
        final canAnalyze = _canPerformAnalysis();
        final buttonText = controller.isLoading
            ? 'Analyzing...'
            : controller.hasResults
                ? 'Run ATS Test Again'
                : 'Start Analysis';

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
                    controller.hasResults ? Icons.refresh : Icons.psychology,
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

  Widget _buildCVContextCard(ContextAwareAnalysisController controller) {
    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: Colors.green.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Analysis Context',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // CV Selection Info
            _buildContextItem(
              'CV Selection',
              controller.cvDisplayName,
              controller.isUsingTailoredCV ? Colors.orange : Colors.blue,
            ),

            _buildContextItem(
              'Source',
              controller.cvSourceDescription,
              Colors.grey,
            ),

            // JD Cache Info
            if (controller.isJDCached) ...[
              _buildContextItem(
                'JD Cache',
                'Cached (${controller.jdCacheDescription})',
                Colors.green,
              ),
              _buildContextItem(
                'Cache Usage',
                'Used ${controller.jdCacheUseCount} times',
                Colors.grey,
              ),
            ] else ...[
              _buildContextItem(
                'JD Cache',
                'Fresh analysis required',
                Colors.blue,
              ),
            ],

            // Analysis Type
            _buildContextItem(
              'Analysis Type',
              controller.isRerun ? 'Rerun (improved)' : 'Fresh analysis',
              controller.isRerun ? Colors.orange : Colors.green,
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
                color: Colors.grey.shade600,
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

  bool _canPerformAnalysis() {
    final hasJdUrl = _jdUrlController.text.trim().isNotEmpty;
    final hasCompany = _companyController.text.trim().isNotEmpty;
    final canAnalyze = hasJdUrl && hasCompany;

    return canAnalyze;
  }

  Future<void> _performAnalysis() async {
    if (!_canPerformAnalysis()) {
      String message = 'Cannot perform analysis:\n';
      if (_jdUrlController.text.trim().isEmpty) {
        message += '• Please enter a job description URL\n';
      }
      if (_companyController.text.trim().isEmpty) {
        message += '• Please enter a company name\n';
      }

      _showSnackBar(message.trim(), isError: true);
      return;
    }

    try {
      // Auto-extract company from URL if not provided
      String company = _companyController.text.trim();
      if (company.isEmpty) {
        company = ContextAwareAnalysisService.extractCompanyFromUrl(
            _jdUrlController.text.trim());
        _companyController.text = company;
      }

      // Perform context-aware analysis
      await _controller.performContextAwareAnalysis(
        jdUrl: _jdUrlController.text.trim(),
        company: company,
        isRerun: _isRerun,
        includeTailoring: _includeTailoring,
      );

      // Notifications are handled by the controller
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

  /// Create a compatible controller for SkillsDisplayWidget
  /// This is a temporary adapter until we fully migrate the UI
  SkillsAnalysisController _createCompatibleController(
      ContextAwareAnalysisController contextController) {
    // This would need to be implemented to bridge the gap between
    // the old SkillsAnalysisController interface and the new ContextAwareAnalysisController
    // For now, we'll return a basic implementation
    throw UnimplementedError(
        'Compatible controller adapter not yet implemented');
  }
}
