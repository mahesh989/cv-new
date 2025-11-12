## Scope

This document captures the exact code paths responsible for rendering the ATS widget in the frontend, the backend endpoints they depend on, and the current runtime behavior observed today. No recommendations are included; this is a cross-check reference.

## Frontend Code That Shows The ATS Widget

1) SkillsAnalysisController: polling and state flags

```650:800:cv-magic-app/mobile_app/lib/controllers/skills_analysis_controller.dart
    print('🔄 [POLLING] Starting polling with extended timeout (120s) for v2 analysis...');
    final completeResults =
        await SkillsAnalysisService.waitForCompleteResults(company, maxWaitTimeSeconds: 120);

    if (completeResults != null) {
      // ... componentAnalysis parsing omitted ...
      // Parse ATS result
      ATSResult? atsResult;
      if (completeResults['ats_score'] != null) {
        final atsJson = completeResults['ats_score'] as Map<String, dynamic>;
        atsResult = ATSResult.fromJson(atsJson);
      } else {
        print('⚠️ [POLLING] No ats_score in completeResults');
      }

      // Store the results
      _fullResult = _fullResult!.copyWith(
        componentAnalysis: componentAnalysis,
        atsResult: atsResult,
        aiRecommendation: aiRecommendation,
      );

      // Show ATS results immediately when available
      if (atsResult != null) {
        _showATSLoading = false;
        _showATSResults = true;
        _result = _result!.copyWith(atsResult: atsResult);
        notifyListeners();
      } else {
        _showATSLoading = false;
        _showNotification('⚠️ ATS analysis not available - backend may still be processing');
      }
    } else {
      print('⚠️ [POLLING] Polling timed out after 120 seconds, analysis incomplete');
    }
```

State flags used:
- `_showATSLoading` and `_showATSResults` determine whether the ATS section renders
- `hasATSResult` is computed as `_result?.atsResult != null`

2) SkillsAnalysisService: poll for complete results until ATS exists

```372:466:cv-magic-app/mobile_app/lib/services/skills_analysis_service.dart
  static Future<Map<String, dynamic>?> getCompleteAnalysisResults(String company) async {
    final result = await APIService.makeAuthenticatedCall(
      endpoint: '/analysis-results/$company',
      method: 'GET',
    );
    if (result['success'] == true && result['data'] != null) {
      final data = result['data'] as Map<String, dynamic>;
      final hasATS = data['ats_score'] != null;
      final hasComponent = data['component_analysis'] != null;
      if (hasATS) {
        return data;
      }
      return null;
    }
    return null;
  }

  static Future<Map<String, dynamic>?> waitForCompleteResults(String company,
      {int maxWaitTimeSeconds = 30}) async {
    const pollInterval = Duration(seconds: 2);
    final maxAttempts = maxWaitTimeSeconds ~/ 2;
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      final completeResults = await getCompleteAnalysisResults(company);
      if (completeResults != null) {
        return completeResults;
      }
      if (attempt < maxAttempts) {
        await Future.delayed(pollInterval);
      }
    }
    return null;
  }
```

3) Widget rendering: ATS section

```291:349:cv-magic-app/mobile_app/lib/widgets/skills_display_widget.dart
// Enhanced ATS Score Widget (progressive)
if (controller.showATSLoading || controller.showATSResults) ...[
  Builder(
    builder: (context) {
      // Loading state
      if (controller.showATSLoading && !controller.showATSResults) {
        return Padding(
          // orange loading container omitted for brevity
        );
      }

      // Actual ATS results
      if (controller.showATSResults && controller.hasATSResult) {
        return ATSScoreWidgetWithProgressBars(controller: controller);
      }

      return const SizedBox.shrink();
    },
  ),
],
```

4) hasATSResult accessors

```103:103:cv-magic-app/mobile_app/lib/controllers/skills_analysis_controller.dart
bool get hasATSResult => _result?.atsResult != null;
```

## Backend Endpoint Used By Frontend

5) analysis-results endpoint (normalized slug resolution now applied)

```2144:2390:cv-magic-app/backend/app/routes/skills_analysis.py
@router.get("/analysis-results/{company}")
async def get_analysis_results(company: str, request: Request = None):
    # ... resolve user from token ...
    base_dir = get_user_base_path(user_email)
    # Normalize company name and locate directory:
    # - exact match
    # - space/underscore variants
    # - case-insensitive scan
    company_dir, resolved_company = _normalize_company_dir(base_dir, company)

    # find latest *skills_analysis*.json and read data
    analysis_file = TimestampUtils.find_latest_timestamped_file(
        company_dir, f"{resolved_company}_skills_analysis", "json")
    if not analysis_file:
        analysis_file = company_dir / f"{resolved_company}_skills_analysis.json"
    if not analysis_file.exists():
        return JSONResponse(status_code=404, content={"error": f"No analysis found for company: {company}"})

    data = json.load(open(analysis_file, 'r', encoding='utf-8'))

    # Build response: component_analysis, preextracted (if any), and ats_score (latest entry)
    # result = { "company": resolved_company, "component_analysis": ..., "ats_score": latest_ats, ... }
    return JSONResponse(content={"success": True, "data": result})
```

## Observed Runtime Behavior (Today)

- Backend (for jogi@gmail.com, Foodbank):
  - Completed pipeline with ATS and recommendation
  - `/api/analysis-results/Foodbank` returned HTTP 200 with ~12 KB body right after analysis
  - Tailored CV and PDF saved

- NGINX access logs:
  - Earlier 404s to `/api/analysis-results/Foodbank` before results were ready
  - Subsequent 200 responses to the same endpoint once files existed

- Frontend controller and widget code (above) expects:
  - `waitForCompleteResults` to return a JSON with `ats_score`
  - On non-null `ats_score`, controller sets `_showATSResults = true` and updates `_result`
  - Widget renders when `showATSResults && hasATSResult`

This reflects that the backend endpoint currently returns ATS results while the frontend rendering waits on `ats_score` presence to switch from loading to display.
*** End Patch```}|{

