import 'package:flutter/material.dart';

/// Detailed side-by-side CV vs JD skills display with comprehensive analysis
/// Shows AFTER user clicks "Proceed" in Analyze Match Decision
class DetailedSkillsDisplayCard extends StatefulWidget {
  final Map<String, dynamic> cvSkills;
  final Map<String, dynamic> jdSkills;
  final String? cvComprehensiveAnalysis;
  final String? jdComprehensiveAnalysis;

  const DetailedSkillsDisplayCard({
    super.key,
    required this.cvSkills,
    required this.jdSkills,
    this.cvComprehensiveAnalysis,
    this.jdComprehensiveAnalysis,
  });

  @override
  State<DetailedSkillsDisplayCard> createState() =>
      _DetailedSkillsDisplayCardState();
}

class _DetailedSkillsDisplayCardState extends State<DetailedSkillsDisplayCard> {
  bool _cvAnalysisExpanded = false;
  bool _jdAnalysisExpanded = false;

  @override
  Widget build(BuildContext context) {
    // Extract and sort skills alphabetically
    final cvTechnical = List<String>.from(widget.cvSkills['technical_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final cvSoft = List<String>.from(widget.cvSkills['soft_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final cvDomain = List<String>.from(widget.cvSkills['domain_keywords'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

    final jdTechnical = List<String>.from(widget.jdSkills['technical_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final jdSoft = List<String>.from(widget.jdSkills['soft_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final jdDomain = List<String>.from(widget.jdSkills['domain_keywords'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

    final cvTotal = cvTechnical.length + cvSoft.length + cvDomain.length;
    final jdTotal = jdTechnical.length + jdSoft.length + jdDomain.length;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: [
              Colors.indigo.shade50,
              Colors.indigo.shade100,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.indigo.shade700,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.analytics_outlined,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Detailed Skills Analysis',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo.shade900,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Comprehensive breakdown with analysis',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.indigo.shade700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Side-by-side skills columns
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // CV Skills Column
                  Expanded(
                    child: _buildSkillsColumn(
                      title: 'Your CV Skills',
                      totalCount: cvTotal,
                      technical: cvTechnical,
                      soft: cvSoft,
                      domain: cvDomain,
                      comprehensiveAnalysis: widget.cvComprehensiveAnalysis,
                      isExpanded: _cvAnalysisExpanded,
                      onExpandToggle: () {
                        setState(() {
                          _cvAnalysisExpanded = !_cvAnalysisExpanded;
                        });
                      },
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 16),

                  // JD Skills Column
                  Expanded(
                    child: _buildSkillsColumn(
                      title: 'Job Requirements',
                      totalCount: jdTotal,
                      technical: jdTechnical,
                      soft: jdSoft,
                      domain: jdDomain,
                      comprehensiveAnalysis: widget.jdComprehensiveAnalysis,
                      isExpanded: _jdAnalysisExpanded,
                      onExpandToggle: () {
                        setState(() {
                          _jdAnalysisExpanded = !_jdAnalysisExpanded;
                        });
                      },
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSkillsColumn({
    required String title,
    required int totalCount,
    required List<String> technical,
    required List<String> soft,
    required List<String> domain,
    required String? comprehensiveAnalysis,
    required bool isExpanded,
    required VoidCallback onExpandToggle,
    required MaterialColor color,
  }) {
    final hasAnalysis = comprehensiveAnalysis != null && 
                        comprehensiveAnalysis.trim().isNotEmpty;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: color.shade300, width: 2),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: color.shade100,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Column header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.shade700,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(10),
                topRight: Radius.circular(10),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      title.contains('CV') ? Icons.person : Icons.work,
                      color: Colors.white,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Total: $totalCount skills',
                  style: TextStyle(
                    fontSize: 12,
                    color: color.shade100,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),

          // Skills content
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Technical Skills
                if (technical.isNotEmpty) ...[ 
                  _buildSkillSection(
                    '🔧 Technical (${technical.length})',
                    technical,
                    color.shade50,
                    color.shade700,
                  ),
                  const SizedBox(height: 12),
                ],

                // Soft Skills
                if (soft.isNotEmpty) ...[
                  _buildSkillSection(
                    '🤝 Soft Skills (${soft.length})',
                    soft,
                    color.shade50,
                    color.shade700,
                  ),
                  const SizedBox(height: 12),
                ],

                // Domain Keywords
                if (domain.isNotEmpty) ...[
                  _buildSkillSection(
                    '📚 Domain (${domain.length})',
                    domain,
                    color.shade50,
                    color.shade700,
                  ),
                  const SizedBox(height: 12),
                ],

                // Empty state
                if (technical.isEmpty && soft.isEmpty && domain.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12.0),
                    child: Center(
                      child: Text(
                        'No skills extracted',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ),

                // Comprehensive Analysis Section (Expandable)
                if (hasAnalysis) ...[
                  const Divider(height: 24),
                  InkWell(
                    onTap: onExpandToggle,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: color.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: color.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.description_outlined,
                            color: color.shade700,
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Comprehensive Analysis',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: color.shade800,
                              ),
                            ),
                          ),
                          Icon(
                            isExpanded 
                                ? Icons.expand_less 
                                : Icons.expand_more,
                            color: color.shade700,
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  // Expandable analysis content
                  if (isExpanded) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: color.shade50.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: color.shade200,
                          width: 1,
                        ),
                      ),
                      child: Text(
                        comprehensiveAnalysis!,
                        style: TextStyle(
                          fontSize: 12,
                          color: color.shade900,
                          height: 1.5,
                        ),
                      ),
                    ),
                  ],
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSkillSection(
    String title,
    List<String> skills,
    Color bgColor,
    Color textColor,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: textColor,
          ),
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: skills.map((skill) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: bgColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey.shade300),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.shade200,
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: Text(
                skill,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: textColor,
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
