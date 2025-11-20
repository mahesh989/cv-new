import 'package:flutter/material.dart';

/// Simple widget to display CV skills vs JD skills side-by-side
/// Shows BEFORE analyze match decision for user to see comparison
class SkillsComparisonCard extends StatelessWidget {
  final Map<String, dynamic> cvSkills;
  final Map<String, dynamic> jdSkills;

  const SkillsComparisonCard({
    super.key,
    required this.cvSkills,
    required this.jdSkills,
  });

  @override
  Widget build(BuildContext context) {
    // Extract skills lists and sort alphabetically (case-insensitive)
    final cvTechnical = List<String>.from(cvSkills['technical_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final cvSoft = List<String>.from(cvSkills['soft_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final cvDomain = List<String>.from(cvSkills['domain_keywords'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    
    final jdTechnical = List<String>.from(jdSkills['technical_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final jdSoft = List<String>.from(jdSkills['soft_skills'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
    final jdDomain = List<String>.from(jdSkills['domain_keywords'] ?? [])
      ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

    final cvTotal = cvTechnical.length + cvSoft.length + cvDomain.length;
    final jdTotal = jdTechnical.length + jdSoft.length + jdDomain.length;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(Icons.compare_arrows, color: Colors.purple.shade700, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Skills Comparison',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.purple.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'Compare your CV skills with job requirements before deciding to proceed',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
              ),
            ),
            const SizedBox(height: 16),

            // Side-by-side comparison
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // CV Skills Column (Blue)
                Expanded(
                  child: _buildSkillsColumn(
                    title: 'Your CV Skills',
                    totalCount: cvTotal,
                    technical: cvTechnical,
                    soft: cvSoft,
                    domain: cvDomain,
                    color: Colors.blue,
                  ),
                ),
                
                const SizedBox(width: 16),
                
                // JD Skills Column (Green)
                Expanded(
                  child: _buildSkillsColumn(
                    title: 'Job Requirements',
                    totalCount: jdTotal,
                    technical: jdTechnical,
                    soft: jdSoft,
                    domain: jdDomain,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
          ],
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
    required MaterialColor color,
  }) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: color.shade200, width: 2),
        borderRadius: BorderRadius.circular(8),
        color: color.shade50,
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Column header
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color.shade800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Total: $totalCount skills',
            style: TextStyle(
              fontSize: 12,
              color: color.shade700,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),

          // Technical Skills
          if (technical.isNotEmpty) ...[
            _buildSkillSection(
              '🔧 Technical (${technical.length})',
              technical,
              color.shade100,
            ),
            const SizedBox(height: 8),
          ],

          // Soft Skills
          if (soft.isNotEmpty) ...[
            _buildSkillSection(
              '🤝 Soft Skills (${soft.length})',
              soft,
              color.shade100,
            ),
            const SizedBox(height: 8),
          ],

          // Domain Keywords
          if (domain.isNotEmpty) ...[
            _buildSkillSection(
              '📚 Domain (${domain.length})',
              domain,
              color.shade100,
            ),
          ],

          // Empty state
          if (technical.isEmpty && soft.isEmpty && domain.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 8.0),
              child: Text(
                'No skills extracted',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSkillSection(String title, List<String> skills, Color bgColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: skills.map((skill) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: bgColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: Text(
                skill,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
