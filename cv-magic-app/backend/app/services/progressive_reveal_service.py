"""
Progressive Reveal Service

Provides consistent progressive reveal functionality across all analysis features.
Ensures uniform timing, messages, and UI patterns.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProgressiveStage(Enum):
    """Standardized stages for progressive reveal"""
    INITIALIZING = "initializing"
    READING_CV = "reading_cv"
    ANALYZING_JD = "analyzing_jd"
    EXTRACTING_SKILLS = "extracting_skills"
    MATCHING_SKILLS = "matching_skills"
    CALCULATING_SCORES = "calculating_scores"
    GENERATING_RECOMMENDATIONS = "generating_recommendations"
    FINALIZING = "finalizing"


class ProgressiveRevealService:
    """Service for managing consistent progressive reveal patterns"""
    
    def __init__(self):
        self.stage_definitions = self._define_stages()
        self.active_sessions = {}
    
    def _define_stages(self) -> Dict[ProgressiveStage, Dict[str, Any]]:
        """Define standardized stages with consistent timing and messages"""
        return {
            ProgressiveStage.INITIALIZING: {
                "icon": "upload_file",
                "message": "Initializing analysis...",
                "color": "blue",
                "duration_ms": 1500,
                "description": "Setting up analysis environment"
            },
            ProgressiveStage.READING_CV: {
                "icon": "description",
                "message": "Reading CV content...",
                "color": "blue", 
                "duration_ms": 2000,
                "description": "Extracting text and structure from CV"
            },
            ProgressiveStage.ANALYZING_JD: {
                "icon": "work_outline",
                "message": "Analyzing job description...",
                "color": "orange",
                "duration_ms": 2500,
                "description": "Identifying key requirements and skills"
            },
            ProgressiveStage.EXTRACTING_SKILLS: {
                "icon": "psychology",
                "message": "Extracting skills and competencies...",
                "color": "purple",
                "duration_ms": 3000,
                "description": "AI-powered skill identification"
            },
            ProgressiveStage.MATCHING_SKILLS: {
                "icon": "compare_arrows",
                "message": "Performing semantic matching...",
                "color": "indigo",
                "duration_ms": 3500,
                "description": "Comparing skills with job requirements"
            },
            ProgressiveStage.CALCULATING_SCORES: {
                "icon": "calculate",
                "message": "Calculating compatibility scores...",
                "color": "red",
                "duration_ms": 2500,
                "description": "Computing ATS and component scores"
            },
            ProgressiveStage.GENERATING_RECOMMENDATIONS: {
                "icon": "lightbulb_outline",
                "message": "Generating improvement recommendations...",
                "color": "amber",
                "duration_ms": 2000,
                "description": "Creating personalized optimization tips"
            },
            ProgressiveStage.FINALIZING: {
                "icon": "check_circle",
                "message": "Finalizing analysis...",
                "color": "green",
                "duration_ms": 1000,
                "description": "Preparing results for display"
            }
        }
    
    def get_stage_sequence_for_analysis_type(self, analysis_type: str) -> List[ProgressiveStage]:
        """Get the appropriate stage sequence for different analysis types"""
        sequences = {
            "skills_comparison": [
                ProgressiveStage.INITIALIZING,
                ProgressiveStage.READING_CV,
                ProgressiveStage.ANALYZING_JD,
                ProgressiveStage.EXTRACTING_SKILLS,
                ProgressiveStage.MATCHING_SKILLS,
                ProgressiveStage.FINALIZING
            ],
            "ats_analysis": [
                ProgressiveStage.INITIALIZING,
                ProgressiveStage.READING_CV,
                ProgressiveStage.ANALYZING_JD,
                ProgressiveStage.EXTRACTING_SKILLS,
                ProgressiveStage.MATCHING_SKILLS,
                ProgressiveStage.CALCULATING_SCORES,
                ProgressiveStage.FINALIZING
            ],
            "full_analysis": [
                ProgressiveStage.INITIALIZING,
                ProgressiveStage.READING_CV,
                ProgressiveStage.ANALYZING_JD,
                ProgressiveStage.EXTRACTING_SKILLS,
                ProgressiveStage.MATCHING_SKILLS,
                ProgressiveStage.CALCULATING_SCORES,
                ProgressiveStage.GENERATING_RECOMMENDATIONS,
                ProgressiveStage.FINALIZING
            ]
        }
        
        return sequences.get(analysis_type, sequences["full_analysis"])
    
    def create_session(self, session_id: str, analysis_type: str, 
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Create a new progressive reveal session"""
        stages = self.get_stage_sequence_for_analysis_type(analysis_type)
        
        session = {
            "session_id": session_id,
            "analysis_type": analysis_type,
            "stages": stages,
            "current_stage_index": 0,
            "start_time": datetime.now(),
            "progress_callback": progress_callback,
            "stage_history": [],
            "is_completed": False,
            "estimated_total_duration": sum(
                self.stage_definitions[stage]["duration_ms"] for stage in stages
            )
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"[PROGRESSIVE] Created session {session_id} for {analysis_type}")
        return session
    
    async def advance_to_stage(self, session_id: str, target_stage: ProgressiveStage, 
                              custom_message: Optional[str] = None) -> Dict[str, Any]:
        """Advance session to a specific stage"""
        if session_id not in self.active_sessions:
            logger.warning(f"[PROGRESSIVE] Session {session_id} not found")
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        stages = session["stages"]
        
        try:
            target_index = stages.index(target_stage)
        except ValueError:
            logger.error(f"[PROGRESSIVE] Stage {target_stage} not in sequence for {session_id}")
            return {"error": "Invalid stage for this analysis type"}
        
        session["current_stage_index"] = target_index
        stage_def = self.stage_definitions[target_stage]
        
        stage_info = {
            "stage": target_stage.value,
            "message": custom_message or stage_def["message"],
            "description": stage_def["description"],
            "icon": stage_def["icon"],
            "color": stage_def["color"],
            "duration_ms": stage_def["duration_ms"],
            "progress_percentage": int((target_index + 1) / len(stages) * 100),
            "stage_number": target_index + 1,
            "total_stages": len(stages),
            "estimated_time_remaining": sum(
                self.stage_definitions[stages[i]]["duration_ms"] 
                for i in range(target_index + 1, len(stages))
            )
        }
        
        # Record stage transition
        session["stage_history"].append({
            "stage": target_stage.value,
            "timestamp": datetime.now().isoformat(),
            "message": stage_info["message"]
        })
        
        # Call progress callback if provided
        if session["progress_callback"]:
            try:
                await session["progress_callback"](stage_info)
            except Exception as e:
                logger.warning(f"[PROGRESSIVE] Progress callback failed for {session_id}: {e}")
        
        logger.info(f"[PROGRESSIVE] {session_id} advanced to {target_stage.value} ({stage_info['progress_percentage']}%)")
        return stage_info
    
    async def auto_advance_session(self, session_id: str, 
                                  stage_override_callbacks: Optional[Dict[ProgressiveStage, Callable]] = None) -> None:
        """Automatically advance through all stages with timing"""
        if session_id not in self.active_sessions:
            logger.warning(f"[PROGRESSIVE] Cannot auto-advance: session {session_id} not found")
            return
        
        session = self.active_sessions[session_id]
        stages = session["stages"]
        
        for i, stage in enumerate(stages):
            # Check for custom stage handler
            if stage_override_callbacks and stage in stage_override_callbacks:
                try:
                    custom_result = await stage_override_callbacks[stage]()
                    if custom_result and isinstance(custom_result, dict):
                        custom_message = custom_result.get("message")
                        await self.advance_to_stage(session_id, stage, custom_message)
                    else:
                        await self.advance_to_stage(session_id, stage)
                except Exception as e:
                    logger.error(f"[PROGRESSIVE] Custom handler for {stage} failed: {e}")
                    await self.advance_to_stage(session_id, stage)
            else:
                await self.advance_to_stage(session_id, stage)
            
            # Wait for stage duration (except for last stage)
            if i < len(stages) - 1:
                duration_ms = self.stage_definitions[stage]["duration_ms"]
                await asyncio.sleep(duration_ms / 1000.0)
        
        # Mark session as completed
        session["is_completed"] = True
        session["completion_time"] = datetime.now()
        
        logger.info(f"[PROGRESSIVE] Session {session_id} completed")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        current_stage = session["stages"][session["current_stage_index"]]
        
        elapsed_time = (datetime.now() - session["start_time"]).total_seconds() * 1000
        
        return {
            "session_id": session_id,
            "analysis_type": session["analysis_type"],
            "current_stage": current_stage.value,
            "current_stage_index": session["current_stage_index"],
            "total_stages": len(session["stages"]),
            "progress_percentage": int((session["current_stage_index"] + 1) / len(session["stages"]) * 100),
            "is_completed": session["is_completed"],
            "elapsed_time_ms": int(elapsed_time),
            "estimated_remaining_ms": session["estimated_total_duration"] - int(elapsed_time),
            "stage_history": session["stage_history"]
        }
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up a completed session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"[PROGRESSIVE] Cleaned up session {session_id}")
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_sessions.keys())


# Global instance
progressive_reveal_service = ProgressiveRevealService()