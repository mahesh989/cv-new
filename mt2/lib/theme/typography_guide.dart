import 'package:flutter/material.dart';
import 'app_theme.dart';

/// 🎨 PROFESSIONAL TYPOGRAPHY GUIDE
///
/// This guide showcases the sophisticated typography system inspired by:
/// - Linear (geometric perfection)
/// - Vercel (clean minimalism)
/// - Stripe (professional confidence)
/// - GitHub (developer-friendly)
/// - Notion (readable hierarchy)
///
/// FONT CHOICES:
/// 📐 Manrope: Display & hero text (geometric, friendly, impactful)
/// 📖 Inter: UI elements & body text (optimized for screens, highly readable)
/// 💻 JetBrains Mono: Code & technical content (developer favorite)

class TypographyGuide extends StatelessWidget {
  const TypographyGuide({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.neutralGray50,
      appBar: AppBar(
        title: Text('Typography System', style: AppTheme.headingMedium),
        backgroundColor: Colors.white,
        foregroundColor: AppTheme.neutralGray900,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSection('🎯 Display & Hero Text', [
              _buildTypeExample('Display Large', AppTheme.displayLarge,
                  'Hero sections, landing pages'),
              _buildTypeExample('Display Medium', AppTheme.displayMedium,
                  'Section headers, page titles'),
              _buildTypeExample('Display Small', AppTheme.displaySmall,
                  'Card titles, dialog headers'),
            ]),
            _buildSection('📝 Headings', [
              _buildTypeExample('Heading Large', AppTheme.headingLarge,
                  'Main content headings'),
              _buildTypeExample('Heading Medium', AppTheme.headingMedium,
                  'Section titles'),
              _buildTypeExample('Heading Small', AppTheme.headingSmall,
                  'Subsection headers'),
            ]),
            _buildSection('📖 Body Text', [
              _buildTypeExample('Body Large', AppTheme.bodyLarge,
                  'Primary content, articles, descriptions'),
              _buildTypeExample('Body Medium', AppTheme.bodyMedium,
                  'Secondary content, helper text'),
              _buildTypeExample('Body Small', AppTheme.bodySmall,
                  'Captions, footnotes, metadata'),
            ]),
            _buildSection('🏷️ Labels & UI', [
              _buildTypeExample('Label Large', AppTheme.labelLarge,
                  'Form labels, table headers'),
              _buildTypeExample('Label Medium', AppTheme.labelMedium,
                  'Small labels, badges'),
              _buildTypeExample('Label Small', AppTheme.labelSmall,
                  'Tiny labels, status indicators'),
            ]),
            _buildSection('🔗 Interactive Elements', [
              _buildTypeExample('Button Large', AppTheme.buttonLarge,
                  'Primary CTAs, major actions'),
              _buildTypeExample('Button Medium', AppTheme.buttonMedium,
                  'Secondary buttons'),
              _buildTypeExample('Button Small', AppTheme.buttonSmall,
                  'Compact buttons, links'),
              _buildTypeExample(
                  'Link Text', AppTheme.linkText, 'Inline links, navigation'),
            ]),
            _buildSection('💻 Monospace', [
              _buildTypeExample('Mono Large', AppTheme.monoLarge,
                  'Code blocks, CV content'),
              _buildTypeExample('Mono Medium', AppTheme.monoMedium,
                  'Filenames, inline code'),
              _buildTypeExample('Mono Small', AppTheme.monoSmall,
                  'Small technical text'),
            ]),
            _buildSection('🎨 Accent Styles', [
              _buildTypeExample('Accent', AppTheme.accent,
                  'Special emphasis, highlights'),
              _buildTypeExample('Success', AppTheme.success,
                  'Success messages, confirmations'),
              _buildTypeExample(
                  'Warning', AppTheme.warning, 'Warnings, cautions'),
              _buildTypeExample('Error', AppTheme.error,
                  'Errors, critical information'),
            ]),
            _buildUsageExamples(),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> examples) {
    return Container(
      margin: const EdgeInsets.only(bottom: 32),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: AppTheme.cardRadius,
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: AppTheme.headingMedium.copyWith(
                color: AppTheme.primaryCosmic,
              )),
          const SizedBox(height: 20),
          ...examples,
        ],
      ),
    );
  }

  Widget _buildTypeExample(String name, TextStyle style, String usage) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.neutralGray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(name,
                  style: AppTheme.labelLarge.copyWith(
                    color: AppTheme.primaryTeal,
                    fontWeight: FontWeight.w600,
                  )),
              const Spacer(),
              Text('${style.fontSize?.toInt()}px', style: AppTheme.caption),
            ],
          ),
          const SizedBox(height: 8),
          Text('The quick brown fox jumps over the lazy dog', style: style),
          const SizedBox(height: 4),
          Text(usage,
              style: AppTheme.caption.copyWith(
                color: AppTheme.neutralGray500,
              )),
        ],
      ),
    );
  }

  Widget _buildUsageExamples() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: AppTheme.cardRadius,
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('💫 Real-World Examples',
              style: AppTheme.headingMedium.copyWith(
                color: AppTheme.primaryCosmic,
              )),
          const SizedBox(height: 20),

          // Card example
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.neutralGray200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('CV Analysis Complete', style: AppTheme.headingSmall),
                const SizedBox(height: 8),
                Text(
                    'Your CV has been successfully analyzed against the job description. Here are the results:',
                    style: AppTheme.bodyMedium),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Text('ATS Score: ', style: AppTheme.labelMedium),
                    Text('87/100', style: AppTheme.accent),
                    const Spacer(),
                    Text('Excellent Match', style: AppTheme.success),
                  ],
                ),
                const SizedBox(height: 16),
                Text('tailored_cv_microsoft_v3.docx',
                    style: AppTheme.monoMedium.copyWith(
                      backgroundColor: AppTheme.neutralGray100,
                    )),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Button examples
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              ElevatedButton(
                onPressed: () {},
                style: AppTheme.primaryButtonStyle,
                child: const Text('Download CV'),
              ),
              ElevatedButton(
                onPressed: () {},
                style: AppTheme.secondaryButtonStyle,
                child: const Text('View Analysis'),
              ),
              ElevatedButton(
                onPressed: () {},
                style: AppTheme.compactButtonStyle,
                child: const Text('Save'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// 🎯 TYPOGRAPHY USAGE PATTERNS
/// 
/// HIERARCHY BEST PRACTICES:
/// 1. Use Display styles for hero sections and landing pages
/// 2. Use Heading styles for content structure
/// 3. Use Body styles for readable content
/// 4. Use Label styles for UI elements and metadata
/// 5. Use Mono styles for technical content
/// 6. Use Accent styles sparingly for emphasis
/// 
/// RESPONSIVE GUIDELINES:
/// - On mobile: Reduce font sizes by 2-4px for headings
/// - Maintain minimum 16px for body text (accessibility)
/// - Increase line height for better mobile readability
/// 
/// COLOR COMBINATIONS:
/// - Primary content: neutralGray900
/// - Secondary content: neutralGray700
/// - Supporting content: neutralGray600
/// - Disabled/placeholder: neutralGray400
/// - Accent content: primaryTeal, primaryCosmic
/// 
/// FONT LOADING:
/// - Inter: Optimized for UI, loads fast
/// - Manrope: Display font, use strategically
/// - JetBrains Mono: Code font, load when needed 