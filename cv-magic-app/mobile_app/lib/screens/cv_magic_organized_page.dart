///
/// Organized CV Magic Page
///
/// This page uses modular components for better code organization:
/// - CVUploadModule for file uploads
/// - CVSelectionModule for CV selection
/// - CVPreviewModule for CV preview
///

import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../modules/cv/cv_upload_module.dart';
import '../modules/cv/cv_selection_module.dart';
import '../modules/cv/cv_preview_module.dart';
import '../widgets/job_input.dart';
import '../services/api_service.dart';

class CVMagicOrganizedPage extends StatefulWidget {
  const CVMagicOrganizedPage({super.key});

  @override
  State<CVMagicOrganizedPage> createState() => _CVMagicOrganizedPageState();
}

class _CVMagicOrganizedPageState extends State<CVMagicOrganizedPage> {
  // State variables
  String? selectedCVFilename;
  bool isLoading = false;

  // Job description controllers
  final TextEditingController jdController = TextEditingController();
  final TextEditingController jdUrlController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic - Organized'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // CV Upload Module
            CVUploadModule(
              onFilePicked: _onFilePicked,
              isLoading: isLoading,
            ),
            const SizedBox(height: 16),

            // CV Selection Module
            CVSelectionModule(
              selectedCVFilename: selectedCVFilename,
              onCVSelected: _onCVSelected,
            ),
            const SizedBox(height: 16),

            // CV Preview Module
            CVPreviewModule(
              selectedCVFilename: selectedCVFilename,
            ),
            const SizedBox(height: 16),

            // Job Description Input
            JobInput(
              jdController: jdController,
              jdUrlController: jdUrlController,
              onExtract:
                  () {}, // Not used anymore, analysis is handled in JobInput widget
            ),

            // Loading indicator
            if (isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _onFilePicked(PlatformFile file) async {
    setState(() {
      isLoading = true;
    });

    try {
      await APIService.uploadCV(file);
      await _refreshCVList();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('CV uploaded successfully: ${file.name}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void _onCVSelected(String? filename) {
    setState(() {
      selectedCVFilename = filename;
    });
  }

  Future<void> _refreshCVList() async {
    // This would trigger a refresh of the CV selection module
    // For now, we'll just update the state
    setState(() {});
  }

  @override
  void dispose() {
    jdController.dispose();
    jdUrlController.dispose();
    super.dispose();
  }
}
