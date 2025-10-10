///
/// Job Tracking Filters Widget
///
/// A reusable filtering and sorting component for job applications
/// with animated filter chips and dropdown menus
///

import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../utils/responsive_utils.dart';

class JobTrackingFilters extends StatefulWidget {
  final String selectedFilter;
  final String sortBy;
  final Function(String) onFilterChanged;
  final Function(String) onSortChanged;
  final List<String>? customFilters;

  const JobTrackingFilters({
    super.key,
    required this.selectedFilter,
    required this.sortBy,
    required this.onFilterChanged,
    required this.onSortChanged,
    this.customFilters,
  });

  @override
  State<JobTrackingFilters> createState() => _JobTrackingFiltersState();
}

class _JobTrackingFiltersState extends State<JobTrackingFilters>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  final List<String> _defaultFilters = [
    'All',
    'Applied',
    'Interview',
    'Rejected',
    'Offered'
  ];
  final List<String> _sortOptions = ['Date', 'Company', 'Priority', 'Status'];

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 400),
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

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Filter chips
          _buildFilterChips(),
          const SizedBox(height: 16),
          // Sort dropdown
          _buildSortDropdown(),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    final filters = widget.customFilters ?? _defaultFilters;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Filter by Status',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.neutralGray700,
              ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 40,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: filters.length,
            itemBuilder: (context, index) {
              final filter = filters[index];
              final isSelected = widget.selectedFilter == filter;

              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: _buildFilterChip(filter, isSelected),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String filter, bool isSelected) {
    return GestureDetector(
      onTap: () => widget.onFilterChanged(filter),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          gradient: isSelected ? AppTheme.primaryGradient : null,
          color: isSelected ? null : AppTheme.neutralGray100,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? Colors.transparent : AppTheme.neutralGray300,
            width: 1,
          ),
        ),
        child: Text(
          filter,
          style: TextStyle(
            color: isSelected ? Colors.white : AppTheme.neutralGray600,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            fontSize: context.isMobile ? 12 : 14,
          ),
        ),
      ),
    );
  }

  Widget _buildSortDropdown() {
    return Row(
      children: [
        Icon(
          Icons.sort,
          size: 20,
          color: AppTheme.neutralGray600,
        ),
        const SizedBox(width: 8),
        Text(
          'Sort by:',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.neutralGray700,
              ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppTheme.neutralGray300,
                width: 1,
              ),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: widget.sortBy,
                isExpanded: true,
                style: TextStyle(
                  color: AppTheme.neutralGray700,
                  fontSize: context.isMobile ? 12 : 14,
                  fontWeight: FontWeight.w500,
                ),
                items: _sortOptions.map((String option) {
                  return DropdownMenuItem<String>(
                    value: option,
                    child: Text(option),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    widget.onSortChanged(newValue);
                  }
                },
              ),
            ),
          ),
        ),
      ],
    );
  }
}
