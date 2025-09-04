import 'package:flutter/material.dart';

Future<bool> showSaveJobDialog(BuildContext context) async {
  return await showDialog<bool>(
        context: context,
        useRootNavigator: true,
        builder: (_) => AlertDialog(
          title: const Text("Save Job?"),
          content: const Text(
              "Do you want to save this job and CV for future reference?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text("No"),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text("Yes, Save"),
            ),
          ],
        ),
      ) ??
      false;
}
