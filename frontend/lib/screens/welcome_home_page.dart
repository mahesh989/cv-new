import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/uniform_top_nav_bar.dart';

class WelcomeHomePage extends StatefulWidget {
  const WelcomeHomePage({super.key});

  @override
  State<WelcomeHomePage> createState() => _WelcomeHomePageState();
}

class _WelcomeHomePageState extends State<WelcomeHomePage>
    with TickerProviderStateMixin {
  late AnimationController _cardController;
  late AnimationController _fadeController;

  @override
  void initState() {
    super.initState();
    _cardController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );
    _fadeController = AnimationController(
      duration: AppTheme.slowAnimation,
      vsync: this,
    );

    _cardController.forward();
    _fadeController.forward();
  }

  @override
  void dispose() {
    _cardController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              const UniformTopNavBar(
                icon: Icons.home_rounded,
                title: 'Welcome Home',
                subtitle: 'Your complete CV optimization guide',
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: FadeTransition(
                    opacity: _fadeController,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildWelcomeSection(),
                        const SizedBox(height: 24),
                        _buildQuickStartSection(),
                        const SizedBox(height: 24),
                        _buildFeaturesSection(),
                        const SizedBox(height: 24),
                        _buildTechnicalCapabilitiesSection(),
                        const SizedBox(height: 16),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection() {
    return AnimatedBuilder(
      animation: _cardController,
      builder: (context, child) {
        return Transform.scale(
          scale: 0.8 + (0.2 * _cardController.value),
          child: AppTheme.createCard(
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: AppTheme.cosmicGradient,
                    shape: BoxShape.circle,
                    boxShadow: AppTheme.glowShadow,
                  ),
                  child: const Icon(
                    Icons.rocket_launch_rounded,
                    size: 48,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  '🚀 Welcome to AI CV Agent!',
                  style: AppTheme.headingMedium.copyWith(
                    color: AppTheme.primaryCosmic,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Text(
                  'The intelligent CV optimization platform that uses AI to analyze, tailor, and perfect your resume for every job application. Beat ATS systems and land more interviews!',
                  style: AppTheme.bodyLarge.copyWith(
                    color: AppTheme.neutralGray700,
                    height: 1.6,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuickStartSection() {
    return _buildSection(
      title: '⚡ Quick Start Guide',
      icon: Icons.flash_on_rounded,
      gradient: AppTheme.oceanGradient,
      children: [
        _buildStepCard(
          step: '1',
          title: 'Upload & Analyze CV',
          description:
              'Upload your CV in PDF/DOCX format. AI extracts skills, experience, and keywords automatically.',
          icon: Icons.upload_file_rounded,
          color: AppTheme.primaryTeal,
        ),
        _buildStepCard(
          step: '2',
          title: 'Add Job Description',
          description:
              'Paste job description or URL. AI analyzes requirements and extracts key skills.',
          icon: Icons.work_rounded,
          color: AppTheme.primaryNeon,
        ),
        _buildStepCard(
          step: '3',
          title: 'ATS Score & Analysis',
          description:
              'Get detailed ATS compatibility score with matched/missing skills analysis.',
          icon: Icons.analytics_rounded,
          color: AppTheme.primaryMagenta,
        ),
        _buildStepCard(
          step: '4',
          title: 'Generate Tailored CV',
          description:
              'AI creates job-specific CV with optimized keywords and improved ATS compatibility.',
          icon: Icons.auto_awesome_rounded,
          color: AppTheme.primaryEmerald,
        ),
      ],
    );
  }

  Widget _buildFeaturesSection() {
    return _buildSection(
      title: '✨ Amazing Features',
      icon: Icons.stars_rounded,
      gradient: AppTheme.royalGradient,
      children: [
        _buildFeatureCard(
          icon: Icons.psychology_rounded,
          title: 'Intelligent CV Analysis',
          description:
              'Advanced NLP and AI models extract skills, analyze compatibility, and identify optimization opportunities.',
          gradient: AppTheme.cosmicGradient,
        ),
        _buildFeatureCard(
          icon: Icons.radar_rounded,
          title: 'Smart ATS Scoring',
          description:
              'Proprietary ATS simulation engine provides accurate compatibility scores with detailed feedback.',
          gradient: AppTheme.forestGradient,
        ),
        _buildFeatureCard(
          icon: Icons.dashboard_rounded,
          title: 'Multi-Job Tracking',
          description:
              'Track applications across multiple jobs with performance analytics and progress monitoring.',
          gradient: AppTheme.sunsetGradient,
        ),
        _buildFeatureCard(
          icon: Icons.auto_fix_high_rounded,
          title: 'Iterative Improvement',
          description:
              'Continuous CV optimization with AI-powered suggestions and customizable enhancement prompts.',
          gradient: AppTheme.oceanGradient,
        ),
      ],
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required Gradient gradient,
    required List<Widget> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: gradient,
            borderRadius: AppTheme.buttonRadius,
            boxShadow: AppTheme.cardShadow,
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: Colors.white, size: 24),
              const SizedBox(width: 12),
              Text(
                title,
                style: AppTheme.headingSmall.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        ...children,
      ],
    );
  }

  Widget _buildStepCard({
    required String step,
    required String title,
    required String description,
    required IconData icon,
    required Color color,
  }) {
    return AppTheme.createCard(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Center(
              child: Text(
                step,
                style: AppTheme.headingSmall.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(icon, color: color, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      title,
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.neutralGray800,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTheme.bodyMedium.copyWith(
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

  Widget _buildFeatureCard({
    required IconData icon,
    required String title,
    required String description,
    required Gradient gradient,
  }) {
    return AppTheme.createCard(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: gradient,
              borderRadius: AppTheme.buttonRadius,
              boxShadow: AppTheme.glowShadow,
            ),
            child: Icon(icon, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTheme.bodyLarge.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTheme.bodyMedium.copyWith(
                    color: AppTheme.neutralGray600,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTechnicalCapabilitiesSection() {
    return _buildSection(
      title: '⚙️ Technical Capabilities',
      icon: Icons.engineering_rounded,
      gradient: AppTheme.primaryGradient,
      children: [
        _buildTechCard(
          '🧠 AI Models',
          'OpenAI GPT, spaCy NLP, and custom algorithms for skill extraction and CV optimization.',
          Icons.psychology_alt_rounded,
          AppTheme.primaryCosmic,
        ),
        _buildTechCard(
          '📄 File Support',
          'PDF and DOCX parsing with advanced text extraction and formatting preservation.',
          Icons.description_rounded,
          AppTheme.primaryNeon,
        ),
        _buildTechCard(
          '🔗 Web Integration',
          'Job URL parsing with automatic company and role extraction using web scraping.',
          Icons.link_rounded,
          AppTheme.primaryMagenta,
        ),
        _buildTechCard(
          '📊 SQLite Database',
          'Local data persistence with job tracking, ATS scores, and application analytics.',
          Icons.storage_rounded,
          AppTheme.primaryEmerald,
        ),
        _buildTechCard(
          '🎯 ATS Simulation',
          'Custom ATS scoring algorithm that mimics real applicant tracking systems.',
          Icons.speed_rounded,
          AppTheme.primaryAurora,
        ),
        _buildTechCard(
          '🔄 Iterative Enhancement',
          'Multi-round CV improvement with AI feedback loops and performance tracking.',
          Icons.refresh_rounded,
          AppTheme.accentCoral,
        ),
      ],
    );
  }

  Widget _buildTechCard(
      String title, String description, IconData icon, Color color) {
    return AppTheme.createCard(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTheme.bodyLarge.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray600,
                    height: 1.4,
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
