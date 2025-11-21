import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/skills_analysis_model.dart';

/// Modular AI Recommendation Display Card - matches ATS widget quality
class AIRecommendationDisplayCard extends StatelessWidget {
  final AIRecommendationResult? aiRecommendation;
  final bool isLoading;
  final VoidCallback? onGenerateCV;

  const AIRecommendationDisplayCard({
    super.key,
    this.aiRecommendation,
    this.isLoading = false,
    this.onGenerateCV,
  });

  @override
  Widget build(BuildContext context) {
    print('🔍 [AI_DEBUG] ===== AIRecommendationDisplayCard.build() START =====');
    print('   isLoading: $isLoading');
    print('   aiRecommendation parameter: ${aiRecommendation != null}');
    
    if (aiRecommendation != null) {
      print('   ✅ [AI_DEBUG] AI_RECOMMENDATION PROVIDED TO WIDGET!');
      print('   content length: ${aiRecommendation!.content.length}');
      print('   hasContent: ${aiRecommendation!.hasContent}');
      print('   isEmpty: ${aiRecommendation!.isEmpty}');
      print('   generatedAt: ${aiRecommendation!.generatedAt}');
      print('   modelInfo: ${aiRecommendation!.modelInfo}');
    } else {
      print('   ❌ [AI_DEBUG] AI_RECOMMENDATION IS NULL IN WIDGET!');
    }

    if (isLoading) {
      print('   → [AI_DEBUG] Showing loading state');
      print('🔍 [AI_DEBUG] ===== AIRecommendationDisplayCard.build() END (LOADING) =====');
      return _buildLoadingState();
    }

    if (aiRecommendation == null || aiRecommendation!.isEmpty) {
      print('   → [AI_DEBUG] Returning empty - no aiRecommendation or empty');
      print('🔍 [AI_DEBUG] ===== AIRecommendationDisplayCard.build() END (NO RESULT) =====');
      return const SizedBox.shrink();
    }
    
    print('   → [AI_DEBUG] Rendering AI recommendation card with data');
    print('🔍 [AI_DEBUG] ===== AIRecommendationDisplayCard.build() END (RENDERING) =====');

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF667EEA).withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 2,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with gradient
          _buildHeader(),

          const Divider(height: 1),

          // Recommendation Content (Markdown)
          _buildMarkdownContent(),

          // Generate Tailored CV Button
          const Divider(height: 1),
          _buildGenerateCVButton(),

          // Footer with generation info
          if (aiRecommendation!.generatedAt != null ||
              aiRecommendation!.modelInfo != null) ...[
            const Divider(height: 1),
            _buildFooter(),
          ],
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200, width: 2),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.orange.shade600),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Generating AI Recommendations...',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Analyzing your CV and job description to provide personalized suggestions',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.orange.shade600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(12),
          topRight: Radius.circular(12),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
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
                const Text(
                  'AI-Powered CV Recommendations',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Personalized suggestions to improve your ATS score',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withOpacity(0.9),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMarkdownContent() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      child: MarkdownBody(
        data: aiRecommendation!.content,
        styleSheet: MarkdownStyleSheet(
          // Headers
          h1: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Color(0xFF667EEA),
          ),
          h2: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF764BA2),
          ),
          h3: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF4A5568),
          ),
          // Body text
          p: const TextStyle(
            fontSize: 14,
            color: Color(0xFF2D3748),
            height: 1.6,
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

  Widget _buildGenerateCVButton() {
    const aiColor = Color(0xFF667EEA);
    
    return Container(
      padding: const EdgeInsets.all(16),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: onGenerateCV,
          icon: const Icon(Icons.rocket_launch, color: Colors.white),
          label: const Text(
            'Generate Tailored CV',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: aiColor,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            elevation: 2,
          ),
        ),
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(12),
          bottomRight: Radius.circular(12),
        ),
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
                  const SizedBox(height: 2),
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
            child: const Text(
              'AI Generated',
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: Color(0xFF667EEA),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateString;
    }
  }
}

