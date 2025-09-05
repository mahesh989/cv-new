import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Import screens
import 'screens/home_page.dart';
import 'screens/demo_auth_screen.dart';

// Import services and state
import 'state/session_state.dart';
import 'services/job_database.dart';
import 'services/enhanced_api_service.dart';

final GlobalKey<HomePageState> homePageKey = GlobalKey<HomePageState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize session state and database
  await SessionState.loadFromDisk();
  final db = JobDatabase();
  await db.migrateFromSharedPreferences();

  // Initialize enhanced API service with background support
  enhancedApiService; // This triggers initialization

  print('🚀 App initialized with SQLite database and background API service ready');

  runApp(const CVAgentApp());
}

class CVAgentApp extends StatelessWidget {
  const CVAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CV Agent',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            foregroundColor: Colors.white,
            backgroundColor: Colors.blue,
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: Colors.blue,
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            side: const BorderSide(color: Colors.blue, width: 2),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        ),
        cardTheme: CardThemeData(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          margin: const EdgeInsets.all(8),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
      ),
      home: const AuthWrapper(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoggedIn = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    // Simulate checking auth status
    await Future.delayed(const Duration(seconds: 1));

    // Check if user was previously logged in (demo purposes)
    final prefs = await SharedPreferences.getInstance();
    final isLoggedIn = prefs.getBool('demo_logged_in') ?? false;

    setState(() {
      _isLoggedIn = isLoggedIn;
      _isLoading = false;
    });
  }

  void _onLogin() {
    setState(() {
      _isLoggedIn = true;
    });
  }

  void _onLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('demo_logged_in', false);
    setState(() {
      _isLoggedIn = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (!_isLoggedIn) {
      return DemoAuthScreen(onLogin: _onLogin);
    }

    return HomePage(key: homePageKey, onLogout: _onLogout);
  }
}
