import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../core/theme/app_theme.dart';

class CvUploader extends StatelessWidget {
  final Function(PlatformFile file) onFilePicked;

  const CvUploader({super.key, required this.onFilePicked});

  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
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
                        color: AppTheme.primaryTeal,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Upload CV',
                          style: AppTheme.bodyLarge.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppTheme.primaryTeal,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  AppTheme.createGradientButton(
                    text: 'Browse Files',
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
                    icon: Icons.folder_open,
                  ),
                ],
              ),
            );
          } else {
            // Desktop layout - horizontal
            return Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    Icons.cloud_upload_outlined,
                    color: AppTheme.primaryTeal,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Upload CV',
                      style: AppTheme.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.primaryTeal,
                      ),
                    ),
                  ),
                  AppTheme.createGradientButton(
                    text: 'Browse',
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
                    icon: Icons.folder_open,
                  ),
                ],
              ),
            );
          }
        },
      ),
    );
  }
}
