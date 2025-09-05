import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class IntelligentSkillAnalysisWidget extends StatefulWidget {
  const IntelligentSkillAnalysisWidget({super.key});

  @override
  State<IntelligentSkillAnalysisWidget> createState() =>
      _IntelligentSkillAnalysisWidgetState();
}

class _IntelligentSkillAnalysisWidgetState
    extends State<IntelligentSkillAnalysisWidget> {
  bool _isLoading = false;
  Map<String, dynamic>? _analysisData;
  String? _error;
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Container(
        decoration: BoxDecoration(
          gradient: AppTheme.royalGradient,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.psychology, color: Colors.white, size: 24),
                  SizedBox(width: 8),
                  Text(
                    'Intelligent Skill Analysis',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Spacer(),
                  if (_isLoading)
                    SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    ),
                ],
              ),
              SizedBox(height: 16),

              // Action Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _fetchIntelligentAnalysis,
                  icon: Icon(Icons.analytics, color: Colors.white),
                  label: Text(
                    'Get Intelligent Skill Analysis',
                    style: TextStyle(
                        color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                    padding: EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),

              SizedBox(height: 16),

              // Error Display
              if (_error != null)
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.withOpacity(0.3)),
                  ),
                  child: Text(
                    _error!,
                    style: TextStyle(color: Colors.red[100]),
                  ),
                ),

              // Analysis Data Display
              if (_analysisData != null) ...[
                SizedBox(height: 16),

                // Expand/Collapse Button
                Row(
                  children: [
                    IconButton(
                      onPressed: () {
                        setState(() {
                          _isExpanded = !_isExpanded;
                        });
                      },
                      icon: Icon(
                        _isExpanded ? Icons.expand_less : Icons.expand_more,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      'Analysis Results',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Spacer(),
                    Text(
                      '${_analysisData!.length} sections',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),

                // JSON Display
                if (_isExpanded)
                  Container(
                    width: double.infinity,
                    constraints: BoxConstraints(maxHeight: 400),
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Raw JSON Analysis Data:',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 8),
                          Container(
                            padding: EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.3),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              JsonEncoder.withIndent('  ')
                                  .convert(_analysisData!),
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontFamily: 'monospace',
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Summary Display
                if (!_isExpanded) ...[
                  SizedBox(height: 8),
                  _buildAnalysisSummary(),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnalysisSummary() {
    if (_analysisData == null) return SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Analysis Summary:',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(height: 8),

        // Metadata
        if (_analysisData!['analysis_metadata'] != null)
          _buildSummaryItem(
            'Source File',
            _analysisData!['analysis_metadata']['source_file'] ?? 'Unknown',
            Icons.description,
          ),

        // Raw content length
        if (_analysisData!['raw_analysis_content'] != null)
          _buildSummaryItem(
            'Content Length',
            '${_analysisData!['raw_analysis_content'].toString().length} characters',
            Icons.text_fields,
          ),

        // Message
        if (_analysisData!['message'] != null)
          _buildSummaryItem(
            'Status',
            _analysisData!['message'],
            Icons.info,
          ),
      ],
    );
  }

  Widget _buildSummaryItem(String label, String value, IconData icon) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(icon, color: Colors.white.withOpacity(0.8), size: 16),
          SizedBox(width: 8),
          Text(
            '$label: ',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 12,
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _fetchIntelligentAnalysis() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/api/get-intelligent-skill-analysis'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _analysisData = data;
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to fetch analysis: ${response.statusCode}';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error fetching analysis: $e';
        _isLoading = false;
      });
    }
  }
}
