// ✅ PATCHED: CvSelector
import 'package:flutter/material.dart';
import '../services/session_updater.dart';
import '../theme/app_theme.dart';
import '../utils/responsive_utils.dart';

class CvSelector extends StatefulWidget {
  final List<String> files;
  final String? selected;
  final Function(String?) onChanged;
  final Future<void> Function() onRefresh;

  const CvSelector({
    super.key,
    required this.files,
    required this.selected,
    required this.onChanged,
    required this.onRefresh,
  });

  @override
  State<CvSelector> createState() => _CvSelectorState();
}

class _CvSelectorState extends State<CvSelector> with TickerProviderStateMixin {
  late AnimationController _refreshController;
  late Animation<double> _rotationAnimation;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _refreshController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _refreshController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _refreshController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppTheme.createCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 20),
          _buildSelector(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: EdgeInsets.all(context.isMobile ? 12 : 16),
      decoration: BoxDecoration(
        gradient: AppTheme.cosmicGradient,
        borderRadius: AppTheme.buttonRadius,
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryCosmic.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isNarrow = constraints.maxWidth < 400;

          if (isNarrow) {
            // Mobile layout - vertical stacking
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.description_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '📄 Select Your CV',
                        style: AppTheme.headingSmall.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Choose from your uploaded CV files',
                  style: AppTheme.bodyMedium.copyWith(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 13,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            );
          } else {
            // Desktop layout - horizontal
            return Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.description_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '📄 Select Your CV',
                        style: AppTheme.headingSmall.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Choose from your uploaded CV files',
                        style: AppTheme.bodyMedium.copyWith(
                          color: Colors.white.withOpacity(0.9),
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildSelector() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isNarrow = constraints.maxWidth < 500;

        if (isNarrow) {
          // Mobile layout - vertical stacking
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                decoration: BoxDecoration(
                  borderRadius: AppTheme.inputRadius,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryCosmic.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: DropdownButtonFormField<String>(
                  value: widget.selected,
                  hint: Row(
                    children: [
                      Icon(
                        Icons.upload_file_rounded,
                        color: AppTheme.primaryCosmic,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '✨ Select CV',
                          style: AppTheme.bodyMedium.copyWith(
                            color: AppTheme.neutralGray500,
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  onChanged: (String? newValue) {
                    if (newValue != null) {
                      SessionUpdater.updateOriginalCV(newValue);
                      widget.onChanged(newValue);
                    }
                  },
                  items: widget.files.map((f) {
                    return DropdownMenuItem(
                      value: f,
                      child: LayoutBuilder(
                        builder: (context, itemConstraints) {
                          return Row(
                            children: [
                              Icon(
                                Icons.description_rounded,
                                color: AppTheme.primaryCosmic,
                                size: 16,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  f,
                                  style: AppTheme.bodyMedium.copyWith(
                                    fontWeight: FontWeight.w500,
                                    fontSize: 13,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                  maxLines: 1,
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    );
                  }).toList(),
                  decoration: AppTheme.getInputDecoration(
                    hintText: '',
                  ).copyWith(
                    prefixIcon: null,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                  ),
                  style: AppTheme.bodyMedium.copyWith(fontSize: 14),
                  dropdownColor: Colors.white,
                  icon: Icon(
                    Icons.keyboard_arrow_down_rounded,
                    color: AppTheme.primaryCosmic,
                    size: 20,
                  ),
                  isExpanded: true,
                ),
              ),
              const SizedBox(height: 12),
              _buildRefreshButton(),
            ],
          );
        } else {
          // Desktop layout - horizontal
          return Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: AppTheme.inputRadius,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primaryCosmic.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: DropdownButtonFormField<String>(
                    value: widget.selected,
                    hint: Row(
                      children: [
                        Icon(
                          Icons.upload_file_rounded,
                          color: AppTheme.primaryCosmic,
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            '✨ Select Uploaded CV',
                            style: AppTheme.bodyMedium.copyWith(
                              color: AppTheme.neutralGray500,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    onChanged: (String? newValue) {
                      if (newValue != null) {
                        SessionUpdater.updateOriginalCV(newValue);
                        widget.onChanged(newValue);
                      }
                    },
                    items: widget.files.map((f) {
                      return DropdownMenuItem(
                        value: f,
                        child: Row(
                          children: [
                            Icon(
                              Icons.description_rounded,
                              color: AppTheme.primaryCosmic,
                              size: 18,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                f,
                                style: AppTheme.bodyMedium.copyWith(
                                  fontWeight: FontWeight.w500,
                                ),
                                overflow: TextOverflow.ellipsis,
                                maxLines: 1,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                    decoration: AppTheme.getInputDecoration(
                      hintText: '',
                    ).copyWith(
                      prefixIcon: null,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 16,
                      ),
                    ),
                    style: AppTheme.bodyMedium,
                    dropdownColor: Colors.white,
                    icon: Icon(
                      Icons.keyboard_arrow_down_rounded,
                      color: AppTheme.primaryCosmic,
                      size: 24,
                    ),
                    isExpanded: true,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              _buildRefreshButton(),
            ],
          );
        }
      },
    );
  }

  Widget _buildRefreshButton() {
    return AnimatedBuilder(
      animation: _rotationAnimation,
      builder: (context, child) {
        return Transform.rotate(
          angle: _rotationAnimation.value * 3.14159,
          child: Container(
            width: context.isMobile ? double.infinity : null,
            decoration: BoxDecoration(
              gradient: AppTheme.forestGradient,
              borderRadius: BorderRadius.circular(context.isMobile ? 8 : 12),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primaryEmerald.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: context.isMobile
                ? ElevatedButton.icon(
                    onPressed: _isRefreshing ? null : _handleRefresh,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.transparent,
                      shadowColor: Colors.transparent,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    icon: Icon(
                      _isRefreshing
                          ? Icons.hourglass_empty_rounded
                          : Icons.refresh_rounded,
                      color: Colors.white,
                      size: 18,
                    ),
                    label: Text(
                      'Refresh CV List',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                    ),
                  )
                : IconButton(
                    onPressed: _isRefreshing ? null : _handleRefresh,
                    icon: Icon(
                      _isRefreshing
                          ? Icons.hourglass_empty_rounded
                          : Icons.refresh_rounded,
                      color: Colors.white,
                      size: 24,
                    ),
                    tooltip: 'Refresh CV List',
                    padding: const EdgeInsets.all(12),
                  ),
          ),
        );
      },
    );
  }

  Future<void> _handleRefresh() async {
    if (_isRefreshing) return;

    setState(() => _isRefreshing = true);
    _refreshController.repeat();

    try {
      await widget.onRefresh();
    } finally {
      if (mounted) {
        _refreshController.stop();
        _refreshController.reset();
        setState(() => _isRefreshing = false);
      }
    }
  }
}
