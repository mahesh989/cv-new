import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../core/theme/app_theme.dart';
import '../services/cv_tailoring_service.dart';
import '../utils/snackbar_helper.dart';

class CVGenerationScreen extends StatefulWidget {
  const CVGenerationScreen({super.key});

  @override
  State<CVGenerationScreen> createState() => _CVGenerationScreenState();
}

class _CVGenerationScreenState extends State<CVGenerationScreen> {
  bool _isGenerating = false;
  CVTailoringResult? _lastResult;
  String? _savedFilePath;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(),
          const SizedBox(height: 20),
          _buildCVGenerationCard(),
          if (_lastResult != null) ...[
            const SizedBox(height: 20),
            _buildResultCard(),
          ],
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

  Widget _buildCVGenerationCard() {
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
            'Generate an optimized CV using our AI-powered framework with sample data.',
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.neutralGray600,
            ),
          ),
          const SizedBox(height: 20),
          
          // Demo Info Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppTheme.primaryTeal.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: AppTheme.primaryTeal,
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'This demo uses sample CV and Google recommendation data to showcase the CV tailoring system.',
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
          
          // Generate Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isGenerating ? null : _generateTailoredCV,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                backgroundColor: AppTheme.primaryTeal,
                disabledBackgroundColor: AppTheme.neutralGray300,
              ),
              child: _isGenerating
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
                          style: AppTheme.bodyMedium.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.auto_awesome,
                          color: Colors.white,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Generate Tailored CV',
                          style: AppTheme.bodyMedium.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultCard() {
    if (_lastResult == null) return const SizedBox.shrink();

    final result = _lastResult!;
    final isSuccess = result.success;

    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isSuccess ? Icons.check_circle : Icons.error,
                color: isSuccess ? Colors.green : Colors.red,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                isSuccess ? 'CV Generated Successfully!' : 'Generation Failed',
                style: AppTheme.headingSmall.copyWith(
                  color: isSuccess ? Colors.green : Colors.red,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          if (isSuccess && result.tailoredCV != null) ...[
            _buildSuccessDetails(result.tailoredCV!),
          ] else ...[
            _buildErrorDetails(result.errorMessage ?? 'Unknown error occurred'),
          ],
          
          if (_savedFilePath != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.save, color: Colors.green, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Saved to: $_savedFilePath',
                      style: AppTheme.bodySmall.copyWith(
                        color: Colors.green.shade700,
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

  Widget _buildSuccessDetails(TailoredCV cv) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildInfoRow('Target Company', cv.targetCompany),
        _buildInfoRow('Target Role', cv.targetRole),
        if (cv.estimatedATSScore != null)
          _buildInfoRow('Estimated ATS Score', '${cv.estimatedATSScore}/100'),
        _buildInfoRow('Keywords Integrated', '${cv.keywordsIntegrated.length}'),
        _buildInfoRow('Framework Version', cv.frameworkVersion),
        
        const SizedBox(height: 12),
        Text(
          'Enhanced Content:',
          style: AppTheme.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
            color: AppTheme.neutralGray800,
          ),
        ),
        const SizedBox(height: 8),
        
        // Show first experience entry as example
        if (cv.experience.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.neutralGray200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${cv.experience.first.title} at ${cv.experience.first.company}',
                  style: AppTheme.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppTheme.neutralGray800,
                  ),
                ),
                const SizedBox(height: 8),
                ...cv.experience.first.bullets.take(2).map(
                  (bullet) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      '• $bullet',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildErrorDetails(String errorMessage) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Text(
        errorMessage,
        style: AppTheme.bodySmall.copyWith(
          color: Colors.red.shade700,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: AppTheme.bodySmall.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.neutralGray700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.neutralGray600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _generateTailoredCV() async {
    setState(() {
      _isGenerating = true;
      _lastResult = null;
      _savedFilePath = null;
    });

    try {
      // Use the example data from the backend
      final originalCV = _getSampleOriginalCV();
      final recommendations = _getSampleRecommendations();

      // Call the CV tailoring service
      final result = await CVTailoringService.tailorCV(
        originalCV: originalCV,
        recommendations: recommendations,
        customInstructions: 'Focus on scalability and system design experience',
        targetATSScore: 85,
      );

      // Save the tailored CV to a file for inspection
      if (result.success && result.tailoredCV != null) {
        final filePath = await _saveTailoredCVToFile(result.tailoredCV!);
        setState(() {
          _savedFilePath = filePath;
        });
        
        // Show success message
        if (mounted) {
          SnackbarHelper.showSuccess(
            context,
            'CV generated successfully! ATS Score: ${result.tailoredCV!.estimatedATSScore ?? "N/A"}/100',
          );
        }
      } else {
        // Show error message
        if (mounted) {
          SnackbarHelper.showError(
            context,
            'CV generation failed: ${result.errorMessage ?? "Unknown error"}',
          );
        }
      }

      setState(() {
        _lastResult = result;
      });
    } catch (e) {
      if (mounted) {
        SnackbarHelper.showError(
          context,
          'CV generation failed: ${e.toString()}',
        );
      }
      
      setState(() {
        _lastResult = CVTailoringResult.error(e.toString());
      });
    } finally {
      setState(() {
        _isGenerating = false;
      });
    }
  }

  Future<String> _saveTailoredCVToFile(TailoredCV cv) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final fileName = 'tailored_cv_${cv.targetCompany.toLowerCase().replaceAll(' ', '_')}_$timestamp.json';
      final file = File('${directory.path}/$fileName');
      
      final jsonString = jsonEncode(cv.toJson());
      await file.writeAsString(jsonString);
      
      return file.path;
    } catch (e) {
      debugPrint('Failed to save tailored CV: $e');
      return 'Error saving file: $e';
    }
  }

  // Sample data methods (using the same data as in the backend examples)
  Map<String, dynamic> _getSampleOriginalCV() {
    return {
      'contact': {
        'name': 'John Doe',
        'phone': '+1-555-0123',
        'email': 'john.doe@email.com',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'location': 'San Francisco, CA'
      },
      'education': [
        {
          'institution': 'University of California, Berkeley',
          'degree': 'Bachelor of Science in Computer Science',
          'location': 'Berkeley, CA',
          'graduation_date': 'May 2020',
          'gpa': '3.7'
        }
      ],
      'experience': [
        {
          'company': 'Tech Startup Inc.',
          'title': 'Software Engineer',
          'location': 'San Francisco, CA',
          'start_date': 'June 2020',
          'end_date': 'Present',
          'bullets': [
            'Developed web applications using React and Node.js',
            'Worked on database optimization projects',
            'Collaborated with team members on various projects'
          ]
        },
        {
          'company': 'Internship Corp',
          'title': 'Software Engineering Intern',
          'location': 'Palo Alto, CA',
          'start_date': 'June 2019',
          'end_date': 'August 2019',
          'bullets': [
            'Built mobile app features using React Native',
            'Participated in code reviews and team meetings'
          ]
        }
      ],
      'projects': [
        {
          'name': 'E-commerce Platform',
          'context': 'Personal project to learn full-stack development',
          'technologies': ['React', 'Node.js', 'MongoDB'],
          'bullets': [
            'Created online shopping platform with user authentication',
            'Implemented payment processing and order management'
          ]
        }
      ],
      'skills': [
        {
          'category': 'Programming Languages',
          'skills': ['JavaScript', 'Python', 'Java', 'SQL']
        },
        {
          'category': 'Frameworks & Libraries',
          'skills': ['React', 'Node.js', 'Express', 'MongoDB']
        },
        {
          'category': 'Tools & Technologies',
          'skills': ['Git', 'Docker', 'AWS', 'REST APIs']
        }
      ],
      'total_years_experience': 3
    };
  }

  Map<String, dynamic> _getSampleRecommendations() {
    return {
      'company': 'Google',
      'job_title': 'Senior Software Engineer',
      'missing_technical_skills': [
        'Kubernetes',
        'microservices',
        'system design',
        'distributed systems',
        'machine learning'
      ],
      'missing_soft_skills': [
        'leadership',
        'mentoring',
        'cross-functional collaboration'
      ],
      'missing_keywords': [
        'scalability',
        'performance optimization',
        'cloud architecture',
        'data structures',
        'algorithms'
      ],
      'technical_enhancements': [
        'Kubernetes orchestration',
        'microservices architecture',
        'system design patterns',
        'performance tuning'
      ],
      'soft_skill_improvements': [
        'technical leadership',
        'team mentoring',
        'stakeholder communication'
      ],
      'keyword_integration': [
        'scalable systems',
        'high-performance applications',
        'cloud-native solutions',
        'algorithmic optimization'
      ],
      'company_values': [
        'innovation',
        'collaboration',
        'user focus',
        'technical excellence'
      ],
      'industry_terminology': [
        'distributed computing',
        'large-scale systems',
        'infrastructure automation'
      ],
      'culture_alignment': [
        'data-driven decisions',
        'continuous learning',
        'collaborative problem-solving'
      ],
      'critical_gaps': [
        'system design experience',
        'scalability expertise',
        'distributed systems knowledge'
      ],
      'important_gaps': [
        'leadership experience',
        'mentoring skills',
        'performance optimization'
      ],
      'nice_to_have': [
        'machine learning experience',
        'open source contributions',
        'technical writing'
      ],
      'match_score': 65,
      'target_score': 85,
      'analysis_date': DateTime.now().toIso8601String()
    };
  }
}