///
/// CV Upload Module
///
/// Handles CV file upload functionality with validation and processing.
///

import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../widgets/cv_uploader.dart';
import '../../services/api_service.dart';

class CVUploadModule extends StatefulWidget {
  final Function(PlatformFile file) onFilePicked;
  final bool isLoading;

  const CVUploadModule({
    super.key,
    required this.onFilePicked,
    this.isLoading = false,
  });

  @override
  State<CVUploadModule> createState() => _CVUploadModuleState();
}

class _CVUploadModuleState extends State<CVUploadModule> {
  @override
  Widget build(BuildContext context) {
    return CvUploader(onFilePicked: widget.onFilePicked);
  }
}

class CVUploadService {
  /// Upload a CV file to the backend
  static Future<void> uploadCV(PlatformFile file) async {
    await APIService.uploadCV(file);
  }

  /// Handle file upload with loading state
  static Future<void> handleUpload({
    required PlatformFile file,
    required Function(bool) setLoading,
    required Function(String) showMessage,
  }) async {
    setLoading(true);

    try {
      await uploadCV(file);
      showMessage('CV uploaded successfully: ${file.name}');
    } catch (e) {
      showMessage('Upload failed: $e');
    } finally {
      setLoading(false);
    }
  }
}
