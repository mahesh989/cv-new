import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:intl/intl.dart'; // For date formatting
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/generate_tailored_cv.dart';
import 'dart:html' as html; // For web open
import 'package:flutter/foundation.dart';
import '../../main.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';

class SavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;
  final TailoredCVService service;
  final Future<void> Function()? onRefresh;

  const SavedJobsTable({
    super.key,
    required this.jobs,
    required this.service,
    this.onRefresh,
  });

  @override
  State<SavedJobsTable> createState() => _SavedJobsTableState();
}

class _SavedJobsTableState extends State<SavedJobsTable> {
  int? _sortColumnIndex;
  bool _isAscending = true;
  List<Map<String, dynamic>> _sortedJobs = [];

  @override
  void initState() {
    super.initState();
    _sortedJobs = widget.jobs;
  }

  @override
  void didUpdateWidget(covariant SavedJobsTable oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.jobs != widget.jobs) {
      _sortedJobs = widget.jobs;
    }
  }

  void openInNewTab(String url) {
    html.window.open(url, '_blank');
  }

  Future<void> _safeLaunch(String? url) async {
    final uri = Uri.tryParse(url ?? '');
    if (uri != null && await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
      Fluttertoast.showToast(
        msg: "Download started 🚀",
        backgroundColor: Colors.green,
        textColor: Colors.white,
        gravity: ToastGravity.BOTTOM,
      );
    } else {
      Fluttertoast.showToast(
        msg: "Invalid download link ❌",
        backgroundColor: Colors.red,
        textColor: Colors.white,
        gravity: ToastGravity.BOTTOM,
      );
    }
  }

  String _formatDate(String? rawDate) {
    if (rawDate == null || rawDate.isEmpty) return '-';
    try {
      final parsed = DateTime.parse(rawDate);
      return DateFormat('d MMM yyyy').format(parsed); // eg. 27 Apr 2025
    } catch (e) {
      return rawDate;
    }
  }

  Future<void> _handleDelete(
      BuildContext context, Map<String, dynamic> job) async {
    final confirm = await showDialog<bool>(
      context: context,
      useRootNavigator: true,
      builder: (_) => AlertDialog(
        title: const Text("Confirm Delete"),
        content: const Text("Are you sure you want to delete this job?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text("Delete"),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await widget.service.deleteJob(job['sn'].toString());
        if (widget.onRefresh != null) await widget.onRefresh!();
        NotificationService.showToast(
          "Job deleted successfully! 🗑️",
          backgroundColor: Colors.green,
        );
      } catch (e) {
        NotificationService.showToast(
          "Failed to delete job: $e",
          backgroundColor: Colors.red,
        );
      }
    }
  }

  void _onSort<T>(Comparable<T> Function(Map<String, dynamic> job) getField,
      int columnIndex, bool ascending) {
    _sortedJobs.sort((a, b) {
      final aField = getField(a);
      final bField = getField(b);
      return ascending
          ? Comparable.compare(aField, bField)
          : Comparable.compare(bField, aField);
    });

    setState(() {
      _sortColumnIndex = columnIndex;
      _isAscending = ascending;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_sortedJobs.isEmpty) {
      return const Center(child: Text('No jobs saved yet.'));
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        child: DataTable(
          sortAscending: _isAscending,
          sortColumnIndex: _sortColumnIndex,
          headingRowColor: WidgetStateProperty.all(Colors.grey.shade200),
          columnSpacing: 20,
          columns: [
            const DataColumn(
                label: Text('S.N.',
                    style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(
              label: const Text('Company',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              onSort: (columnIndex, ascending) => _onSort(
                (job) => (job['company'] ?? '').toLowerCase(),
                columnIndex,
                ascending,
              ),
            ),
            const DataColumn(
                label: Text('Phone',
                    style: TextStyle(fontWeight: FontWeight.bold))),
            DataColumn(
              label: const Text('Applied Date',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              onSort: (columnIndex, ascending) => _onSort(
                (job) => job['date_applied'] ?? '',
                columnIndex,
                ascending,
              ),
            ),
            DataColumn(
              label: const Text('Location',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              onSort: (columnIndex, ascending) => _onSort(
                (job) => (job['location'] ?? '').toLowerCase(),
                columnIndex,
                ascending,
              ),
            ),
            const DataColumn(
                label: Text('CV Name 🟢',
                    style: TextStyle(fontWeight: FontWeight.bold))),
            const DataColumn(
                label: Text('CV Preview',
                    style: TextStyle(fontWeight: FontWeight.bold))),
            const DataColumn(
                label: Text('Download',
                    style: TextStyle(fontWeight: FontWeight.bold))),
            const DataColumn(
                label: Text('Delete',
                    style: TextStyle(fontWeight: FontWeight.bold))),
          ],
          rows: _sortedJobs.asMap().entries.map((entry) {
            final index = entry.key;
            final job = entry.value;

            return DataRow(cells: [
              DataCell(Text((index + 1).toString())),
              DataCell(
                Row(
                  children: [
                    Flexible(
                      child: Text(job['company'] ?? '',
                          overflow: TextOverflow.ellipsis),
                    ),
                    if (job['job_link'] != null &&
                        job['job_link'].toString().isNotEmpty &&
                        job['job_link'] != 'N/A' &&
                        job['job_link'] != 'Manual Save' &&
                        (job['job_link'].toString().startsWith('http://') ||
                            job['job_link'].toString().startsWith('https://')))
                      IconButton(
                        icon: const Icon(Icons.open_in_new, size: 20),
                        tooltip: 'Open Job Link',
                        onPressed: () => openInNewTab(job['job_link']),
                      ),
                  ],
                ),
              ),
              DataCell(Text(job['phone']?.toString().isNotEmpty == true
                  ? job['phone']
                  : 'N/A')),
              DataCell(Text(_formatDate(job['date_applied']))),
              DataCell(Text(job['location']?.toString().isNotEmpty == true
                  ? job['location']
                  : 'N/A')),
              DataCell(Container(
                color: Colors.yellow.shade200,
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                child: _buildCVNameCellWithDebug(job),
              )),
              DataCell(
                TextButton(
                  child: const Text('Preview'),
                  onPressed: () async {
                    try {
                      final preview = await widget.service
                          .fetchCVPreview(job['tailored_cv']);
                      if (!context.mounted) return;
                      showDialog(
                        context: context,
                        useRootNavigator: true,
                        builder: (_) => AlertDialog(
                          title: const Text("CV Preview"),
                          content: SizedBox(
                            width: double.maxFinite,
                            child: SingleChildScrollView(child: Text(preview)),
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: const Text('Close'),
                            ),
                          ],
                        ),
                      );
                    } catch (e) {
                      if (!context.mounted) return;
                      NotificationService.showError(
                          "Failed to load preview: $e");
                    }
                  },
                ),
              ),
              DataCell(IconButton(
                icon: const Icon(Icons.download),
                onPressed: () => _downloadCV(job),
              )),
              DataCell(
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => _handleDelete(context, job),
                ),
              ),
            ]);
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildCVNameCellWithDebug(Map<String, dynamic> job) {
    final cvName = job['cv_display_name'] ?? job['tailored_cv'] ?? 'Unknown CV';
    return Text(cvName);
  }

  void _downloadCV(Map<String, dynamic> job) async {
    try {
      String? filename = job['tailored_cv'];

      // Handle generic filenames like "Current CV" by finding actual files
      if (filename != null &&
          (filename.toLowerCase().contains('current cv') ||
              filename.toLowerCase() == 'current cv' ||
              filename.toLowerCase() == 'cv')) {
        print(
            '🔍 [SAVED_JOBS] Generic filename detected: $filename, trying to find actual file');

        // Try to find an actual CV file for this company
        try {
          String company = job['company'] ?? 'Unknown';
          final response = await http.get(Uri.parse(
              'http://localhost:8000/list-tailored-cvs-with-formats/'));

          if (response.statusCode == 200) {
            final List<dynamic> cvFiles = json.decode(response.body);

            // Look for CV files that match the company name
            final companyClean =
                company.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '');
            final matchingFiles = cvFiles
                .where((cv) => cv['base_name']
                    .toString()
                    .toLowerCase()
                    .contains(companyClean.toLowerCase()))
                .toList();

            if (matchingFiles.isNotEmpty) {
              // Use the most recent matching file
              final latestFile = matchingFiles.first;

              // Prefer PDF, fallback to DOCX
              if (latestFile['pdf'] == true) {
                filename = '${latestFile['base_name']}.pdf';
              } else if (latestFile['docx'] == true) {
                filename = '${latestFile['base_name']}.docx';
              }

              print(
                  '🔍 [SAVED_JOBS] Found actual file: $filename for company: $company');
            } else {
              print(
                  '⚠️ [SAVED_JOBS] No matching files found for company: $company');
              // Use the format-specific endpoint which will find the latest file
              filename = 'Current CV'; // Let backend handle it
            }
          }
        } catch (e) {
          print('❌ [SAVED_JOBS] Error finding actual file: $e');
          // Continue with original filename and let backend handle it
        }
      }

      // Use format-specific download to prefer PDF
      final url = filename != null
          ? 'http://localhost:8000/download-cv/$filename/format/pdf'
          : null;

      if (url != null) {
        final uri = Uri.tryParse(url);
        if (uri != null && await canLaunchUrl(uri)) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
          NotificationService.showToast(
            "Download started 🚀",
            backgroundColor: Colors.green,
          );
        } else {
          throw Exception('Could not open download URL');
        }
      } else {
        throw Exception('No CV filename available');
      }
    } catch (e) {
      NotificationService.showError('Download failed: $e');
    }
  }
}
