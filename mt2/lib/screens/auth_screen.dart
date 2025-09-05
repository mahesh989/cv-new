// TODO: Uncomment when Firebase Auth is ready

/*
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../theme/app_theme.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();
  
  // Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _nameController = TextEditingController();
  
  // Loading states
  bool _isLoading = false;
  bool _isGoogleLoading = false;
  
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
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    const SizedBox(height: 40),
                    Icon(
                      Icons.account_circle,
                      size: 80,
                      color: AppTheme.primaryCosmic,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Welcome to CV Maker',
                      style: AppTheme.headingLarge.copyWith(
                        color: AppTheme.primaryCosmic,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Sign in to sync your CVs across devices',
                      style: AppTheme.bodyMedium.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              
              // Tab bar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: TabBar(
                  controller: _tabController,
                  tabs: const [
                    Tab(text: 'Sign In'),
                    Tab(text: 'Sign Up'),
                  ],
                  labelColor: AppTheme.primaryCosmic,
                  unselectedLabelColor: AppTheme.neutralGray500,
                  indicatorColor: AppTheme.primaryCosmic,
                  indicatorWeight: 3,
                ),
              ),
              
              // Tab views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildSignInTab(),
                    _buildSignUpTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildSignInTab() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Google Sign In Button
          _buildGoogleSignInButton(),
          
          const SizedBox(height: 20),
          
          // Divider
          Row(
            children: [
              const Expanded(child: Divider()),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'OR',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray500,
                  ),
                ),
              ),
              const Expanded(child: Divider()),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Email/Password Form
          Form(
            key: _formKey,
            child: Column(
              children: [
                _buildEmailField(),
                const SizedBox(height: 16),
                _buildPasswordField(),
                const SizedBox(height: 20),
                _buildSignInButton(),
                const SizedBox(height: 16),
                _buildForgotPasswordButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSignUpTab() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Google Sign In Button
          _buildGoogleSignInButton(),
          
          const SizedBox(height: 20),
          
          // Divider
          Row(
            children: [
              const Expanded(child: Divider()),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'OR',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray500,
                  ),
                ),
              ),
              const Expanded(child: Divider()),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Sign Up Form
          Form(
            key: _formKey,
            child: Column(
              children: [
                _buildNameField(),
                const SizedBox(height: 16),
                _buildEmailField(),
                const SizedBox(height: 16),
                _buildPasswordField(),
                const SizedBox(height: 16),
                _buildConfirmPasswordField(),
                const SizedBox(height: 20),
                _buildSignUpButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildGoogleSignInButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _isGoogleLoading ? null : _signInWithGoogle,
        icon: _isGoogleLoading 
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.login, color: Colors.white),
        label: Text(_isGoogleLoading ? 'Signing in...' : 'Continue with Google'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red.shade600,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 2,
        ),
      ),
    );
  }
  
  Widget _buildEmailField() {
    return TextFormField(
      controller: _emailController,
      keyboardType: TextInputType.emailAddress,
      decoration: InputDecoration(
        labelText: 'Email',
        prefixIcon: const Icon(Icons.email),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter your email';
        }
        if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
          return 'Please enter a valid email';
        }
        return null;
      },
    );
  }
  
  Widget _buildPasswordField() {
    return TextFormField(
      controller: _passwordController,
      obscureText: true,
      decoration: InputDecoration(
        labelText: 'Password',
        prefixIcon: const Icon(Icons.lock),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter your password';
        }
        if (value.length < 6) {
          return 'Password must be at least 6 characters';
        }
        return null;
      },
    );
  }
  
  Widget _buildConfirmPasswordField() {
    return TextFormField(
      controller: _confirmPasswordController,
      obscureText: true,
      decoration: InputDecoration(
        labelText: 'Confirm Password',
        prefixIcon: const Icon(Icons.lock_outline),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please confirm your password';
        }
        if (value != _passwordController.text) {
          return 'Passwords do not match';
        }
        return null;
      },
    );
  }
  
  Widget _buildNameField() {
    return TextFormField(
      controller: _nameController,
      decoration: InputDecoration(
        labelText: 'Full Name',
        prefixIcon: const Icon(Icons.person),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter your name';
        }
        return null;
      },
    );
  }
  
  Widget _buildSignInButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _signInWithEmail,
        style: AppTheme.primaryButtonStyle.copyWith(
          padding: MaterialStateProperty.all(
            const EdgeInsets.symmetric(vertical: 16),
          ),
        ),
        child: _isLoading
          ? const CircularProgressIndicator(color: Colors.white)
          : const Text('Sign In'),
      ),
    );
  }
  
  Widget _buildSignUpButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _signUpWithEmail,
        style: AppTheme.primaryButtonStyle.copyWith(
          padding: MaterialStateProperty.all(
            const EdgeInsets.symmetric(vertical: 16),
          ),
        ),
        child: _isLoading
          ? const CircularProgressIndicator(color: Colors.white)
          : const Text('Create Account'),
      ),
    );
  }
  
  Widget _buildForgotPasswordButton() {
    return TextButton(
      onPressed: _resetPassword,
      child: Text(
        'Forgot Password?',
        style: AppTheme.bodyMedium.copyWith(
          color: AppTheme.primaryCosmic,
        ),
      ),
    );
  }
  
  Future<void> _signInWithGoogle() async {
    setState(() => _isGoogleLoading = true);
    
    try {
      final user = await AuthService.signInWithGoogle();
      if (user != null && mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      // Error handling is done in AuthService
    } finally {
      if (mounted) {
        setState(() => _isGoogleLoading = false);
      }
    }
  }
  
  Future<void> _signInWithEmail() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      final user = await AuthService.signInWithEmailPassword(
        _emailController.text.trim(),
        _passwordController.text,
      );
      
      if (user != null && mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      // Error handling is done in AuthService
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
  
  Future<void> _signUpWithEmail() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      final user = await AuthService.createAccountWithEmailPassword(
        _emailController.text.trim(),
        _passwordController.text,
        _nameController.text.trim(),
      );
      
      if (user != null && mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } catch (e) {
      // Error handling is done in AuthService
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
  
  Future<void> _resetPassword() async {
    if (_emailController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter your email address first'),
        ),
      );
      return;
    }
    
    await AuthService.sendPasswordResetEmail(_emailController.text.trim());
  }
}
*/
