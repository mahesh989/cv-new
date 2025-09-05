/// Enhanced Flutter CV Agent App
/// Comprehensive improvements including architecture, state management, 
/// error handling, performance, and security

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Core architecture imports
import 'core/architecture.dart';
import 'core/state_management.dart';
import 'core/error_handling.dart' as error_handling;
import 'core/performance.dart';
import 'core/security.dart';

// Screen imports
import 'screens/home_page.dart';
import 'screens/demo_auth_screen.dart';

// Service imports
import 'services/job_database.dart';
import 'services/enhanced_api_service.dart';

// Theme imports
import 'theme/app_theme.dart';

// Global keys and instances
final GlobalKey<HomePageState> homePageKey = GlobalKey<HomePageState>();
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize error handling first
  error_handling.GlobalErrorHandler.initialize();

  try {
    // Initialize core systems
    await _initializeApp();
    
    // Run the app
    runApp(const EnhancedCVAgentApp());
  } catch (e, stackTrace) {
    Logger.error('Failed to initialize app', e, stackTrace);
    
    // Fallback app for critical errors
    runApp(MaterialApp(
      home: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text(
                'Failed to initialize app',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Error: $e',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14),
              ),
            ],
          ),
        ),
      ),
    ));
  }
}

/// Initialize all app systems
Future<void> _initializeApp() async {
  Logger.info('🚀 Initializing Enhanced CV Agent App...');
  
  final stopwatch = Stopwatch()..start();

  try {
    // Initialize in parallel where possible
    await Future.wait([
      // Core systems
      initializeStateManagement(),
      initializePerformanceOptimizations(),
      initializeSecurity(),
      
      // App-specific systems
      _initializeAppSystems(),
    ]);

    stopwatch.stop();
    Logger.info('✅ App initialization completed in ${stopwatch.elapsedMilliseconds}ms');

  } catch (e, stackTrace) {
    stopwatch.stop();
    Logger.error('❌ App initialization failed after ${stopwatch.elapsedMilliseconds}ms', e, stackTrace);
    rethrow;
  }
}

/// Initialize app-specific systems
Future<void> _initializeAppSystems() async {
  try {
    // Initialize database
    final db = JobDatabase();
    await db.migrateFromSharedPreferences();

    // Initialize enhanced API service
    final apiService = EnhancedApiService();

    // Set up service locator
    serviceLocator.registerSingleton<JobDatabase>(db);
    serviceLocator.registerSingleton<EnhancedApiService>(apiService);

    Logger.info('📱 App-specific systems initialized');
  } catch (e) {
    Logger.error('Failed to initialize app systems', e);
    rethrow;
  }
}

/// Enhanced CV Agent App with comprehensive improvements
class EnhancedCVAgentApp extends StatelessWidget {
  const EnhancedCVAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return StateProvider(
      appState: appState,
      analysisState: analysisState,
      uiState: uiState,
      child: MaterialApp(
        title: 'CV Agent - Enhanced',
        navigatorKey: navigatorKey,
        
        // Theme configuration
        theme: _buildLightTheme(),
        darkTheme: _buildDarkTheme(),
        themeMode: ThemeMode.system, // Responds to system dark mode
        
        // Home widget
        home: const AppWrapper(),
        
        // Global configurations
        debugShowCheckedModeBanner: false,
        
        // Navigation configuration
        onGenerateRoute: _onGenerateRoute,
        
        // Global builders
        builder: (context, child) {
          return MediaQuery(
            // Ensure text scaling doesn't break layouts
            data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
            child: child!,
          );
        },
      ),
    );
  }

  /// Build light theme
  ThemeData _buildLightTheme() {
    return ThemeData(
      brightness: Brightness.light,
      
      // Color scheme
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppTheme.primaryTeal,
        brightness: Brightness.light,
      ),
      
      // Visual density
      visualDensity: VisualDensity.adaptivePlatformDensity,
      
      // App bar theme
      appBarTheme: const AppBarTheme(
        backgroundColor: AppTheme.primaryTeal,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      
      // Button themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryTeal,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Card theme
      cardTheme: CardThemeData(
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.all(8),
      ),
      
      // Input decoration theme
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppTheme.primaryTeal, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      
      // Progress indicator theme
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppTheme.primaryTeal,
      ),
    );
  }

  /// Build dark theme
  ThemeData _buildDarkTheme() {
    return ThemeData(
      brightness: Brightness.dark,
      
      // Color scheme
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppTheme.primaryTeal,
        brightness: Brightness.dark,
      ),
      
      // Visual density
      visualDensity: VisualDensity.adaptivePlatformDensity,
      
      // Similar configurations as light theme but adapted for dark mode
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF1E1E1E),
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        systemOverlayStyle: SystemUiOverlayStyle.light,
      ),
    );
  }

  /// Handle route generation
  Route<dynamic>? _onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/':
        return MaterialPageRoute(builder: (_) => const AppWrapper());
      case '/home':
        return MaterialPageRoute(
          builder: (_) => HomePage(key: homePageKey, onLogout: () {}),
        );
      default:
        return null;
    }
  }
}

/// App wrapper with authentication and global state management
class AppWrapper extends StatefulWidget {
  const AppWrapper({super.key});

  @override
  State<AppWrapper> createState() => _AppWrapperState();
}

class _AppWrapperState extends State<AppWrapper> with LoadingStateMixin {
  bool _isLoggedIn = false;

  @override
  String get pageTitle => 'CV Agent';

  @override
  bool get showAppBar => false;

  @override
  void onPageLoad() {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    await executeWithLoading(() async {
      // Simulate auth check
      await Future.delayed(const Duration(milliseconds: 1500));

      // Check stored auth state
      final prefs = await SharedPreferences.getInstance();
      final isLoggedIn = prefs.getBool('demo_logged_in') ?? false;

      setState(() {
        _isLoggedIn = isLoggedIn;
      });

      // Update session security
      if (isLoggedIn) {
        sessionSecurity.startSession();
        
        // Log security event
        securityMonitor.logSecurityEvent(
          type: SecurityEventType.login,
          description: 'User logged in via stored credentials',
        );
      }

      Logger.info('🔐 Auth status checked: ${isLoggedIn ? 'Logged in' : 'Not logged in'}');
    });
  }

  void _onLogin() {
    setState(() {
      _isLoggedIn = true;
    });
    
    // Start security session
    sessionSecurity.startSession();
    
    // Log security event
    securityMonitor.logSecurityEvent(
      type: SecurityEventType.login,
      description: 'User successfully logged in',
    );
    
    Logger.info('✅ User logged in successfully');
  }

  Future<void> _onLogout() async {
    // Clear stored auth
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('demo_logged_in', false);
    
    // End security session
    sessionSecurity.endSession();
    
    // Log security event
    securityMonitor.logSecurityEvent(
      type: SecurityEventType.logout,
      description: 'User logged out',
    );
    
    setState(() {
      _isLoggedIn = false;
    });
    
    Logger.info('👋 User logged out');
  }

  @override
  Widget buildContent(BuildContext context) {
    return Column(
      children: [
        // Connection status indicator
        ListenableBuilder(
          listenable: appState,
          builder: (context, child) => error_handling.OfflineIndicator(
            isOnline: appState.isOnline,
          ),
        ),
        
        // Main content
        Expanded(
          child: _isLoggedIn
              ? HomePage(key: homePageKey, onLogout: _onLogout)
              : DemoAuthScreen(onLogin: _onLogin),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        body: error_handling.LoadingWidget(
          state: error_handling.LoadingState.initial('Initializing app...'),
          size: 48,
        ),
      );
    }

    if (hasError) {
      return Scaffold(
        body: error_handling.ErrorWidget(
          error: error_handling.AppError.unknown(error ?? 'Unknown error'),
          onRetry: () {
            clearError();
            onPageLoad();
          },
        ),
      );
    }

    return buildContent(context);
  }
}

/// Global app lifecycle observer
class AppLifecycleObserver extends WidgetsBindingObserver {
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    
    switch (state) {
      case AppLifecycleState.resumed:
        Logger.info('📱 App resumed');
        // Update activity for session security
        sessionSecurity.updateActivity();
        break;
        
      case AppLifecycleState.paused:
        Logger.info('📱 App paused');
        break;
        
      case AppLifecycleState.detached:
        Logger.info('📱 App detached');
        // Clean up resources
        memoryTracker.dispose();
        securityMonitor.dispose();
        break;
        
      default:
        break;
    }
  }

  @override
  void didChangeMetrics() {
    super.didChangeMetrics();
    // Handle screen size changes, keyboard appearance, etc.
  }

  @override
  Future<bool> didPopRoute() async {
    // Handle back button press
    Logger.info('🔙 Back button pressed');
    return false; // Let the system handle it
  }
}

/// Initialize app lifecycle observer
void _initializeAppLifecycle() {
  final observer = AppLifecycleObserver();
  WidgetsBinding.instance.addObserver(observer);
}
