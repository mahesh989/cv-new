import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;
import 'dart:convert';
import '../tailored_cv_preview_dialog.dart';

class CVPreviewWidget extends StatefulWidget {
  final String? cvFilename;
  final bool showCloseButton;
  final VoidCallback? onClose;
  final String? preferredFormat; // "pdf" or "docx"

  const CVPreviewWidget({
    super.key,
    this.cvFilename,
    this.showCloseButton = false,
    this.onClose,
    this.preferredFormat,
  });

  @override
  State<CVPreviewWidget> createState() => _CVPreviewWidgetState();
}

class _CVPreviewWidgetState extends State<CVPreviewWidget> {
  @override
  void initState() {
    super.initState();
    // Automatically open the preview dialog when widget loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _openBeautifulPreview();
    });
  }

  void _openBeautifulPreview() async {
    if (widget.cvFilename == null || widget.cvFilename!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No CV selected for preview')),
      );
      return;
    }

    try {
      // Load the CV content for our beautiful preview
      String baseFilename = widget.cvFilename!;
      if (baseFilename.contains('.')) {
        baseFilename = baseFilename.substring(0, baseFilename.lastIndexOf('.'));
      }

      final response = await http.get(
        Uri.parse('http://localhost:8000/tailored-cvs/$baseFilename/preview'),
      );

      if (mounted && response.statusCode == 200) {
        // Open our beautiful preview dialog directly
        final result = await showDialog(
          context: context,
          useRootNavigator: true,
          builder: (context) => TailoredCVPreviewDialog(
            tailoredCVFilename: widget.cvFilename!,
            originalCVFilename: widget.cvFilename!,
            jdText: 'Sample job description', // We could make this configurable
            atsScore: 85, // Default score - could be made dynamic
            previewOverride: response.body,
          ),
        );

        // When dialog is closed, pop this widget too to return to previous screen
        if (mounted) {
          Navigator.of(context).pop();
        }
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content:
                  Text('Failed to load CV preview: ${response.statusCode}')),
        );
        // Also pop on error
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading CV preview: $e')),
        );
        // Also pop on error
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Return a simple loading indicator since we're opening the dialog immediately
    return Container(
      height: 400,
      child: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
