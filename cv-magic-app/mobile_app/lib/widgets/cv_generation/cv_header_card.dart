import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Static header card shown at the top of the CV Generation screen.
class CVHeaderCard extends StatelessWidget {
  const CVHeaderCard({super.key});

  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.auto_awesome, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'CV Generation',
                  style: AppTheme.headingSmall.copyWith(
                    color: AppTheme.primaryTeal,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Generate professional CVs with AI assistance',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
