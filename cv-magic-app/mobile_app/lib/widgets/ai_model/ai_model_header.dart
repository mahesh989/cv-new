import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/ai_model.dart';

/// Collapsible header row for the AI Model selector card.
class AIModelHeader extends StatelessWidget {
  final AIModel currentModel;
  final bool isExpanded;
  final VoidCallback onToggle;

  const AIModelHeader({
    super.key,
    required this.currentModel,
    required this.isExpanded,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onToggle,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: AppTheme.cosmicGradient,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryCosmic.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.smart_toy_rounded,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '🤖 AI Model Configuration',
                    style: AppTheme.headingSmall.copyWith(
                      color: AppTheme.primaryCosmic,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Currently using: ${currentModel.name}',
                    style:
                        AppTheme.bodySmall.copyWith(color: AppTheme.neutralGray600),
                  ),
                ],
              ),
            ),
            Icon(
              isExpanded ? Icons.expand_less : Icons.expand_more,
              color: AppTheme.primaryCosmic,
              size: 28,
            ),
          ],
        ),
      ),
    );
  }
}
