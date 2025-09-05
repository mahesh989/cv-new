import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../services/generate_tailored_cv.dart';
import '../services/ats_service.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';

class SavedATSApplication {
  final String originalCV;
  final String tailoredCV;
  final int atsScore;
  final String jdText;

  SavedATSApplication({
    required this.originalCV,
    required this.tailoredCV,
    required this.atsScore,
    required this.jdText,
  });
}

class SavedATSTabPage extends StatefulWidget {
  const SavedATSTabPage({super.key});

  @override
  State<SavedATSTabPage> createState() => _SavedATSTabPageState();
}

class _SavedATSTabPageState extends State<SavedATSTabPage> {
  List<SavedATSApplication> _saved = [];

  @override
  void initState() {
    super.initState();
    _saved = []; // Empty list for now
  }

  Future<void> _handleDelete(int index) async {
    final confirm = await showDialog<bool>(
      context: context,
      useRootNavigator: true,
      builder: (_) => AlertDialog(
        title: const Text("Delete CV?"),
        content: const Text(
            "Are you sure you want to remove this CV from saved ATS list?"),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text("Cancel")),
          ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text("Delete")),
        ],
      ),
    );

    if (confirm == true) {
      setState(() {
        _saved.removeAt(index);
      });
    }
  }

  Future<void> _showPreview(String filename) async {
    try {
      // For saved ATS results, we can directly download and view the PDF
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
        print("Downloaded successfully.");
      } else {
        print("Download failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Download failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_saved.isEmpty) {
      return const Center(child: Text('No ATS CVs saved yet.'));
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStateProperty.all(Colors.grey.shade200),
        columns: const [
          DataColumn(
              label:
                  Text('S.N.', style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(
              label: Text('Original CV',
                  style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(
              label: Text('Tailored CV',
                  style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(
              label: Text('ATS Score',
                  style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(
              label: Text('Job Description',
                  style: TextStyle(fontWeight: FontWeight.bold))),
          DataColumn(
              label: Text('Actions',
                  style: TextStyle(fontWeight: FontWeight.bold))),
        ],
        rows: List.generate(_saved.length, (index) {
          final item = _saved[index];
          return DataRow(cells: [
            DataCell(Text('${index + 1}')),
            DataCell(Text(item.originalCV)),
            DataCell(Text(item.tailoredCV)),
            DataCell(Text('${item.atsScore}/100')),
            DataCell(Text(item.jdText.length > 50
                ? '${item.jdText.substring(0, 50)}...'
                : item.jdText)),
            DataCell(Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.visibility),
                  tooltip: 'Preview',
                  onPressed: () => _showPreview(item.tailoredCV),
                ),
                IconButton(
                  icon: const Icon(Icons.download),
                  tooltip: 'Download',
                  onPressed: () => _download(item.tailoredCV),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  tooltip: 'Delete',
                  onPressed: () => _handleDelete(index),
                ),
              ],
            )),
          ]);
        }),
      ),
    );
  }
}
