import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class CVRecommendationsWidget extends StatefulWidget {
  final String? analysisFilepath;

  const CVRecommendationsWidget({
    super.key,
    this.analysisFilepath,
  });

  @override
  State<CVRecommendationsWidget> createState() =>
      _CVRecommendationsWidgetState();
}

class _CVRecommendationsWidgetState extends State<CVRecommendationsWidget> {
  bool _isLoading = false;
  Map<String, dynamic>? _recommendations;
  String? _error;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    if (widget.analysisFilepath != null) {
      _generateRecommendations();
    }
  }

  Future<void> _generateRecommendations() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // First, get the latest analysis file from the backend
      final latestFileResponse = await http.get(
        Uri.parse('${ApiService.baseUrl}/api/get-latest-analysis-file'),
      );

      if (latestFileResponse.statusCode != 200) {
        setState(() {
          _error =
              'No analysis files found. Please complete an ATS analysis first.';
          _isLoading = false;
        });
        return;
      }

      final latestFileData = jsonDecode(latestFileResponse.body);
      final analysisFilepath = latestFileData['filepath'];

      if (analysisFilepath == null) {
        setState(() {
          _error =
              'No analysis files found. Please complete an ATS analysis first.';
          _isLoading = false;
        });
        return;
      }

      // Now generate recommendations using the actual filepath
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/api/generate-recommendations'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'analysis_filepath': analysisFilepath,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _recommendations = data['recommendations'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to generate recommendations: ${response.statusCode}';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error generating recommendations: $e';
        _isLoading = false;
      });
    }
  }

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
                  Icon(Icons.lightbulb_outline, color: Colors.white, size: 24),
                  SizedBox(width: 8),
                  Text(
                    'CV Improvement Recommendations',
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
              if (_isLoading)
                _buildLoadingState()
              else if (_error != null)
                _buildErrorState()
              else if (_recommendations != null)
                _buildRecommendationsContent()
              else
                _buildEmptyState(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Column(
      children: [
        Text(
          'Generating personalized CV recommendations...',
          style: TextStyle(color: Colors.white70),
        ),
        SizedBox(height: 8),
        LinearProgressIndicator(
          backgroundColor: Colors.white24,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
        ),
      ],
    );
  }

  Widget _buildErrorState() {
    return Column(
      children: [
        Icon(Icons.error_outline, color: Colors.white, size: 48),
        SizedBox(height: 8),
        Text(
          _error!,
          style: TextStyle(color: Colors.white),
          textAlign: TextAlign.center,
        ),
        SizedBox(height: 16),
        ElevatedButton(
          onPressed: _generateRecommendations,
          child: Text('Retry'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.white,
            foregroundColor: Colors.blue,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Column(
      children: [
        Icon(Icons.assignment_outlined, color: Colors.white70, size: 48),
        SizedBox(height: 8),
        Text(
          'No recommendations available yet.\nComplete an ATS analysis to get personalized CV improvement suggestions.',
          style: TextStyle(color: Colors.white70),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildRecommendationsContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // CV Improvements
        if (_recommendations!['cv_improvements'] != null)
          _buildSection(
            'CV Sections to Modify',
            Icons.edit,
            _recommendations!['cv_improvements'],
            _buildCVImprovementItem,
          ),

        // Priority Actions
        if (_recommendations!['priority_actions'] != null)
          _buildSection(
            'Priority Actions',
            Icons.priority_high,
            _recommendations!['priority_actions'],
            _buildPriorityActionItem,
          ),

        // Quick Wins
        if (_recommendations!['quick_wins'] != null)
          _buildSection(
            'Quick Wins',
            Icons.flash_on,
            _recommendations!['quick_wins'],
            _buildQuickWinItem,
          ),

        // Score Projection
        if (_recommendations!['score_projection'] != null)
          _buildScoreProjection(),

        // Overall Strategy
        if (_recommendations!['overall_cv_strategy'] != null)
          _buildOverallStrategy(),
      ],
    );
  }

  Widget _buildSection(String title, IconData icon, List items,
      Widget Function(Map<String, dynamic>) itemBuilder) {
    if (items.isEmpty) return SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: Colors.white, size: 20),
            SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        SizedBox(height: 8),
        ...items.map((item) => itemBuilder(item)).toList(),
        SizedBox(height: 16),
      ],
    );
  }

  Widget _buildCVImprovementItem(Map<String, dynamic> item) {
    return Container(
      margin: EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item['section'] ?? 'Unknown Section',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 4),
          if (item['recommended_changes'] != null)
            ...(item['recommended_changes'] as List).map(
              (change) => Padding(
                padding: EdgeInsets.only(left: 8, top: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• ', style: TextStyle(color: Colors.white)),
                    Expanded(
                      child: Text(
                        change.toString(),
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          SizedBox(height: 4),
          Row(
            children: [
              Icon(Icons.trending_up, color: Colors.green, size: 16),
              SizedBox(width: 4),
              Text(
                'Impact: ${item['expected_score_impact'] ?? 'N/A'}',
                style: TextStyle(color: Colors.green, fontSize: 12),
              ),
              Spacer(),
              Text(
                'Timeline: ${item['timeline'] ?? 'N/A'}',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPriorityActionItem(Map<String, dynamic> item) {
    return Container(
      margin: EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.orange.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item['action'] ?? 'Unknown Action',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 4),
          Row(
            children: [
              Icon(Icons.schedule, color: Colors.orange, size: 16),
              SizedBox(width: 4),
              Text(
                'Timeline: ${item['timeline'] ?? 'N/A'}',
                style: TextStyle(color: Colors.orange, fontSize: 12),
              ),
              Spacer(),
              Text(
                'Impact: ${item['expected_impact'] ?? 'N/A'}',
                style: TextStyle(color: Colors.green, fontSize: 12),
              ),
            ],
          ),
          if (item['implementation'] != null) ...[
            SizedBox(height: 4),
            Text(
              'Implementation: ${item['implementation']}',
              style: TextStyle(color: Colors.white70, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildQuickWinItem(Map<String, dynamic> item) {
    return Container(
      margin: EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item['action'] ?? 'Unknown Action',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 4),
          Row(
            children: [
              Icon(Icons.flash_on, color: Colors.green, size: 16),
              SizedBox(width: 4),
              Text(
                'Impact: ${item['impact'] ?? 'N/A'}',
                style: TextStyle(color: Colors.green, fontSize: 12),
              ),
              Spacer(),
              Text(
                'Timeline: ${item['timeline'] ?? 'N/A'}',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildScoreProjection() {
    final projection = _recommendations!['score_projection'];
    return Container(
      margin: EdgeInsets.only(bottom: 16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up, color: Colors.blue, size: 20),
              SizedBox(width: 8),
              Text(
                'Score Projection',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 8),
          Row(
            children: [
              Text(
                'Current: ${projection['current_score'] ?? 'N/A'}',
                style: TextStyle(color: Colors.white70),
              ),
              SizedBox(width: 16),
              Icon(Icons.arrow_forward, color: Colors.white70, size: 16),
              SizedBox(width: 16),
              Text(
                'Projected: ${projection['projected_score'] ?? 'N/A'}',
                style:
                    TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          if (projection['total_improvement'] != null) ...[
            SizedBox(height: 4),
            Text(
              'Total Improvement: ${projection['total_improvement']}',
              style: TextStyle(color: Colors.green, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildOverallStrategy() {
    return Container(
      margin: EdgeInsets.only(top: 8),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.purple.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: Colors.purple, size: 20),
              SizedBox(width: 8),
              Text(
                'Overall CV Strategy',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 8),
          Text(
            _recommendations!['overall_cv_strategy'],
            style: TextStyle(color: Colors.white70),
          ),
        ],
      ),
    );
  }
}
