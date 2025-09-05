///
/// CV Selection Module
///
/// Handles CV listing and selection functionality.
///

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
      final response =
          await http.get(Uri.parse('http://localhost:8000/api/cv/list'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> cvList = data['uploaded_cvs'] ?? [];
        setState(() {
          availableCVs = cvList.map((cv) => cv.toString()).toList();
        });
      }
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
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
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
                          child: Text(cv),
                        ))
                    .toList(),
                onChanged: widget.onCVSelected,
              ),
          ],
        ),
      ),
    );
  }
}

class CVSelectionService {
  /// Load available CVs from backend
  static Future<List<String>> loadAvailableCVs() async {
    try {
      final response =
          await http.get(Uri.parse('http://localhost:8000/api/cv/list'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> cvList = data['uploaded_cvs'] ?? [];
        return cvList.map((cv) => cv.toString()).toList();
      }
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
      final response = await http
          .get(Uri.parse('http://localhost:8000/api/cv/info/$filename'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      debugPrint('Error getting CV info: $e');
    }
    return null;
  }
}
