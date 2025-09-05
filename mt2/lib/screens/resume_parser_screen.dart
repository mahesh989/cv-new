import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import '../models/resume.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';
import '../utils/resume_parser_utils.dart';

class ResumeParserScreen extends StatefulWidget {
  const ResumeParserScreen({super.key});

  @override
  State<ResumeParserScreen> createState() => _ResumeParserScreenState();
}

class _ResumeParserScreenState extends State<ResumeParserScreen> {
  final ApiService _apiService = ApiService();
  Resume? _parsedResume;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Padding(
            padding: EdgeInsets.all(MediaQuery.of(context).size.width > 768 ? 24.0 : 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildHeader(),
                SizedBox(height: MediaQuery.of(context).size.height > 600 ? 24 : 16),
                Expanded(
                  child: SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (_parsedResume == null && !_isLoading) _buildUploadSection(),
                        if (_isLoading) _buildLoadingSection(),
                        if (_errorMessage != null) _buildErrorSection(),
                        if (_parsedResume != null) _buildResumeDisplay(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    final isSmallScreen = screenWidth < 600 || screenHeight < 600;
    
    return Container(
      padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.blue.shade600,
            Colors.purple.shade600,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            Icons.description_outlined,
            size: isSmallScreen ? 36 : 48,
            color: Colors.white,
          ),
          SizedBox(height: isSmallScreen ? 12 : 16),
          Text(
            'Resume Parser',
            style: TextStyle(
              fontSize: isSmallScreen ? 22 : 28,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          SizedBox(height: isSmallScreen ? 6 : 8),
          Text(
            'Upload your resume to extract structured information using AI',
            style: TextStyle(
              fontSize: isSmallScreen ? 14 : 16,
              color: Colors.white.withOpacity(0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildUploadSection() {
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(
              Icons.cloud_upload_outlined,
              size: 64,
              color: AppTheme.primaryCosmic,
            ),
            const SizedBox(height: 16),
            const Text(
              'Upload Your Resume',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Supported formats: PDF, DOCX\nAI will extract contact info, experience, education, and skills',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _pickAndParseResume,
                icon: const Icon(Icons.upload_file),
                label: const Text('Choose File'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryCosmic,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingSection() {
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryCosmic),
            ),
            const SizedBox(height: 16),
            const Text(
              'Parsing Resume...',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'AI is extracting structured information from your resume',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorSection() {
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: Colors.red.shade600,
            ),
            const SizedBox(height: 16),
            const Text(
              'Parsing Failed',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage ?? 'An error occurred while parsing the resume',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _errorMessage = null;
                });
              },
              child: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResumeDisplay() {
    List<Widget> sections = [];
    
    sections.add(_buildContactSection());
    sections.add(const SizedBox(height: 16));
    
    if (_parsedResume!.summary.isNotEmpty) {
      sections.add(_buildSummarySection());
      sections.add(const SizedBox(height: 16));
    }
    
    if (_parsedResume!.experience.isNotEmpty) {
      sections.add(_buildExperienceSection());
      sections.add(const SizedBox(height: 16));
    }
    
    if (_parsedResume!.education.isNotEmpty) {
      sections.add(_buildEducationSection());
      sections.add(const SizedBox(height: 16));
    }
    
    // Handle skills section - check if it's a dynamic section first
    if (_parsedResume!.dynamicSections.containsKey('skills')) {
      sections.add(_buildDynamicSection(_parsedResume!.dynamicSections['skills']!));
      sections.add(const SizedBox(height: 16));
    } else if (_parsedResume!.skills.isNotEmpty) {
      sections.add(_buildSkillsSection());
      sections.add(const SizedBox(height: 16));
    }
    
    if (_parsedResume!.projects.isNotEmpty) {
      sections.add(_buildProjectsSection());
      sections.add(const SizedBox(height: 16));
    }
    
    if (_parsedResume!.certifications.isNotEmpty) {
      sections.add(_buildCertificationsSection());
      sections.add(const SizedBox(height: 16));
    }
    
    if (_parsedResume!.languages.isNotEmpty) {
      sections.add(_buildLanguagesSection());
      sections.add(const SizedBox(height: 16));
    }
    
    // Add dynamic sections
    for (final entry in _parsedResume!.dynamicSections.entries) {
      if (entry.key != 'skills') { // Skip skills as it's handled above
        sections.add(_buildDynamicSection(entry.value));
        sections.add(const SizedBox(height: 16));
      }
    }
    
    sections.add(const SizedBox(height: 32)); // Extra bottom padding
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: sections,
    );
  }

  Widget _buildContactSection() {
    final contact = _parsedResume!.contact;
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.person, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Contact Information',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('Name', contact.name),
            _buildInfoRow('Email', contact.email),
            _buildInfoRow('Phone', contact.phone),
            _buildInfoRow('Location', contact.location),
            if (contact.links.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Links:',
                style:
                    AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: contact.links
                    .map((link) => Chip(
                          label: Text(link),
                          backgroundColor:
                              AppTheme.primaryCosmic.withOpacity(0.1),
                        ))
                    .toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSummarySection() {
    if (_parsedResume!.summary.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.description, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Summary',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _parsedResume!.summary,
              style: AppTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExperienceSection() {
    if (_parsedResume!.experience.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.work, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Experience',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._parsedResume!.experience
                .map((exp) => _buildExperienceItem(exp)),
          ],
        ),
      ),
    );
  }

  Widget _buildExperienceItem(Experience exp) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            exp.title,
            style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            '${exp.company} • ${exp.location}',
            style: AppTheme.bodyMedium.copyWith(color: Colors.grey.shade600),
          ),
          const SizedBox(height: 4),
          Text(
            exp.date,
            style: AppTheme.bodySmall.copyWith(color: Colors.grey.shade500),
          ),
          if (exp.bullets.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...exp.bullets.map((bullet) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                      Expanded(child: Text(bullet)),
                    ],
                  ),
                )),
          ],
        ],
      ),
    );
  }

  Widget _buildEducationSection() {
    if (_parsedResume!.education.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.school, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Education',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._parsedResume!.education.map((edu) => _buildEducationItem(edu)),
          ],
        ),
      ),
    );
  }

  Widget _buildEducationItem(Education edu) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            edu.degree,
            style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            edu.institution,
            style: AppTheme.bodyMedium.copyWith(color: Colors.grey.shade600),
          ),
          const SizedBox(height: 4),
          Text(
            edu.date,
            style: AppTheme.bodySmall.copyWith(color: Colors.grey.shade500),
          ),
        ],
      ),
    );
  }

  Widget _buildSkillsSection() {
    if (_parsedResume!.skills.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.psychology, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Skills',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _parsedResume!.skills
                  .map((skill) => Chip(
                        label: Text(skill),
                        backgroundColor:
                            AppTheme.primaryCosmic.withOpacity(0.1),
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProjectsSection() {
    if (_parsedResume!.projects.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.code, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Projects',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._parsedResume!.projects
                .map((project) => _buildProjectItem(project)),
          ],
        ),
      ),
    );
  }

  Widget _buildProjectItem(Project project) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            project.title,
            style: AppTheme.bodyLarge.copyWith(fontWeight: FontWeight.bold),
          ),
          if (project.description.isNotEmpty) ...[
            const SizedBox(height: 8),
            _buildProjectDescription(project.description),
          ],
          if (project.technologies.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Technologies:',
              style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 4),
            Wrap(
              spacing: 4,
              runSpacing: 4,
              children: project.technologies
                  .map((tech) => Chip(
                        label: Text(tech, style: const TextStyle(fontSize: 12)),
                        backgroundColor: Colors.blue.shade100,
                      ))
                  .toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCertificationsSection() {
    if (_parsedResume!.certifications.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.verified, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Certifications',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._parsedResume!.certifications
                .map((cert) => _buildCertificationItem(cert)),
          ],
        ),
      ),
    );
  }

  Widget _buildLanguagesSection() {
    if (_parsedResume!.languages.isEmpty) return const SizedBox.shrink();

    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.language, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  'Languages',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _parsedResume!.languages
                  .map((lang) => Chip(
                        label: Text(lang),
                        backgroundColor: Colors.orange.shade100,
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }


  Widget _buildInfoRow(String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProjectDescription(String description) {
    // Split description into sentences or bullet points
    List<String> lines = description.split('\n')
        .where((line) => line.trim().isNotEmpty)
        .map((line) => line.trim())
        .toList();

    // If it's a single paragraph, just show it as text
    if (lines.length == 1) {
      return Text(
        description,
        style: AppTheme.bodyMedium,
      );
    }

    // If multiple lines, show as bullet points
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: lines.map((line) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
            Expanded(child: Text(line, style: AppTheme.bodyMedium)),
          ],
        ),
      )).toList(),
    );
  }

  Widget _buildCertificationItem(String certification) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        children: [
          Icon(
            Icons.verified,
            color: Colors.green.shade600,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              certification,
              style: AppTheme.bodyMedium.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDynamicSection(ResumeSection section) {
    IconData sectionIcon = _getSectionIcon(section.title);
    
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(sectionIcon, color: AppTheme.primaryCosmic),
                const SizedBox(width: 8),
                Text(
                  section.title,
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildDynamicSectionContent(section),
          ],
        ),
      ),
    );
  }

  Widget _buildDynamicSectionContent(ResumeSection section) {
    if (section.type == 'bullets' || section.type == 'list') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: section.content.map((item) => Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
              Expanded(
                child: Text(
                  item.toString(),
                  style: AppTheme.bodyMedium,
                ),
              ),
            ],
          ),
        )).toList(),
      );
    } else if (section.type == 'chips') {
      return Wrap(
        spacing: 8,
        runSpacing: 8,
        children: section.content
            .map((item) => Chip(
                  label: Text(item.toString()),
                  backgroundColor: AppTheme.primaryCosmic.withOpacity(0.1),
                ))
            .toList(),
      );
    } else {
      // Default to text display
      return Text(
        section.content.join('\n'),
        style: AppTheme.bodyMedium,
      );
    }
  }

  IconData _getSectionIcon(String sectionTitle) {
    final title = sectionTitle.toLowerCase();
    if (title.contains('skill')) {
      return Icons.psychology;
    } else if (title.contains('achievement') || title.contains('award')) {
      return Icons.emoji_events;
    } else if (title.contains('certification') || title.contains('certificate')) {
      return Icons.verified;
    } else if (title.contains('publication')) {
      return Icons.article;
    } else if (title.contains('volunteer')) {
      return Icons.volunteer_activism;
    } else if (title.contains('language')) {
      return Icons.language;
    } else if (title.contains('competenc')) {
      return Icons.star;
    } else {
      return Icons.info_outline;
    }
  }

  Future<void> _pickAndParseResume() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'docx'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        await _parseResume(file);
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
      NotificationService.showError('Error picking file: $e');
    }
  }

  Future<void> _parseResume(PlatformFile file) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _parsedResume = null;
    });

    try {
      final result = await _apiService.parseResume(file);

      if (result.containsKey('error')) {
        throw Exception(result['error']);
      }

      // 🔧 Post-process the parsed data to fix bullet splitting and formatting issues
      final processedData = ResumeParserUtils.postProcessResumeData(result);
      
      // Add comprehensive debug logging
      print('=== RESUME PARSING DEBUG ===');
      print('\n--- RAW DATA ---');
      for (final key in result.keys) {
        print('Raw $key: ${result[key]}');
      }
      
      print('\n--- PROCESSED DATA ---');
      for (final key in processedData.keys) {
        print('Processed $key: ${processedData[key]}');
      }
      
      print('\n--- EXPERIENCE SECTION ---');
      print('Raw experience count: ${(result['experience'] as List?)?.length ?? 0}');
      print('Processed experience count: ${(processedData['experience'] as List?)?.length ?? 0}');
      if (processedData['experience'] is List) {
        final experiences = processedData['experience'] as List;
        for (int i = 0; i < experiences.length; i++) {
          final exp = experiences[i];
          print('Experience $i: ${exp['title']} at ${exp['company']}');
          print('  Bullets: ${(exp['bullets'] as List?)?.length ?? 0}');
          if (exp['bullets'] is List) {
            final bullets = exp['bullets'] as List;
            for (int j = 0; j < bullets.length && j < 3; j++) {
              print('    Bullet $j: ${bullets[j]}');
            }
          }
        }
      }
      
      print('\n--- SKILLS SECTION ---');
      print('Raw skills: ${result['skills']}');
      print('Processed skills: ${processedData['skills']}');
      
      print('\n--- PROJECTS SECTION ---');
      print('Raw projects: ${result['projects']}');
      print('Processed projects: ${processedData['projects']}');
      
      print('\n--- CERTIFICATIONS SECTION ---');
      print('Raw certifications: ${result['certifications']}');
      print('Processed certifications: ${processedData['certifications']}');
      
      print('\n--- EDUCATION SECTION ---');
      print('Raw education: ${result['education']}');
      print('Processed education: ${processedData['education']}');
      
      print('\n--- LANGUAGES SECTION ---');
      print('Raw languages: ${result['languages']}');
      print('Processed languages: ${processedData['languages']}');
      
      print('\n--- SUMMARY SECTION ---');
      print('Raw summary: ${result['summary']}');
      print('Processed summary: ${processedData['summary']}');
      
      print('\n--- CONTACT INFO ---');
      print('Raw contact_info: ${result['contact_info']}');
      print('Processed contact_info: ${processedData['contact_info']}');
      
      print('\n--- DYNAMIC SECTIONS ---');
      final knownKeys = {'contact_info', 'experience', 'education', 'skills', 'summary', 'certifications', 'projects', 'languages'};
      for (final key in processedData.keys) {
        if (!knownKeys.contains(key)) {
          print('Dynamic section $key: ${processedData[key]}');
        }
      }
      
      print('=== END DEBUG ===');

      final resume = Resume.fromJson(processedData);

      setState(() {
        _parsedResume = resume;
        _isLoading = false;
      });

      NotificationService.showSuccess('Resume parsed successfully!');
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
      NotificationService.showError('Failed to parse resume: $e');
    }
  }

  Future<void> _exportResume() async {
    if (_parsedResume == null) return;

    try {
      // Convert resume back to JSON for export
      final jsonData = {
        'contact_info': {
          'name': _parsedResume!.contact.name,
          'email': _parsedResume!.contact.email,
          'phone': _parsedResume!.contact.phone,
          'location': _parsedResume!.contact.location,
          'links': _parsedResume!.contact.links,
        },
        'summary': _parsedResume!.summary,
        'experience': _parsedResume!.experience
            .map((exp) => {
                  'company': exp.company,
                  'location': exp.location,
                  'title': exp.title,
                  'date': exp.date,
                  'bullets': exp.bullets,
                })
            .toList(),
        'education': _parsedResume!.education
            .map((edu) => {
                  'degree': edu.degree,
                  'institution': edu.institution,
                  'date': edu.date,
                })
            .toList(),
        'skills': _parsedResume!.skills,
        'certifications': _parsedResume!.certifications,
        'projects': _parsedResume!.projects
            .map((proj) => {
                  'title': proj.title,
                  'description': proj.description,
                  'technologies': proj.technologies,
                })
            .toList(),
        'languages': _parsedResume!.languages,
      };

      // In a real app, you would save this to a file
      // For now, we'll just show a success message
      NotificationService.showSuccess('Resume data ready for export!');

      // You could implement actual file download here
      // For example, using url_launcher to download the JSON
    } catch (e) {
      NotificationService.showError('Failed to export resume: $e');
    }
  }
}
