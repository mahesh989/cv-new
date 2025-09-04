import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../services/generate_tailored_cv.dart';
import '../services/ats_service.dart';
import '../widgets/enhanced_saved_jobs_table.dart';
import '../theme/app_theme.dart';
import '../main.dart';
import '../utils/notification_service.dart';
import 'dart:typed_data';

class SavedJobsPage extends StatefulWidget {
  const SavedJobsPage({super.key});

  @override
  State<SavedJobsPage> createState() => _SavedJobsPageState();
}

class _SavedJobsPageState extends State<SavedJobsPage> {
  final TailoredCVService _service = TailoredCVService('http://localhost:8000');

  List<Map<String, dynamic>> savedJobs = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    if (!mounted) return;
    setState(() => isLoading = true);

    try {
      final jobs = await _service.fetchSavedJobs();
      if (mounted) {
        setState(() {
          savedJobs = jobs;
          isLoading = false;
        });
      }
    } catch (e) {
      NotificationService.showError('Failed to load jobs: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _deleteAllJobs() async {
    final confirm = await showDialog<bool>(
      context: context,
      useRootNavigator: true,
      builder: (_) => AlertDialog(
        title: const Text("Delete All Jobs"),
        content: const Text(
            "Are you sure you want to delete ALL saved jobs? This will also clean up orphaned CV files. This cannot be undone."),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text("Delete All"),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        final result = await _service.deleteAllJobs();
        await _loadJobs();

        // Show detailed cleanup information
        final cleanupResult = result['cleanup_result'] ?? {};
        final deletedFiles = cleanupResult['deleted_files'] ?? [];
        final deletedCount = deletedFiles.length;

        String message = 'All jobs deleted successfully!';
        if (deletedCount > 0) {
          message += '\n🗑️ Also cleaned up $deletedCount orphaned CV files.';
        }

        NotificationService.showSuccess(message);
      } catch (e) {
        NotificationService.showError('Failed to delete jobs: $e');
      }
    }
  }

  Future<void> _showPreview(String filename) async {
    try {
      // For saved jobs, we can directly download and view the PDF
      // since it's already generated and stored
      if (filename.endsWith('.pdf')) {
        NotificationService.showInfo(
            "PDF preview available - downloading file for viewing");
        await _download(filename);
      } else {
        NotificationService.showError(
            "Preview only available for PDF files. Please regenerate this CV to get PDF format.");
      }
    } catch (e) {
      if (!mounted) return;
      NotificationService.showError("Failed to load CV preview: $e");
    }
  }

  Future<void> _download(String filename) async {
    try {
      // Use format-specific endpoint that handles generic filenames properly
      final baseFilename = filename.contains('.')
          ? filename.substring(0, filename.lastIndexOf('.'))
          : filename;
      final url = Uri.parse(
          'http://localhost:8000/download-cv/$baseFilename/format/pdf');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        NotificationService.showSuccess("Download started 🚀");
      } else {
        NotificationService.showError("Download failed ❌");
      }
    } catch (e) {
      NotificationService.showError("Download failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Gradient Header (reuse your existing header logic)
              Container(
                width: double.infinity,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Colors.blue.shade600,
                      Colors.purple.shade600,
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final isNarrow = constraints.maxWidth < 600;

                    if (isNarrow) {
                      // Mobile layout - vertical stacking
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      "📋 Saved Jobs",
                                      style: TextStyle(
                                        fontSize: 22,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.white,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      "${savedJobs.length} job${savedJobs.length != 1 ? 's' : ''} saved",
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.white.withOpacity(0.9),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              IconButton(
                                onPressed: _loadJobs,
                                icon: const Icon(Icons.refresh,
                                    color: Colors.white, size: 22),
                                tooltip: 'Refresh',
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          if (savedJobs.isNotEmpty)
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton.icon(
                                onPressed: _deleteAllJobs,
                                icon:
                                    const Icon(Icons.delete_forever, size: 18),
                                label: const Text("Delete All",
                                    style: TextStyle(fontSize: 14)),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red.shade600,
                                  foregroundColor: Colors.white,
                                  elevation: 2,
                                  padding: const EdgeInsets.symmetric(
                                      vertical: 8, horizontal: 16),
                                ),
                              ),
                            ),
                        ],
                      );
                    } else {
                      // Desktop layout - horizontal
                      return Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  "📋 Saved Jobs",
                                  style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "${savedJobs.length} job${savedJobs.length != 1 ? 's' : ''} saved",
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.white.withOpacity(0.9),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                onPressed: _loadJobs,
                                icon: const Icon(Icons.refresh,
                                    color: Colors.white),
                                tooltip: 'Refresh',
                              ),
                              const SizedBox(width: 8),
                              ElevatedButton.icon(
                                onPressed:
                                    savedJobs.isEmpty ? null : _deleteAllJobs,
                                icon: const Icon(Icons.delete_forever),
                                label: const Text("Delete All"),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red.shade600,
                                  foregroundColor: Colors.white,
                                  disabledBackgroundColor: Colors.grey.shade400,
                                  disabledForegroundColor: Colors.white,
                                  elevation: 2,
                                ),
                              ),
                            ],
                          ),
                        ],
                      );
                    }
                  },
                ),
              ),
              // Main Content
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                  child: isLoading
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              CircularProgressIndicator(
                                valueColor: AlwaysStoppedAnimation<Color>(
                                    Colors.blue.shade600),
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Loading your saved jobs...',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                        )
                      : savedJobs.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.search,
                                    size: 48,
                                    color: Colors.grey.shade600,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'No jobs found. Start by analyzing a job description on the CV page!',
                                    style: TextStyle(
                                      color: Colors.grey.shade600,
                                      fontSize: 16,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                            )
                          : EnhancedSavedJobsTable(
                              jobs: savedJobs,
                              service: _service,
                              onRefresh: _loadJobs,
                            ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
