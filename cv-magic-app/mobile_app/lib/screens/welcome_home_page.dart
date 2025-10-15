import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../widgets/ai_model_selector.dart';
import '../widgets/ai_test_widget.dart';

class WelcomeHomePage extends StatelessWidget {
  final VoidCallback? onNavigateToCVMagic;
  
  const WelcomeHomePage({super.key, this.onNavigateToCVMagic});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildWelcomeCard(),
          const SizedBox(height: 20),
          const AIModelSelector(),
          const SizedBox(height: 20),
          const AITestWidget(),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildWelcomeCard() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: AppTheme.cosmicGradient,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.waving_hand,
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
                      'Ready to optimize your CV?',
                      style: AppTheme.headingSmall.copyWith(
                        color: AppTheme.primaryCosmic,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Select your AI model below and start creating amazing resumes!',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Proceed to create tailored CV button
          _buildProceedButton(),
        ],
      ),
    );
  }

  Widget _buildProceedButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onNavigateToCVMagic,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: Colors.blue.shade600,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: Colors.blue.shade200, width: 1),
          ),
          elevation: 2,
          shadowColor: Colors.blue.withOpacity(0.2),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Proceed to create tailored CV',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.blue.shade600,
              ),
            ),
            const SizedBox(width: 8),
            Icon(
              Icons.arrow_forward,
              color: Colors.blue.shade600,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }

  // Quick actions card was removed for backend-only focus
}
