import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

class CvUploader extends StatelessWidget {
  final Function(PlatformFile file) onFilePicked;

  const CvUploader({super.key, required this.onFilePicked});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isNarrow = constraints.maxWidth < 400;

          if (isNarrow) {
            // Mobile layout - vertical stacking
            return Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.cloud_upload_outlined,
                        size: 20,
                        color: Theme.of(context).primaryColor,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Upload CV',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: () async {
                      final result = await FilePicker.platform.pickFiles(
                        type: FileType.custom,
                        allowedExtensions: ['pdf', 'docx'],
                        withData: true,
                      );
                      if (result != null) {
                        onFilePicked(result.files.first);
                      }
                    },
                    icon: Icon(Icons.folder_open, size: 18),
                    label: Text(
                      'Browse Files',
                      style: TextStyle(fontSize: 14),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ],
              ),
            );
          } else {
            // Desktop layout - horizontal
            return ListTile(
              leading: Icon(
                Icons.cloud_upload_outlined,
                color: Theme.of(context).primaryColor,
              ),
              title: const Text('Upload CV'),
              trailing: ElevatedButton.icon(
                onPressed: () async {
                  final result = await FilePicker.platform.pickFiles(
                    type: FileType.custom,
                    allowedExtensions: ['pdf', 'docx'],
                    withData: true,
                  );
                  if (result != null) {
                    onFilePicked(result.files.first);
                  }
                },
                icon: Icon(Icons.folder_open, size: 18),
                label: const Text('Browse'),
              ),
            );
          }
        },
      ),
    );
  }
}
