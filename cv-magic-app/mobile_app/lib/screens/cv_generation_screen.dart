import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/theme/app_theme.dart';

class CVGenerationScreen extends StatefulWidget {
  const CVGenerationScreen({super.key});

  @override
  State<CVGenerationScreen> createState() => _CVGenerationScreenState();
}

class _CVGenerationScreenState extends State<CVGenerationScreen> {
  bool _isGenerating = false;

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

  String? tailoredCVContent;
  bool _isLoadingCV = false;
  String? selectedCompany = 'Australia_for_UNHCR'; // TODO: Make this dynamic

  Future<void> _loadTailoredCV() async {
    setState(() {
      _isLoadingCV = true;
      _isGenerating = true;
      tailoredCVContent = null; // Reset content before loading
    });

    try {
      // Try to load the company-specific tailored CV
      final response = await http.get(
        Uri.parse(
            'http://localhost:8000/api/cv/read-tailored-cv/$selectedCompany'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          tailoredCVContent = data['content'] ?? 'No content available';
        });
      } else {
        setState(() {
          tailoredCVContent =
              'Failed to load tailored CV. Status: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        tailoredCVContent = 'Error loading tailored CV: $e';
      });
    } finally {
      setState(() {
        _isLoadingCV = false;
        _isGenerating = false;
      });
    }
  }

  String _formatTailoredCVContent(String content) {
    final lines = content.split('\n');
    final formattedLines = <String>[];

    for (final line in lines) {
      if (line.trim().isEmpty) {
        formattedLines.add('');
        continue;
      }

      // Skip metadata header section - filter out any metadata lines
      if (line.contains('TAILORED CV TEXT') ||
          line.contains('Target Company:') ||
          line.contains('Generated:') ||
          line.contains('ATS Score:') ||
          line.contains('Framework Version:') ||
          line.contains('CV GENERATION METADATA') ||
          line.startsWith('===') ||
          line.startsWith('=')) {
        continue;
      }

      // Format section headers (all caps words)
      if (line == line.toUpperCase() &&
          line.length > 3 &&
          !line.contains('•')) {
        formattedLines.add('');
        formattedLines.add('┌─ ' + line + ' ─' + '─' * (70 - line.length));
        formattedLines.add('');
        continue;
      }

      // Format bullet points
      if (line.startsWith('•')) {
        formattedLines.add('  ' + line);
        continue;
      }

      // Format job titles (lines ending with date ranges)
      if (line.contains(' – ') ||
          line.contains(' - ') ||
          (line.contains('Present') ||
              line.contains('2024') ||
              line.contains('2023') ||
              line.contains('2022') ||
              line.contains('2021') ||
              line.contains('2020'))) {
        formattedLines.add('');
        formattedLines.add('📅 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format company names (lines that might be company names)
      if (line.contains(',') &&
          (line.contains('Australia') ||
              line.contains('France') ||
              line.contains('Sydney') ||
              line.contains('Victoria') ||
              line.contains('Cergy'))) {
        formattedLines.add('🏢 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format education entries
      if (line.contains('University') ||
          line.contains('Master') ||
          line.contains('PhD')) {
        formattedLines.add('');
        formattedLines.add('🎓 ' + line);
        continue;
      }

      // Format contact information
      if (line.contains('@') ||
          line.contains('|') ||
          line.contains('LinkedIn') ||
          line.contains('GitHub') ||
          line.contains('Portfolio')) {
        formattedLines.add('📧 ' + line);
        continue;
      }

      // Regular content
      formattedLines.add(line);
    }

    return formattedLines.join('\n');
  }

  Widget _buildCVPreview() {
    if (_isLoadingCV) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (tailoredCVContent == null) {
      return const SizedBox.shrink();
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.preview, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                'Tailored CV Preview',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            height: 300,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[900], // Black background like original CV
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[700]!),
            ),
            child: SingleChildScrollView(
              child: SelectableText(
                _formatTailoredCVContent(tailoredCVContent!),
                style: TextStyle(
                  fontSize: 13,
                  height: 1.6,
                  fontFamily: 'monospace', // Monospace font like original CV
                  color: Colors.grey[100], // Light text like original CV
                ),
              ),
            ),
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
              onPressed: _isGenerating
                  ? null
                  : () async {
                      await _loadTailoredCV();
                    },
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
                            valueColor:
                                AlwaysStoppedAnimation<Color>(Colors.white),
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
          const SizedBox(height: 20),
          if (tailoredCVContent != null) _buildCVPreview(),
        ],
      ),
    );
  }
}
