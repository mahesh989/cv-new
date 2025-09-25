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

class _SavedJobsTableState extends State<SavedJobsTable> {
  final Map<String, bool> _appliedStatus = {};
  final Map<String, String> _remarks = {};
  final Set<String> _hoveredRows = {};

  @override
  void initState() {
    super.initState();
    _loadSavedStatuses();
  }

  Future<void> _loadSavedStatuses() async {
    final prefs = await SharedPreferences.getInstance();
    for (var job in widget.jobs) {
      final key = _getJobKey(job);
      setState(() {
        _appliedStatus[key] = prefs.getBool('applied_$key') ?? false;
        _remarks[key] = prefs.getString('remarks_$key') ?? '';
      });
    }
  }

  Future<void> _saveStatus(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('applied_$key', value);
  }

  Future<void> _saveRemark(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('remarks_$key', value);
  }

  String _getJobKey(Map<String, dynamic> job) {
    return '${job['company_name']}_${job['job_url']}';
  }

  String _formatDate(String? dateString) {
    if (dateString == null || dateString.isEmpty) {
      return 'Unknown Date';
    }

    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return 'Invalid Date';
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: 1200, // Fixed minimum width
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTableHeader(),
            const SizedBox(height: 8),
            widget.jobs.isEmpty ? _buildEmptyState() : _buildJobList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTableHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // Name column
          Expanded(
            flex: 3,
            child: Text(
              'Name',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Location column
          Expanded(
            flex: 2,
            child: Text(
              'Location',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Post column
          Expanded(
            flex: 3,
            child: Text(
              'Post',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Date column
          Expanded(
            flex: 2,
            child: Text(
              'Date',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Contact column
          Expanded(
            flex: 2,
            child: Text(
              'Contact',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Already Applied? column
          SizedBox(
            width: 120,
            child: Text(
              'Already Applied?',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Remarks column
          Expanded(
            flex: 2,
            child: Text(
              'Remarks',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildJobList() {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: widget.jobs.length,
      itemBuilder: (context, index) => _buildJobRow(widget.jobs[index]),
    );
  }

  Widget _buildJobRow(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final isHovered = _hoveredRows.contains(key);
    final isApplied = _appliedStatus[key] ?? false;

    return MouseRegion(
      onEnter: (_) => setState(() => _hoveredRows.add(key)),
      onExit: (_) => setState(() => _hoveredRows.remove(key)),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isHovered ? AppTheme.neutralGray50 : Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: AppTheme.neutralGray200,
            width: 1,
          ),
        ),
        child: Row(
          children: [
            // Name (company_name) - clickable if has URL
            Expanded(
              flex: 3,
              child: GestureDetector(
                onTap: job['job_url'] != null
                    ? () => _launchUrl(job['job_url'])
                    : null,
                child: Text(
                  job['company_name'] ?? 'Unknown Company',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                        color: job['job_url'] != null
                            ? (isHovered ? Colors.blue : AppTheme.primaryTeal)
                            : AppTheme.neutralGray700,
                        decoration: job['job_url'] != null && isHovered
                            ? TextDecoration.underline
                            : null,
                      ),
                ),
              ),
            ),
            // Location
            Expanded(
              flex: 2,
              child: Text(
                job['location'] ?? 'Unknown Location',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray600,
                    ),
              ),
            ),
            // Post (job_title)
            Expanded(
              flex: 3,
              child: Text(
                job['job_title'] ?? 'Unknown Position',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray700,
                    ),
              ),
            ),
            // Date (extracted_at)
            Expanded(
              flex: 2,
              child: Text(
                _formatDate(job['extracted_at']),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray600,
                    ),
              ),
            ),
            // Contact info (email/phone)
            Expanded(
              flex: 2,
              child: _buildContactInfo(job),
            ),
            // Already Applied? toggle
            SizedBox(
              width: 120,
              child: Switch(
                value: isApplied,
                onChanged: (value) async {
                  setState(() => _appliedStatus[key] = value);
                  await _saveStatus(key, value);
                  // Notify parent about status change
                  widget.onAppliedStatusChanged?.call(job, value);
                },
                activeColor: Colors.green,
              ),
            ),
            // Remarks
            Expanded(
              flex: 2,
              child: GestureDetector(
                onTap: () => _showRemarksDialog(job),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                  decoration: BoxDecoration(
                    color: AppTheme.neutralGray50,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(
                      color: AppTheme.neutralGray200,
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          _remarks[key]?.isEmpty ?? true
                              ? 'Add note...'
                              : _remarks[key]!,
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: _remarks[key]?.isEmpty ?? true
                                        ? AppTheme.neutralGray400
                                        : AppTheme.neutralGray700,
                                    fontStyle: _remarks[key]?.isEmpty ?? true
                                        ? FontStyle.italic
                                        : FontStyle.normal,
                                  ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Icon(
                        Icons.edit,
                        size: 14,
                        color: AppTheme.neutralGray400,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContactInfo(Map<String, dynamic> job) {
    final email = job['email'];
    final phone = job['phone_number'];

    if (email == null && phone == null) {
      return Text(
        'N/A',
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppTheme.neutralGray500,
              fontStyle: FontStyle.italic,
            ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (email != null)
          InkWell(
            onTap: () => _launchUrl('mailto:$email'),
            child: Text(
              email,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.blue,
                    decoration: TextDecoration.underline,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        if (email != null && phone != null) const SizedBox(height: 4),
        if (phone != null)
          InkWell(
            onTap: () => _launchUrl('tel:$phone'),
            child: Text(
              phone,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.blue,
                    decoration: TextDecoration.underline,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
      ],
    );
  }

  Future<void> _launchUrl(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    }
  }

  void _showRemarksDialog(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final controller = TextEditingController(text: _remarks[key] ?? '');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Add Remarks',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppTheme.neutralGray800,
              ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Add notes for ${job['company_name']} - ${job['job_title']}',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray600,
                  ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Enter your notes here...',
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
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Cancel',
              style: TextStyle(color: AppTheme.neutralGray600),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              setState(() => _remarks[key] = controller.text);
              await _saveRemark(key, controller.text);
              Navigator.of(context).pop();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryTeal,
              foregroundColor: Colors.white,
            ),
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.neutralGray200),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.work_outline,
            size: 48,
            color: AppTheme.neutralGray400,
          ),
          const SizedBox(height: 16),
          Text(
            'No jobs found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppTheme.neutralGray600,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your saved jobs will appear here',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
          ),
        ],
      ),
    );
  }
}
