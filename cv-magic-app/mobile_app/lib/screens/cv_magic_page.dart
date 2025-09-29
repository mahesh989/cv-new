import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import '../widgets/cv_uploader.dart';
import '../services/api_service.dart';

class CVMagicPage extends StatefulWidget {
  const CVMagicPage({super.key});

  @override
  State<CVMagicPage> createState() => _CVMagicPageState();
}

class _CVMagicPageState extends State<CVMagicPage> {
  // CV selection
  String? selectedCVFilename;
  String? cvContent;
  bool isLoadingContent = false;

  // Available CVs (dynamic list)
  List<String> availableCVs = [];
  bool isLoading = false;
  int cvRefreshToken = 0;

  @override
  void initState() {
    super.initState();
    _loadAvailableCVs();
  }

  Future<void> _loadAvailableCVs() async {
    try {
      final response =
          await http.get(Uri.parse('http://localhost:8000/api/cv/list'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> cvList = data['uploaded_cvs'] ?? [];
        setState(() {
          availableCVs = cvList.map((cv) => cv.toString()).toList();
          // Do not auto-select; let the user choose explicitly
        });
      }
    } catch (e) {
      debugPrint('Error loading CVs: $e');
      // Do NOT fallback to default list; prompt user to upload instead
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
    }
  }

  Future<void> _loadCVContent(String filename) async {
    setState(() {
      isLoadingContent = true;
    });

    try {
      final response = await http
          .get(Uri.parse('http://localhost:8000/api/cv/content/$filename'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          cvContent = data['content'];
        });
      } else {
        setState(() {
          cvContent = 'Failed to load CV content';
        });
      }
    } catch (e) {
      setState(() {
        cvContent = 'Error loading CV content: $e';
      });
    } finally {
      setState(() {
        isLoadingContent = false;
      });
    }
  }

  Future<void> _onFilePicked(PlatformFile file) async {
    setState(() {
      isLoading = true;
    });

    try {
      final exists = await APIService.cvExists(file.name);
      if (exists) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Replacing existing CV: ${file.name}'),
            backgroundColor: Colors.orange,
          ),
        );
      }

      await APIService.uploadCV(file);
      // Trigger a refresh of the list and try to auto-select the uploaded CV
      await _loadAvailableCVs();
      setState(() {
        cvRefreshToken++;
      });
      // Do not auto-select after upload; user will choose from dropdown

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('CV uploaded successfully: ${file.name}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  Widget _buildCVSelectionSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (isLoading)
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: LinearProgressIndicator(),
              ),
            const Text('Select CV:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            DropdownButton<String>(
              value: selectedCVFilename,
              hint: const Text('Choose CV'),
              isExpanded: true,
              items: availableCVs
                  .map((cv) => DropdownMenuItem(
                        value: cv,
                        child: Text(cv),
                      ))
                  .toList(),
              onChanged: isLoading
                  ? null
                  : (value) {
                      setState(() {
                        selectedCVFilename = value;
                        cvContent = null; // Clear previous content
                      });
                      // Save selection in backend and load content
                      if (value != null) {
                        APIService.saveCVForAnalysis(value)
                            .then((_) => _loadCVContent(value))
                            .catchError((e) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Failed to save original CV: $e'),
                              backgroundColor: Colors.red,
                            ),
                          );
                        });
                      }
                    },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCVPreviewSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.preview, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'CV Preview: ${selectedCVFilename ?? ""}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (isLoadingContent)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (cvContent != null)
              Container(
                width: double.infinity,
                height: 300,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: SingleChildScrollView(
                  child: Text(
                    cvContent!,
                    style: const TextStyle(
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              )
            else
              Container(
                width: double.infinity,
                height: 100,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: const Center(
                  child: Text(
                    'Select a CV to view its content',
                    style: TextStyle(
                      color: Colors.grey,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // CV Upload Section
            CvUploader(onFilePicked: _onFilePicked, isLoading: isLoading),
            const SizedBox(height: 16),

            // CV Selection
            _buildCVSelectionSection(),
            const SizedBox(height: 16),

            // CV Preview Section
            if (selectedCVFilename != null) _buildCVPreviewSection(),

            // Loading indicator
            if (isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
