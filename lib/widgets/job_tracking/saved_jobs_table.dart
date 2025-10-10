///
/// Saved Jobs Table Widget
///
/// A beautiful, modern table displaying saved jobs with interactive elements,
/// hover effects, and iOS-style toggles for application status.
///

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/theme/app_theme.dart';

class SavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;
  final Function(Map<String, dynamic>, bool)? onAppliedStatusChanged;
  final Function(Map<String, dynamic>, String)? onRemarksChanged;

  const SavedJobsTable({
    super.key,
    required this.jobs,
    this.onAppliedStatusChanged,
    this.onRemarksChanged,
  });

  @override
  State<SavedJobsTable> createState() => _SavedJobsTableState();
}

class _SavedJobsTableState extends State<SavedJobsTable>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // Track applied status for each job
  final Map<String, bool> _appliedStatus = {};
  final Map<String, String> _remarks = {};
  final Set<String> _hoveredKeys = {};

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeJobStates();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _animationController.forward();
  }

  void _initializeJobStates() {
    for (var job in widget.jobs) {
      final key = _getJobKey(job);
      _appliedStatus[key] = false; // Default to not applied
      _remarks[key] = '';
    }
    _loadPersistedState();
  }

  String _getJobKey(Map<String, dynamic> job) {
    return '${job['company_name']}_${job['job_url']}';
  }

  Future<void> _loadPersistedState() async {
    final prefs = await SharedPreferences.getInstance();
    for (var job in widget.jobs) {
      final key = _getJobKey(job);
      final applied = prefs.getBool('saved_jobs_applied_$key');
      final note = prefs.getString('saved_jobs_remarks_$key');
      if (applied != null || note != null) {
        setState(() {
          if (applied != null) _appliedStatus[key] = applied;
          if (note != null) _remarks[key] = note;
        });
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    print(
        '📊 [SAVED_JOBS_TABLE] Building table with ${widget.jobs.length} jobs');
    for (var job in widget.jobs) {
      print(
          '📋 [SAVED_JOBS_TABLE] Job: ${job['company_name']} - ${job['job_title']}');
    }

    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildTableHeader(),
          const SizedBox(height: 16),
          if (widget.jobs.isEmpty)
            _buildEmptyTableState()
          else
            _buildJobsList(),
        ],
      ),
    );
  }

  Widget _buildEmptyTableState() {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: AppTheme.createCard(
        child: Container(
          decoration: BoxDecoration(
            color: AppTheme.neutralGray50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: AppTheme.neutralGray200,
              width: 1,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row with placeholder company name and applied status
                Row(
                  children: [
                    Expanded(
                      child: _buildPlaceholderCompanyName(),
                    ),
                    const SizedBox(width: 12),
                    _buildPlaceholderAppliedToggle(),
                  ],
                ),

                const SizedBox(height: 12),

                // Job details row
                Row(
                  children: [
                    Expanded(
                      child: _buildPlaceholderJobTitle(),
                    ),
                    const SizedBox(width: 12),
                    _buildPlaceholderLocation(),
                  ],
                ),

                const SizedBox(height: 12),

                // Contact and remarks row
                Row(
                  children: [
                    Expanded(
                      child: _buildPlaceholderContact(),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildPlaceholderRemarks(),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholderCompanyName() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray200,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: AppTheme.neutralGray300,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.business,
            size: 16,
            color: AppTheme.neutralGray500,
          ),
          const SizedBox(width: 6),
          Text(
            'No jobs available',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.neutralGray500,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlaceholderJobTitle() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Post',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          'No position available',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.neutralGray400,
                fontStyle: FontStyle.italic,
              ),
        ),
      ],
    );
  }

  Widget _buildPlaceholderLocation() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Location',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            Icon(
              Icons.location_on,
              size: 16,
              color: AppTheme.neutralGray400,
            ),
            const SizedBox(width: 4),
            Text(
              'No location',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray400,
                    fontStyle: FontStyle.italic,
                  ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPlaceholderContact() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Contact',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          'N/A',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppTheme.neutralGray400,
                fontStyle: FontStyle.italic,
              ),
        ),
      ],
    );
  }

  Widget _buildPlaceholderAppliedToggle() {
    return Column(
      children: [
        Text(
          'Applied?',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Container(
          width: 50,
          height: 28,
          decoration: BoxDecoration(
            color: AppTheme.neutralGray300,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Center(
            child: Icon(
              Icons.close,
              size: 14,
              color: AppTheme.neutralGray500,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPlaceholderRemarks() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Remarks',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: AppTheme.neutralGray100,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: AppTheme.neutralGray300,
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                Icons.note_add,
                size: 16,
                color: AppTheme.neutralGray400,
              ),
              const SizedBox(width: 8),
              Text(
                'No remarks available',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.neutralGray400,
                      fontStyle: FontStyle.italic,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTableHeader() {
    return Row(
      children: [
        Icon(
          Icons.table_chart,
          size: 20,
          color: AppTheme.primaryTeal,
        ),
        const SizedBox(width: 8),
        Text(
          'Saved Jobs (${widget.jobs.length})',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppTheme.neutralGray800,
              ),
        ),
        if (widget.jobs.isEmpty) ...[
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray200,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'No data available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.neutralGray600,
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildJobsList() {
    // Keep this simple and constraint-safe under SingleChildScrollView
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: widget.jobs.length,
      itemBuilder: (context, index) {
        final job = widget.jobs[index];
        return _buildJobCard(job, index);
      },
    );
  }

  Widget _buildJobCard(Map<String, dynamic> job, int index) {
    final isEven = index % 2 == 0;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: AppTheme.createCard(
        child: Container(
          decoration: BoxDecoration(
            color: isEven
                ? Colors.white
                : AppTheme.neutralGray50.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: AppTheme.neutralGray200,
              width: 1,
            ),
          ),
          child: InkWell(
            onTap: () => _handleJobCardTap(job),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header row with company name and applied status
                  Row(
                    children: [
                      Expanded(
                        child: _buildCompanyName(job),
                      ),
                      const SizedBox(width: 12),
                      _buildAppliedToggle(job),
                    ],
                  ),

                  const SizedBox(height: 12),

                  // Job details row
                  Row(
                    children: [
                      Expanded(
                        child: _buildJobTitle(job),
                      ),
                      const SizedBox(width: 12),
                      _buildLocation(job),
                    ],
                  ),

                  const SizedBox(height: 12),

                  // Contact and remarks row
                  Row(
                    children: [
                      Expanded(
                        child: _buildContact(job),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildRemarks(job),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCompanyName(Map<String, dynamic> job) {
    final companyName = job['company_name'] ?? 'Unknown Company';
    final jobUrl = job['job_url'];
    final key = _getJobKey(job);
    final isHovered = _hoveredKeys.contains(key);

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hoveredKeys.add(key)),
      onExit: (_) => setState(() => _hoveredKeys.remove(key)),
      child: GestureDetector(
        onTap: () => _openJobUrl(jobUrl),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                (isHovered ? Colors.blue : AppTheme.primaryTeal)
                    .withValues(alpha: 0.12),
                (isHovered ? Colors.blue : AppTheme.primaryTeal)
                    .withValues(alpha: 0.06),
              ],
            ),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: (isHovered ? Colors.blue : AppTheme.primaryTeal)
                  .withValues(alpha: 0.35),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: (isHovered ? Colors.blue : AppTheme.primaryTeal)
                    .withValues(alpha: 0.12),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.business,
                size: 16,
                color: isHovered ? Colors.blue : AppTheme.primaryTeal,
              ),
              const SizedBox(width: 6),
              Text(
                companyName,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isHovered ? Colors.blue : AppTheme.primaryTeal,
                      decoration: isHovered ? TextDecoration.underline : null,
                    ),
              ),
              const SizedBox(width: 4),
              Icon(
                Icons.open_in_new,
                size: 14,
                color: (isHovered ? Colors.blue : AppTheme.primaryTeal)
                    .withValues(alpha: 0.7),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildJobTitle(Map<String, dynamic> job) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Post',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          job['job_title'] ?? 'Unknown Position',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.neutralGray700,
              ),
        ),
      ],
    );
  }

  Widget _buildLocation(Map<String, dynamic> job) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Location',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            Icon(
              Icons.location_on,
              size: 16,
              color: AppTheme.neutralGray500,
            ),
            const SizedBox(width: 4),
            Expanded(
              child: Text(
                job['location'] ?? 'Unknown Location',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray600,
                    ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildContact(Map<String, dynamic> job) {
    final email = job['email'];
    final phone = job['phone_number'];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Contact',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        if (email != null || phone != null) ...[
          if (email != null)
            _buildContactItem(Icons.email, email, 'mailto:$email'),
          if (email != null && phone != null) const SizedBox(height: 4),
          if (phone != null)
            _buildContactItem(Icons.phone, phone, 'tel:$phone'),
        ] else ...[
          Text(
            'N/A',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray400,
                  fontStyle: FontStyle.italic,
                ),
          ),
        ],
      ],
    );
  }

  Widget _buildContactItem(IconData icon, String contact, String url) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => _openUrl(url),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppTheme.primaryTeal.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(6),
            border: Border.all(
              color: AppTheme.primaryTeal.withValues(alpha: 0.2),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: 16,
                color: AppTheme.primaryTeal,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  contact,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.primaryTeal,
                        fontWeight: FontWeight.w500,
                      ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppliedToggle(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final isApplied = _appliedStatus[key] ?? false;

    return Column(
      children: [
        Text(
          'Applied?',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        GestureDetector(
          onTap: () => _toggleAppliedStatus(job),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 50,
            height: 28,
            decoration: BoxDecoration(
              color: isApplied ? Colors.green : AppTheme.neutralGray300,
              borderRadius: BorderRadius.circular(14),
            ),
            child: AnimatedAlign(
              duration: const Duration(milliseconds: 200),
              alignment:
                  isApplied ? Alignment.centerRight : Alignment.centerLeft,
              child: Container(
                width: 24,
                height: 24,
                margin: const EdgeInsets.all(2),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.2),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Icon(
                  isApplied ? Icons.check : Icons.close,
                  size: 14,
                  color: isApplied ? Colors.green : AppTheme.neutralGray500,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRemarks(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final remarks = _remarks[key] ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Remarks',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.neutralGray500,
                fontWeight: FontWeight.w500,
              ),
        ),
        const SizedBox(height: 4),
        GestureDetector(
          onTap: () => _showRemarksDialog(job),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  AppTheme.neutralGray50,
                  AppTheme.neutralGray100,
                ],
              ),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppTheme.neutralGray300,
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 2,
                  offset: const Offset(0, 1),
                ),
              ],
            ),
            child: Row(
              children: [
                Icon(
                  Icons.note_add,
                  size: 16,
                  color: AppTheme.neutralGray400,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    remarks.isEmpty ? 'Add note...' : remarks,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: remarks.isEmpty
                              ? AppTheme.neutralGray400
                              : AppTheme.neutralGray600,
                          fontStyle: remarks.isEmpty
                              ? FontStyle.italic
                              : FontStyle.normal,
                        ),
                  ),
                ),
                if (remarks.isNotEmpty)
                  Icon(
                    Icons.edit,
                    size: 14,
                    color: AppTheme.primaryTeal,
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _handleJobCardTap(Map<String, dynamic> job) {
    // Handle card tap if needed
  }

  void _openJobUrl(String? url) async {
    if (url != null && url.isNotEmpty) {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }

  void _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  void _toggleAppliedStatus(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    setState(() {
      _appliedStatus[key] = !(_appliedStatus[key] ?? false);
    });
    _persistApplied(key, _appliedStatus[key] ?? false);
    widget.onAppliedStatusChanged?.call(job, _appliedStatus[key]!);
  }

  void _showRemarksDialog(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final currentRemarks = _remarks[key] ?? '';
    final controller = TextEditingController(text: currentRemarks);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.note_add,
              color: AppTheme.primaryTeal,
            ),
            const SizedBox(width: 8),
            Text('Add Remarks'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${job['company_name']} - ${job['job_title']}',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray600,
                    fontWeight: FontWeight.w500,
                  ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Add your notes about this job...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppTheme.primaryTeal),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _remarks[key] = controller.text;
              });
              _persistRemarks(key, controller.text);
              widget.onRemarksChanged?.call(job, controller.text);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryTeal,
              foregroundColor: Colors.white,
            ),
            child: Text('Save'),
          ),
        ],
      ),
    );
  }

  Future<void> _persistApplied(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('saved_jobs_applied_$key', value);
  }

  Future<void> _persistRemarks(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('saved_jobs_remarks_$key', value);
  }
}
