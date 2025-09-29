import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../core/theme/app_theme.dart';

class CvUploader extends StatelessWidget {
  final Function(PlatformFile file) onFilePicked;
  final bool isLoading;

  const CvUploader(
      {super.key, required this.onFilePicked, this.isLoading = false});

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
                  if (isLoading)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        gradient: LinearGradient(
                          colors: [
                            Colors.orange.shade50,
                            Colors.orange.shade100,
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 3,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                    Colors.orange),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Uploading CV...',
                              style: AppTheme.bodyMedium.copyWith(
                                color: Colors.orange.shade700,
                                fontWeight: FontWeight.w600,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  if (isLoading) const SizedBox(height: 12),
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
                    isLoading: isLoading,
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
                  if (isLoading) ...[
                    Container(
                      margin: const EdgeInsets.only(right: 12),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: const [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(Colors.orange),
                            ),
                          ),
                          SizedBox(width: 8),
                          Text('Uploading...',
                              style: TextStyle(color: Colors.orange)),
                        ],
                      ),
                    ),
                  ],
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
                    isLoading: isLoading,
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
