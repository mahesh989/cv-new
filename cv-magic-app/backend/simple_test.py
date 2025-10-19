#!/usr/bin/env python3
import sys
sys.path.append('/app/app')

from tailored_cv.services.pdf_export_service import _map_tailored_json_to_generator_schema

# Test skills mapping
test_cv = {
    'skills': [
        {'category': 'Technical Skills', 'skills': ['Python', 'SQL']},
        {'category': 'Soft Skills', 'skills': ['Communication']}
    ]
}

mapped = _map_tailored_json_to_generator_schema(test_cv)
skills = mapped.get('skills', {})

print('✅ Skills mapping test:')
print(f'  is_categorized: {skills.get("is_categorized")}')
print(f'  Technical Skills: {skills.get("Technical Skills")}')
print(f'  Soft Skills: {skills.get("Soft Skills")}')

if skills.get('is_categorized') == True:
    print('✅ Skills categorization mapping is working correctly!')
else:
    print('❌ Skills categorization mapping failed!')
