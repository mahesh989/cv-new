import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import 'cv_preview_widget.dart';

/// Main card on the CV Generation screen.
///
/// Shows the description, an info banner, the generate/close buttons,
/// and — when content is available — the [CVPreviewWidget].
class CVGenerationCard extends StatelessWidget {
  final bool isGenerating;
  final String? tailoredCVContent;
  final bool isLoadingCV;
  final bool isEditMode;
  final TextEditingController editController;
  final VoidCallback onGenerate;
  final VoidCallback onClear;
  final ValueChanged<String> onContentChanged;
  final VoidCallback onToggleEditMode;
  final VoidCallback onAdditionalPrompt;
  final VoidCallback onRunATSAgain;

  const CVGenerationCard({
    super.key,
    required this.isGenerating,
    required this.tailoredCVContent,
    required this.isLoadingCV,
    required this.isEditMode,
    required this.editController,
    required this.onGenerate,
    required this.onClear,
    required this.onContentChanged,
    required this.onToggleEditMode,
    required this.onAdditionalPrompt,
    required this.onRunATSAgain,
  });

  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Tailored CV Generation',
            style: AppTheme.headingMedium.copyWith(
              color: AppTheme.primaryTeal,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Generate an optimized CV using our AI-powered framework. The system '
            'will automatically find and display the latest tailored CV from your '
            'analysis pipeline.',
            style: AppTheme.bodyMedium.copyWith(color: AppTheme.neutralGray600),
          ),
          const SizedBox(height: 20),

          // Info banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppTheme.primaryTeal.withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: AppTheme.primaryTeal, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'The system automatically finds the most recent tailored CV from '
                    'your analysis pipeline and displays it in the preview.',
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.primaryTeal,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Generate / Close buttons row
          Row(
            children: [
              Expanded(child: _buildGenerateButton()),
              if (tailoredCVContent != null) ...[
                const SizedBox(width: 12),
                _buildClearButton(),
              ],
            ],
          ),

          const SizedBox(height: 20),

          if (tailoredCVContent != null)
            CVPreviewWidget(
              isLoadingCV: isLoadingCV,
              tailoredCVContent: tailoredCVContent,
              isEditMode: isEditMode,
              editController: editController,
              onContentChanged: onContentChanged,
              onToggleEditMode: onToggleEditMode,
              onAdditionalPrompt: onAdditionalPrompt,
              onRunATSAgain: onRunATSAgain,
            ),
        ],
      ),
    );
  }

  Widget _buildGenerateButton() {
    return ElevatedButton(
      onPressed: isGenerating ? null : onGenerate,
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        backgroundColor: AppTheme.primaryTeal,
        disabledBackgroundColor: AppTheme.neutralGray300,
      ),
      child: isGenerating
          ? Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Generating CV...',
                  style: AppTheme.bodyMedium
                      .copyWith(color: Colors.white, fontWeight: FontWeight.w600),
                ),
              ],
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.auto_awesome, color: Colors.white, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Generate Tailored CV',
                  style: AppTheme.bodyMedium
                      .copyWith(color: Colors.white, fontWeight: FontWeight.w600),
                ),
              ],
            ),
    );
  }

  Widget _buildClearButton() {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: Colors.red[100],
        shape: BoxShape.circle,
        border: Border.all(color: Colors.red[300]!, width: 1),
      ),
      child: IconButton(
        onPressed: onClear,
        icon: Icon(Icons.close, color: Colors.red[600], size: 20),
        padding: EdgeInsets.zero,
        constraints: const BoxConstraints(),
      ),
    );
  }
}
