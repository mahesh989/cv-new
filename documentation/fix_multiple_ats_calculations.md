# Fix Multiple ATS Calculations & Recommendation Issues

## Issue Summary

The analysis pipeline was running multiple times for the same company/content, causing:

1. **Multiple ATS score calculations** (71.9 → 73.11 → 74.6)
2. **Inconsistent CV-JD matching results** due to AI JSON parsing failures
3. **Recommendation generation race conditions** where first attempt succeeds but subsequent attempts are skipped

## Root Cause Analysis

### 1. Pipeline Triggering
- Each `/api/preliminary-analysis` call triggers `_schedule_post_skill_pipeline()`
- No deduplication mechanism to prevent multiple runs for same content
- Each run creates new analysis entries

### 2. CV-JD Matching Issues
- AI responses have JSON formatting problems (unquoted values in matching_notes)
- 3 retry attempts failing before finally working
- Different keyword matching results across runs

### 3. Recommendation Generation
- First run: ✅ Creates recommendation file successfully
- Later runs: ⚠️ Skip generation due to existing file check
- Race condition between ATS calculation and file existence check

## Solution Implementation

### Phase 1: Immediate Fixes

#### 1. Integrate Pipeline Deduplicator

**Modify `skills_analysis.py`:**

```python
# Add import at top
from app.services.pipeline_deduplicator import pipeline_deduplicator

# Modify _schedule_post_skill_pipeline function:
def _schedule_post_skill_pipeline(company_name: Optional[str], cv_content: str, jd_content: str):
    """Fire-and-forget JD analysis and CV–JD match pipeline with deduplication."""
    if not company_name:
        logger.warning("⚠️ [PIPELINE] No company detected; skipping JD analysis & CV–JD matching.")
        return

    # Check if pipeline should run
    dedup_check = pipeline_deduplicator.should_run_pipeline(company_name, cv_content, jd_content)
    
    if not dedup_check["should_run"]:
        logger.info(f"🚫 [PIPELINE] Skipping duplicate run for {company_name}: {dedup_check['reason']}")
        return
    
    logger.info(f"🚀 [PIPELINE] Scheduling JD analysis and CV–JD matching for '{company_name}'...")
    session_hash = dedup_check["session_hash"]
    
    # Mark pipeline as started
    pipeline_deduplicator.mark_pipeline_started(company_name, session_hash)

    async def _run_pipeline(cname: str, session_hash: str):
        """Run the complete analysis pipeline with error recovery and deduplication"""
        pipeline_results = {
            "jd_analysis": False,
            "cv_jd_matching": False,
            "component_analysis": False
        }
        
        try:
            # [Existing pipeline steps...]
            
            # Mark as completed at the end
            successful_steps = [step for step, success in pipeline_results.items() if success]
            pipeline_deduplicator.mark_pipeline_completed(cname, session_hash, successful_steps)
            
        except Exception as e:
            pipeline_deduplicator.mark_pipeline_failed(cname, session_hash, str(e))
            raise e

    try:
        asyncio.create_task(_run_pipeline(company_name, session_hash))
    except Exception as e:
        logger.warning(f"⚠️ [PIPELINE] Failed to schedule background pipeline: {e}")
        pipeline_deduplicator.mark_pipeline_failed(company_name, session_hash, str(e))
```

#### 2. Replace CV-JD Matcher

**Modify `cv_jd_matching/cv_jd_matcher.py`:**

```python
# Replace the existing match_cv_against_jd method with enhanced version
from app.services.enhanced_cv_jd_matcher import enhanced_cv_jd_matcher

async def match_cv_against_jd(self, company_name: str, cv_file_path: Optional[str] = None, 
                             jd_file_path: Optional[str] = None, temperature: float = 0.3) -> Dict[str, Any]:
    """Enhanced CV-JD matching with robust JSON handling"""
    
    # [Load CV and JD analysis as before...]
    
    # Use enhanced matcher instead of direct AI call
    result = await enhanced_cv_jd_matcher.match_cv_against_jd(cv_content, jd_analysis)
    
    # [Save results as before...]
    return result
```

#### 3. Add Progressive Reveal Integration

**Create new endpoint in `skills_analysis.py`:**

```python
from app.services.progressive_reveal_service import progressive_reveal_service, ProgressiveStage

@router.post("/preliminary-analysis-with-progress")
async def preliminary_analysis_with_progress(request: Request, current_model: str = Depends(get_current_model)):
    """Preliminary analysis with progressive reveal"""
    
    # [Authentication and validation as before...]
    
    # Create progressive reveal session
    session_id = f"analysis_{company_name}_{int(datetime.now().timestamp())}"
    session = progressive_reveal_service.create_session(session_id, "full_analysis")
    
    # Define stage callbacks
    async def reading_cv_callback():
        cv_content_result = cv_content_service.get_cv_content(cv_filename, user_id, use_fallback=False)
        return {"message": f"Reading CV: {cv_filename}"}
    
    async def analyzing_jd_callback():
        return {"message": f"Analyzing {len(jd_text)} chars of job description"}
    
    stage_callbacks = {
        ProgressiveStage.READING_CV: reading_cv_callback,
        ProgressiveStage.ANALYZING_JD: analyzing_jd_callback,
    }
    
    # Start progressive reveal
    asyncio.create_task(progressive_reveal_service.auto_advance_session(session_id, stage_callbacks))
    
    # Run analysis
    result = await perform_preliminary_skills_analysis(
        cv_content=cv_content,
        jd_text=jd_text,
        cv_filename=cv_filename,
        current_model=current_model,
        config_name=config_name,
        user_id=user_id
    )
    
    # Mark session completed
    progressive_reveal_service.cleanup_session(session_id)
    
    return JSONResponse(content=result)

@router.get("/analysis-progress/{session_id}")
async def get_analysis_progress(session_id: str):
    """Get progress status for an analysis session"""
    status = progressive_reveal_service.get_session_status(session_id)
    return JSONResponse(content=status)
```

### Phase 2: Frontend Integration

#### Update Flutter Progressive Dialog

**Modify `ats_loading_dialog.dart`:**

```dart
class _ATSLoadingDialogState extends State<ATSLoadingDialog> with TickerProviderStateMixin {
  String? sessionId;
  Timer? _progressTimer;
  Map<String, dynamic>? currentStageInfo;
  
  @override
  void initState() {
    super.initState();
    _startProgressTracking();
  }
  
  void _startProgressTracking() {
    if (sessionId != null) {
      _progressTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) async {
        try {
          final response = await http.get(
            Uri.parse('${AppConfig.baseUrl}/api/analysis-progress/$sessionId'),
            headers: {'Authorization': 'Bearer $token'}
          );
          
          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            if (mounted) {
              setState(() {
                currentStageInfo = data;
                if (data['is_completed'] == true) {
                  _progressTimer?.cancel();
                  widget.onComplete?.call();
                }
              });
            }
          }
        } catch (e) {
          print('Error fetching progress: $e');
        }
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (currentStageInfo != null) {
      return _buildProgressDialog(currentStageInfo!);
    }
    return _buildGenericLoadingDialog();
  }
  
  Widget _buildProgressDialog(Map<String, dynamic> stageInfo) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Progress indicator
            LinearProgressIndicator(
              value: (stageInfo['progress_percentage'] ?? 0) / 100.0,
              backgroundColor: Colors.grey[300],
              valueColor: AlwaysStoppedAnimation<Color>(
                _getColorFromString(stageInfo['color'] ?? 'blue')
              ),
            ),
            const SizedBox(height: 16),
            
            // Stage icon and message
            Icon(
              _getIconFromString(stageInfo['icon'] ?? 'hourglass_empty'),
              color: _getColorFromString(stageInfo['color'] ?? 'blue'),
              size: 48,
            ),
            const SizedBox(height: 12),
            
            Text(
              stageInfo['message'] ?? 'Processing...',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            
            Text(
              stageInfo['description'] ?? '',
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            
            // Progress info
            Text(
              'Step ${stageInfo['stage_number'] ?? 1} of ${stageInfo['total_stages'] ?? 8}',
              style: TextStyle(fontSize: 12, color: Colors.grey[500]),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Phase 3: Monitoring & Validation

#### Add Monitoring Endpoint

```python
@router.get("/pipeline-health")
async def get_pipeline_health():
    """Get pipeline health and deduplication statistics"""
    active_sessions = progressive_reveal_service.get_active_sessions()
    
    return JSONResponse(content={
        "active_progressive_sessions": len(active_sessions),
        "pipeline_deduplication_stats": {
            "active_companies": len(pipeline_deduplicator.get_active_sessions()),
        },
        "health_status": "operational"
    })
```

## Validation Steps

### 1. Test Deduplication
```bash
# Test same analysis multiple times quickly
curl -X POST "http://localhost:8000/api/preliminary-analysis" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"cv_filename": "test.pdf", "jd_text": "same content"}' &
  
curl -X POST "http://localhost:8000/api/preliminary-analysis" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"cv_filename": "test.pdf", "jd_text": "same content"}' &
```

**Expected Result:** Second call should be skipped with deduplication message.

### 2. Verify Single ATS Calculation
Check logs for only ONE ATS calculation per unique content combination.

### 3. Test Progressive Reveal Consistency
All analysis types should show consistent stage progression and timing.

## Migration Timeline

- **Week 1:** Implement deduplication and enhanced CV-JD matching
- **Week 2:** Add progressive reveal service and update frontend
- **Week 3:** Testing and validation
- **Week 4:** Production deployment with monitoring

## Success Metrics

- ✅ Zero duplicate ATS calculations for same content
- ✅ CV-JD matching success rate > 95% (vs current ~33%)
- ✅ Consistent progressive reveal across all features  
- ✅ Recommendation generation success rate = 100%
- ✅ Reduced server load from duplicate processing