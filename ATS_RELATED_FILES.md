# ATS Score Related Files

## 📝 Prompt Files (Used for ATS Score Calculation)

### Main Prompt Files
- `cv-magic-app/backend/prompt/ats_skills_relevance_prompt.py` - Skills relevance analysis prompt
- `cv-magic-app/backend/prompt/ats_technical_prompt.py` - Technical depth analysis prompt
- `cv-magic-app/backend/prompt/ats_experience_prompt.py` - Experience alignment prompt
- `cv-magic-app/backend/prompt/ats_industry_prompt.py` - Industry fit analysis prompt
- `cv-magic-app/backend/prompt/ats_seniority_prompt.py` - Role seniority analysis prompt
- `cv-magic-app/backend/prompt/unified_technical_skills_prompt.py` - Unified technical skills prompt
- `cv-magic-app/backend/prompt/unified_experience_fit_prompt.py` - Unified experience fit prompt

### Prompt Configuration
- `cv-magic-app/backend/app/services/ats/components/standardized_config.py` - Standardized prompt templates and AI parameters

---

## 🧮 ATS Score Calculation Files

### Core Calculator
- `cv-magic-app/backend/app/services/ats/ats_score_calculator.py` - Main ATS score calculation logic (v2 65/35 split)

### Component Assembler
- `cv-magic-app/backend/app/services/ats/component_assembler.py` - Assembles components and runs ATS calculation

### Bonus Calculator
- `cv-magic-app/backend/app/services/ats/requirement_bonus_calculator.py` - Calculates bonus points

---

## 🔍 Component Analyzers (Used in ATS Calculation)

### Individual Analyzers
- `cv-magic-app/backend/app/services/ats/components/skills_relevance_analyzer.py` - Skills relevance analysis
- `cv-magic-app/backend/app/services/ats/components/technical_analyzer.py` - Technical depth analysis
- `cv-magic-app/backend/app/services/ats/components/experience_analyzer.py` - Experience alignment analysis
- `cv-magic-app/backend/app/services/ats/components/industry_analyzer.py` - Industry fit analysis
- `cv-magic-app/backend/app/services/ats/components/seniority_analyzer.py` - Role seniority analysis

### New Analyzers (v2)
- `cv-magic-app/backend/app/services/ats/components/technical_skills_analyzer.py` - Technical & skills component analyzer
- `cv-magic-app/backend/app/services/ats/components/experience_fit_analyzer.py` - Experience & fit component analyzer

### Utility Analyzers
- `cv-magic-app/backend/app/services/ats/components/batched_analyzer.py` - Batched analysis for efficiency
- `cv-magic-app/backend/app/services/ats/components/consistency_validator.py` - Validates analysis consistency
- `cv-magic-app/backend/app/services/ats/components/new_to_legacy_mapper.py` - Maps new format to legacy format

---

## 🎯 ATS Orchestrators (Coordination)

- `cv-magic-app/backend/app/services/ats/modular_ats_orchestrator.py` - Modular ATS orchestration
- `cv-magic-app/backend/app/services/ats/enhanced_ats_orchestrator.py` - Enhanced ATS orchestration

---

## 🌐 API/Route Files

- `cv-magic-app/backend/app/routes/skills_analysis.py` - API routes for ATS score endpoints

---

## 🎨 Frontend Display Files

### Widgets
- `cv-magic-app/mobile_app/lib/widgets/ats_score_widget_with_progress_bars.dart` - Main ATS score widget with progress bars
- `cv-magic-app/mobile_app/lib/widgets/ats_score_widget.dart` - Basic ATS score widget

### Models
- `cv-magic-app/mobile_app/lib/models/skills_analysis_model.dart` - ATSResult and related models

### Controllers
- `cv-magic-app/mobile_app/lib/controllers/context_aware_analysis_controller.dart` - Controller that handles ATS results
- `cv-magic-app/mobile_app/lib/controllers/skills_analysis_controller.dart` - Skills analysis controller with ATS support

---

## 🔗 Related Service Files

- `cv-magic-app/backend/app/services/ats_recommendation_service.py` - ATS-based recommendations
- `cv-magic-app/backend/app/services/context_aware_analysis_pipeline.py` - Pipeline that includes ATS calculation
- `cv-magic-app/backend/app/services/ai_recommendation_generator.py` - Generates recommendations including ATS scores
- `cv-magic-app/backend/app/services/progressive_reveal_service.py` - Progressive reveal of ATS results

---

## 📄 Documentation

- `ATS_SCORE_EXPLANATION.md` - Detailed explanation of ATS score calculation and display

---

## 📋 Summary by Category

### Prompts (7 files)
1. `cv-magic-app/backend/prompt/ats_skills_relevance_prompt.py`
2. `cv-magic-app/backend/prompt/ats_technical_prompt.py`
3. `cv-magic-app/backend/prompt/ats_experience_prompt.py`
4. `cv-magic-app/backend/prompt/ats_industry_prompt.py`
5. `cv-magic-app/backend/prompt/ats_seniority_prompt.py`
6. `cv-magic-app/backend/prompt/unified_technical_skills_prompt.py`
7. `cv-magic-app/backend/prompt/unified_experience_fit_prompt.py`

### Core Calculation (3 files)
1. `cv-magic-app/backend/app/services/ats/ats_score_calculator.py`
2. `cv-magic-app/backend/app/services/ats/component_assembler.py`
3. `cv-magic-app/backend/app/services/ats/requirement_bonus_calculator.py`

### Component Analyzers (9 files)
1. `cv-magic-app/backend/app/services/ats/components/skills_relevance_analyzer.py`
2. `cv-magic-app/backend/app/services/ats/components/technical_analyzer.py`
3. `cv-magic-app/backend/app/services/ats/components/experience_analyzer.py`
4. `cv-magic-app/backend/app/services/ats/components/industry_analyzer.py`
5. `cv-magic-app/backend/app/services/ats/components/seniority_analyzer.py`
6. `cv-magic-app/backend/app/services/ats/components/technical_skills_analyzer.py`
7. `cv-magic-app/backend/app/services/ats/components/experience_fit_analyzer.py`
8. `cv-magic-app/backend/app/services/ats/components/batched_analyzer.py`
9. `cv-magic-app/backend/app/services/ats/components/standardized_config.py`

### Orchestrators (2 files)
1. `cv-magic-app/backend/app/services/ats/modular_ats_orchestrator.py`
2. `cv-magic-app/backend/app/services/ats/enhanced_ats_orchestrator.py`

### Frontend (4 files)
1. `cv-magic-app/mobile_app/lib/widgets/ats_score_widget_with_progress_bars.dart`
2. `cv-magic-app/mobile_app/lib/widgets/ats_score_widget.dart`
3. `cv-magic-app/mobile_app/lib/models/skills_analysis_model.dart`
4. `cv-magic-app/mobile_app/lib/controllers/context_aware_analysis_controller.dart`

### API/Routes (1 file)
1. `cv-magic-app/backend/app/routes/skills_analysis.py`

### Related Services (4 files)
1. `cv-magic-app/backend/app/services/ats_recommendation_service.py`
2. `cv-magic-app/backend/app/services/context_aware_analysis_pipeline.py`
3. `cv-magic-app/backend/app/services/ai_recommendation_generator.py`
4. `cv-magic-app/backend/app/services/progressive_reveal_service.py`

**Total: 30+ files related to ATS score calculation and display**

