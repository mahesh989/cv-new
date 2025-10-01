import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/theme/app_theme.dart';
import '../core/config/environment_config.dart';

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

  bool _isValidEmail(String email) {
    // Simple email validation - must contain @ and end with .com
    return RegExp(r'^[^@]+@[^@]+\.[^@]+$').hasMatch(email) &&
        email.endsWith('.com');
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Future<void> _handleRegistration() async {
    // Validate form
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Check if we have required fields
    if (_emailController.text.trim().isEmpty ||
        _passwordController.text.trim().isEmpty) {
      _showErrorDialog('Please enter both email and password');
      return;
    }

    // Validate email format
    if (!_isValidEmail(_emailController.text.trim())) {
      _showErrorDialog('Please enter a valid email address ending with .com');
      return;
    }

    setState(() => _isLoading = true);

    try {
      // Call backend registration endpoint
      final response = await http.post(
        Uri.parse('${EnvironmentConfig.baseUrl}/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': _emailController.text.trim(),
          'password': _passwordController.text,
          'full_name': _nameController.text.trim().isNotEmpty
              ? _nameController.text.trim()
              : null,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Store auth data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('is_logged_in', true);
        await prefs.setString('auth_token', data['access_token']);
        await prefs.setString('user_email', data['user']['email']);
        await prefs.setString('user_name', data['user']['name']);

        // Call the login callback
        widget.onLogin();
      } else {
        final errorData = json.decode(response.body);
        _showErrorDialog(errorData['detail'] ?? 'Registration failed');
      }
    } catch (e) {
      _showErrorDialog('Network error: ${e.toString()}');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _handleEmailAuth() async {
    // Validate form
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Check if we have required fields
    if (_emailController.text.trim().isEmpty ||
        _passwordController.text.trim().isEmpty) {
      _showErrorDialog('Please enter both email and password');
      return;
    }

    // Validate email format
    if (!_isValidEmail(_emailController.text.trim())) {
      _showErrorDialog('Please enter a valid email address ending with .com');
      return;
    }
    setState(() => _isLoading = true);

    try {
      // Call backend login endpoint
      final response = await http.post(
        Uri.parse('${EnvironmentConfig.baseUrl}/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': _emailController.text.isNotEmpty
              ? _emailController.text
              : 'demo@cvagent.com',
          'password': _passwordController.text.isNotEmpty
              ? _passwordController.text
              : 'demo123',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access_token'];

        // Save authentication data
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('is_logged_in', true);
        await prefs.setString('auth_token', accessToken);
        await prefs.setString(
          'user_email',
          _emailController.text.isNotEmpty
              ? _emailController.text
              : 'demo@cvagent.com',
        );
        await prefs.setString(
          'user_name',
          _nameController.text.isNotEmpty ? _nameController.text : 'Demo User',
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                _tabController.index == 0
                    ? '🎉 Welcome back!'
                    : '🎉 Account created successfully!',
              ),
              backgroundColor: AppTheme.primaryTeal,
              behavior: SnackBarBehavior.floating,
            ),
          );

          widget.onLogin();
        }
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Authentication failed: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
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
        Uri.parse('${EnvironmentConfig.baseUrl}/api/auth/login'),
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
                              _buildAuthNotice(isSmallScreen),
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
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Email is required';
              }
              if (!_isValidEmail(value.trim())) {
                return 'Please enter a valid email ending with .com';
              }
              return null;
            },
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
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Password is required';
              }
              return null;
            },
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
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Full Name (Optional)',
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
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Email is required';
              }
              if (!_isValidEmail(value.trim())) {
                return 'Please enter a valid email ending with .com';
              }
              return null;
            },
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
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Password is required';
              }
              return null;
            },
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: AppTheme.createGradientButton(
              text: 'Create Account',
              onPressed: _handleRegistration,
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

  Widget _buildAuthNotice(bool isSmallScreen) {
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
            size: isSmallScreen ? 18 : 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '🔐 Create an account to get started. Use admin@admin.com for admin access.',
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
