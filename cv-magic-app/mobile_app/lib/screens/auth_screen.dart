import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/theme/app_theme.dart';
import '../core/config/app_config.dart';

class AuthScreen extends StatefulWidget {
  final VoidCallback onLogin;

  const AuthScreen({super.key, required this.onLogin});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();

  // Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();

  // States
  bool _isLoading = false;
  bool _isGoogleLoading = false;
  bool _obscurePassword = true;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

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
    _tabController.dispose();
    _animationController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _handleEmailAuth() async {
    print('🔵 [FRONTEND] Starting authentication process');
    setState(() => _isLoading = true);

    // Determine if this is login or registration based on tab index
    final isLogin = _tabController.index == 0;
    final endpoint = isLogin ? '/auth/login' : '/auth/register';
    print(
        '🔵 [FRONTEND] Tab index: ${_tabController.index}, isLogin: $isLogin, endpoint: $endpoint');

    try {
      // Get trimmed values
      final email = _emailController.text.trim();
      final password = _passwordController.text.trim();
      final name = _nameController.text.trim();

      print('🔵 [FRONTEND] Raw form values:');
      print('  - Email: "${_emailController.text}" -> trimmed: "$email"');
      print(
          '  - Password: "${_passwordController.text}" -> trimmed: "$password" (length: ${password.length})');
      print('  - Name: "${_nameController.text}" -> trimmed: "$name"');

      // Validate required fields with early return
      if (email.isEmpty) {
        print('🔴 [FRONTEND] Validation failed: Email is empty');
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                '❌ Email is required to create your account',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      if (password.isEmpty) {
        print('🔴 [FRONTEND] Validation failed: Password is empty');
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                '❌ Password is required for security',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      if (!isLogin && name.isEmpty) {
        print(
            '🔴 [FRONTEND] Validation failed: Name is empty for registration');
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                '❌ Name is required to personalize your account',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      // Additional validation for password length
      if (password.length < 6) {
        print(
            '🔴 [FRONTEND] Validation failed: Password too short (${password.length} characters)');
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                '❌ Password must be at least 6 characters for security',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      // Basic email format validation
      if (!email.contains('@') || !email.contains('.')) {
        print('🔴 [FRONTEND] Validation failed: Invalid email format');
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                '❌ Please enter a valid email address (e.g., user@example.com)',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 3),
            ),
          );
        }
        return;
      }

      print('✅ [FRONTEND] All validations passed');

      // Prepare request body based on endpoint
      Map<String, dynamic> requestBody;
      if (isLogin) {
        requestBody = {
          'email': email,
          'password': password,
        };
        print('🔵 [FRONTEND] Login request body: $requestBody');
      } else {
        // Registration requires name field
        requestBody = {
          'email': email,
          'password': password,
          'name': name,
        };
        print('🔵 [FRONTEND] Registration request body: $requestBody');
      }

      // Call backend endpoint
      final url = '${AppConfig.baseUrl}/api$endpoint';
      print('🔵 [FRONTEND] Making HTTP request to: $url');
      print(
          '🔵 [FRONTEND] Request headers: {\'Content-Type\': \'application/json\'}');
      print('🔵 [FRONTEND] Request body: ${jsonEncode(requestBody)}');

      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );

      print('🔵 [FRONTEND] HTTP response received:');
      print('  - Status code: ${response.statusCode}');
      print('  - Response body: ${response.body}');

      if (response.statusCode == 200) {
        print('✅ [FRONTEND] HTTP 200 - Success response');
        final data = jsonDecode(response.body);
        print('🔵 [FRONTEND] Parsed response data: $data');

        if (isLogin) {
          print('🔵 [FRONTEND] Processing login response');
          // Login response includes tokens
          final accessToken = data['access_token'];
          print(
              '🔵 [FRONTEND] Access token received: ${accessToken.substring(0, 20)}...');

          // Save authentication data
          print(
              '🔵 [FRONTEND] Saving authentication data to SharedPreferences');
          final prefs = await SharedPreferences.getInstance();
          await prefs.setBool('is_logged_in', true);
          await prefs.setString('auth_token', accessToken);
          await prefs.setString('user_email', email);
          await prefs.setString('user_name', name);
          print('✅ [FRONTEND] Authentication data saved successfully');

          if (mounted) {
            print('🔵 [FRONTEND] Showing success message and calling onLogin');
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  '🎉 Welcome back! AI features are now available.',
                  style: TextStyle(color: Colors.white),
                ),
                backgroundColor: AppTheme.primaryTeal,
                behavior: SnackBarBehavior.floating,
                duration: Duration(seconds: 3),
              ),
            );

            widget.onLogin();
          }
        } else {
          print('🔵 [FRONTEND] Processing registration response');
          // Registration response - no tokens, just success message
          if (mounted) {
            print(
                '🔵 [FRONTEND] Showing registration success message and switching to login tab');
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: const Text(
                  '🎉 Account created successfully! Please sign in to access AI features.',
                  style: TextStyle(color: Colors.white),
                ),
                backgroundColor: AppTheme.primaryTeal,
                behavior: SnackBarBehavior.floating,
                duration: const Duration(seconds: 4),
                action: SnackBarAction(
                  label: 'Sign In',
                  textColor: Colors.white,
                  onPressed: () {
                    ScaffoldMessenger.of(context).hideCurrentSnackBar();
                  },
                ),
              ),
            );

            // Switch to login tab after successful registration
            _tabController.animateTo(0);
          }
        }
      } else {
        print('🔴 [FRONTEND] HTTP Error - Status code: ${response.statusCode}');
        // Handle specific error responses
        String errorMessage = '${isLogin ? "Login" : "Registration"} failed';
        try {
          final errorData = jsonDecode(response.body);
          print('🔵 [FRONTEND] Error response data: $errorData');
          if (errorData['detail'] != null) {
            errorMessage = errorData['detail'].toString();
            print('🔵 [FRONTEND] Extracted error message: $errorMessage');
          }
        } catch (e) {
          // If we can't parse the error, use the status code
          errorMessage =
              '${isLogin ? "Login" : "Registration"} failed: ${response.statusCode}';
          print('🔴 [FRONTEND] Could not parse error response: $e');
        }
        print('🔴 [FRONTEND] Throwing exception with message: $errorMessage');
        throw Exception(errorMessage);
      }
    } catch (e) {
      print('🔴 [FRONTEND] Exception caught: $e');
      if (mounted) {
        print('🔵 [FRONTEND] Showing error message to user');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '❌ ${isLogin ? "Login" : "Registration"} failed: $e',
              style: const TextStyle(color: Colors.white),
            ),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 4),
            action: SnackBarAction(
              label: 'Try Again',
              textColor: Colors.white,
              onPressed: () {
                ScaffoldMessenger.of(context).hideCurrentSnackBar();
              },
            ),
          ),
        );
      }
    } finally {
      print(
          '🔵 [FRONTEND] Authentication process completed, setting loading to false');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() => _isGoogleLoading = true);

    try {
      // Call backend login endpoint with Google user credentials
      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': 'demo@gmail.com',
          'password': 'google123',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access_token'];

        // Save authentication data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('is_logged_in', true);
        await prefs.setString('auth_token', accessToken);
        await prefs.setString('user_email', 'demo@gmail.com');
        await prefs.setString('user_name', 'Demo User');

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🎉 Welcome! Signed in with Google'),
              backgroundColor: AppTheme.primaryTeal,
              behavior: SnackBarBehavior.floating,
            ),
          );

          widget.onLogin();
        }
      } else {
        throw Exception('Google sign-in failed: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Google sign-in failed: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isGoogleLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final screenHeight = MediaQuery.of(context).size.height;
    final isSmallScreen = screenHeight < 700;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppTheme.neutralGray50,
              Color(0xFFE0F2F1),
              Color(0xFFE3F2FD),
            ],
          ),
        ),
        child: SafeArea(
          child: AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              return FadeTransition(
                opacity: _fadeAnimation,
                child: SlideTransition(
                  position: _slideAnimation,
                  child: SingleChildScrollView(
                    padding: EdgeInsets.only(
                      left: 24.0,
                      right: 24.0,
                      top: isSmallScreen ? 16.0 : 32.0,
                      bottom: keyboardHeight > 0 ? 16.0 : 32.0,
                    ),
                    child: Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 400),
                        child: AppTheme.createCard(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              _buildHeader(isSmallScreen, keyboardHeight),
                              _buildTabBar(),
                              const SizedBox(height: 24),
                              _buildTabContent(isSmallScreen),
                              const SizedBox(height: 16),
                              _buildDivider(),
                              const SizedBox(height: 16),
                              _buildGoogleSignInButton(),
                              const SizedBox(height: 16),
                              _buildDemoNotice(isSmallScreen),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(bool isSmallScreen, double keyboardHeight) {
    if (isSmallScreen && keyboardHeight > 0) return const SizedBox.shrink();

    return Column(
      children: [
        Container(
          padding: EdgeInsets.all(isSmallScreen ? 16 : 20),
          decoration: const BoxDecoration(
            gradient: AppTheme.primaryGradient,
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.description_rounded,
            size: isSmallScreen ? 36 : 48,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'CV Agent',
          style: AppTheme.displaySmall.copyWith(
            color: AppTheme.primaryTeal,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'AI-Powered Resume Optimization',
          style: AppTheme.bodyMedium.copyWith(
            color: AppTheme.neutralGray600,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildTabBar() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: TabBar(
        controller: _tabController,
        indicator: BoxDecoration(
          gradient: AppTheme.primaryGradient,
          borderRadius: BorderRadius.circular(12),
        ),
        labelColor: Colors.white,
        unselectedLabelColor: AppTheme.neutralGray600,
        labelStyle: AppTheme.bodyMedium.copyWith(
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: AppTheme.bodyMedium,
        tabs: const [
          Tab(text: 'Sign In'),
          Tab(text: 'Sign Up'),
        ],
      ),
    );
  }

  Widget _buildTabContent(bool isSmallScreen) {
    return SizedBox(
      height: isSmallScreen ? 280 : 320,
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildSignInForm(),
          _buildSignUpForm(),
        ],
      ),
    );
  }

  Widget _buildSignInForm() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email *',
              prefixIcon: Icon(Icons.email_outlined),
              hintText: 'Enter your email address',
            ),
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Password *',
              prefixIcon: const Icon(Icons.lock_outlined),
              hintText: 'Enter your password',
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility : Icons.visibility_off,
                ),
                onPressed: () {
                  setState(() => _obscurePassword = !_obscurePassword);
                },
              ),
            ),
            obscureText: _obscurePassword,
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: AppTheme.createGradientButton(
              text: 'Sign In',
              onPressed: _handleEmailAuth,
              isLoading: _isLoading,
              icon: Icons.login_rounded,
            ),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('🔗 Password reset email sent (demo)'),
                  backgroundColor: AppTheme.primaryTeal,
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            child: Text(
              'Forgot Password?',
              style: AppTheme.labelMedium.copyWith(
                color: AppTheme.primaryTeal,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSignUpForm() {
    return Form(
      child: Column(
        children: [
          TextFormField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Full Name *',
              prefixIcon: Icon(Icons.person_outlined),
              hintText: 'Enter your full name',
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email *',
              prefixIcon: Icon(Icons.email_outlined),
              hintText: 'Enter your email address',
            ),
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Password *',
              prefixIcon: const Icon(Icons.lock_outlined),
              hintText: 'Enter your password (min 6 characters)',
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility : Icons.visibility_off,
                ),
                onPressed: () {
                  setState(() => _obscurePassword = !_obscurePassword);
                },
              ),
            ),
            obscureText: _obscurePassword,
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: AppTheme.createGradientButton(
              text: 'Create Account',
              onPressed: _handleEmailAuth,
              isLoading: _isLoading,
              icon: Icons.person_add_rounded,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Row(
      children: [
        const Expanded(child: Divider(color: AppTheme.neutralGray300)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'OR',
            style: AppTheme.labelMedium.copyWith(
              color: AppTheme.neutralGray600,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        const Expanded(child: Divider(color: AppTheme.neutralGray300)),
      ],
    );
  }

  Widget _buildGoogleSignInButton() {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: _isGoogleLoading ? null : _handleGoogleSignIn,
        icon: _isGoogleLoading
            ? const SpinKitFadingCircle(
                color: AppTheme.primaryTeal,
                size: 20,
              )
            : const Icon(
                Icons.g_mobiledata,
                size: 24,
                color: Colors.red,
              ),
        label: Text(
          _isGoogleLoading ? 'Signing in...' : 'Continue with Google',
          style: AppTheme.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
          side: const BorderSide(color: AppTheme.neutralGray300),
        ),
      ),
    );
  }

  Widget _buildDemoNotice(bool isSmallScreen) {
    return Container(
      padding: EdgeInsets.all(isSmallScreen ? 12 : 16),
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
            Icons.info_outline_rounded,
            color: AppTheme.primaryTeal,
            asize: isSmallScreen ? 18 : 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '✨ Demo Mode: Click Sign In to login instantly (no credentials required)',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.primaryTeal,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
