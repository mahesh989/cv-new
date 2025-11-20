import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import '../controllers/context_aware_analysis_controller.dart';
import '../controllers/skills_analysis_controller.dart';
import '../widgets/skills_display_widget.dart';
import '../widgets/skills_comparison_card.dart';
import '../core/theme/app_theme.dart';
import '../services/context_aware_analysis_service.dart';
import '../models/skills_analysis_model.dart';

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
  _ContextAwareSkillsAdapter? _adapterController;
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
    _adapterController?.dispose();
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

              // Skills Comparison Card (shown BEFORE analyze match decision)
              // Simple side-by-side display of CV vs JD skills from initial analysis
              Consumer<ContextAwareAnalysisController>(
                builder: (context, controller, child) {
                  debugPrint('🔍 [SCREEN] Checking skills comparison:');
                  debugPrint('   hasInitialResults: ${controller.hasInitialResults}');
                  debugPrint('   initialResult != null: ${controller.initialResult != null}');
                  debugPrint('   initialResult?.results != null: ${controller.initialResult?.results != null}');
                  
                  // Show skills comparison if we have initial analysis results
                  if (controller.hasInitialResults && 
                      controller.initialResult?.results != null) {
                    debugPrint('✅ [SCREEN] Showing SkillsComparisonCard');
                    final results = controller.initialResult!.results!;
                    
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
                  debugPrint('❌ [SCREEN] Not showing skills comparison');
                  return const SizedBox.shrink();
                },
              ),

              // Analyze Match Decision
              // Shows decision widget when:
              // 1. Waiting for user decision, OR
              // 2. Has initial results with decision (persists after clicking proceed)
              Consumer<ContextAwareAnalysisController>(
                builder: (context, controller, child) {
                  debugPrint('🔍 [SCREEN] Checking decision widget:');
                  debugPrint('   waitingForUserDecision: ${controller.waitingForUserDecision}');
                  debugPrint('   hasAnalyzeMatchDecision: ${controller.hasAnalyzeMatchDecision}');
                  debugPrint('   hasInitialResults: ${controller.hasInitialResults}');
                  debugPrint('   state: ${controller.state}');
                  
                  // Show widget if we have initial results with decision
                  // This persists even after clicking proceed
                  if (controller.hasInitialResults && controller.hasAnalyzeMatchDecision) {
                    debugPrint('✅ [SCREEN] Showing decision widget');
                    return Column(
                      children: [
                        _buildAnalyzeMatchDecisionCard(controller),
                        const SizedBox(height: 16),
                      ],
                    );
                  }
                  debugPrint('❌ [SCREEN] Not showing decision widget');
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

  Widget _buildAnalyzeMatchDecisionCard(ContextAwareAnalysisController controller) {
    final decision = controller.analyzeMatchDecision;
    
    // Safety check - if no decision, show fallback UI
    if (decision == null) {
      debugPrint('⚠️ [SCREEN] Decision is null, showing fallback');
      return Card(
        margin: const EdgeInsets.symmetric(vertical: 16.0),
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
                        controller.continueFullAnalysis(includeTailoring: _includeTailoring);
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
                        controller.skipFullAnalysis();
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
                  _buildScoreItem('Match Score', '${decision.matchScore}%', iconColor),
                  _buildScoreItem('Confidence', '${decision.confidence}%', iconColor),
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
                    labelStyle: TextStyle(color: Colors.red.shade900, fontSize: 12),
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],
            
            // Action Buttons - only show when waiting for decision
            if (controller.waitingForUserDecision) ...[
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        controller.continueFullAnalysis(includeTailoring: _includeTailoring);
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
                        controller.skipFullAnalysis();
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
              
              // Info text
              const SizedBox(height: 12),
              Text(
                decision.isDontProceed
                    ? '⚠️ Full analysis is not recommended. You can still proceed if you want, but it may not be cost-effective.'
                    : '💡 Full analysis includes Component Analysis, ATS Recommendations, AI Recommendations, and CV Tailoring.',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ] else ...[
              // Status indicator when decision has been made
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      controller.showAnalysisResults 
                        ? Icons.check_circle 
                        : Icons.hourglass_empty,
                      color: controller.showAnalysisResults 
                        ? Colors.green.shade600 
                        : Colors.orange.shade600,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        controller.showAnalysisResults
                          ? '✅ Full analysis completed'
                          : '⏳ Full analysis in progress...',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: Colors.grey.shade800,
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
    );
  }

  Widget _buildScoreItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
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
    if (_adapterController == null || _adapterController!.source != contextController) {
      _adapterController?.dispose();
      _adapterController = _ContextAwareSkillsAdapter(contextController);
    }
    return _adapterController!;
  }
}

class _ContextAwareSkillsAdapter extends SkillsAnalysisController {
  final ContextAwareAnalysisController _source;
  late final VoidCallback _relay;

  _ContextAwareSkillsAdapter(this._source) {
    _relay = () => notifyListeners();
    _source.addListener(_relay);
  }

  ContextAwareAnalysisController get source => _source;

  SkillsAnalysisState _mapState(ContextAwareAnalysisState state) {
    switch (state) {
      case ContextAwareAnalysisState.loading:
        return SkillsAnalysisState.loading;
      case ContextAwareAnalysisState.completed:
        return SkillsAnalysisState.completed;
      case ContextAwareAnalysisState.error:
        return SkillsAnalysisState.error;
      case ContextAwareAnalysisState.cancelled:
        return SkillsAnalysisState.cancelled;
      case ContextAwareAnalysisState.idle:
        return SkillsAnalysisState.idle;
    }
  }

  @override
  void dispose() {
    _source.removeListener(_relay);
    super.dispose();
  }

  // State + status mapping
  @override
  SkillsAnalysisState get state => _mapState(_source.state);

  @override
  bool get hasResults => _source.hasResults;

  @override
  bool get hasError => _source.hasError;

  @override
  bool get isLoading => _source.isLoading;

  @override
  bool get isCancelled => _source.isCancelled;

  @override
  String? get errorMessage => _source.errorMessage;

  @override
  Duration get executionDuration => _source.executionDuration;

  // Result + skills mapping
  @override
  SkillsAnalysisResult? get result => _source.result;

  @override
  int get cvTotalSkills => _source.cvTotalSkills;

  @override
  int get jdTotalSkills => _source.jdTotalSkills;

  @override
  List<String> get cvTechnicalSkills =>
      _source.cvSkills?.technicalSkills ?? const [];

  @override
  List<String> get cvSoftSkills =>
      _source.cvSkills?.softSkills ?? const [];

  @override
  List<String> get cvDomainKeywords =>
      _source.cvSkills?.domainKeywords ?? const [];

  @override
  List<String> get jdTechnicalSkills =>
      _source.jdSkills?.technicalSkills ?? const [];

  @override
  List<String> get jdSoftSkills =>
      _source.jdSkills?.softSkills ?? const [];

  @override
  List<String> get jdDomainKeywords =>
      _source.jdSkills?.domainKeywords ?? const [];

  @override
  String? get cvComprehensiveAnalysis => _source.cvComprehensiveAnalysis;

  @override
  String? get jdComprehensiveAnalysis => _source.jdComprehensiveAnalysis;

  @override
  List<String> get extractedKeywords => _source.extractedKeywords;

  // Progressive display flags
  @override
  bool get showAnalyzeMatch => _source.showAnalyzeMatch;

  @override
  bool get showPreextractedComparison => _source.showPreextractedComparison;

  @override
  bool get showATSLoading => _source.showATSLoading;

  @override
  bool get showATSResults => _source.showATSResults;

  @override
  bool get showAIRecommendationLoading =>
      _source.showAIRecommendationLoading;

  @override
  bool get showAIRecommendationResults =>
      _source.showAIRecommendationResults;

  // Analyze match / ATS / AI data
  @override
  bool get hasAnalyzeMatch => _source.hasAnalyzeMatch;

  @override
  AnalyzeMatchResult? get analyzeMatch => _source.analyzeMatch;

  @override
  bool get hasATSResult => _source.hasATSResult;

  @override
  ATSResult? get atsResult => _source.atsResult;
}
