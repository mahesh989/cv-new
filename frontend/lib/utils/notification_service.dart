import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

/// Centralized notification service that ensures all notifications
/// appear above all other UI elements including dialogs and overlays
class NotificationService {
  static OverlayEntry? _currentOverlayEntry;
  static final List<OverlayEntry> _overlayQueue = [];

  /// Show a success notification
  static void showSuccess(String message, {VoidCallback? onTap}) {
    _showSnackBar(
      message: message,
      backgroundColor: Colors.green,
      icon: Icons.check_circle,
    );
  }

  /// Show an error notification
  static void showError(String message, {VoidCallback? onTap}) {
    _showSnackBar(
      message: message,
      backgroundColor: Colors.red,
      icon: Icons.error,
    );
  }

  /// Show an info notification
  static void showInfo(String message, {VoidCallback? onTap}) {
    _showSnackBar(
      message: message,
      backgroundColor: Colors.blue,
      icon: Icons.info,
    );
  }

  /// Show a warning notification
  static void showWarning(String message, {VoidCallback? onTap}) {
    _showSnackBar(
      message: message,
      backgroundColor: Colors.orange,
      icon: Icons.warning,
    );
  }

  /// Show a custom notification
  static void showCustom({
    required String message,
    required Color backgroundColor,
    required IconData icon,
    VoidCallback? onTap,
  }) {
    _showSnackBar(
      message: message,
      backgroundColor: backgroundColor,
      icon: icon,
    );
  }

  /// Show a toast notification (fallback method)
  static void showToast(
    String message, {
    Color backgroundColor = Colors.green,
    Toast toastLength = Toast.LENGTH_SHORT,
  }) {
    Fluttertoast.showToast(
      msg: message,
      toastLength: toastLength,
      gravity: ToastGravity.TOP,
      timeInSecForIosWeb: 3,
      backgroundColor: backgroundColor,
      textColor: Colors.white,
      fontSize: 16.0,
    );
  }

  /// Show an overlay notification that appears above all other elements
  static void showOverlayNotification({
    required String message,
    required IconData icon,
    Color backgroundColor = Colors.green,
    Duration duration = const Duration(seconds: 3),
    VoidCallback? onTap,
  }) {
    // Fallback to toast for now since we don't have global context
    showToast(message, backgroundColor: backgroundColor);
  }

  /// Show a dialog that appears above all other elements with useRootNavigator
  static Future<T?> showTopDialog<T>({
    required BuildContext context,
    required Widget child,
    bool barrierDismissible = true,
    Color? barrierColor,
    bool useRootNavigator = true,
  }) {
    return showDialog<T>(
      context: context,
      useRootNavigator: useRootNavigator,
      barrierDismissible: barrierDismissible,
      barrierColor: barrierColor,
      builder: (context) => child,
    );
  }

  /// Show a loading overlay that appears above all elements
  static void showLoadingOverlay({
    String message = "Loading...",
    bool dismissible = false,
  }) {
    // For now, just show a toast as fallback
    showToast("$message Please wait...");
  }

  /// Hide the current loading overlay
  static void hideLoadingOverlay() {
    _removeCurrentOverlay();
  }

  /// Private method to show SnackBar with proper z-index
  static void _showSnackBar({
    required String message,
    required Color backgroundColor,
    required IconData icon,
    BuildContext? context,
  }) {
    // Use toast as primary method since we don't have global scaffold messenger
    showToast(message, backgroundColor: backgroundColor);
  }

  /// Remove the current overlay entry
  static void _removeCurrentOverlay() {
    _currentOverlayEntry?.remove();
    _currentOverlayEntry = null;
  }

  /// Convert Color to hex string for web toast
  static String _colorToHex(Color color) {
    return '#${color.value.toRadixString(16).padLeft(8, '0').substring(2)}';
  }

  /// Clear all notifications
  static void clearAll() {
    _removeCurrentOverlay();
    Fluttertoast.cancel();
  }

  /// Show SnackBar using provided context
  static void showSnackBarWithContext(
    BuildContext context, {
    required String message,
    required Color backgroundColor,
    required IconData icon,
  }) {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(icon, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(child: Text(message)),
            ],
          ),
          backgroundColor: backgroundColor,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 4),
        ),
      );
    } catch (e) {
      // Fallback to toast
      showToast(message, backgroundColor: backgroundColor);
    }
  }
}

/// Custom overlay notification widget
class _OverlayNotification extends StatefulWidget {
  final String message;
  final IconData icon;
  final Color backgroundColor;
  final VoidCallback? onTap;
  final VoidCallback onDismiss;

  const _OverlayNotification({
    required this.message,
    required this.icon,
    required this.backgroundColor,
    this.onTap,
    required this.onDismiss,
  });

  @override
  State<_OverlayNotification> createState() => _OverlayNotificationState();
}

class _OverlayNotificationState extends State<_OverlayNotification>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeIn,
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _dismiss() async {
    await _controller.reverse();
    widget.onDismiss();
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 16,
      left: 16,
      right: 16,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Material(
            elevation: 12,
            borderRadius: BorderRadius.circular(16),
            child: GestureDetector(
              onTap: widget.onTap ?? _dismiss,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: widget.backgroundColor,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Icon(
                      widget.icon,
                      color: Colors.white,
                      size: 24,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        widget.message,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: _dismiss,
                      icon: const Icon(
                        Icons.close,
                        color: Colors.white70,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Custom loading overlay widget
class _LoadingOverlay extends StatelessWidget {
  final String message;
  final bool dismissible;
  final VoidCallback? onDismiss;

  const _LoadingOverlay({
    required this.message,
    required this.dismissible,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black54,
      child: GestureDetector(
        onTap: dismissible ? onDismiss : null,
        child: Container(
          width: double.infinity,
          height: double.infinity,
          child: Center(
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    message,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  if (dismissible) ...[
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: onDismiss,
                      child: const Text('Cancel'),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
