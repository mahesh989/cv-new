import 'package:flutter/material.dart';
import '../steps/analysis_orchestrator.dart';
import '../steps/step_1_preliminary_analysis/preliminary_analysis_controller.dart';
import '../steps/step_1_preliminary_analysis/preliminary_analysis_widget.dart';
import '../steps/step_2_ai_analysis/ai_analysis_controller.dart';
import '../steps/step_2_ai_analysis/ai_analysis_widget.dart';
import '../steps/step_3_skill_comparison/skill_comparison_controller.dart';
import '../steps/step_3_skill_comparison/skill_comparison_widget.dart';
import '../steps/step_4_enhanced_ats/enhanced_ats_controller.dart';
import '../steps/step_4_enhanced_ats/enhanced_ats_widget.dart';
import '../steps/step_5_ai_recommendations/ai_recommendations_controller.dart';
import '../steps/step_5_ai_recommendations/ai_recommendations_widget.dart';
import '../utils/notification_service.dart';

/// Modular Analysis Widget that replaces the old AnalysisWorkflowWidget
/// Integrates all 5 analysis steps using the new orchestrator
class ModularAnalysisWidget extends StatefulWidget {
  final String cvFilename;
  final String jdText;
  final String currentPrompt;

  const ModularAnalysisWidget({
    super.key,
    required this.cvFilename,
    required this.jdText,
    required this.currentPrompt,
  });

  @override
  State<ModularAnalysisWidget> createState() => _ModularAnalysisWidgetState();
}

class _ModularAnalysisWidgetState extends State<ModularAnalysisWidget> {
  late final AnalysisOrchestrator _orchestrator;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeOrchestrator();
  }

  void _initializeOrchestrator() {
    _orchestrator = AnalysisOrchestrator();

    // Register all 5 analysis steps
    _orchestrator.registerStep(PreliminaryAnalysisController());
    _orchestrator.registerStep(AIAnalysisController());
    _orchestrator.registerStep(SkillComparisonController());
    _orchestrator.registerStep(EnhancedATSController());
    _orchestrator.registerStep(AIRecommendationsController());

    // Load cached results if available
    if (widget.cvFilename.isNotEmpty && widget.jdText.isNotEmpty) {
      _orchestrator.loadCachedResults(widget.cvFilename, widget.jdText);
    }

    setState(() {
      _isInitialized = true;
    });

    debugPrint(
        '[MODULAR_ANALYSIS] Orchestrator initialized with ${_orchestrator.steps.length} steps');
  }

  @override
  void dispose() {
    _orchestrator.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(ModularAnalysisWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Reload cached results if CV filename or JD text changed
    if (oldWidget.cvFilename != widget.cvFilename ||
        oldWidget.jdText != widget.jdText) {
      if (widget.cvFilename.isNotEmpty && widget.jdText.isNotEmpty) {
        _orchestrator.loadCachedResults(widget.cvFilename, widget.jdText);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListenableBuilder(
      listenable: _orchestrator,
      builder: (context, _) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Main action button
            _buildActionButton(),

            // Progress indicators
            if (_orchestrator.isRunning) ...[
              const SizedBox(height: 16),
              _buildProgressIndicator(),
            ],

            // Progressive results display
            if (_orchestrator.hasResults) ...[
              const SizedBox(height: 24),
              _buildResultsSection(),
            ],
          ],
        );
      },
    );
  }

  Widget _buildActionButton() {
    final isAnyRunning = _orchestrator.isRunning;
    final canAnalyze = widget.cvFilename.isNotEmpty && widget.jdText.isNotEmpty;
    
    debugPrint(
      '🔍 [DEBUG] Button state - canAnalyze: $canAnalyze, isAnalyzing: $isAnyRunning',
    );
    debugPrint('🔍 [DEBUG] selectedCVFilename: ${widget.cvFilename}');
    debugPrint('🔍 [DEBUG] jdController.text.length: ${widget.jdText.length}');

    return ElevatedButton.icon(
      onPressed: (isAnyRunning || !canAnalyze) ? null : _executeAnalysis,
      icon: isAnyRunning
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.auto_awesome_mosaic),
      label: Text(
        isAnyRunning
            ? 'Running Full Analysis...'
            : canAnalyze
                ? 'Preliminary Analysis + Skill Comparison'
                : 'Please provide CV and JD text first',
      ),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16),
        backgroundColor: canAnalyze ? null : Colors.grey,
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.analytics, color: Colors.blue[700], size: 20),
              const SizedBox(width: 8),
              Text(
                'Analysis Progress',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LinearProgressIndicator(
            value: _orchestrator.progress,
            backgroundColor: Colors.blue[100],
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[700]!),
          ),
          const SizedBox(height: 8),
          Text(
            'Step ${_orchestrator.completedStepsCount + 1} of ${_orchestrator.totalStepsCount}: ${_orchestrator.currentStepId ?? 'Initializing...'}',
            style: TextStyle(
              fontSize: 14,
              color: Colors.blue[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Step 1: Preliminary Analysis
        if (_orchestrator.steps.containsKey('preliminary_analysis')) ...[
          PreliminaryAnalysisWidget(
            controller: _orchestrator.steps['preliminary_analysis']!
                as PreliminaryAnalysisController,
          ),
          const SizedBox(height: 16),
        ],

        // Step 2: AI Analysis
        if (_orchestrator.steps.containsKey('ai_analysis')) ...[
          AIAnalysisWidget(
            controller:
                _orchestrator.steps['ai_analysis']! as AIAnalysisController,
          ),
          const SizedBox(height: 16),
        ],

        // Step 3: Skill Comparison
        if (_orchestrator.steps.containsKey('skill_comparison')) ...[
          SkillComparisonWidget(
            controller: _orchestrator.steps['skill_comparison']!
                as SkillComparisonController,
          ),
          const SizedBox(height: 16),
        ],

        // Step 4: Enhanced ATS Score
        if (_orchestrator.steps.containsKey('enhanced_ats')) ...[
          EnhancedATSWidget(
            controller:
                _orchestrator.steps['enhanced_ats']! as EnhancedATSController,
          ),
          const SizedBox(height: 16),
        ],

        // Step 5: AI Recommendations
        if (_orchestrator.steps.containsKey('ai_recommendations')) ...[
          AIRecommendationsWidget(
            controller: _orchestrator.steps['ai_recommendations']!
                as AIRecommendationsController,
          ),
        ],
      ],
    );
  }

  Future<void> _executeAnalysis() async {
    debugPrint('[MODULAR_ANALYSIS] _executeAnalysis called with:');
    debugPrint('  cvFilename: "${widget.cvFilename}"');
    debugPrint('  jdText length: ${widget.jdText.length}');
    debugPrint('  cvFilename.isEmpty: ${widget.cvFilename.isEmpty}');
    debugPrint('  jdText.isEmpty: ${widget.jdText.isEmpty}');
    
    if (widget.cvFilename.isEmpty || widget.jdText.isEmpty) {
      NotificationService.showError('Please provide CV and JD text first');
      debugPrint('[MODULAR_ANALYSIS] Blocked execution - missing CV or JD');
      return;
    }

    try {
      debugPrint('[MODULAR_ANALYSIS] Starting orchestrator.executeAllSteps...');
      await _orchestrator.executeAllSteps(
        cvFilename: widget.cvFilename,
        jdText: widget.jdText,
        initialData: {
          'current_prompt': widget.currentPrompt,
        },
      );

      NotificationService.showSuccess('Full analysis completed successfully!');
    } catch (e) {
      NotificationService.showError('Analysis workflow failed: $e');
      debugPrint('[MODULAR_ANALYSIS] Error: $e');
    }
  }
}
