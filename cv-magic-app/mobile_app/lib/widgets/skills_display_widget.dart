import 'package:flutter/material.dart';
import '../controllers/skills_analysis_controller.dart';

/// Widget for displaying side-by-side CV and JD skills comparison
class SkillsDisplayWidget extends StatelessWidget {
  final SkillsAnalysisController controller;

  const SkillsDisplayWidget({
    super.key,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        if (controller.isLoading) {
          return _buildLoadingState();
        }

        if (controller.hasError) {
          return _buildErrorState();
        }

        if (!controller.hasResults) {
          return _buildEmptyState();
        }

        return _buildResultsContent();
      },
    );
  }

  Widget _buildLoadingState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            'Analyzing Skills...',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Colors.blue.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Extracting skills from CV and Job Description using AI',
            style: TextStyle(
              fontSize: 14,
              color: Colors.blue.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.error_outline,
            color: Colors.red.shade600,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            'Analysis Failed',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.red.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            controller.errorMessage ?? 'Unknown error occurred',
            style: TextStyle(
              fontSize: 14,
              color: Colors.red.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Icon(
            Icons.analytics_outlined,
            color: Colors.grey.shade600,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            'No Analysis Results',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Start analysis to see CV and JD skills comparison',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildResultsContent() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with execution info
          _buildResultsHeader(),

          // Side by side comparison
          Padding(
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
          ),
        ],
      ),
    );
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
          Icon(
            Icons.analytics,
            color: Colors.blue.shade700,
            size: 20,
          ),
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
          _buildSkillSection(
            '🤝 Soft Skills',
            softSkills,
            baseColor.shade200,
          ),
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

        // Expandable Comprehensive Analysis
        debugPrint('🔍 [UI_DEBUG] Checking comprehensive analysis for $type');
        debugPrint('   comprehensiveAnalysis is null: ${comprehensiveAnalysis == null}');
        debugPrint('   comprehensiveAnalysis is empty: ${comprehensiveAnalysis?.isEmpty ?? true}');
        debugPrint('   comprehensiveAnalysis length: ${comprehensiveAnalysis?.length ?? 0}');
        
        if (comprehensiveAnalysis != null &&
            comprehensiveAnalysis.isNotEmpty) ...[
          debugPrint('   ✅ Building expandable analysis for $type');
          _buildExpandableAnalysis(
            comprehensiveAnalysis,
            baseColor,
            type,
          ),
        ] else ...[
          debugPrint('   ❌ Skipping expandable analysis for $type - no content');
        ],
      ],
    );
  }

  Widget _buildSkillSection(
    String title,
    List<String> skills,
    Color backgroundColor,
  ) {
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
            children: skills
                .map(
                  (skill) => Chip(
                    label: Text(
                      skill,
                      style: const TextStyle(fontSize: 12),
                    ),
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

  Widget _buildExpandableAnalysis(
    String analysis,
    MaterialColor baseColor,
    String type,
  ) {
    // Debug logging
    debugPrint('🔍 [UI_DEBUG] Building expandable analysis for $type');
    debugPrint('   Analysis length: ${analysis.length}');
    debugPrint(
        '   Analysis preview: ${analysis.substring(0, analysis.length > 100 ? 100 : analysis.length)}');

    return _ExpandableAnalysisWidget(
      analysis: analysis,
      baseColor: baseColor,
      type: type,
    );
  }
}

class _ExpandableAnalysisWidget extends StatefulWidget {
  final String analysis;
  final MaterialColor baseColor;
  final String type;

  const _ExpandableAnalysisWidget({
    required this.analysis,
    required this.baseColor,
    required this.type,
  });

  @override
  State<_ExpandableAnalysisWidget> createState() =>
      _ExpandableAnalysisWidgetState();
}

class _ExpandableAnalysisWidgetState extends State<_ExpandableAnalysisWidget> {
  bool isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              debugPrint(
                  '📝 [UI_DEBUG] Expand button clicked for ${widget.type}. Current state: $isExpanded');
              setState(() => isExpanded = !isExpanded);
              debugPrint('📝 [UI_DEBUG] New expand state: $isExpanded');
            },
            icon: Icon(
              isExpanded ? Icons.expand_less : Icons.expand_more,
              size: 20,
            ),
            label: Text(
              isExpanded ? 'Hide Analysis' : 'Show Detailed Analysis',
              style: const TextStyle(fontSize: 14),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: widget.baseColor.shade100,
              foregroundColor: widget.baseColor.shade700,
              elevation: 0,
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
                side: BorderSide(color: widget.baseColor.shade300),
              ),
            ),
          ),
        ),
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          height: isExpanded ? null : 0,
          child: isExpanded
              ? Container(
                  margin: const EdgeInsets.only(top: 8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: widget.baseColor.shade300),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.psychology,
                            size: 16,
                            color: widget.baseColor.shade600,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'AI Detailed Analysis',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: widget.baseColor.shade700,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Builder(
                        builder: (context) {
                          debugPrint(
                              '📝 [UI_DEBUG] Rendering analysis text for ${widget.type}');
                          debugPrint(
                              '   Analysis content: ${widget.analysis.isEmpty ? "EMPTY" : "${widget.analysis.length} chars"}');
                          return Text(
                            widget.analysis.isEmpty
                                ? "No detailed analysis available"
                                : widget.analysis,
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey.shade700,
                              height: 1.4,
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                )
              : const SizedBox.shrink(),
        ),
      ],
    );
  }
}
