import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/generate_tailored_cv.dart';
// Remove dart:html import - not needed for mobile platforms
import '../main.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';
import '../utils/ats_helpers.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import 'ats/cv_preview_widget.dart';

class EnhancedSavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;
  final TailoredCVService service;
  final Future<void> Function()? onRefresh;

  const EnhancedSavedJobsTable({
    super.key,
    required this.jobs,
    required this.service,
    this.onRefresh,
  });

  @override
  State<EnhancedSavedJobsTable> createState() => _EnhancedSavedJobsTableState();
}

class _EnhancedSavedJobsTableState extends State<EnhancedSavedJobsTable>
    with TickerProviderStateMixin {
  late AnimationController _slideController;
  late AnimationController _fadeController;

  int _currentPage = 0;
  int _itemsPerPage = 10;
  String _searchQuery = '';
  int? _sortColumnIndex;
  bool _isAscending = false; // Default to newest first
  List<Map<String, dynamic>> _filteredJobs = [];
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();

    _slideController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );

    // Initialize filtered jobs
    _filteredJobs = List.from(widget.jobs);
    _updateFilteredJobs();

    _slideController.forward();
    _fadeController.forward();
  }

  @override
  void didUpdateWidget(covariant EnhancedSavedJobsTable oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.jobs != widget.jobs) {
      _updateFilteredJobs();
    }
  }

  @override
  void dispose() {
    _slideController.dispose();
    _fadeController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _updateFilteredJobs() {
    setState(() {
      _filteredJobs = widget.jobs.where((job) {
        final company = (job['company'] ?? '').toLowerCase();
        final location = (job['location'] ?? '').toLowerCase();
        final query = _searchQuery.toLowerCase();
        final matches = company.contains(query) || location.contains(query);
        return matches;
      }).toList();

      // Sort by date (newest first) by default
      _filteredJobs.sort((a, b) {
        final dateA =
            DateTime.tryParse(a['date_applied'] ?? '') ?? DateTime(1970);
        final dateB =
            DateTime.tryParse(b['date_applied'] ?? '') ?? DateTime(1970);
        return _isAscending ? dateA.compareTo(dateB) : dateB.compareTo(dateA);
      });

      _currentPage = 0; // Reset to first page when filtering
    });
  }

  void _onSearch(String query) {
    _searchQuery = query;
    _updateFilteredJobs();
  }

  void _onSort<T>(
    Comparable<T> Function(Map<String, dynamic> job) getField,
    int columnIndex,
    bool ascending,
  ) {
    _filteredJobs.sort((a, b) {
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

  List<Map<String, dynamic>> get _paginatedJobs {
    final startIndex = _currentPage * _itemsPerPage;
    final endIndex = (startIndex + _itemsPerPage).clamp(
      0,
      _filteredJobs.length,
    );

    final result = _filteredJobs.sublist(startIndex, endIndex);

    return result;
  }

  int get _totalPages => (_filteredJobs.length / _itemsPerPage).ceil();

  void _nextPage() {
    if (_currentPage < _totalPages - 1) {
      setState(() => _currentPage++);
      _animatePageChange();
    }
  }

  void _previousPage() {
    if (_currentPage > 0) {
      setState(() => _currentPage--);
      _animatePageChange();
    }
  }

  void _animatePageChange() {
    _fadeController.reset();
    _fadeController.forward();
  }

  String _formatDate(String? rawDate) {
    if (rawDate == null || rawDate.isEmpty) return '-';
    try {
      final parsed = DateTime.parse(rawDate);
      return DateFormat('d MMM yyyy').format(parsed);
    } catch (e) {
      return rawDate;
    }
  }

  Future<void> _handleDelete(
    BuildContext context,
    Map<String, dynamic> job,
  ) async {
    final confirm = await showDialog<bool>(
      context: context,
      useRootNavigator: true,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(
              Icons.warning_amber_rounded,
              color: Colors.orange.shade600,
            ),
            const SizedBox(width: 8),
            const Text("Confirm Delete"),
          ],
        ),
        content: Text(
          "Are you sure you want to delete the job at ${job['company']}?",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
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
        NotificationService.showError("Failed to delete job: $e");
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.jobs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.work_off, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'No jobs saved yet',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Start by generating and saving your first tailored CV!',
              style: TextStyle(color: Colors.grey.shade500),
            ),
          ],
        ),
      );
    }

    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.1),
        end: Offset.zero,
      ).animate(
        CurvedAnimation(parent: _slideController, curve: Curves.easeOutCubic),
      ),
      child: FadeTransition(
        opacity: _slideController,
        child: Column(
          children: [
            // Search and Controls Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          onChanged: _onSearch,
                          decoration: InputDecoration(
                            hintText: 'Search by company or location...',
                            prefixIcon: const Icon(Icons.search),
                            suffixIcon: _searchQuery.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear),
                                    onPressed: () {
                                      _searchController.clear();
                                      _onSearch('');
                                    },
                                  )
                                : null,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: BorderSide(
                                color: Colors.grey.shade300,
                              ),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(color: Colors.blue),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      DropdownButton<int>(
                        value: _itemsPerPage,
                        items: [5, 10, 20, 50].map((value) {
                          return DropdownMenuItem(
                            value: value,
                            child: Text('$value per page'),
                          );
                        }).toList(),
                        onChanged: (value) {
                          setState(() {
                            _itemsPerPage = value!;
                            _currentPage = 0;
                          });
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Showing ${_paginatedJobs.length} of ${_filteredJobs.length} jobs',
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (_filteredJobs.length > _itemsPerPage)
                        Row(
                          children: [
                            IconButton(
                              onPressed:
                                  _currentPage > 0 ? _previousPage : null,
                              icon: const Icon(Icons.chevron_left),
                              tooltip: 'Previous page',
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                '${_currentPage + 1} of $_totalPages',
                                style: TextStyle(
                                  color: Colors.blue.shade700,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            IconButton(
                              onPressed: _currentPage < _totalPages - 1
                                  ? _nextPage
                                  : null,
                              icon: const Icon(Icons.chevron_right),
                              tooltip: 'Next page',
                            ),
                          ],
                        ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Beautiful Card Grid for ALL Screen Sizes
            Expanded(
              child: FadeTransition(
                opacity: _fadeController,
                child: _buildUniversalCardLayout(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoleCell(Map<String, dynamic> job) {
    final role = job['role'] ?? 'Unknown Role';
    final level = job['level'] ?? '';
    final workType = job['work_type'] ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          role,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: 2),
        Row(
          children: [
            if (level.isNotEmpty && level != 'Not specified') ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.blue.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  level,
                  style: TextStyle(
                    fontSize: 10,
                    color: Colors.blue.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(width: 4),
            ],
            if (workType.isNotEmpty && workType != 'Not specified')
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  workType,
                  style: TextStyle(
                    fontSize: 10,
                    color: Colors.green.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildCVNameCell(Map<String, dynamic> job) {
    final displayName = _getCleanCVName(job);
    final generationSource = job['generation_source'] ?? 'manual';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          displayName,
          style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: 2),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: _getGenerationSourceColor(generationSource),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            _getGenerationSourceLabel(generationSource),
            style: const TextStyle(
              fontSize: 10,
              color: Colors.white,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildIndustryCell(Map<String, dynamic> job) {
    final industry = job['industry'] ?? 'Not specified';
    final keySkills = job['key_skills'] as List? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          industry,
          style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        if (keySkills.isNotEmpty) ...[
          const SizedBox(height: 2),
          Text(
            '${keySkills.length} key skills',
            style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
          ),
        ],
      ],
    );
  }

  Widget _buildATSScoreCell(Map<String, dynamic> job) {
    final score = job['ats_score'] ?? 0;
    final color = _getScoreColor(score);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        '$score%',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: color,
          fontSize: 14,
        ),
      ),
    );
  }

  Widget _buildDateCell(Map<String, dynamic> job) {
    final applied = job['applied'] ?? false;
    final dateApplied = _formatDate(job['date_applied']);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          dateApplied,
          style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13),
        ),
        const SizedBox(height: 2),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: applied ? Colors.green.shade100 : Colors.orange.shade100,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            applied ? 'Applied' : 'Not Applied',
            style: TextStyle(
              fontSize: 10,
              color: applied ? Colors.green.shade700 : Colors.orange.shade700,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Color _getGenerationSourceColor(String source) {
    switch (source) {
      case 'ats_workflow':
        return Colors.purple.shade600;
      case 'ats_regeneration':
        return Colors.indigo.shade600;
      case 'initial':
        return Colors.blue.shade600;
      default:
        return Colors.grey.shade600;
    }
  }

  String _getGenerationSourceLabel(String source) {
    switch (source) {
      case 'ats_workflow':
        return 'ATS Optimized';
      case 'ats_regeneration':
        return 'Regenerated';
      case 'initial':
        return 'Initial';
      default:
        return 'Manual';
    }
  }

  Color _getScoreColor(int score) => ATSHelpers.getScoreColor(score);

  Widget _buildActionsCell(Map<String, dynamic> job) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // For narrow cells, use compact icon buttons
        final isNarrow = constraints.maxWidth < 140;

        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Stack(
                children: [
                  Icon(
                    Icons.visibility_rounded,
                    color: Colors.blue.shade600,
                    size: isNarrow ? 18 : 20,
                  ),
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      width: isNarrow ? 8 : 10,
                      height: isNarrow ? 8 : 10,
                      decoration: BoxDecoration(
                        color: Colors.red.shade600,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 1),
                      ),
                      child: Icon(
                        Icons.picture_as_pdf,
                        color: Colors.white,
                        size: isNarrow ? 4 : 5,
                      ),
                    ),
                  ),
                ],
              ),
              tooltip: 'Preview CV (PDF)',
              padding: EdgeInsets.all(isNarrow ? 4 : 8),
              constraints: BoxConstraints(
                minWidth: isNarrow ? 32 : 40,
                minHeight: isNarrow ? 32 : 40,
              ),
              onPressed: () async {
                try {
                  if (!context.mounted) return;

                  print(
                      '🔍 [SAVED_JOBS] Opening CV preview for: ${job['tailored_cv']}');
                  print('🔍 [SAVED_JOBS] Company: ${job['company']}');
                  print('🔍 [SAVED_JOBS] Job data keys: ${job.keys.toList()}');

                  showDialog(
                    context: context,
                    useRootNavigator: true,
                    builder: (dialogContext) => Dialog.fullscreen(
                      child: Scaffold(
                        appBar: AppBar(
                          title: Row(
                            children: [
                              Icon(Icons.picture_as_pdf,
                                  color: Colors.red.shade600),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  "CV Preview - ${job['company']}",
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w600,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                          backgroundColor: Colors.white,
                          elevation: 1,
                          leading: IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () => Navigator.pop(dialogContext),
                            tooltip: 'Close PDF Preview',
                            style: IconButton.styleFrom(
                              backgroundColor: Colors.grey.shade100,
                              foregroundColor: Colors.grey.shade700,
                            ),
                          ),
                        ),
                        body: Container(
                          padding: const EdgeInsets.all(16),
                          child: CVPreviewWidget(
                            cvFilename: job['tailored_cv'],
                            showCloseButton: true,
                            onClose: () => Navigator.pop(dialogContext),
                          ),
                        ),
                      ),
                    ),
                  );
                } catch (e) {
                  if (!context.mounted) return;
                  NotificationService.showError('Failed to load preview: $e');
                }
              },
            ),
            IconButton(
              icon: Icon(
                Icons.download_rounded,
                color: Colors.green.shade600,
                size: isNarrow ? 18 : 20,
              ),
              tooltip: 'Download CV',
              padding: EdgeInsets.all(isNarrow ? 4 : 8),
              constraints: BoxConstraints(
                minWidth: isNarrow ? 32 : 40,
                minHeight: isNarrow ? 32 : 40,
              ),
              onPressed: () => _downloadCV(job),
            ),
            IconButton(
              icon: Icon(
                Icons.delete_rounded,
                color: Colors.red.shade600,
                size: isNarrow ? 18 : 20,
              ),
              tooltip: 'Delete Job',
              padding: EdgeInsets.all(isNarrow ? 4 : 8),
              constraints: BoxConstraints(
                minWidth: isNarrow ? 32 : 40,
                minHeight: isNarrow ? 32 : 40,
              ),
              onPressed: () => _handleDelete(context, job),
            ),
          ],
        );
      },
    );
  }

  String _getCleanCVName(Map<String, dynamic> job) {
    final existingName = job['cv_display_name'] ?? job['tailored_cv'] ?? '';

    // If already in new format (contains _V and ends with version number), return as is
    if (existingName.contains('_V') &&
        RegExp(r'_V\d+$').hasMatch(existingName)) {
      return existingName;
    }

    // If we have a cv_display_name that's already clean, use it
    if (job['cv_display_name'] != null &&
        job['cv_display_name'].toString().isNotEmpty) {
      return job['cv_display_name'];
    }

    // Generate a clean name from company and filename
    final company = job['company'] ?? 'Unknown_Company';
    final tailoredCv = job['tailored_cv'] ?? '';

    // Clean company name
    String cleanCompany = company
        .replaceAll(RegExp(r'[^a-zA-Z0-9\s]'), '')
        .replaceAll(RegExp(r'\s+'), '_')
        .trim();

    if (cleanCompany.isEmpty) {
      cleanCompany = 'Company';
    }

    // Extract version from filename if possible
    final versionMatch = RegExp(r'(\d+)\.docx?$').firstMatch(tailoredCv);
    final version = versionMatch?.group(1) ?? '1';

    return '${cleanCompany}_V$version';
  }

  Widget _buildInfoItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  // Universal Beautiful Card Grid Layout 🎨 - Works on ALL screen sizes
  Widget _buildUniversalCardLayout() {
    if (_paginatedJobs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.work_off, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'No jobs to display',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Colors.white, Colors.blue.shade50.withOpacity(0.3)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 8),
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        children: [
          // Stunning Header Section with HORIZONTAL text fix
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.indigo.shade600,
                  Colors.blue.shade600,
                  Colors.cyan.shade500,
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.work_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // FIXED: Horizontal text that won't wrap on mobile
                      FittedBox(
                        fit: BoxFit.scaleDown,
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Your Job Applications',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: MediaQuery.of(context).size.width > 600
                                ? 22
                                : 20,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.visible,
                        ),
                      ),
                      const SizedBox(height: 4),
                      FittedBox(
                        fit: BoxFit.scaleDown,
                        alignment: Alignment.centerLeft,
                        child: Text(
                          '${_filteredJobs.length} opportunities tracked',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.9),
                            fontSize: MediaQuery.of(context).size.width > 600
                                ? 14
                                : 13,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.visible,
                        ),
                      ),
                    ],
                  ),
                ),
                // Quick stats pills
                Row(
                  children: [
                    _buildStatPill(
                      'Total',
                      _filteredJobs.length.toString(),
                      Colors.white.withOpacity(0.2),
                      Colors.white,
                    ),
                    const SizedBox(width: 12),
                    _buildStatPill(
                      'Applied',
                      _filteredJobs
                          .where((j) => j['applied'] == true)
                          .length
                          .toString(),
                      Colors.green.withOpacity(0.2),
                      Colors.white,
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Modern Grid Layout - Responsive
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(
                  MediaQuery.of(context).size.width > 600 ? 20 : 12),
              child: GridView.builder(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: _getGridColumns(
                    MediaQuery.of(context).size.width,
                  ),
                  childAspectRatio:
                      _getCardAspectRatio(MediaQuery.of(context).size.width),
                  crossAxisSpacing:
                      MediaQuery.of(context).size.width > 600 ? 16 : 12,
                  mainAxisSpacing:
                      MediaQuery.of(context).size.width > 600 ? 16 : 12,
                ),
                itemCount: _paginatedJobs.length,
                itemBuilder: (context, index) {
                  final job = _paginatedJobs[index];
                  final globalIndex = _currentPage * _itemsPerPage + index;
                  final isRecent = DateTime.now()
                          .difference(
                            DateTime.tryParse(job['date_applied'] ?? '') ??
                                DateTime(1970),
                          )
                          .inDays <
                      7;

                  return _buildJobCard(job, globalIndex, isRecent);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  int _getGridColumns(double width) {
    // Mobile-first responsive design
    if (width > 1400) return 3; // Large desktop: 3 columns
    if (width > 1000) return 2; // Desktop/tablet landscape: 2 columns
    if (width > 600) return 2; // Tablet portrait: 2 columns
    return 1; // Mobile: 1 column
  }

  double _getCardAspectRatio(double width) {
    // Adjust aspect ratio based on screen size for optimal card appearance
    if (width > 1000) return 1.4; // Desktop: wider cards
    if (width > 600) return 1.3; // Tablet: slightly taller
    return 1.1; // Mobile: taller cards for better content fit
  }

  Widget _buildStatPill(
    String label,
    String value,
    Color bgColor,
    Color textColor,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: TextStyle(
              color: textColor.withOpacity(0.8),
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            value,
            style: TextStyle(
              color: textColor,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildJobCard(
    Map<String, dynamic> job,
    int globalIndex,
    bool isRecent,
  ) {
    final isMobile = MediaQuery.of(context).size.width <= 600;

    return TweenAnimationBuilder<double>(
      duration: Duration(milliseconds: 300 + (globalIndex % 6) * 100),
      tween: Tween(begin: 0.0, end: 1.0),
      builder: (context, value, child) {
        return Transform.scale(
          scale: 0.8 + (0.2 * value),
          child: Opacity(
            opacity: value,
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: isRecent
                      ? [Colors.green.shade50, Colors.white]
                      : [
                          Colors.white,
                          Colors.blue.shade50.withOpacity(0.5),
                        ],
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color:
                      isRecent ? Colors.green.shade300 : Colors.blue.shade200,
                  width: isRecent ? 2 : 1,
                ),
                boxShadow: [
                  BoxShadow(
                    color: isRecent
                        ? Colors.green.withOpacity(0.15)
                        : Colors.blue.withOpacity(0.1),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                    spreadRadius: 1,
                  ),
                ],
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () async {
                    final url = job['job_link'];
                    if (url != null) {
                      final uri = Uri.tryParse(url);
                      if (uri != null && await canLaunchUrl(uri)) {
                        await launchUrl(
                          uri,
                          mode: LaunchMode.externalApplication,
                        );
                      }
                    }
                  },
                  child: Padding(
                    padding: EdgeInsets.all(isMobile ? 16 : 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Header with number and status
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: [
                                    Colors.indigo.shade600,
                                    Colors.blue.shade600,
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(20),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.indigo.withOpacity(0.3),
                                    blurRadius: 8,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              child: Text(
                                '#${globalIndex + 1}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            if (isRecent)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Text(
                                  'NEW',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                          ],
                        ),

                        SizedBox(height: isMobile ? 12 : 16),

                        // Company name
                        Text(
                          job['company'] ?? 'Unknown Company',
                          style: TextStyle(
                            fontSize: isMobile ? 16 : 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),

                        SizedBox(height: isMobile ? 6 : 8),

                        // Location with icon
                        Row(
                          children: [
                            Icon(
                              Icons.location_on_rounded,
                              size: 16,
                              color: Colors.grey.shade600,
                            ),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                job['location'] ?? 'Not specified',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey.shade600,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 12),

                        // Date and status
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: job['applied'] == true
                                    ? Colors.green.shade100
                                    : Colors.orange.shade100,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                job['applied'] == true
                                    ? 'Applied'
                                    : 'Not Applied',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: job['applied'] == true
                                      ? Colors.green.shade700
                                      : Colors.orange.shade700,
                                ),
                              ),
                            ),
                            const Spacer(),
                            Text(
                              _formatDate(job['date_applied']),
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade500,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 16),

                        // CV name with icon
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.indigo.shade50,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.indigo.shade200),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.description_rounded,
                                size: 18,
                                color: Colors.indigo.shade600,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  job['cv_display_name'] ??
                                      job['tailored_cv'] ??
                                      'No CV',
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.indigo.shade700,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Action buttons
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _buildActionButton(
                              icon: Icons.visibility_rounded,
                              color: Colors.blue,
                              onPressed: () => _previewCV(job),
                            ),
                            _buildActionButton(
                              icon: Icons.download_rounded,
                              color: Colors.green,
                              onPressed: () => _downloadCV(job),
                            ),
                            if (job['job_link'] != null &&
                                job['job_link'].toString().isNotEmpty &&
                                job['job_link'] != 'N/A' &&
                                job['job_link'] != 'Manual Save' &&
                                (job['job_link']
                                        .toString()
                                        .startsWith('http://') ||
                                    job['job_link']
                                        .toString()
                                        .startsWith('https://')))
                              _buildActionButton(
                                icon: Icons.open_in_new_rounded,
                                color: Colors.orange,
                                onPressed: () async {
                                  final url = job['job_link'];
                                  if (url != null) {
                                    final uri = Uri.tryParse(url);
                                    if (uri != null &&
                                        await canLaunchUrl(uri)) {
                                      await launchUrl(uri,
                                          mode: LaunchMode.externalApplication);
                                    }
                                  }
                                },
                              ),
                            _buildActionButton(
                              icon: Icons.delete_rounded,
                              color: Colors.red,
                              onPressed: () => _handleDelete(context, job),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required Color color,
    required VoidCallback onPressed,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: IconButton(
        icon: Icon(icon, color: color, size: 20),
        onPressed: onPressed,
        padding: const EdgeInsets.all(8),
        constraints: const BoxConstraints(minWidth: 40, minHeight: 40),
      ),
    );
  }

  // Helper methods for mobile actions
  void _previewCV(Map<String, dynamic> job) async {
    try {
      if (!context.mounted) return;

      print('🔍 [SAVED_JOBS] Opening CV preview for: ${job['tailored_cv']}');
      print('🔍 [SAVED_JOBS] Company: ${job['company']}');
      print('🔍 [SAVED_JOBS] Job data keys: ${job.keys.toList()}');

      showDialog(
        context: context,
        useRootNavigator: true,
        builder: (dialogContext) => Dialog.fullscreen(
          child: Scaffold(
            appBar: AppBar(
              title: Row(
                children: [
                  Icon(Icons.picture_as_pdf, color: Colors.red.shade600),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "CV Preview - ${job['company']}",
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              backgroundColor: Colors.white,
              elevation: 1,
              leading: IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.pop(dialogContext),
                tooltip: 'Close PDF Preview',
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey.shade100,
                  foregroundColor: Colors.grey.shade700,
                ),
              ),
            ),
            body: Container(
              padding: const EdgeInsets.all(16),
              child: CVPreviewWidget(
                cvFilename: job['tailored_cv'],
                showCloseButton: true,
                onClose: () => Navigator.pop(dialogContext),
              ),
            ),
          ),
        ),
      );
    } catch (e) {
      if (!context.mounted) return;
      NotificationService.showError('Failed to load preview: $e');
    }
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
