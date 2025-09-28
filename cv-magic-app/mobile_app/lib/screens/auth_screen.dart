import 'package:flutter/material.dart';
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
  final _signInFormKey = GlobalKey<FormState>();
  final _signUpFormKey = GlobalKey<FormState>();

  // Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  final _usernameController = TextEditingController();

  // States
  bool _isLoading = false;
  bool _obscurePassword = true;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
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
    _usernameController.dispose();
    super.dispose();
  }

  Future<void> _handleAuth() async {
    final isSignUp = _tabController.index == 1;

    try {
      final formKey = isSignUp ? _signUpFormKey : _signInFormKey;

      if (formKey.currentState == null) {
        print('Form state is null for ${isSignUp ? "signup" : "signin"} form');
        return;
      }

      if (!formKey.currentState!.validate()) {
        return;
      }
    } catch (e) {
      print('Error in form validation: $e');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final endpoint = isSignUp ? 'register' : 'login';

      Map<String, dynamic> requestBody;
      if (isSignUp) {
        requestBody = {
          'username': _usernameController.text.trim(),
          'email': _emailController.text.trim(),
          'password': _passwordController.text.trim(),
          'full_name': _nameController.text.trim().isNotEmpty
              ? _nameController.text.trim()
              : null,
        };
      } else {
        requestBody = {
          'email': _emailController.text.trim(),
          'password': _passwordController.text.trim(),
        };
      }

      final response = await http
          .post(
            Uri.parse('${AppConfig.apiBaseUrl}/auth/$endpoint'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(requestBody),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);

        if (isSignUp) {
          // Registration successful
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(data['verification_message'] ??
                    'Account created successfully! Please check your email to verify your account.'),
                backgroundColor: AppTheme.primaryTeal,
                behavior: SnackBarBehavior.floating,
                duration: const Duration(seconds: 5),
              ),
            );
            _tabController.animateTo(0); // Switch to login tab
          }
        } else {
          // Login successful
          final accessToken = data['access_token'];
          final userEmail = _emailController.text.trim();
          final userName = _nameController.text.trim().isNotEmpty
              ? _nameController.text.trim()
              : 'User';

          // Save authentication data
          final prefs = await SharedPreferences.getInstance();
          await prefs.setBool('is_logged_in', true);
          await prefs.setString('auth_token', accessToken);
          await prefs.setString('user_email', userEmail);
          await prefs.setString('user_name', userName);

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('🎉 Welcome back!'),
                backgroundColor: AppTheme.primaryTeal,
                behavior: SnackBarBehavior.floating,
              ),
            );
            widget.onLogin();
          }
        }
      } else {
        final errorData = jsonDecode(response.body);
        String errorMessage = 'Authentication failed';

        if (errorData is Map<String, dynamic>) {
          if (errorData.containsKey('detail')) {
            if (errorData['detail'] is List) {
              // Handle Pydantic validation errors (422 status)
              final errors = errorData['detail'] as List;
              final errorMessages = <String>[];

              for (var error in errors) {
                if (error is Map<String, dynamic> && error.containsKey('msg')) {
                  errorMessages.add(error['msg']);
                }
              }

              if (errorMessages.isNotEmpty) {
                errorMessage = errorMessages.join('\n• ');
              }
            } else if (errorData['detail'] is String) {
              // Handle simple error messages (401, 400 status)
              errorMessage = errorData['detail'];
            }
          }
        }

        throw Exception(errorMessage);
      }
    } catch (e) {
      if (mounted) {
        String errorText = e.toString();
        if (errorText.startsWith('Exception: ')) {
          errorText = errorText.substring(11);
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ $errorText'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
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
          'Transform Your Resume with AI-Powered Analysis',
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
      height: isSmallScreen ? 400 : 450,
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
      key: _signInFormKey,
      child: SingleChildScrollView(
        child: Column(
          children: [
            TextFormField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                prefixIcon: Icon(Icons.email_outlined),
                hintText: 'your.email@example.com',
              ),
              keyboardType: TextInputType.emailAddress,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Email is required';
                }
                if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                    .hasMatch(value)) {
                  return 'Please enter a valid email address';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Password',
                prefixIcon: const Icon(Icons.lock_outlined),
                hintText: 'Your password',
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
                if (value == null || value.isEmpty) {
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
                onPressed: _handleAuth,
                isLoading: _isLoading,
                icon: Icons.login_rounded,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSignUpForm() {
    return Form(
      key: _signUpFormKey,
      child: SingleChildScrollView(
        child: Column(
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Full Name',
                prefixIcon: Icon(Icons.person_outlined),
                hintText: 'John Doe',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Full name is required';
                }
                final trimmedValue = value.trim();
                if (trimmedValue.length < 2) {
                  return 'Full name must be at least 2 characters long';
                }
                if (trimmedValue.length > 100) {
                  return 'Full name must be less than 100 characters';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _usernameController,
              decoration: const InputDecoration(
                labelText: 'Username',
                prefixIcon: Icon(Icons.account_circle_outlined),
                hintText: 'johndoe123',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Username is required';
                }
                final trimmedValue = value.trim();
                if (trimmedValue.length < 3) {
                  return 'Username must be at least 3 characters long';
                }
                if (trimmedValue.length > 50) {
                  return 'Username must be less than 50 characters';
                }
                if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(trimmedValue)) {
                  return 'Username can only contain letters, numbers, and underscores';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email Address',
                prefixIcon: Icon(Icons.email_outlined),
                hintText: 'your.email@example.com',
              ),
              keyboardType: TextInputType.emailAddress,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Email is required';
                }
                if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
                    .hasMatch(value)) {
                  return 'Please enter a valid email address';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Password',
                prefixIcon: const Icon(Icons.lock_outlined),
                hintText: 'Create a strong password',
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
                if (value == null || value.isEmpty) {
                  return 'Password is required';
                }
                if (value.length < 8) {
                  return 'Password must be at least 8 characters long';
                }
                if (value.length > 100) {
                  return 'Password must be less than 100 characters';
                }
                return null;
              },
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: AppTheme.createGradientButton(
                text: 'Create Account',
                onPressed: _handleAuth,
                isLoading: _isLoading,
                icon: Icons.person_add_rounded,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
