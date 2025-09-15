import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class CVGenerationScreen extends StatelessWidget {
  const CVGenerationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(),
          const SizedBox(height: 20),
          _buildComingSoonCard(),
        ],
      ),
    );
  }

  Widget _buildHeaderCard() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.auto_awesome,
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
        ],
      ),
    );
  }

  Widget _buildComingSoonCard() {
    return AppTheme.createCard(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.construction,
                color: Colors.white,
                size: 48,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Coming Soon!',
              style: AppTheme.headingMedium.copyWith(
                color: AppTheme.primaryTeal,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'CV Generation features are currently under development.\nStay tuned for exciting updates!',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.neutralGray600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}