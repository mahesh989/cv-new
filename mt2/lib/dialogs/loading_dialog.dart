import 'package:flutter/material.dart';

class LoadingDialog extends StatelessWidget {
  final String text;

  const LoadingDialog({super.key, this.text = "Loading..."});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(
              strokeWidth: 5,
            ),
            const SizedBox(height: 20),
            Text(
              text,
              style: const TextStyle(color: Colors.white, fontSize: 18),
            ),
          ],
        ),
      ),
    );
  }
}
