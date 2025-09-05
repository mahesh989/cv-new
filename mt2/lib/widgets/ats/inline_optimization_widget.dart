import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../services/api_service.dart' as api;
import '../../services/ats_service.dart' as ats;
import '../../utils/ats_helpers.dart';
import '../../utils/responsive_utils.dart';
import 'ats_result_widget.dart';
import 'cv_preview_widget.dart';

class InlineOptimizationWidget extends StatefulWidget {
  final List<Map<String, dynamic>> optimizationSteps;
  final Function(String) onRerunATSTest;
  final Function(String) onDownloadCV;
  final Function(String) onSaveToJobs;
  final Function() onGenerateImprovedCV;
  final TextEditingController inlinePromptController;
  final bool isInlineGenerating;
  final bool hasInlinePromptText;
  final bool isImprovementExpanded;
  final Function() onToggleImprovement;

  const InlineOptimizationWidget({
    super.key,
    required this.optimizationSteps,
    required this.onRerunATSTest,
    required this.onDownloadCV,
    required this.onSaveToJobs,
    required this.onGenerateImprovedCV,
    required this.inlinePromptController,
    required this.isInlineGenerating,
    required this.hasInlinePromptText,
    required this.isImprovementExpanded,
    required this.onToggleImprovement,
  });

  @override
  State<InlineOptimizationWidget> createState() =>
      _InlineOptimizationWidgetState();
}

class _InlineOptimizationWidgetState extends State<InlineOptimizationWidget> {
  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.timeline, color: AppTheme.primaryCosmic, size: 28),
              const SizedBox(width: 12),
              Text('ATS Optimization Flow', style: AppTheme.headingMedium),
            ],
          ),
          const SizedBox(height: 20),
          ...widget.optimizationSteps.asMap().entries.map((entry) {
            final index = entry.key;
            final step = entry.value;
            return _buildInlineStep(step, index);
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildInlineStep(Map<String, dynamic> step, int index) {
    final type = step['type'] as String;
    final timestamp = step['timestamp'] as DateTime;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (index > 0) const SizedBox(height: 24),

        // Step header with timestamp
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.primaryCosmic.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                'Step ${index + 1}',
                style: AppTheme.bodySmall.copyWith(
                  color: AppTheme.primaryCosmic,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.neutralGray500,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Step content based on type
        if (type == 'ats_result') ...[
          _buildInlineATSResult(
              step['atsResult'] as ats.ATSResult, step['cvName'] as String),
        ] else if (type == 'cv_generated') ...[
          _buildInlineCVPreview(step['cvName'] as String),
        ],
      ],
    );
  }

  Widget _buildInlineATSResult(ats.ATSResult atsResult, String cvName) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ATS Score Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.primaryCosmic.withOpacity(0.1),
                AppTheme.primaryTeal.withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: AppTheme.primaryCosmic.withOpacity(0.2),
            ),
          ),
          child: Row(
            children: [
              Icon(Icons.analytics, color: AppTheme.primaryCosmic, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ATS Test Results',
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.primaryCosmic,
                      ),
                    ),
                    Text(
                      'CV: $cvName',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: ATSHelpers.getScoreColor(atsResult.overallScore),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${atsResult.overallScore}/100',
                  style: AppTheme.bodyMedium.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Use the extracted ATS result widget
        ATSResultWidget(atsResult: atsResult),

        const SizedBox(height: 20),

        // Continue Improving CV Expandable Section
        _buildContinueImprovingSection(),
      ],
    );
  }

  Widget _buildInlineCVPreview(String cvName) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // CV Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.successGreen.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: AppTheme.successGreen.withOpacity(0.2),
            ),
          ),
          child: Row(
            children: [
              Icon(Icons.description, color: AppTheme.successGreen, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Generated CV',
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.successGreen,
                      ),
                    ),
                    Text(
                      'CV: $cvName',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.successGreen,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'NEW',
                  style: AppTheme.bodySmall.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Use the CV preview widget
        CVPreviewWidget(cvFilename: cvName),
        const SizedBox(height: 16),

        // Action Buttons - NEW RESPONSIVE DESIGN WITH CONSISTENT TYPOGRAPHY!
        LayoutBuilder(
          builder: (context, constraints) {
            final isMobile = constraints.maxWidth < 500;

            return Column(
              children: [
                // First row: Re-run ATS Test and Download
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => widget.onRerunATSTest(cvName),
                        icon: Icon(
                          Icons.refresh_rounded,
                          size: isMobile ? 16 : 18,
                        ),
                        label: Text(
                          isMobile ? 'Re-run' : 'Re-run ATS Test',
                          style: AppTheme.buttonMedium.copyWith(
                            color: Colors.white,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryCosmic,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shadowColor: Colors.transparent,
                          shape: const RoundedRectangleBorder(
                            borderRadius: AppTheme.buttonRadius,
                          ),
                          padding: EdgeInsets.symmetric(
                            vertical: isMobile ? 12 : 16,
                            horizontal: isMobile ? 12 : 20,
                          ),
                          textStyle: AppTheme.buttonMedium,
                        ),
                      ),
                    ),
                    SizedBox(width: isMobile ? 8 : 16),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => widget.onDownloadCV(cvName),
                        icon: Icon(
                          Icons.download_rounded,
                          size: isMobile ? 16 : 18,
                        ),
                        label: Text(
                          'Download',
                          style: AppTheme.buttonMedium.copyWith(
                            color: AppTheme.neutralGray700,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.neutralGray100,
                          foregroundColor: AppTheme.neutralGray700,
                          elevation: 0,
                          shadowColor: Colors.transparent,
                          shape: const RoundedRectangleBorder(
                            borderRadius: AppTheme.buttonRadius,
                          ),
                          padding: EdgeInsets.symmetric(
                            vertical: isMobile ? 12 : 16,
                            horizontal: isMobile ? 12 : 20,
                          ),
                          textStyle: AppTheme.buttonMedium,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: isMobile ? 12 : 16),
                // Second row: Save to Jobs (full width)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => widget.onSaveToJobs(cvName),
                    icon: Icon(
                      Icons.save_rounded,
                      size: isMobile ? 16 : 18,
                    ),
                    label: Text(
                      'Save to Jobs',
                      style: AppTheme.buttonMedium.copyWith(
                        color: Colors.white,
                      ),
                      overflow: TextOverflow.ellipsis,
                      maxLines: 1,
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.successGreen,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shadowColor: Colors.transparent,
                      shape: const RoundedRectangleBorder(
                        borderRadius: AppTheme.buttonRadius,
                      ),
                      padding: EdgeInsets.symmetric(
                        vertical: isMobile ? 12 : 16,
                        horizontal: isMobile ? 16 : 24,
                      ),
                      textStyle: AppTheme.buttonMedium,
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ],
    );
  }

  Widget _buildContinueImprovingSection() {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          // Expandable Header
          InkWell(
            onTap: widget.onToggleImprovement,
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    widget.isImprovementExpanded
                        ? Icons.keyboard_arrow_down
                        : Icons.keyboard_arrow_right,
                    color: AppTheme.primaryCosmic,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Continue Improving CV',
                    style: AppTheme.bodyLarge.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AppTheme.primaryCosmic,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Expandable Content
          if (widget.isImprovementExpanded) ...[
            Container(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Additional Instructions',
                    style: AppTheme.bodyMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: widget.inlinePromptController,
                    maxLines: 3,
                    style: AppTheme.bodyMedium,
                    decoration: InputDecoration(
                      hintText:
                          'Enter specific improvements you\'d like to make...',
                      hintStyle: AppTheme.bodyMedium.copyWith(
                        color: AppTheme.neutralGray400,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: widget.isInlineGenerating ||
                              !widget.hasInlinePromptText
                          ? null
                          : widget.onGenerateImprovedCV,
                      icon: widget.isInlineGenerating
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.auto_fix_high),
                      label: Text(
                        widget.isInlineGenerating
                            ? 'Generating Improved CV...'
                            : 'Generate Improved CV',
                        style: AppTheme.buttonLarge.copyWith(
                          color: Colors.white,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryCosmic,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shadowColor: Colors.transparent,
                        shape: const RoundedRectangleBorder(
                          borderRadius: AppTheme.buttonRadius,
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 32,
                          vertical: 18,
                        ),
                        textStyle: AppTheme.buttonLarge,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
