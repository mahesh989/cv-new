import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Core architecture imports
import '../core/architecture.dart';
import '../core/error_handling.dart';
import '../core/security.dart';

class DemoAuthScreen extends StatefulWidget {
  final VoidCallback onLogin;

  const DemoAuthScreen({super.key, required this.onLogin});

  @override
  State<DemoAuthScreen> createState() => _DemoAuthScreenState();
}

class _DemoAuthScreenState extends State<DemoAuthScreen>
    with TickerProviderStateMixin, LoadingStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();

  // Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _nameController = TextEditingController();

  // States
  bool _isGoogleLoading = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  String get pageTitle => 'Authentication';

  @override
  bool get showAppBar => false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _handleEmailAuth() async {
    await executeWithLoading(() async {
      // Log authentication attempt
      Logger.info('🔐 Demo authentication attempt');
      
      // Simulate authentication delay
      await Future.delayed(const Duration(seconds: 1));

      // Save demo login state with default values if fields are empty
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('demo_logged_in', true);
      await prefs.setString(
          'demo_user_email',
          _emailController.text.isNotEmpty
              ? _emailController.text
              : 'demo@cvagent.com');
      await prefs.setString('demo_user_name',
          _nameController.text.isNotEmpty ? _nameController.text : 'Demo User');

      // Start security session
      sessionSecurity.startSession();
      
      // Log security event
      securityMonitor.logSecurityEvent(
        type: SecurityEventType.login,
        description: 'Demo authentication successful',
        metadata: {
          'method': 'demo',
          'tab': _tabController.index == 0 ? 'signin' : 'signup',
        },
      );

      // Show success message
      if (mounted) {
        SnackBarHelper.showSuccess(
          context,
          _tabController.index == 0
              ? 'Welcome back!'
              : 'Account created successfully!',
        );

        // Call the login callback
        widget.onLogin();
      }
    });
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() => _isGoogleLoading = true);

    try {
      Logger.info('🔐 Google sign-in attempt');
      
      // Simulate Google sign-in delay
      await Future.delayed(const Duration(seconds: 2));

      // Save demo login state
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('demo_logged_in', true);
      await prefs.setString('demo_user_email', 'demo@gmail.com');
      await prefs.setString('demo_user_name', 'Demo User');

      // Start security session
      sessionSecurity.startSession();
      
      // Log security event
      securityMonitor.logSecurityEvent(
        type: SecurityEventType.login,
        description: 'Google sign-in successful',
        metadata: {'method': 'google'},
      );

      // Show success message
      if (mounted) {
        SnackBarHelper.showSuccess(
          context,
          'Welcome! Signed in with Google',
        );

        // Call the login callback
        widget.onLogin();
      }
    } catch (e) {
      Logger.error('Google sign-in failed', e);
      
      if (mounted) {
        SnackBarHelper.showError(
          context,
          'Google sign-in failed: ${e.toString()}',
        );
      }
    } finally {
      setState(() => _isGoogleLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isSmallScreen = MediaQuery.of(context).size.height < 700;
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.blue.shade50,
              Colors.purple.shade50,
              Colors.pink.shade50,
            ],
          ),
        ),
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              // Responsive design based on screen size
              final isMobile =
                  constraints.maxWidth < 600 || constraints.maxHeight < 600;

              return SingleChildScrollView(
                padding: EdgeInsets.only(
                  left: 24.0,
                  right: 24.0,
                  top: isMobile ? 16.0 : 24.0,
                  bottom: keyboardHeight > 0 ? 16.0 : 24.0,
                ),
                child: Center(
                  child: Card(
                    elevation: 8,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Container(
                      width: double.infinity,
                      constraints: const BoxConstraints(maxWidth: 400),
                      padding: EdgeInsets.all(isMobile ? 24.0 : 32.0),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // App Logo/Title - Responsive sizing
                          if (!isSmallScreen || keyboardHeight == 0) ...[
                            Container(
                              padding: EdgeInsets.all(isMobile ? 12 : 16),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade100,
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                Icons.description,
                                size: isMobile ? 36 : 48,
                                color: Colors.blue.shade700,
                              ),
                            ),
                            SizedBox(height: isMobile ? 16 : 24),
                          ],

                          Text(
                            'CV Agent',
                            style: Theme.of(context)
                                .textTheme
                                .headlineMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey.shade800,
                                  fontSize: isMobile ? 24 : null,
                                ),
                          ),
                          SizedBox(height: isMobile ? 4 : 8),

                          Text(
                            'AI-Powered Resume Optimization',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: Colors.grey.shade600,
                                  fontSize: isMobile ? 14 : null,
                                ),
                          ),
                          SizedBox(height: isMobile ? 20 : 32),

                          // Tab Bar
                          Container(
                            decoration: BoxDecoration(
                              color: Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: TabBar(
                              controller: _tabController,
                              indicator: BoxDecoration(
                                color: Colors.blue,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              labelColor: Colors.white,
                              unselectedLabelColor: Colors.grey.shade600,
                              tabs: const [
                                Tab(text: 'Sign In'),
                                Tab(text: 'Sign Up'),
                              ],
                            ),
                          ),
                          SizedBox(height: isMobile ? 16 : 24),

                          // Tab Content - Dynamic height instead of fixed
                          SizedBox(
                            height: isMobile
                                ? 240
                                : 280, // Dynamic height based on screen size
                            child: TabBarView(
                              controller: _tabController,
                              children: [
                                _buildSignInForm(),
                                _buildSignUpForm(),
                              ],
                            ),
                          ),

                          SizedBox(height: isMobile ? 12 : 16), // Reduced gap

                          // Divider
                          Row(
                            children: [
                              Expanded(
                                  child: Divider(color: Colors.grey.shade300)),
                              Padding(
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 16),
                                child: Text(
                                  'OR',
                                  style: TextStyle(
                                    color: Colors.grey.shade600,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                              Expanded(
                                  child: Divider(color: Colors.grey.shade300)),
                            ],
                          ),
                          SizedBox(height: isMobile ? 12 : 16), // Reduced gap

                          // Google Sign In Button
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed:
                                  _isGoogleLoading ? null : _handleGoogleSignIn,
                              icon: _isGoogleLoading
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2),
                                    )
                                  : Icon(Icons.g_mobiledata,
                                      size: 20, color: Colors.red),
                              label: Text(_isGoogleLoading
                                  ? 'Signing in...'
                                  : 'Continue with Google'),
                              style: OutlinedButton.styleFrom(
                                padding: EdgeInsets.symmetric(
                                  vertical: isMobile ? 12 : 16,
                                ),
                                side: BorderSide(color: Colors.grey.shade300),
                              ),
                            ),
                          ),
                          SizedBox(height: isMobile ? 12 : 16),

                          // Demo Notice
                          Container(
                            padding: EdgeInsets.all(isMobile ? 10 : 12),
                            decoration: BoxDecoration(
                              color: Colors.green.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.green.shade200),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.info_outline,
                                    color: Colors.green.shade700,
                                    size: isMobile ? 18 : 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'Demo Mode: Click Sign In to login instantly (no credentials required)',
                                    style: TextStyle(
                                      color: Colors.green.shade700,
                                      fontSize: isMobile ? 11 : 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
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

  Widget _buildSignInForm() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email (Optional)',
              prefixIcon: Icon(Icons.email_outlined),
              hintText: 'Leave empty for demo mode',
            ),
            keyboardType: TextInputType.emailAddress,
            // Removed validation - now optional
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Password (Optional)',
              prefixIcon: const Icon(Icons.lock_outlined),
              hintText: 'Leave empty for demo mode',
              suffixIcon: IconButton(
                icon: Icon(
                    _obscurePassword ? Icons.visibility : Icons.visibility_off),
                onPressed: () =>
                    setState(() => _obscurePassword = !_obscurePassword),
              ),
            ),
            obscureText: _obscurePassword,
            // Removed validation - now optional
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isLoading ? null : _handleEmailAuth,
              child: isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Sign In'),
            ),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Password reset email sent (demo)'),
                  backgroundColor: Colors.blue,
                ),
              );
            },
            child: const Text('Forgot Password?'),
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
              hintText: 'Leave empty for demo mode',
            ),
            // Removed validation - now optional
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(
              labelText: 'Email (Optional)',
              prefixIcon: Icon(Icons.email_outlined),
              hintText: 'Leave empty for demo mode',
            ),
            keyboardType: TextInputType.emailAddress,
            // Removed validation - now optional
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Password (Optional)',
              prefixIcon: const Icon(Icons.lock_outlined),
              hintText: 'Leave empty for demo mode',
              suffixIcon: IconButton(
                icon: Icon(
                    _obscurePassword ? Icons.visibility : Icons.visibility_off),
                onPressed: () =>
                    setState(() => _obscurePassword = !_obscurePassword),
              ),
            ),
            obscureText: _obscurePassword,
            // Removed validation - now optional
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isLoading ? null : _handleEmailAuth,
              child: isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Create Account'),
            ),
          ),
        ],
      ),
    );
  }
}
