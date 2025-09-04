import 'package:flutter/material.dart';

class CvUploader extends StatelessWidget {
  const CvUploader({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [
          const Text("Upload your CV (PDF or DOCX):"),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: () {
              // TODO: Implement file picking logic
            },
            icon: const Icon(Icons.upload_file),
            label: const Text("Choose File"),
          ),
        ],
      ),
    );
  }
}
