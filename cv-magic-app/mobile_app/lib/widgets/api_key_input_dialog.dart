import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/api_key_service.dart';

class APIKeyInputDialog extends StatefulWidget {
  final String provider;
  final String providerDisplayName;
  final VoidCallback? onSuccess;
  final VoidCallback? onCancel;

  const APIKeyInputDialog({
    super.key,
    required this.provider,
    required this.providerDisplayName,
    this.onSuccess,
    this.onCancel,
  });

  @override
  State<APIKeyInputDialog> createState() => _APIKeyInputDialogState();
}

class _APIKeyInputDialogState extends State<APIKeyInputDialog>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _apiKeyController = TextEditingController();
  final _confirmApiKeyController = TextEditingController();

  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  bool _isValidating = false;
  bool _obscureText = true;
  bool _obscureConfirmText = true;
  String? _errorMessage;
  String? _successMessage;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _apiKeyController.dispose();
    _confirmApiKeyController.dispose();
    super.dispose();
  }

  Future<void> _validateAndSaveAPIKey() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isValidating = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final apiKeyService = APIKeyService();
      final success = await apiKeyService.setAPIKey(
        widget.provider,
        _apiKeyController.text.trim(),
      );

      if (success) {
        setState(() {
          _successMessage = 'API key saved and validated successfully!';
          _isValidating = false;
        });

        // Show success for a moment, then close
        await Future.delayed(const Duration(seconds: 1));

        if (mounted) {
          Navigator.of(context).pop();
          widget.onSuccess?.call();
        }
      } else {
        setState(() {
          _errorMessage =
              'Failed to validate API key. Please check your key and try again.';
          _isValidating = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
        _isValidating = false;
      });
    }
  }

  void _toggleObscureText() {
    setState(() {
      _obscureText = !_obscureText;
    });
  }

  void _toggleObscureConfirmText() {
    setState(() {
      _obscureConfirmText = !_obscureConfirmText;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: Container(
                constraints: const BoxConstraints(maxWidth: 400),
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildHeader(),
                      const SizedBox(height: 24),
                      _buildAPIKeyInput(),
                      const SizedBox(height: 16),
                      _buildConfirmAPIKeyInput(),
                      const SizedBox(height: 24),
                      _buildMessages(),
                      const SizedBox(height: 24),
                      _buildActions(),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _getProviderColor().withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            _getProviderIcon(),
            color: _getProviderColor(),
            size: 24,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Configure API Key',
                style: AppTheme.headingSmall.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Add your ${widget.providerDisplayName} API key to use this provider',
                style: AppTheme.bodySmall.copyWith(
                  color: AppTheme.neutralGray600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAPIKeyInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'API Key',
          style: AppTheme.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _apiKeyController,
          obscureText: _obscureText,
          decoration: InputDecoration(
            hintText: 'Enter your ${widget.providerDisplayName} API key',
            prefixIcon: const Icon(Icons.key_rounded),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureText ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: _toggleObscureText,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter your API key';
            }
            if (value.trim().length < 10) {
              return 'API key seems too short';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildConfirmAPIKeyInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Confirm API Key',
          style: AppTheme.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: _confirmApiKeyController,
          obscureText: _obscureConfirmText,
          decoration: InputDecoration(
            hintText: 'Re-enter your API key to confirm',
            prefixIcon: const Icon(Icons.key_rounded),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmText ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: _toggleObscureConfirmText,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please confirm your API key';
            }
            if (value.trim() != _apiKeyController.text.trim()) {
              return 'API keys do not match';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildMessages() {
    if (_errorMessage != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                _errorMessage!,
                style: AppTheme.bodySmall.copyWith(color: Colors.red),
              ),
            ),
          ],
        ),
      );
    }

    if (_successMessage != null) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.green.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.green.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.check_circle_outline,
                color: Colors.green, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                _successMessage!,
                style: AppTheme.bodySmall.copyWith(color: Colors.green),
              ),
            ),
          ],
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _buildActions() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: _isValidating
                ? null
                : () {
                    Navigator.of(context).pop();
                    widget.onCancel?.call();
                  },
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text('Cancel'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton(
            onPressed: _isValidating ? null : _validateAndSaveAPIKey,
            style: ElevatedButton.styleFrom(
              backgroundColor: _getProviderColor(),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isValidating
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Text('Save & Validate'),
          ),
        ),
      ],
    );
  }

  Color _getProviderColor() {
    switch (widget.provider) {
      case 'openai':
        return AppTheme.primaryCosmic;
      case 'anthropic':
        return AppTheme.primaryAurora;
      case 'deepseek':
        return AppTheme.primaryEmerald;
      default:
        return AppTheme.primaryTeal;
    }
  }

  IconData _getProviderIcon() {
    switch (widget.provider) {
      case 'openai':
        return Icons.auto_awesome_rounded;
      case 'anthropic':
        return Icons.psychology_alt_rounded;
      case 'deepseek':
        return Icons.code_rounded;
      default:
        return Icons.smart_toy_rounded;
    }
  }
}
