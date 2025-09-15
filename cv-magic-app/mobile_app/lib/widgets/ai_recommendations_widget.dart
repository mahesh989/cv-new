import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/skills_analysis_model.dart';

/// Widget for displaying AI-powered CV recommendations
class AIRecommendationsWidget extends StatelessWidget {
  final AIRecommendationResult? aiRecommendation;
  final bool isLoading;

  const AIRecommendationsWidget({
    super.key,
    this.aiRecommendation,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    // Show loading state
    if (isLoading) {
      return _buildLoadingState();
    }

    // Don't show anything if no recommendation
    if (aiRecommendation == null || aiRecommendation!.isEmpty) {
      return const SizedBox.shrink();
    }

    return _buildRecommendationContent();
  }

  Widget _buildLoadingState() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.orange.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.orange.shade200),
        ),
        child: Row(
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(
                    Colors.orange.shade600),
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Generating AI recommendations...',
              style: TextStyle(
                fontSize: 14,
                color: Colors.orange.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationContent() {
    return Card(
      margin: const EdgeInsets.all(16),
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              const Color(0xFFE3F2FD), // Light blue
              const Color(0xFFF3E5F5), // Light purple
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: const Color(0xFF667EEA).withOpacity(0.3),
            width: 2,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(),
              const SizedBox(height: 16),

              // Recommendation Content (Markdown)
              _buildMarkdownContent(),
              
              // Generate New CV Button
              const SizedBox(height: 24),
              _buildGenerateNewCVButton(),
              
              // Footer with generation info
              if (aiRecommendation!.generatedAt != null ||
                  aiRecommendation!.modelInfo != null) ...[ 
                const SizedBox(height: 16),
                _buildFooter(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
            ),
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF667EEA).withOpacity(0.3),
                spreadRadius: 1,
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Icon(
            Icons.auto_awesome,
            color: Colors.white,
            size: 28,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'AI-Powered CV Recommendations',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF667EEA),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Personalized suggestions to improve your ATS score',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMarkdownContent() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: MarkdownBody(
        data: aiRecommendation!.content,
        styleSheet: MarkdownStyleSheet(
          // Headers
          h1: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Color(0xFF667EEA),
          ),
          h2: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF764BA2),
          ),
          h3: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF4A5568),
          ),
          // Body text
          p: const TextStyle(
            fontSize: 14,
            color: Color(0xFF2D3748),
            height: 1.5,
          ),
          // Lists
          listBullet: const TextStyle(
            fontSize: 14,
            color: Color(0xFF667EEA),
            fontWeight: FontWeight.bold,
          ),
          // Strong/bold text
          strong: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF2D3748),
          ),
          // Emphasis/italic text
          em: const TextStyle(
            fontStyle: FontStyle.italic,
            color: Color(0xFF4A5568),
          ),
          // Code
          code: TextStyle(
            fontSize: 13,
            fontFamily: 'monospace',
            backgroundColor: Colors.grey.shade100,
            color: const Color(0xFF2D3748),
          ),
          codeblockDecoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
        ),
        selectable: true,
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            size: 16,
            color: Colors.grey[600],
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (aiRecommendation!.modelInfo != null) ...[ 
                  Text(
                    'Generated by ${aiRecommendation!.modelInfo!['model'] ?? 'AI'} (${aiRecommendation!.modelInfo!['provider'] ?? ''})',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
                if (aiRecommendation!.generatedAt != null) ...[ 
                  Text(
                    'Generated: ${_formatDate(aiRecommendation!.generatedAt!)}',
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF667EEA).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'AI Generated',
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF667EEA),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGenerateNewCVButton() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.green.shade50,
            Colors.blue.shade50,
          ],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF667EEA).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.green.shade400, Colors.blue.shade400],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.rocket_launch,
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
                      'Ready to Generate Your CV?',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Use these AI recommendations to create an optimized CV',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _navigateToCVGeneration,
              icon: const Icon(Icons.auto_awesome, color: Colors.white),
              label: const Text(
                'Generate New CV',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade600,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToCVGeneration() {
    debugPrint('🚀 Navigate to CV Generation tab pressed!');
    
    // Find the context and navigate to CV Generation tab (index 2)
    final context = navigatorKey.currentContext;
    if (context != null) {
      // Get the HomeScreen state and switch to CV Generation tab
      final scaffoldMessenger = ScaffoldMessenger.of(context);
      scaffoldMessenger.showSnackBar(
        const SnackBar(
          content: Text('🚀 Navigating to CV Generation tab...'),
          duration: Duration(seconds: 2),
        ),
      );
      
      // For now, just show a message. In a full implementation, you'd use
      // a proper navigation method or state management to switch tabs.
      debugPrint('TODO: Implement tab switching to CV Generation (index 2)');
    }
  }

  // Global navigator key reference (you'd normally get this from your app)
  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateString;
    }
  }
}
