import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Static information card explaining the available model categories.
class ModelInfoCard extends StatelessWidget {
  const ModelInfoCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppTheme.cosmicGradient.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.primaryCosmic.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.info_outline_rounded,
                  color: AppTheme.primaryCosmic, size: 18),
              const SizedBox(width: 8),
              Text(
                'Model Information',
                style: AppTheme.bodyMedium.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primaryCosmic,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '• The selected model will be used for all AI operations\n'
            '• GPT models are fast and versatile for most tasks\n'
            '• Claude models excel at analysis and reasoning\n'
            '• DeepSeek models offer excellent performance at low cost\n'
            '• You can change the model anytime from this screen',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.neutralGray700,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
