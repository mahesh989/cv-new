import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../utils/responsive_utils.dart';

class CVGenerationScreen extends StatefulWidget {
  const CVGenerationScreen({super.key});

  @override
  State<CVGenerationScreen> createState() => _CVGenerationScreenState();
}

class _CVGenerationScreenState extends State<CVGenerationScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text(
          'CV Generation',
          style: AppTheme.headingMedium.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: AppTheme.primaryTeal,
        elevation: 0,
        centerTitle: true,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(context.isMobile ? 16.0 : 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
              Container(
                padding: EdgeInsets.all(context.isMobile ? 20.0 : 24.0),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppTheme.primaryTeal.withOpacity(0.1),
                      Colors.white,
                      AppTheme.primaryAurora.withOpacity(0.1),
                    ],
                  ),
                  borderRadius:
                      BorderRadius.circular(context.isMobile ? 16 : 20),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryTeal.withOpacity(0.1),
                      spreadRadius: 2,
                      blurRadius: 20,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            gradient: AppTheme.primaryGradient,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            Icons.auto_awesome_rounded,
                            color: Colors.white,
                            size: context.isMobile ? 24 : 28,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Tailored CV Generation',
                                style: AppTheme.headingMedium.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: AppTheme.primaryTeal,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Create personalized CVs optimized for specific job requirements',
                                style: AppTheme.bodyMedium.copyWith(
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Container(
                      padding: EdgeInsets.all(context.isMobile ? 16 : 20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: AppTheme.primaryTeal.withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '🚀 Coming Soon',
                            style: AppTheme.headingSmall.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primaryTeal,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'We\'re working on an amazing CV generation feature that will help you create tailored CVs based on job requirements and ATS analysis.',
                            style: AppTheme.bodyMedium.copyWith(
                              color: Colors.grey[700],
                            ),
                          ),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              Icon(
                                Icons.check_circle_rounded,
                                color: AppTheme.primaryEmerald,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'AI-powered CV customization',
                                  style: AppTheme.bodyMedium.copyWith(
                                    color: Colors.grey[700],
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(
                                Icons.check_circle_rounded,
                                color: AppTheme.primaryEmerald,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'Job-specific optimization',
                                  style: AppTheme.bodyMedium.copyWith(
                                    color: Colors.grey[700],
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(
                                Icons.check_circle_rounded,
                                color: AppTheme.primaryEmerald,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'ATS-friendly formatting',
                                  style: AppTheme.bodyMedium.copyWith(
                                    color: Colors.grey[700],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
