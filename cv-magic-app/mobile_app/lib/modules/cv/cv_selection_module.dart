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

  const CVSelectionModule({
    super.key,
    required this.selectedCVFilename,
    required this.onCVSelected,
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
      // Fallback to default list
      setState(() {
        availableCVs = [
          'MichaelPage_v1.pdf',
          'NoToViolence_v10.pdf',
          'example_professional_cv.pdf',
        ];
      });
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

    // Fallback to default list
    return [
      'MichaelPage_v1.pdf',
      'NoToViolence_v10.pdf',
      'example_professional_cv.pdf',
    ];
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
