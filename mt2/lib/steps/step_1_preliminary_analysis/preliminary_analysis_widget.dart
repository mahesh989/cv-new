import 'package:flutter/material.dart';
import '../base/analysis_step_widget.dart';
import 'preliminary_analysis_controller.dart';

/// Widget for displaying Step 1: Preliminary Analysis results
class PreliminaryAnalysisWidget extends AnalysisStepWidget {
  const PreliminaryAnalysisWidget({
    super.key,
    required PreliminaryAnalysisController controller,
    super.showHeader = true,
    super.showProgress = true,
    super.showErrors = true,
  }) : super(controller: controller);

  @override
  Widget buildStepContent(BuildContext context) {
    final prelimController = controller as PreliminaryAnalysisController;

    return Container(
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header removed as requested

          // Side by side comparison
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // CV Skills Column
              Expanded(
                child: _buildSkillsColumn(
                  'CV Skills',
                  {
                    'technical_skills':
                        prelimController.cvTechnicalSkills ?? [],
                    'soft_skills': prelimController.cvSoftSkills ?? [],
                    'domain_keywords': prelimController.domainKeywords ?? [],
                  },
                  Colors.blue,
                  'cv',
                ),
              ),
              const SizedBox(width: 16),
              // JD Skills Column
              Expanded(
                child: _buildSkillsColumn(
                  'JD Skills',
                  {
                    'technical_skills':
                        prelimController.jdTechnicalSkills ?? [],
                    'soft_skills': prelimController.jdSoftSkills ?? [],
                    'domain_keywords': prelimController.jdDomainKeywords ?? [],
                  },
                  Colors.green,
                  'jd',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build skills column for side-by-side comparison
  Widget _buildSkillsColumn(
    String title,
    Map<String, List<String>> skills,
    MaterialColor baseColor,
    String type,
  ) {
    final prelimController = controller as PreliminaryAnalysisController;
    final technicalSkills = skills['technical_skills'] ?? [];
    final softSkills = skills['soft_skills'] ?? [];
    final domainKeywords = skills['domain_keywords'] ?? [];

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

        // Expandable Comprehensive Analysis
        if (type == 'cv' &&
            prelimController.cvComprehensiveAnalysis?.isNotEmpty == true) ...[
          _buildExpandableAnalysis(
              prelimController.cvComprehensiveAnalysis!, baseColor, type),
        ] else if (type == 'jd' &&
            prelimController.jdComprehensiveAnalysis?.isNotEmpty == true) ...[
          _buildExpandableAnalysis(
              prelimController.jdComprehensiveAnalysis!, baseColor, type),
        ],
      ],
    );
  }

  /// Build skill section with chips
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
                    label: Text(skill, style: const TextStyle(fontSize: 12)),
                    backgroundColor: Colors.white,
                    side: BorderSide(color: Colors.grey.shade400),
                  ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }

  /// Build expandable analysis section
  Widget _buildExpandableAnalysis(
    String analysis,
    MaterialColor baseColor,
    String type,
  ) {
    bool isExpanded = false;

    return StatefulBuilder(
      builder: (context, setState) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    isExpanded = !isExpanded;
                  });
                },
                icon: Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  size: 16,
                ),
                label: Text(
                  isExpanded
                      ? 'Hide Full Claude AI Analysis'
                      : 'Show Full Claude AI Analysis',
                  style: const TextStyle(fontSize: 12),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: baseColor.shade100,
                  foregroundColor: baseColor.shade900,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            if (isExpanded) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: _buildFormattedText(analysis),
              ),
            ],
          ],
        );
      },
    );
  }

  /// Build formatted text that handles markdown-style formatting
  Widget _buildFormattedText(String text) {
    final spans = <TextSpan>[];
    final lines = text.split('\n');

    for (final line in lines) {
      if (line.trim().isEmpty) {
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Handle headers (##)
      if (line.startsWith('##')) {
        final headerText = line.replaceFirst('##', '').trim();
        spans.add(TextSpan(
          text: '$headerText\n',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
            fontFamily: 'monospace',
          ),
        ));
        continue;
      }

      // Handle bold text (**text**)
      if (line.contains('**')) {
        final regex = RegExp(r'\*\*(.*?)\*\*');
        int lastIndex = 0;
        final lineSpans = <TextSpan>[];

        for (final match in regex.allMatches(line)) {
          // Add text before the match
          if (match.start > lastIndex) {
            lineSpans.add(TextSpan(
              text: line.substring(lastIndex, match.start),
              style: const TextStyle(
                fontSize: 12,
                height: 1.4,
                fontFamily: 'monospace',
              ),
            ));
          }
          // Add the bold text (without the ** markers)
          lineSpans.add(TextSpan(
            text: match.group(1),
            style: const TextStyle(
              fontSize: 12,
              height: 1.4,
              fontFamily: 'monospace',
              fontWeight: FontWeight.bold,
            ),
          ));
          lastIndex = match.end;
        }
        // Add remaining text after the last match
        if (lastIndex < line.length) {
          lineSpans.add(TextSpan(
            text: line.substring(lastIndex),
            style: const TextStyle(
              fontSize: 12,
              height: 1.4,
              fontFamily: 'monospace',
            ),
          ));
        }
        spans.addAll(lineSpans);
        spans.add(const TextSpan(text: '\n'));
        continue;
      }

      // Regular text
      spans.add(TextSpan(
        text: '$line\n',
        style: const TextStyle(
          fontSize: 12,
          height: 1.4,
          fontFamily: 'monospace',
        ),
      ));
    }

    return SelectableText.rich(
      TextSpan(children: spans),
    );
  }
}
