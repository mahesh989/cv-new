import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../core/config/environment_config.dart';

/// Popup widget to display backend connection errors
class BackendErrorPopup extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onRetry;
  final VoidCallback? onDismiss;
  final bool showRetryButton;

  const BackendErrorPopup({
    super.key,
    required this.title,
    required this.message,
    this.onRetry,
    this.onDismiss,
    this.showRetryButton = true,
  });

  /// Show the backend error popup
  static Future<void> show({
    required BuildContext context,
    required String title,
    required String message,
    VoidCallback? onRetry,
    VoidCallback? onDismiss,
    bool showRetryButton = true,
  }) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false, // Prevent dismissing by tapping outside
      builder: (BuildContext context) {
        return BackendErrorPopup(
          title: title,
          message: message,
          onRetry: onRetry,
          onDismiss: onDismiss,
          showRetryButton: showRetryButton,
        );
      },
    );
  }

  /// Show a connection error popup specifically for backend issues
  static Future<void> showConnectionError({
    required BuildContext context,
    VoidCallback? onRetry,
    VoidCallback? onDismiss,
  }) {
    return show(
      context: context,
      title: 'Backend Connection Error',
      message:
          'Unable to connect to the backend server. Please check if the server is running and try again.',
      onRetry: onRetry,
      onDismiss: onDismiss,
    );
  }

  /// Show a server error popup for 500-level errors
  static Future<void> showServerError({
    required BuildContext context,
    String? customMessage,
    VoidCallback? onRetry,
    VoidCallback? onDismiss,
  }) {
    return show(
      context: context,
      title: 'Server Error',
      message: customMessage ??
          'The server encountered an error. Please try again later.',
      onRetry: onRetry,
      onDismiss: onDismiss,
    );
  }

  /// Show an authentication error popup
  static Future<void> showAuthError({
    required BuildContext context,
    VoidCallback? onRetry,
    VoidCallback? onDismiss,
  }) {
    return show(
      context: context,
      title: 'Authentication Error',
      message: 'Your session has expired. Please log in again.',
      onRetry: onRetry,
      onDismiss: onDismiss,
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.red.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.error_outline,
              color: Colors.red,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: AppTheme.headingSmall.copyWith(
                color: Colors.red,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            message,
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.neutralGray700,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppTheme.primaryTeal.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: AppTheme.primaryTeal,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Make sure the backend server is running on ${EnvironmentConfig.baseUrl}',
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.primaryTeal,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      actions: [
        if (showRetryButton) ...[
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              onDismiss?.call();
            },
            child: Text(
              'Dismiss',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.neutralGray600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              onRetry?.call();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryTeal,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.refresh,
                  size: 18,
                ),
                const SizedBox(width: 6),
                Text(
                  'Retry',
                  style: AppTheme.bodyMedium.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ] else ...[
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              onDismiss?.call();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryTeal,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 12,
              ),
            ),
            child: Text(
              'OK',
              style: AppTheme.bodyMedium.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ],
    );
  }
}
