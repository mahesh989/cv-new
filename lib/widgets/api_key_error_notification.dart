import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import 'api_key_input_dialog.dart';

class APIKeyErrorNotification extends StatelessWidget {
  final String provider;
  final String providerDisplayName;
  final String? errorMessage;
  final VoidCallback? onConfigureAPIKey;
  final VoidCallback? onDismiss;

  const APIKeyErrorNotification({
    super.key,
    required this.provider,
    required this.providerDisplayName,
    this.errorMessage,
    this.onConfigureAPIKey,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.orange.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.warning_rounded,
                  color: Colors.orange,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'API Key Required',
                      style: AppTheme.labelMedium.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade700,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Configure your $providerDisplayName API key to use this provider',
                      style: AppTheme.bodySmall.copyWith(
                        color: Colors.orange.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: onDismiss,
                icon: const Icon(
                  Icons.close_rounded,
                  color: Colors.orange,
                  size: 20,
                ),
              ),
            ],
          ),
          if (errorMessage != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Colors.red.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.error_outline,
                    color: Colors.red,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      errorMessage!,
                      style: AppTheme.bodySmall.copyWith(
                        color: Colors.red.shade700,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: onDismiss,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.orange,
                    side: BorderSide(color: Colors.orange.withOpacity(0.5)),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Dismiss'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () => _showAPIKeyDialog(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Configure'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showAPIKeyDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => APIKeyInputDialog(
        provider: provider,
        providerDisplayName: providerDisplayName,
        onSuccess: () {
          Navigator.of(context).pop();
          onConfigureAPIKey?.call();
        },
        onCancel: () {
          Navigator.of(context).pop();
        },
      ),
    );
  }
}

class APIKeyErrorSnackBar {
  static void show(
    BuildContext context, {
    required String provider,
    required String providerDisplayName,
    String? errorMessage,
    VoidCallback? onConfigureAPIKey,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: APIKeyErrorNotification(
          provider: provider,
          providerDisplayName: providerDisplayName,
          errorMessage: errorMessage,
          onConfigureAPIKey: onConfigureAPIKey,
          onDismiss: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 10),
        margin: const EdgeInsets.all(16),
      ),
    );
  }
}
