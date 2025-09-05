import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PromptDialog extends StatefulWidget {
  final String currentPrompt;
  final String backendUrl;
  final ValueChanged<String> onPromptUpdated;

  const PromptDialog({
    super.key,
    required this.currentPrompt,
    required this.backendUrl,
    required this.onPromptUpdated,
  });

  @override
  State<PromptDialog> createState() => _PromptDialogState();
}

class _PromptDialogState extends State<PromptDialog> {
  late TextEditingController _controller;
  bool isSaving = false;

  final String _defaultPrompt = '''
You are a highly accurate AI assistant that generates ATS-friendly, tailored CVs based on:

1. A candidate’s general CV (uploaded by the user)
2. A job description
3. A list of important keywords and phrases extracted from the JD
4. A predefined set of tailoring rules

---

🎯 Step 1: Determine JD Category  
Analyze the job description and assign it to one of the following categories:

1. Graduate role – terms like “graduate,” “student,” “no experience required,” or open to freshers.
2. Entry-level – requires up to 1 year of experience or basic exposure to common tools.
3. 1–3 years of experience – mentions 1 to 3 years of relevant work experience.
4. More than 3 years – if the job requires over 3 years of experience or asks for mid/senior-level applicants, return this message instead of a CV: 
   “This role requires more than 3 years of experience and is not suitable for this candidate’s current level.”

---

📄 Step 2: Tailored CV Construction Rules

- Only use technical skills, tools, and certifications that are already present in the candidate’s master CV.
- Do not include skills or tools that are found in the job description but not present in the candidate’s CV — no hallucination.
- Include soft skills (from the job description) where appropriate, especially in bullet points under experience.
- Include keywords and key phrases provided in the analysis throughout:
  - In project descriptions
  - In experience bullet points
  - In summary/profile if applicable

---

📁 Project Inclusion Based on JD Category

- Graduate roles → include up to 2 projects that highlight relevant skills.
- Entry-level (up to 1 year) → include 1 strong project, if available.
- 1–3 years of experience → do not include a Projects section unless a project is highly relevant or explicitly required.
- More than 3 years → skip tailoring and return rejection message.

---

✅ Tailoring Guidelines

- Reword experience to emphasize alignment with the JD and identified keywords.
- Embed key technical skills and phrases naturally into bullet points and project outcomes.
- Add or highlight soft skills (e.g., communication, adaptability) in bullet points only if mentioned in the job description.
- Slightly adjust job titles (e.g., “Data Intern” → “Data Analyst Intern”) if that improves alignment, but don’t fabricate roles.
- Light fabrication of one minor project is allowed only if the JD has a low-bar technical requirement that aligns closely with what's already in the CV (e.g., Google Sheets if Excel is in CV).

---

Now, using the candidate’s general CV, the job description, and the extracted keywords and phrases, generate a tailored, truthful, and ATS-optimized CV in plain text format.

---

📄 Candidate CV:  
{cv_text}

---

🧾 Job Description:  
{job_description}

---

🧠 Important Keywords:  
{keywords}

🧠 Key Phrases:  
{key_phrases}
''';

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.currentPrompt.isNotEmpty ? widget.currentPrompt : _defaultPrompt,
    );
  }

  Future<void> _savePrompt() async {
    setState(() => isSaving = true);
    final response = await http.post(
      Uri.parse('${widget.backendUrl}/update-prompt/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'prompt': _controller.text}),
    );
    if (response.statusCode == 200) {
      widget.onPromptUpdated(_controller.text);
      Navigator.pop(context);
    }
    setState(() => isSaving = false);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit AI Prompt'),
      content: TextField(
        controller: _controller,
        maxLines: 18,
        decoration: const InputDecoration(
          border: OutlineInputBorder(),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: isSaving ? null : _savePrompt,
          child: isSaving
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Save'),
        ),
      ],
    );
  }
}
