import 'package:flutter/material.dart';

class MatchButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onPressed;

  const MatchButton({super.key, required this.isLoading, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: isLoading ? null : onPressed,
      icon: const Icon(Icons.analytics),
      label: isLoading
          ? const SizedBox(
              height: 18,
              width: 18,
              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
            )
          : const Text('Analyze Match'),
    );
  }
}
