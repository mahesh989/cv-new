import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/api_service.dart';

class JobInput extends StatefulWidget {
  final TextEditingController jdController;
  final TextEditingController jdUrlController;
  final VoidCallback onExtract;

  const JobInput({
    super.key,
    required this.jdController,
    required this.jdUrlController,
    required this.onExtract,
  });

  @override
  State<JobInput> createState() => _JobInputState();
}

class _JobInputState extends State<JobInput> with TickerProviderStateMixin {
  bool _hasJDText = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  bool _isExtracting = false;

  @override
  void initState() {
    super.initState();

    // Initialize animations
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // Add listener to JD controller
    widget.jdController.addListener(_onJDTextChanged);
  }

  void _onJDTextChanged() {
    final hasText = widget.jdController.text.trim().isNotEmpty;
    if (hasText != _hasJDText) {
      setState(() {
        _hasJDText = hasText;
      });

      if (_hasJDText) {
        _pulseController.forward();
      } else {
        _pulseController.reset();
      }
    }
  }

  @override
  void dispose() {
    widget.jdController.removeListener(_onJDTextChanged);
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _extractFromUrl() async {
    if (widget.jdUrlController.text.trim().isEmpty) {
      _showSnackBar('Please enter a job posting URL', isError: true);
      return;
    }

    setState(() {
      _isExtracting = true;
    });

    try {
      final result = await APIService.scrapeJobDescription(
          widget.jdUrlController.text.trim());

      if (result != null && result.isNotEmpty) {
        widget.jdController.text = result;
        _showSnackBar('Job description extracted successfully!');
      } else {
        _showSnackBar('No job description found at the provided URL',
            isError: true);
      }
    } catch (e) {
      _showSnackBar('Error extracting job description: $e', isError: true);
    } finally {
      setState(() {
        _isExtracting = false;
      });
    }
  }

  void _showSnackBar(String message, {bool isError = false}) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: isError ? Colors.red : Colors.green,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  Future<void> _analyzeJob() async {
    if (widget.jdController.text.trim().isEmpty) {
      _showSnackBar('Please enter a job description first', isError: true);
      return;
    }

    setState(() {
      _isExtracting = true;
    });

    try {
      final result = await APIService.extractAndSaveJob(
        jobDescription: widget.jdController.text.trim(),
        jobUrl: widget.jdUrlController.text.trim().isNotEmpty
            ? widget.jdUrlController.text.trim()
            : null,
      );

      if (result['success'] == true) {
        _showSnackBar(
          'Job analyzed successfully! Company: ${result['company_name']}, Title: ${result['job_title']}',
        );
      } else {
        _showSnackBar('Job analysis failed: ${result['error']}', isError: true);
      }
    } catch (e) {
      _showSnackBar('Error analyzing job: $e', isError: true);
    } finally {
      setState(() {
        _isExtracting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.work_outline,
                  color: AppTheme.primaryNeon,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'Job Description Input',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                const Spacer(),
                if (_hasJDText)
                  AnimatedBuilder(
                    animation: _pulseAnimation,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _pulseAnimation.value,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryNeon.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: AppTheme.primaryNeon.withOpacity(0.3),
                            ),
                          ),
                          child: Text(
                            '${widget.jdController.text.length} chars',
                            style: TextStyle(
                              color: AppTheme.primaryNeon,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // URL Input Section
            Text(
              'Job Posting URL (Optional)',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: widget.jdUrlController,
                    decoration: InputDecoration(
                      hintText: 'https://example.com/job-posting',
                      prefixIcon: const Icon(Icons.link),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(
                          color: AppTheme.primaryNeon,
                          width: 2,
                        ),
                      ),
                    ),
                    keyboardType: TextInputType.url,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _isExtracting ? null : _extractFromUrl,
                  icon: _isExtracting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                          ),
                        )
                      : const Icon(Icons.download),
                  label: Text(_isExtracting ? 'Extracting...' : 'Extract'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryNeon,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Manual Input Section
            Text(
              'Job Description Text',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: widget.jdController,
              maxLines: 8,
              decoration: InputDecoration(
                hintText: 'Paste or type the job description here...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: AppTheme.primaryNeon,
                    width: 2,
                  ),
                ),
                alignLabelWithHint: true,
              ),
              onChanged: (value) {
                // Trigger the listener manually if needed
                _onJDTextChanged();
              },
            ),
            const SizedBox(height: 16),

            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _hasJDText ? _analyzeJob : null,
                    icon: const Icon(Icons.analytics),
                    label: const Text('Analyze & Save Job'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _hasJDText ? Colors.blue : Colors.grey,
                      foregroundColor: _hasJDText ? Colors.white : Colors.grey,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _hasJDText
                      ? () {
                          widget.jdController.clear();
                          widget.jdUrlController.clear();
                        }
                      : null,
                  icon: const Icon(Icons.clear),
                  tooltip: 'Clear all',
                  style: IconButton.styleFrom(
                    backgroundColor: _hasJDText
                        ? Colors.red.withOpacity(0.1)
                        : Colors.grey.withOpacity(0.1),
                    foregroundColor: _hasJDText ? Colors.red : Colors.grey,
                  ),
                ),
              ],
            ),

            // Help Text
            if (!_hasJDText) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: Colors.blue.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: Colors.blue,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Enter a job description manually or extract it from a job posting URL.',
                        style: TextStyle(
                          color: Colors.blue[700],
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
