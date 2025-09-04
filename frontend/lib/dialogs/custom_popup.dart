import 'package:flutter/material.dart';

/// Enum for popup types
enum PopupType { success, error, warning, info }

/// ✅ Custom Animated Popup Widget
class CustomAnimatedPopup extends StatelessWidget {
  final PopupType type;
  final String message;

  const CustomAnimatedPopup({
    super.key,
    required this.type,
    required this.message,
  }); // ✅ FIXED

  @override
  Widget build(BuildContext context) {
    // ✅ MUST HAVE build method
    final config = _popupConfig(type);

    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Icon(config['icon'], color: config['color'], size: 32),
          const SizedBox(width: 10),
          Text(
            config['title'],
            style:
                TextStyle(color: config['color'], fontWeight: FontWeight.bold),
          ),
        ],
      ),
      content: Text(message, style: const TextStyle(fontSize: 16)),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text("OK"),
        ),
      ],
    );
  }

  Map<String, dynamic> _popupConfig(PopupType type) {
    switch (type) {
      case PopupType.success:
        return {
          'color': Colors.green,
          'icon': Icons.check_circle_outline,
          'title': 'Success!',
        };
      case PopupType.error:
        return {
          'color': Colors.red,
          'icon': Icons.error_outline,
          'title': 'Error!',
        };
      case PopupType.warning:
        return {
          'color': Colors.orange,
          'icon': Icons.warning_amber_rounded,
          'title': 'Warning!',
        };
      case PopupType.info:
        return {
          'color': Colors.blue,
          'icon': Icons.info_outline,
          'title': 'Info',
        };
    }
  }
}

/// ✅ Simple function to show Custom Popup
Future<void> showCustomPopup({
  required BuildContext context,
  required PopupType type,
  required String message,
}) async {
  return showDialog(
    context: context,
    useRootNavigator: true,
    barrierDismissible: false,
    builder: (_) => CustomAnimatedPopup(type: type, message: message),
  );
}
