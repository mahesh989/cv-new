import 'package:flutter/material.dart';
import '../models/profile_model.dart';
import '../services/profile_service.dart';
import '../services/notification_service.dart';
import '../services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  final bool hideAppBar;

  const ProfileScreen({super.key, this.hideAppBar = false});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _locationController = TextEditingController();
  final _linkedinController = TextEditingController();
  final _githubController = TextEditingController();
  final _portfolioController = TextEditingController();
  final _websiteController = TextEditingController();

  bool _isLoading = false;
  bool _isSaving = false;
  UserProfile? _currentProfile;
  bool _profileExists = false;
  bool _hasFormData = false; // Track if user has entered any data

  @override
  void initState() {
    super.initState();
    _loadProfile();
    _setupFormListeners();
  }

  void _setupFormListeners() {
    // Listen to all text fields to track if user has entered data
    void _checkFormData() {
      final hasData = _fullNameController.text.trim().isNotEmpty ||
          _emailController.text.trim().isNotEmpty ||
          _phoneController.text.trim().isNotEmpty ||
          _locationController.text.trim().isNotEmpty ||
          _linkedinController.text.trim().isNotEmpty ||
          _githubController.text.trim().isNotEmpty ||
          _portfolioController.text.trim().isNotEmpty ||
          _websiteController.text.trim().isNotEmpty;

      if (_hasFormData != hasData) {
        setState(() {
          _hasFormData = hasData;
        });
      }
    }

    _fullNameController.addListener(_checkFormData);
    _emailController.addListener(_checkFormData);
    _phoneController.addListener(_checkFormData);
    _locationController.addListener(_checkFormData);
    _linkedinController.addListener(_checkFormData);
    _githubController.addListener(_checkFormData);
    _portfolioController.addListener(_checkFormData);
    _websiteController.addListener(_checkFormData);
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _locationController.dispose();
    _linkedinController.dispose();
    _githubController.dispose();
    _portfolioController.dispose();
    _websiteController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await ProfileService.getProfile();
      if (response.success && response.profile != null) {
        _currentProfile = response.profile;
        _profileExists = true;
        _populateFields(_currentProfile!);
        debugPrint(
            'Profile loaded successfully for user: ${_currentProfile!.userEmail}');
      } else {
        _profileExists = false;
        _currentProfile = null;
        debugPrint('No profile found, will create new one');
      }
    } catch (e) {
      debugPrint('Error loading profile: $e');
      _profileExists = false;
      _currentProfile = null;
      // Don't show error notification on load - user might not have profile yet
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _populateFields(UserProfile profile) {
    _fullNameController.text = profile.fullName;
    _emailController.text = profile.email;
    _phoneController.text = profile.phone;
    _locationController.text = profile.location;
    _linkedinController.text = profile.linkedinUrl ?? '';
    _githubController.text = profile.githubUrl ?? '';
    _portfolioController.text = profile.portfolioUrl ?? '';
    _websiteController.text = profile.websiteUrl ?? '';
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      final now = DateTime.now();

      if (_profileExists && _currentProfile != null) {
        // Update existing profile
        final updates = {
          'full_name': _fullNameController.text.trim(),
          'email': _emailController.text.trim(),
          'phone': _phoneController.text.trim(),
          'location': _locationController.text.trim(),
          'linkedin_url': _linkedinController.text.trim().isEmpty
              ? null
              : _linkedinController.text.trim(),
          'github_url': _githubController.text.trim().isEmpty
              ? null
              : _githubController.text.trim(),
          'portfolio_url': _portfolioController.text.trim().isEmpty
              ? null
              : _portfolioController.text.trim(),
          'website_url': _websiteController.text.trim().isEmpty
              ? null
              : _websiteController.text.trim(),
        };

        final response = await ProfileService.updateProfile(updates);
        if (response.success) {
          NotificationService.showSuccess('Profile updated successfully!');
          _currentProfile = response.profile;
        } else {
          NotificationService.showError(response.message);
          // If update fails, try creating a new profile
          debugPrint('Profile update failed, attempting to create new profile');
          _profileExists = false;
          _currentProfile = null;
          // Fall through to create new profile
        }
      }

      if (!_profileExists || _currentProfile == null) {
        // Create new profile - use authenticated user's email
        final authenticatedEmail = await AuthService.getUserEmail();
        if (authenticatedEmail == null) {
          NotificationService.showError('Authentication required');
          return;
        }

        final profile = UserProfile(
          userEmail: authenticatedEmail,
          fullName: _fullNameController.text.trim(),
          email: _emailController.text.trim(),
          phone: _phoneController.text.trim(),
          location: _locationController.text.trim(),
          linkedinUrl: _linkedinController.text.trim().isEmpty
              ? null
              : _linkedinController.text.trim(),
          githubUrl: _githubController.text.trim().isEmpty
              ? null
              : _githubController.text.trim(),
          portfolioUrl: _portfolioController.text.trim().isEmpty
              ? null
              : _portfolioController.text.trim(),
          websiteUrl: _websiteController.text.trim().isEmpty
              ? null
              : _websiteController.text.trim(),
          createdAt: now,
          updatedAt: now,
        );

        final response = await ProfileService.createProfile(profile);
        if (response.success) {
          NotificationService.showSuccess('Profile created successfully!');
          _currentProfile = response.profile;
          _profileExists = true;
        } else {
          NotificationService.showError(response.message);
        }
      }
    } catch (e) {
      debugPrint('Error saving profile: $e');
      NotificationService.showError('Failed to save profile');
    } finally {
      setState(() {
        _isSaving = false;
      });
    }
  }

  Future<void> _deleteProfile() async {
    final confirmed = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.8),
      useRootNavigator: true,
      builder: (context) => WillPopScope(
        onWillPop: () async => false,
        child: Material(
          type: MaterialType.transparency,
          child: AlertDialog(
          title: const Text('Delete Profile'),
          content: const Text(
              'Are you sure you want to delete your profile? This action cannot be undone.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Delete'),
            ),
          ],
          ),
        ),
      ),
    );

    if (confirmed == true) {
      try {
        final response = await ProfileService.deleteProfile();
        if (response.success) {
          NotificationService.showSuccess('Profile deleted successfully');
          _currentProfile = null;
          _profileExists = false;
          _clearFields();
        } else {
          NotificationService.showError(response.message);
        }
      } catch (e) {
        debugPrint('Error deleting profile: $e');
        NotificationService.showError('Failed to delete profile');
      }
    }
  }

  void _clearFields() {
    _fullNameController.clear();
    _emailController.clear();
    _phoneController.clear();
    _locationController.clear();
    _linkedinController.clear();
    _githubController.clear();
    _portfolioController.clear();
    _websiteController.clear();
  }

  String? _validateRequired(String? value, String fieldName) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }

  String? _validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Email is required';
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return 'Please enter a valid email address';
    }
    return null;
  }

  String? _validateUrl(String? value, String fieldName) {
    if (value != null && value.trim().isNotEmpty) {
      final uri = Uri.tryParse(value.trim());
      if (uri == null || !uri.hasAbsolutePath) {
        return 'Please enter a valid URL for $fieldName';
      }
    }
    return null;
  }

  Widget _buildProfileContent() {
    return _isLoading
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.person,
                                color: Theme.of(context).primaryColor,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Personal Information',
                                style: Theme.of(context)
                                    .textTheme
                                    .titleLarge
                                    ?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'This information will be used in all your CV generations. Update it here and all future CVs will use the new information.',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: Colors.grey.shade600,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Required Fields
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Required Information',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.red.shade700,
                                ),
                          ),
                          const SizedBox(height: 16),

                          // Full Name
                          TextFormField(
                            controller: _fullNameController,
                            decoration: const InputDecoration(
                              labelText: 'Full Name *',
                              hintText: 'John Smith',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.person),
                            ),
                            validator: (value) =>
                                _validateRequired(value, 'Full name'),
                          ),
                          const SizedBox(height: 16),

                          // Email
                          TextFormField(
                            controller: _emailController,
                            decoration: const InputDecoration(
                              labelText: 'Email *',
                              hintText: 'john@example.com',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.email),
                            ),
                            keyboardType: TextInputType.emailAddress,
                            validator: _validateEmail,
                          ),
                          const SizedBox(height: 16),

                          // Phone
                          TextFormField(
                            controller: _phoneController,
                            decoration: const InputDecoration(
                              labelText: 'Phone *',
                              hintText: '+61 400 123 456',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.phone),
                            ),
                            keyboardType: TextInputType.phone,
                            validator: (value) =>
                                _validateRequired(value, 'Phone'),
                          ),
                          const SizedBox(height: 16),

                          // Location
                          TextFormField(
                            controller: _locationController,
                            decoration: const InputDecoration(
                              labelText: 'Location *',
                              hintText: 'Sydney, NSW, Australia',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.location_on),
                            ),
                            validator: (value) =>
                                _validateRequired(value, 'Location'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Optional Fields
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Optional Links',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue.shade700,
                                ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'These will appear as clickable links in your CV',
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Colors.grey.shade600,
                                    ),
                          ),
                          const SizedBox(height: 16),

                          // LinkedIn
                          TextFormField(
                            controller: _linkedinController,
                            decoration: const InputDecoration(
                              labelText: 'LinkedIn URL',
                              hintText: 'https://linkedin.com/in/johnsmith',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.work),
                            ),
                            keyboardType: TextInputType.url,
                            validator: (value) =>
                                _validateUrl(value, 'LinkedIn'),
                          ),
                          const SizedBox(height: 16),

                          // GitHub
                          TextFormField(
                            controller: _githubController,
                            decoration: const InputDecoration(
                              labelText: 'GitHub URL',
                              hintText: 'https://github.com/johnsmith',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.code),
                            ),
                            keyboardType: TextInputType.url,
                            validator: (value) => _validateUrl(value, 'GitHub'),
                          ),
                          const SizedBox(height: 16),

                          // Portfolio
                          TextFormField(
                            controller: _portfolioController,
                            decoration: const InputDecoration(
                              labelText: 'Portfolio URL',
                              hintText: 'https://johnsmith.dev',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.web),
                            ),
                            keyboardType: TextInputType.url,
                            validator: (value) =>
                                _validateUrl(value, 'Portfolio'),
                          ),
                          const SizedBox(height: 16),

                          // Website
                          TextFormField(
                            controller: _websiteController,
                            decoration: const InputDecoration(
                              labelText: 'Website URL',
                              hintText: 'https://www.johnsmith.com',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.language),
                            ),
                            keyboardType: TextInputType.url,
                            validator: (value) =>
                                _validateUrl(value, 'Website'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Save Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isSaving ? null : _saveProfile,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Theme.of(context).primaryColor,
                        foregroundColor: Colors.white,
                      ),
                      child: _isSaving
                          ? const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white),
                                  ),
                                ),
                                SizedBox(width: 12),
                                Text('Saving...'),
                              ],
                            )
                          : Text((_profileExists || _hasFormData)
                              ? 'Update Profile'
                              : 'Create Profile'),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Profile Status
                  if (_currentProfile != null)
                    Card(
                      color: _currentProfile!.isComplete
                          ? Colors.green.shade50
                          : Colors.orange.shade50,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  _currentProfile!.isComplete
                                      ? Icons.check_circle
                                      : Icons.warning,
                                  color: _currentProfile!.isComplete
                                      ? Colors.green
                                      : Colors.orange,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  _currentProfile!.isComplete
                                      ? 'Profile Complete'
                                      : 'Profile Incomplete',
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleMedium
                                      ?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: _currentProfile!.isComplete
                                            ? Colors.green.shade700
                                            : Colors.orange.shade700,
                                      ),
                                ),
                              ],
                            ),
                            if (!_currentProfile!.isComplete) ...[
                              const SizedBox(height: 8),
                              Text(
                                'Missing: ${_currentProfile!.missingFields.join(', ')}',
                                style: Theme.of(context)
                                    .textTheme
                                    .bodyMedium
                                    ?.copyWith(
                                      color: Colors.orange.shade700,
                                    ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: widget.hideAppBar
          ? null
          : AppBar(
              title: const Text('Profile Settings'),
              backgroundColor: Theme.of(context).colorScheme.inversePrimary,
              actions: [
                if (_profileExists)
                  IconButton(
                    onPressed: _deleteProfile,
                    icon: const Icon(Icons.delete, color: Colors.red),
                    tooltip: 'Delete Profile',
                  ),
              ],
            ),
      body: _buildProfileContent(),
    );
  }
}
