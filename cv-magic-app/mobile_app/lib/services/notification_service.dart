import 'package:flutter/material.dart';

/// Global notification service for showing user-friendly messages
class NotificationService {
  static final GlobalKey<NavigatorState> navigatorKey =
      GlobalKey<NavigatorState>();

  /// Show a snackbar notification
  static void showSnackBar({
    required String message,
    Color backgroundColor = Colors.blue,
    Duration duration = const Duration(seconds: 3),
    String? actionLabel,
    VoidCallback? onAction,
  }) {
    final context = navigatorKey.currentContext;
    if (context == null) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          message,
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
        duration: duration,
        action: actionLabel != null && onAction != null
            ? SnackBarAction(
                label: actionLabel,
                textColor: Colors.white,
                onPressed: onAction,
              )
            : null,
      ),
    );
  }

  /// Show an error notification
  static void showError(String message) {
    showSnackBar(
      message: message,
      backgroundColor: Colors.red,
      duration: const Duration(seconds: 4),
    );
  }

  /// Show a success notification
  static void showSuccess(String message) {
    showSnackBar(
      message: message,
      backgroundColor: Colors.green,
      duration: const Duration(seconds: 2),
    );
  }

  /// Show a warning notification
  static void showWarning(String message) {
    showSnackBar(
      message: message,
      backgroundColor: Colors.orange,
      duration: const Duration(seconds: 3),
    );
  }

  /// Show an info notification
  static void showInfo(String message) {
    showSnackBar(
      message: message,
      backgroundColor: Colors.blue,
      duration: const Duration(seconds: 3),
    );
  }

  /// Show login expired notification with action
  static void showLoginExpired() {
    showSnackBar(
      message: '🔐 Login expired, please log in again',
      backgroundColor: Colors.red,
      duration: const Duration(seconds: 5),
      actionLabel: 'Login',
      onAction: () {
        // Navigate to login screen
        final context = navigatorKey.currentContext;
        if (context != null) {
          Navigator.of(context).pushNamedAndRemoveUntil(
            '/auth',
            (route) => false,
          );
        }
      },
    );
  }
}
