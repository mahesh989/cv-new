///
/// CV Selection Module
///
/// Handles CV listing and selection functionality.
///

import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class CVSelectionModule extends StatefulWidget {
  final String? selectedCVFilename;
  final Function(String?) onCVSelected;
  final int refreshToken;

  const CVSelectionModule({
    super.key,
    required this.selectedCVFilename,
    required this.onCVSelected,
    this.refreshToken = 0,
  });

  @override
  State<CVSelectionModule> createState() => _CVSelectionModuleState();
}

class _CVSelectionModuleState extends State<CVSelectionModule> {
  List<String> availableCVs = [];
  bool isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadAvailableCVs();
  }

  @override
  void didUpdateWidget(covariant CVSelectionModule oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Trigger reload when refresh token changes
    if (oldWidget.refreshToken != widget.refreshToken) {
      _loadAvailableCVs();
    }
  }

  Future<void> _loadAvailableCVs() async {
    setState(() {
      isLoading = true;
    });

    try {
      // Use APIService instead of direct HTTP call
      final cvs = await APIService.fetchUploadedCVs();
      setState(() {
        availableCVs = cvs;
      });
    } catch (e) {
      debugPrint('Error loading CVs: $e');
      // Do NOT fallback to hardcoded list; prompt user to upload instead
      setState(() {
        availableCVs = [];
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No CVs found. Please upload a CV to continue.'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Select CV:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              if (isLoading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(20),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (availableCVs.isEmpty)
                const Text(
                  'No CVs available. Please upload a CV to proceed.',
                  style: TextStyle(color: Colors.grey),
                )
              else
                DropdownButton<String>(
                  value: widget.selectedCVFilename,
                  hint: const Text('Choose CV'),
                  isExpanded: true,
                  items: availableCVs
                      .map((cv) => DropdownMenuItem(
                            value: cv,
                            child: Text(
                              cv,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ))
                      .toList(),
                  onChanged: widget.onCVSelected,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class CVSelectionService {
  /// Load available CVs from backend
  static Future<List<String>> loadAvailableCVs() async {
    try {
      // Use APIService instead of direct HTTP call
      return await APIService.fetchUploadedCVs();
    } catch (e) {
      debugPrint('Error loading CVs: $e');
    }

    // No fallback list; force user to upload
    return [];
  }

  /// Get CV information
  static Future<Map<String, dynamic>?> getCVInfo(String filename) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/cv/info/$filename',
        method: 'GET',
      );
      return response;
    } catch (e) {
      debugPrint('Error getting CV info: $e');
    }
    return null;
  }
}
