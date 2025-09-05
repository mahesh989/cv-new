import 'package:flutter/material.dart';

class ATSTestResult extends StatelessWidget {
  final Map<String, dynamic> result;

  const ATSTestResult({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ATS Test Result',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),

          // JD Analysis Section
          if (result.containsKey('jd_analysis')) ...[
            const Text(
              '📋 Skills & Keywords from Job Description:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSkillSection(
                      '🔧 Technical Skills & Tools',
                      (result['jd_analysis']['technical_skills']
                              as List<dynamic>)
                          .cast<String>(),
                      Colors.blue.shade50,
                    ),
                    const SizedBox(height: 16),
                    _buildSkillSection(
                      '🤝 Soft Skills',
                      (result['jd_analysis']['soft_skills'] as List<dynamic>)
                          .cast<String>(),
                      Colors.green.shade50,
                    ),
                    const SizedBox(height: 16),
                    _buildSkillSection(
                      '📚 Domain Keywords',
                      (result['jd_analysis']['domain_keywords']
                              as List<dynamic>)
                          .cast<String>(),
                      Colors.purple.shade50,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 30),
          ],

          // Matching Results Section
          const Text(
            '🎯 Matching Results:',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),

          // Scores
          _buildScoreSection(),
          const SizedBox(height: 20),

          // Matched Skills
          _buildSkillSection(
            '✅ Matched Hard Skills:',
            (result['matched_hard_skills'] as List<dynamic>).cast<String>(),
            Colors.green.shade50,
          ),
          const SizedBox(height: 16),
          _buildSkillSection(
            '✅ Matched Soft Skills:',
            (result['matched_soft_skills'] as List<dynamic>).cast<String>(),
            Colors.green.shade50,
          ),
          const SizedBox(height: 16),
          _buildSkillSection(
            '✅ Extra Matched Keywords:',
            (result['matched_extra_keywords'] as List<dynamic>).cast<String>(),
            Colors.green.shade50,
          ),
          const SizedBox(height: 30),

          // Missed Skills
          _buildSkillSection(
            '❌ Missed Hard Skills:',
            (result['missed_hard_skills'] as List<dynamic>).cast<String>(),
            Colors.red.shade50,
          ),
          const SizedBox(height: 16),
          _buildSkillSection(
            '❌ Missed Soft Skills:',
            (result['missed_soft_skills'] as List<dynamic>).cast<String>(),
            Colors.red.shade50,
          ),
          const SizedBox(height: 16),
          _buildSkillSection(
            '❌ Missed Other Keywords:',
            (result['missed_other_keywords'] as List<dynamic>).cast<String>(),
            Colors.red.shade50,
          ),
          const SizedBox(height: 30),

          // Improvement Tips
          if (result.containsKey('tips') &&
              (result['tips'] as List).isNotEmpty) ...[
            const Text(
              '💡 Improvement Tips:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    for (var tip in result['tips'])
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• ', style: TextStyle(fontSize: 16)),
                            Expanded(
                                child: Text(tip,
                                    style: const TextStyle(fontSize: 14))),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildScoreSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildScore('✨ Overall Score:', result['overall_score']),
            const SizedBox(height: 8),
            _buildScore('🎯 Skills Match:', result['skills_match']),
            const SizedBox(height: 8),
            _buildScore('🔍 Keyword Match:', result['keyword_match']),
          ],
        ),
      ),
    );
  }

  Widget _buildScore(String label, int score) {
    return Row(
      children: [
        Text(label, style: const TextStyle(fontSize: 16)),
        const SizedBox(width: 8),
        Text('$score/100',
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildSkillSection(String title, List<String> skills, Color bgColor) {
    if (skills.isEmpty || (skills.length == 1 && skills[0] == 'N/A')) {
      return Container();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: skills.map((skill) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: bgColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(skill),
            );
          }).toList(),
        ),
      ],
    );
  }
}
