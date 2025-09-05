import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/app_theme.dart';
import '../utils/responsive_utils.dart';
import '../widgets/mobile_bottom_nav.dart';
import '../widgets/ai_model_selector.dart';
import 'welcome_home_page.dart';
import 'cv_page.dart';
import 'my_prompts_page.dart';
import 'saved_jobs_page.dart';
import 'resume_parser_screen.dart';
import 'cv_generation_screen.dart';
import 'ats_tab_page.dart';

class HomePage extends StatefulWidget {
  final VoidCallback? onLogout;

  const HomePage({super.key, this.onLogout});

  @override
  State<HomePage> createState() => HomePageState();
}

class HomePageState extends State<HomePage> with TickerProviderStateMixin {
  int _currentIndex = 0;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  final WelcomeHomePage _welcomeHomePage = const WelcomeHomePage();
  final CvPage _cvPage = const CvPage();
  final MyPromptsPage _myPromptsPage = const MyPromptsPage();
  final SavedJobsPage _savedJobsPage = const SavedJobsPage();
  final ResumeParserScreen _resumeParserScreen = const ResumeParserScreen();
  final CVGenerationScreen _cvGenerationScreen = const CVGenerationScreen();
  final ATSTabPage _atsTabPage = const ATSTabPage();

  late final List<Widget> _pages = [
    _welcomeHomePage,
    _cvPage,
    _myPromptsPage,
    _savedJobsPage,
    _atsTabPage,
    _resumeParserScreen,
    _cvGenerationScreen,
  ];

  // 🎨 Beautiful tab data with cosmic icons and gradients
  final List<TabData> _tabData = [
    TabData(
      icon: Icons.home_rounded,
      label: 'Home',
      gradient: AppTheme.primaryGradient,
      color: AppTheme.primaryTeal,
    ),
    TabData(
      icon: Icons.description_rounded,
      label: 'CV Magic',
      gradient: AppTheme.primaryGradient,
      color: AppTheme.primaryTeal,
    ),
    TabData(
      icon: Icons.auto_awesome_rounded,
      label: 'My Prompts',
      gradient: AppTheme.royalGradient,
      color: AppTheme.primaryAurora,
    ),
    TabData(
      icon: Icons.bookmark_rounded,
      label: 'Saved Jobs',
      gradient: AppTheme.forestGradient,
      color: AppTheme.primaryEmerald,
    ),
    TabData(
      icon: Icons.analytics_rounded,
      label: 'ATS Test',
      gradient: AppTheme.oceanGradient,
      color: AppTheme.primaryNeon,
    ),
    TabData(
      icon: Icons.article_rounded,
      label: 'Resume Parser',
      gradient: AppTheme.royalGradient,
      color: AppTheme.primaryAurora,
    ),
    TabData(
      icon: Icons.auto_awesome_rounded,
      label: 'CV Generation',
      gradient: AppTheme.royalGradient,
      color: AppTheme.primaryAurora,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.smoothCurve,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.smoothCurve,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onTabTapped(int index) {
    if (_currentIndex == index) return;

    setState(() {
      _currentIndex = index;
    });

    // Trigger smooth transition animation
    _animationController.reset();
    _animationController.forward();
  }

  // Expose this method for global tab switching
  void switchToTab(int index) {
    _onTabTapped(index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: Column(
        children: [
          Expanded(
            child: SafeArea(
              bottom:
                  false, // Don't apply safe area to bottom - let bottom nav handle it
              child: AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  return FadeTransition(
                    opacity: _fadeAnimation,
                    child: SlideTransition(
                      position: _slideAnimation,
                      child: _buildTabContent(),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: context.isMobile
          ? MobileBottomNav(
              currentIndex: _currentIndex,
              onTabTapped: _onTabTapped,
              tabData: _tabData,
            )
          : _buildCosmicBottomNavBar(),
    );
  }

  Widget _buildTabContent() {
    switch (_currentIndex) {
      case 0:
        return SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.only(
            left: context.responsivePadding.left,
            right: context.responsivePadding.right,
            top: context.responsivePadding.top,
            bottom: context.isMobile
                ? 80
                : context
                    .responsivePadding.bottom, // Extra space for mobile nav
          ),
          child: _buildGuideSection(),
        );
      case 1:
      case 2:
      case 3:
      case 4:
      case 5:
      case 6:
        // All tabs now handle their own scaffold structure
        return _getTabWidget(_currentIndex);
      default:
        return Container();
    }
  }

  Widget _getTabWidget(int index) {
    switch (index) {
      case 1:
        return _cvPage;
      case 2:
        return _myPromptsPage;
      case 3:
        return _savedJobsPage;
      case 4:
        return _atsTabPage;
      case 5:
        return _resumeParserScreen;
      case 6:
        return _cvGenerationScreen;
      default:
        return Container();
    }
  }

  Widget _buildGuideSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Guide Section
        Container(
          padding: EdgeInsets.all(context.isMobile ? 16.0 : 24.0),
          margin: EdgeInsets.only(bottom: context.isMobile ? 16.0 : 24.0),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.blue.shade50,
                Colors.white,
                Colors.purple.shade50,
              ],
            ),
            borderRadius: BorderRadius.circular(context.isMobile ? 16 : 20),
            boxShadow: [
              BoxShadow(
                color: Colors.blue.withOpacity(0.1),
                spreadRadius: 2,
                blurRadius: 20,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: context.isMobile ? 12 : 16,
                  vertical: context.isMobile ? 10 : 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius:
                      BorderRadius.circular(context.isMobile ? 10 : 12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.blue.withOpacity(0.1),
                      spreadRadius: 1,
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: context.isMobile
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(6),
                                decoration: BoxDecoration(
                                  color: Colors.amber.shade100,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  Icons.lightbulb_outline,
                                  color: Colors.amber[800],
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  'How to Use CV Magic',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.grey[800],
                                  ),
                                ),
                              ),
                              if (widget.onLogout != null)
                                IconButton(
                                  onPressed: () async {
                                    final shouldLogout = await showDialog<bool>(
                                      context: context,
                                      builder: (context) => AlertDialog(
                                        title: const Text('Logout'),
                                        content: const Text(
                                            'Are you sure you want to logout?'),
                                        actions: [
                                          TextButton(
                                            onPressed: () =>
                                                Navigator.pop(context, false),
                                            child: const Text('Cancel'),
                                          ),
                                          TextButton(
                                            onPressed: () =>
                                                Navigator.pop(context, true),
                                            child: const Text('Logout'),
                                          ),
                                        ],
                                      ),
                                    );

                                    if (shouldLogout == true) {
                                      widget.onLogout!();
                                    }
                                  },
                                  icon: Icon(
                                    Icons.logout,
                                    color: Colors.red.shade600,
                                    size: 20,
                                  ),
                                  tooltip: 'Logout',
                                ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Follow these simple steps to optimize your CV',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      )
                    : Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.amber.shade100,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Icon(
                              Icons.lightbulb_outline,
                              color: Colors.amber[800],
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'How to Use CV Magic',
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.grey[800],
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Follow these simple steps to optimize your CV',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Add logout button
                          if (widget.onLogout != null)
                            IconButton(
                              onPressed: () async {
                                final shouldLogout = await showDialog<bool>(
                                  context: context,
                                  builder: (context) => AlertDialog(
                                    title: const Text('Logout'),
                                    content: const Text(
                                        'Are you sure you want to logout?'),
                                    actions: [
                                      TextButton(
                                        onPressed: () =>
                                            Navigator.pop(context, false),
                                        child: const Text('Cancel'),
                                      ),
                                      TextButton(
                                        onPressed: () =>
                                            Navigator.pop(context, true),
                                        child: const Text('Logout'),
                                      ),
                                    ],
                                  ),
                                );

                                if (shouldLogout == true) {
                                  widget.onLogout!();
                                }
                              },
                              icon: Icon(
                                Icons.logout,
                                color: Colors.red.shade600,
                              ),
                              tooltip: 'Logout',
                            ),
                        ],
                      ),
              ),
              const SizedBox(height: 20),
              _buildGuideItem(
                icon: Icons.upload_file,
                title: 'Upload Your CV',
                description:
                    'Start by uploading your current CV in PDF format. We\'ll help you optimize it for your target job.',
                color: Colors.blue,
              ),
              _buildGuideItem(
                icon: Icons.description,
                title: 'Add Job Description',
                description:
                    'Paste the job description you want to target. Our AI will analyze it to identify key requirements.',
                color: Colors.purple,
              ),
              _buildGuideItem(
                icon: Icons.auto_awesome,
                title: 'Get AI Analysis',
                description:
                    'Our AI will analyze your CV against the job requirements and provide detailed feedback.',
                color: Colors.orange,
              ),
              _buildGuideItem(
                icon: Icons.save_alt,
                title: 'Save & Track Progress',
                description:
                    'Save your optimized CV and track your application progress in the Saved Jobs section.',
                color: Colors.green,
              ),
            ],
          ),
        ),

        // AI Model Selector Section
        const SizedBox(height: 16),
        const AIModelSelector(),
      ],
    );
  }

  Widget _buildCosmicBottomNavBar() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.symmetric(vertical: 2.5),
      decoration: BoxDecoration(
        borderRadius: AppTheme.cardRadius,
        gradient: AppTheme.glowCardGradient,
        boxShadow: AppTheme.elevatedShadow,
        border: Border.all(
          color: AppTheme.primaryTeal.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: ClipRRect(
        borderRadius: AppTheme.cardRadius,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: List.generate(_tabData.length, (index) {
            final isSelected = _currentIndex == index;
            return _buildNavItem(index, isSelected);
          }),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, bool isSelected) {
    final tabData = _tabData[index];

    return Expanded(
      child: InkWell(
        onTap: () => _onTabTapped(index),
        borderRadius: AppTheme.buttonRadius,
        child: AnimatedContainer(
          duration: AppTheme.fastAnimation,
          curve: AppTheme.smoothCurve,
          margin: const EdgeInsets.symmetric(horizontal: 2, vertical: 1),
          padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 6),
          decoration: BoxDecoration(
            borderRadius: AppTheme.buttonRadius,
            gradient: isSelected ? tabData.gradient : null,
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: tabData.color.withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : null,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedContainer(
                duration: AppTheme.fastAnimation,
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isSelected
                      ? Colors.white.withOpacity(0.2)
                      : Colors.transparent,
                ),
                child: Icon(
                  tabData.icon,
                  size: isSelected ? 22 : 18,
                  color: isSelected ? Colors.white : tabData.color,
                ),
              ),
              const SizedBox(height: 2),
              AnimatedDefaultTextStyle(
                duration: AppTheme.fastAnimation,
                style: AppTheme.bodySmall.copyWith(
                  color: isSelected ? Colors.white : tabData.color,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  fontSize: isSelected ? 16 : 14,
                ),
                child: Text(
                  tabData.label,
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGuideItem({
    required IconData icon,
    required String title,
    required String description,
    required Color color,
  }) {
    return Container(
      padding: EdgeInsets.all(context.isMobile ? 14.0 : 18.0),
      margin: EdgeInsets.only(bottom: context.isMobile ? 12.0 : 16.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(
          ResponsiveUtils.getResponsiveValue(
            context,
            mobile: 12.0,
            tablet: 16.0,
            desktop: 20.0,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: context.isMobile
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(context.isMobile ? 8 : 10),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            color.withOpacity(0.2),
                            color.withOpacity(0.1),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        icon,
                        color: color,
                        size: context.responsiveIconSize,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        title,
                        style: TextStyle(
                          fontSize: ResponsiveUtils.getResponsiveFontSize(
                            context,
                            mobile: 16.0,
                            tablet: 18.0,
                            desktop: 20.0,
                          ),
                          fontWeight: FontWeight.w600,
                          color: color,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: ResponsiveUtils.getResponsiveFontSize(
                      context,
                      mobile: 14.0,
                      tablet: 15.0,
                      desktop: 16.0,
                    ),
                    height: 1.4,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            )
          : Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        color.withOpacity(0.2),
                        color.withOpacity(0.1),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: context.responsiveIconSize,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: ResponsiveUtils.getResponsiveFontSize(
                            context,
                            mobile: 16.0,
                            tablet: 18.0,
                            desktop: 20.0,
                          ),
                          fontWeight: FontWeight.w600,
                          color: color,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        description,
                        style: TextStyle(
                          fontSize: ResponsiveUtils.getResponsiveFontSize(
                            context,
                            mobile: 14.0,
                            tablet: 15.0,
                            desktop: 16.0,
                          ),
                          height: 1.4,
                          color: Colors.grey[600],
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
