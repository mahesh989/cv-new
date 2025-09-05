import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

// Core imports
import 'core/theme/app_theme.dart';
import 'services/ai_model_service.dart';
import 'screens/auth_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize AI Model Service with backend sync
  await aiModelService.initializeWithBackend();

  debugPrint('🚀 CV Agent Mobile App initialized');

  runApp(const CVAgentApp());
}

class CVAgentApp extends StatelessWidget {
  const CVAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<AIModelService>.value(
          value: aiModelService,
        ),
      ],
      child: MaterialApp(
        title: 'CV Agent',
        theme: AppTheme.lightTheme,
        home: const AuthWrapper(),
        debugShowCheckedModeBanner: false,
      ),
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
    try {
      // Simulate checking auth status
      await Future.delayed(const Duration(seconds: 1));

      // Check if user was previously logged in
      final prefs = await SharedPreferences.getInstance();
      final isLoggedIn = prefs.getBool('is_logged_in') ?? false;

      setState(() {
        _isLoggedIn = isLoggedIn;
        _isLoading = false;
      });

      debugPrint(
          '🔐 Auth status checked: ${isLoggedIn ? "Logged in" : "Logged out"}');
    } catch (e) {
      debugPrint('❌ Error checking auth status: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _onLogin() {
    setState(() {
      _isLoggedIn = true;
    });
    debugPrint('✅ User logged in successfully');

    // Sync AI model with backend after authentication
    aiModelService.syncAfterAuth();
  }

  void _onLogout() async {
    // Clear authentication data
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('is_logged_in');
    await prefs.remove('auth_token');
    await prefs.remove('user_email');
    await prefs.remove('user_name');

    setState(() {
      _isLoggedIn = false;
    });
    debugPrint('👋 User logged out');
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppTheme.neutralGray50,
        body: Container(
          decoration: const BoxDecoration(
            gradient: AppTheme.primaryGradient,
          ),
          child: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // App logo
                Icon(
                  Icons.description_rounded,
                  size: 80,
                  color: Colors.white,
                ),
                SizedBox(height: 24),

                // App title
                Text(
                  'CV Agent',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 8),

                // Subtitle
                Text(
                  'AI-Powered Resume Optimization',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                ),
                SizedBox(height: 48),

                // Loading indicator
                SpinKitFadingCircle(
                  color: Colors.white,
                  size: 50,
                ),
                SizedBox(height: 16),

                Text(
                  'Loading...',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (!_isLoggedIn) {
      return AuthScreen(onLogin: _onLogin);
    }

    return HomeScreen(onLogout: _onLogout);
  }
}
