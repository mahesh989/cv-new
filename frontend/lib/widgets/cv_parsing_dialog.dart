import 'package:flutter/material.dart';
import '../models/resume.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';
import '../utils/resume_parser_utils.dart';
import '../state/session_state.dart';
import '../screens/cv_page.dart';

class CVParsingDialog extends StatefulWidget {
  final String cvFilename;

  const CVParsingDialog({
    super.key,
    required this.cvFilename,
  });

  @override
  State<CVParsingDialog> createState() => _CVParsingDialogState();
}

class _CVParsingDialogState extends State<CVParsingDialog> {
  final ApiService _apiService = ApiService();
  Resume? _parsedResume;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _checkCacheAndParseCV();
  }

  void _checkCacheAndParseCV() {
    // Check if we have cached results for this CV
    if (CvPage.cvParsingCache.containsKey(widget.cvFilename)) {
      final cachedData = CvPage.cvParsingCache[widget.cvFilename]!;
      setState(() {
        _parsedResume = Resume.fromJson(cachedData);
        _isLoading = false;
      });
      return;
    }

    // Check SessionState for last parsing result
    if (SessionState.lastCVParsingResult != null &&
        SessionState.originalCVFilename == widget.cvFilename) {
      setState(() {
        _parsedResume = Resume.fromJson(SessionState.lastCVParsingResult!);
        _isLoading = false;
      });
      return;
    }

    // No cached results, parse the CV
    _parseCV();
  }

  Future<void> _parseCV() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      final result = await _apiService.parseUploadedCV(widget.cvFilename);

      if (result.containsKey('error')) {
        throw Exception(result['error']);
      }

      // Post-process the parsed data
      final processedData = ResumeParserUtils.postProcessResumeData(result);

      setState(() {
        _parsedResume = Resume.fromJson(processedData);
        _isLoading = false;
      });

      // Cache the results for persistence
      CvPage.cvParsingCache[widget.cvFilename] = processedData;
      SessionState.lastCVParsingResult = processedData;
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
      NotificationService.showError('Error parsing CV: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        width: MediaQuery.of(context).size.width * 0.9,
        height: MediaQuery.of(context).size.height * 0.9,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          children: [
            _buildHeader(),
            Expanded(
              child: _buildContent(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.blue.shade600,
            Colors.purple.shade600,
          ],
        ),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(16),
          topRight: Radius.circular(16),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.description_outlined,
            size: 32,
            color: Colors.white,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'CV Parser Results',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Parsed from: ${widget.cvFilename}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(
              Icons.close,
              color: Colors.white,
              size: 24,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_isLoading) {
      return _buildLoadingSection();
    }

    if (_errorMessage != null) {
      return _buildErrorSection();
    }

    if (_parsedResume != null) {
      return _buildResumeDisplay();
    }

    return const SizedBox.shrink();
  }

  Widget _buildLoadingSection() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryCosmic),
          ),
          const SizedBox(height: 16),
          const Text(
            'Parsing CV...',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'AI is extracting structured information from your CV',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildErrorSection() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
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
              _errorMessage ?? 'An error occurred while parsing the CV',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _parseCV,
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

    if (_parsedResume!.skills.isNotEmpty) {
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

    sections.add(const SizedBox(height: 32));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: sections,
      ),
    );
  }

  Widget _buildContactSection() {
    final contact = _parsedResume!.contact;
    return _buildCard(
      icon: Icons.person,
      title: 'Contact Information',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildInfoRow('Name', contact.name),
          _buildInfoRow('Email', contact.email),
          _buildInfoRow('Phone', contact.phone),
          _buildInfoRow('Location', contact.location),
          if (contact.links.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Links:',
              style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.w600),
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
    );
  }

  Widget _buildSummarySection() {
    if (_parsedResume!.summary.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.description,
      title: 'Summary',
      child: Text(
        _parsedResume!.summary,
        style: AppTheme.bodyMedium,
      ),
    );
  }

  Widget _buildExperienceSection() {
    if (_parsedResume!.experience.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.work,
      title: 'Experience',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _parsedResume!.experience
            .map((exp) => _buildExperienceItem(exp))
            .toList(),
      ),
    );
  }

  Widget _buildEducationSection() {
    if (_parsedResume!.education.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.school,
      title: 'Education',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _parsedResume!.education
            .map((edu) => _buildEducationItem(edu))
            .toList(),
      ),
    );
  }

  Widget _buildSkillsSection() {
    // Check if we have structured skills in dynamicSections
    if (_parsedResume!.dynamicSections.containsKey('skills')) {
      final skillsSection = _parsedResume!.dynamicSections['skills']!;
      return _buildCard(
        icon: Icons.star,
        title: skillsSection.title.isNotEmpty ? skillsSection.title : 'Skills',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: skillsSection.content
              .map((skill) => _buildSkillBulletPoint(skill.toString()))
              .toList(),
        ),
      );
    }

    // Fallback to old format
    if (_parsedResume!.skills.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.star,
      title: 'Skills',
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: _parsedResume!.skills
            .map((skill) => Chip(
                  label: Text(skill),
                  backgroundColor: AppTheme.primaryCosmic.withOpacity(0.1),
                ))
            .toList(),
      ),
    );
  }

  Widget _buildSkillBulletPoint(String skill) {
    // Clean up the skill text and ensure proper bullet formatting
    String cleanSkill = skill.trim();

    // If it already starts with a bullet, use it as is
    if (cleanSkill.startsWith('•') || cleanSkill.startsWith('-')) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 8.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              cleanSkill.substring(0, 1), // Get the bullet character
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.primaryCosmic,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                cleanSkill.substring(1).trim(), // Get the rest of the text
                style: AppTheme.bodyMedium,
              ),
            ),
          ],
        ),
      );
    }

    // If it doesn't start with a bullet, add one
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '•',
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.primaryCosmic,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              cleanSkill,
              style: AppTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProjectsSection() {
    if (_parsedResume!.projects.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.build,
      title: 'Projects',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _parsedResume!.projects
            .map((project) => _buildProjectItem(project))
            .toList(),
      ),
    );
  }

  Widget _buildCertificationsSection() {
    if (_parsedResume!.certifications.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.verified,
      title: 'Certifications',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _parsedResume!.certifications
            .map((cert) => _buildCertificationItem(cert))
            .toList(),
      ),
    );
  }

  Widget _buildLanguagesSection() {
    if (_parsedResume!.languages.isEmpty) return const SizedBox.shrink();

    return _buildCard(
      icon: Icons.language,
      title: 'Languages',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _parsedResume!.languages
            .map((lang) => _buildLanguageItem(lang))
            .toList(),
      ),
    );
  }

  Widget _buildCard({
    required IconData icon,
    required String title,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: AppTheme.primaryCosmic),
              const SizedBox(width: 8),
              Text(
                title,
                style: AppTheme.headingMedium.copyWith(
                  color: AppTheme.primaryCosmic,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
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
            child: Text(value, style: AppTheme.bodyMedium),
          ),
        ],
      ),
    );
  }

  Widget _buildExperienceItem(Experience exp) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
            exp.title,
            style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.bold),
          ),
          if (exp.company.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              exp.company,
              style: AppTheme.bodyMedium.copyWith(color: Colors.grey.shade600),
            ),
          ],
          if (exp.date.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              exp.date,
              style: AppTheme.bodySmall.copyWith(color: Colors.grey.shade500),
            ),
          ],
          if (exp.bullets.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...exp.bullets
                .map<Widget>((bullet) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        '• $bullet',
                        style: AppTheme.bodySmall,
                      ),
                    ))
                .toList(),
          ],
        ],
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
            style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.bold),
          ),
          if (edu.institution.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              edu.institution,
              style: AppTheme.bodyMedium.copyWith(color: Colors.grey.shade600),
            ),
          ],
          if (edu.date.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              edu.date,
              style: AppTheme.bodySmall.copyWith(color: Colors.grey.shade500),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildProjectItem(Project project) {
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
          // Project title with context and date
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      project.title,
                      style: AppTheme.bodyMedium
                          .copyWith(fontWeight: FontWeight.bold),
                    ),
                    if (project.context.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        project.context,
                        style: AppTheme.bodyMedium.copyWith(
                          color: Colors.grey.shade600,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (project.date.isNotEmpty) ...[
                const SizedBox(width: 8),
                Text(
                  project.date,
                  style: AppTheme.bodyMedium.copyWith(
                    color: Colors.grey.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ],
          ),

          // Project description
          if (project.description.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              project.description,
              style: AppTheme.bodyMedium,
            ),
          ],

          // Project bullets
          if (project.bullets.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...project.bullets.map((bullet) => _buildProjectBullet(bullet)),
          ],

          // Technologies
          if (project.technologies.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 4,
              children: project.technologies
                  .map<Widget>((tech) => Chip(
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

  Widget _buildProjectBullet(String bullet) {
    // Clean up the bullet text and ensure proper bullet formatting
    String cleanBullet = bullet.trim();

    // If it already starts with a bullet, use it as is
    if (cleanBullet.startsWith('•') || cleanBullet.startsWith('-')) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 4.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              cleanBullet.substring(0, 1), // Get the bullet character
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.primaryCosmic,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                cleanBullet.substring(1).trim(), // Get the rest of the text
                style: AppTheme.bodyMedium,
              ),
            ),
          ],
        ),
      );
    }

    // If it doesn't start with a bullet, add one
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '•',
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.primaryCosmic,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              cleanBullet,
              style: AppTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCertificationItem(String cert) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Text(
        '• $cert',
        style: AppTheme.bodyMedium,
      ),
    );
  }

  Widget _buildLanguageItem(String lang) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      child: Text(
        '• $lang',
        style: AppTheme.bodyMedium,
      ),
    );
  }
}
