import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/theme/app_theme.dart';
import '../utils/responsive_utils.dart';
import '../widgets/mobile_bottom_nav.dart';
import 'welcome_home_page.dart';
import 'cv_magic_organized_page.dart';
import 'cv_generation_screen.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback? onLogout;

  const HomeScreen({super.key, this.onLogout});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  int _currentIndex = 0;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  String _userName = 'User';
  bool _shouldClearCVMagicResults = false;

  final WelcomeHomePage _welcomeHomePage = const WelcomeHomePage();
  late final CVMagicOrganizedPage _cvMagicPage;
  late final CVGenerationScreen _cvGenerationScreen;

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
      icon: Icons.auto_awesome,
      label: 'CV Generation',
      gradient: AppTheme.primaryGradient,
      color: AppTheme.primaryTeal,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _loadUserInfo();

    // Initialize CV Magic page with navigation callback
    _cvMagicPage = CVMagicOrganizedPage(
      onNavigateToCVGeneration: _navigateToCVGenerationTab,
      shouldClearResults: () => _shouldClearCVMagicResults,
      onResultsCleared: () => _shouldClearCVMagicResults = false,
    );

    // Initialize CV Generation screen with navigation callback
    _cvGenerationScreen = CVGenerationScreen(
      onNavigateToCVMagic: _navigateToCVMagicTab,
    );

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

  Future<void> _loadUserInfo() async {
    final prefs = await SharedPreferences.getInstance();
    final userName = prefs.getString('user_name') ?? 'User';
    setState(() {
      _userName = userName;
    });
  }

  Future<void> _handleLogout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Logout',
          style: AppTheme.headingMedium.copyWith(
            color: AppTheme.neutralGray800,
          ),
        ),
        content: Text(
          'Are you sure you want to logout?',
          style: AppTheme.bodyMedium,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(
              'Cancel',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.neutralGray600,
              ),
            ),
          ),
          AppTheme.createGradientButton(
            text: 'Logout',
            onPressed: () => Navigator.of(context).pop(true),
            width: 80,
            height: 36,
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_logged_in', false);

      if (widget.onLogout != null) {
        widget.onLogout!();
      }
    }
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  void _navigateToCVGenerationTab() {
    debugPrint('🚀 HomeScreen: Navigating to CV Generation tab (index 2)');
    _onTabTapped(2); // Switch to CV Generation tab (index 2)
  }

  void _navigateToCVMagicTab() {
    debugPrint(
        '🔄 HomeScreen: Navigating to CV Magic tab (index 1) and clearing results');
    _shouldClearCVMagicResults = true; // Set flag to clear results
    _onTabTapped(1); // Switch to CV Magic tab (index 1)
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      body: Column(
        children: [
          // App Bar - same as mt2
          _buildAppBar(),
          // Main Content - same navigation structure as mt2
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
                      child: _buildTabContentWithKeepAlive(),
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

  Widget _buildTabContentWithKeepAlive() {
    // Use IndexedStack to preserve state of all tabs
    return IndexedStack(
      index: _currentIndex,
      children: [
        _welcomeHomePage, // Index 0: Home
        _cvMagicPage, // Index 1: CV Magic
        _cvGenerationScreen, // Index 2: CV Generation
      ],
    );
  }

  Widget _buildAppBar() {
    return Container(
      decoration: const BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(20),
          bottomRight: Radius.circular(20),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Welcome back,',
                      style: AppTheme.bodyMedium.copyWith(
                        color: Colors.white70,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _userName,
                      style: AppTheme.headingLarge.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              PopupMenuButton<String>(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.more_vert,
                    color: Colors.white,
                  ),
                ),
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'profile',
                    child: Row(
                      children: [
                        const Icon(Icons.person, size: 20),
                        const SizedBox(width: 12),
                        Text('Profile', style: AppTheme.bodyMedium),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'logout',
                    child: Row(
                      children: [
                        const Icon(Icons.logout, size: 20, color: Colors.red),
                        const SizedBox(width: 12),
                        Text(
                          'Logout',
                          style:
                              AppTheme.bodyMedium.copyWith(color: Colors.red),
                        ),
                      ],
                    ),
                  ),
                ],
                onSelected: (value) {
                  if (value == 'logout') {
                    _handleLogout();
                  } else if (value == 'profile') {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('👤 Profile feature coming soon!'),
                        backgroundColor: AppTheme.primaryTeal,
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Desktop bottom nav bar - same as mt2
  Widget _buildCosmicBottomNavBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Container(
          height: 80,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(
              _tabData.length,
              (index) => _buildDesktopNavItem(index),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDesktopNavItem(int index) {
    final tabData = _tabData[index];
    final isSelected = _currentIndex == index;

    return Expanded(
      child: GestureDetector(
        onTap: () => _onTabTapped(index),
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 8),
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
          decoration: BoxDecoration(
            gradient: isSelected ? tabData.gradient : null,
            color: isSelected ? null : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? Colors.transparent : AppTheme.neutralGray300,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                tabData.icon,
                size: 20,
                color: isSelected ? Colors.white : Colors.grey[600],
              ),
              const SizedBox(width: 8),
              Text(
                tabData.label,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                  color: isSelected ? Colors.white : Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
