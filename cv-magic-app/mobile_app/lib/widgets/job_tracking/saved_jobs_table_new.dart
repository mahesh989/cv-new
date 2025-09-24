import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class SavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;

  const SavedJobsTable({
    super.key,
    required this.jobs,
  });

  @override
  State<SavedJobsTable> createState() => _SavedJobsTableState();
}

class _SavedJobsTableState extends State<SavedJobsTable> {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      constraints: BoxConstraints(minWidth: 800),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildJobsList(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(
              'Company',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              'Position',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
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
          SizedBox(
            width: 100,
            child: Text(
              'Status',
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

  Widget _buildJobsList() {
    if (widget.jobs.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      itemCount: widget.jobs.length,
      itemBuilder: (context, index) {
        final job = widget.jobs[index];
        return _buildJobRow(job);
      },
    );
  }

  Widget _buildJobRow(Map<String, dynamic> job) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.neutralGray200,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  job['company_name'] ?? 'Unknown Company',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.neutralGray800,
                      ),
                ),
                if (job['job_url'] != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    job['job_url'],
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.blue,
                          decoration: TextDecoration.underline,
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              job['job_title'] ?? 'Unknown Position',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(
              job['location'] ?? 'Unknown Location',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray600,
                  ),
            ),
          ),
          SizedBox(
            width: 100,
            child: _buildStatusChip(job['status'] ?? 'New'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color color;
    Color bgColor;
    
    switch (status.toLowerCase()) {
      case 'applied':
        color = Colors.blue;
        bgColor = Colors.blue.withOpacity(0.1);
        break;
      case 'interviewing':
        color = Colors.orange;
        bgColor = Colors.orange.withOpacity(0.1);
        break;
      case 'offered':
        color = Colors.green;
        bgColor = Colors.green.withOpacity(0.1);
        break;
      case 'rejected':
        color = Colors.red;
        bgColor = Colors.red.withOpacity(0.1);
        break;
      default:
        color = AppTheme.neutralGray600;
        bgColor = AppTheme.neutralGray100;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        status,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.neutralGray200,
          width: 1,
        ),
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
            'No saved jobs found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppTheme.neutralGray600,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Jobs you save will appear here',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
          ),
        ],
      ),
    );
  }
}