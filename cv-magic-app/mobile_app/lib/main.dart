import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';

// Core imports
import 'core/theme/app_theme.dart';
import 'firebase_options.dart';
import 'services/ai_model_service.dart';
import 'services/auth_service.dart';
import 'screens/auth_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialise Firebase before everything else
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Initialise AI Model Service with backend sync
  await aiModelService.initializeWithBackend();

  debugPrint('🚀 CV Agent Mobile App initialised');

  runApp(const CVAgentApp());
}

class CVAgentApp extends StatelessWidget {
  const CVAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<AIModelService>.value(value: aiModelService),
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

/// Listens to Firebase auth state changes and decides which screen to show.
///
/// This replaces the old SharedPreferences polling approach — Firebase tells
/// us instantly when the user signs in or out, including on cold start.
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    _setupAIServiceNotifications();
  }

  void _setupAIServiceNotifications() {
    aiModelService.setAuthRequiredCallback(() {
      if (mounted && authService.currentUser == null) {
        _showSnackBar(
          '🔐 AI features require login. Please sign in.',
          Colors.orange,
        );
      }
    });
  }

  void _onSignedIn() {
    aiModelService.syncAfterAuth();
    _showSnackBar('🎉 Welcome! AI features are now available.', Colors.green);
  }

  void _onSignedOut() {
    _showSnackBar('👋 Logged out. Sign in to use AI features.', Colors.blue);
  }

  void _showSnackBar(String message, Color color) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message, style: const TextStyle(color: Colors.white)),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: authService.authStateChanges,
      builder: (context, snapshot) {
        // Waiting for Firebase to emit the first auth state
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const _SplashScreen();
        }

        final user = snapshot.data;

        if (user != null) {
          // User is signed in
          return HomeScreen(
            onLogout: () async {
              await authService.signOut();
              _onSignedOut();
            },
          );
        }

        // User is not signed in
        return AuthScreen(
          onLogin: _onSignedIn,
        );
      },
    );
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.primaryGradient),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.description_rounded, size: 80, color: Colors.white),
              SizedBox(height: 24),
              Text(
                'CV Agent',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'AI-Powered Resume Optimisation',
                style: TextStyle(fontSize: 16, color: Colors.white70),
              ),
              SizedBox(height: 48),
              SpinKitFadingCircle(color: Colors.white, size: 50),
              SizedBox(height: 16),
              Text('Loading…', style: TextStyle(color: Colors.white70, fontSize: 14)),
            ],
          ),
        ),
      ),
    );
  }
}
