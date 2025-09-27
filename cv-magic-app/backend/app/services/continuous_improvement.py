"""
Continuous Improvement Service for CV Management API
Phase 10: Post-Launch Optimization & Continuous Improvement
"""
import logging
import time
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from sqlalchemy.orm import Session
from app.database import get_database
from app.models.user import User
from app.models.user_data import UserActivityLog
from app.services.post_launch_monitoring import post_launch_monitoring
from app.services.optimization_framework import optimization_framework

logger = logging.getLogger(__name__)


class ImprovementType(Enum):
    """Types of improvements"""
    FEATURE = "feature"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"


class ImprovementStatus(Enum):
    """Improvement status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    DEPLOYED = "deployed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ImprovementItem:
    """Improvement item"""
    id: str
    type: ImprovementType
    title: str
    description: str
    priority: int
    effort_estimate: int  # in hours
    impact_score: float
    user_feedback_count: int
    technical_debt_score: float
    status: ImprovementStatus
    created_at: datetime
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    assigned_to: Optional[str] = None
    progress: float = 0.0
    notes: List[str] = None


@dataclass
class ImprovementCycle:
    """Improvement cycle"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    status: str
    improvements: List[str]
    metrics: Dict[str, Any]
    lessons_learned: List[str]


class ContinuousImprovementService:
    """Continuous improvement service"""
    
    def __init__(self):
        self.improvements: List[ImprovementItem] = []
        self.cycles: List[ImprovementCycle] = []
        self.improvement_active = True
        self.cycle_duration_days = 30  # 30-day improvement cycles
        
        logger.info("ContinuousImprovementService initialized")
    
    def analyze_user_feedback_for_improvements(self) -> List[ImprovementItem]:
        """Analyze user feedback and generate improvement items"""
        logger.info("Analyzing user feedback for improvements...")
        
        improvements = []
        
        try:
            # Get feedback analysis
            feedback_analysis = post_launch_monitoring.analyze_user_feedback()
            
            # Generate improvements based on feedback
            improvements.extend(self._generate_feedback_improvements(feedback_analysis))
            
            # Generate improvements based on optimization recommendations
            optimization_recs = optimization_framework.recommendations
            improvements.extend(self._generate_optimization_improvements(optimization_recs))
            
            # Generate improvements based on system metrics
            improvements.extend(self._generate_metrics_improvements())
            
            # Store improvements
            self.improvements.extend(improvements)
            
            logger.info(f"Generated {len(improvements)} improvement items")
            return improvements
            
        except Exception as e:
            logger.error(f"Error analyzing user feedback for improvements: {e}")
            return []
    
    def _generate_feedback_improvements(self, feedback_analysis: Dict[str, Any]) -> List[ImprovementItem]:
        """Generate improvements based on user feedback"""
        improvements = []
        
        # Low rating improvements
        if feedback_analysis.get("average_rating", 0) < 4.0:
            improvements.append(ImprovementItem(
                id=f"feedback_rating_{int(time.time())}",
                type=ImprovementType.USABILITY,
                title="Improve User Experience",
                description=f"User satisfaction rating is {feedback_analysis.get('average_rating', 0):.1f}/5.0",
                priority=1,
                effort_estimate=40,
                impact_score=9.0,
                user_feedback_count=feedback_analysis.get("total_feedback", 0),
                technical_debt_score=8.0,
                status=ImprovementStatus.PLANNED,
                created_at=datetime.now(timezone.utc)
            ))
        
        # Common issues improvements
        common_issues = feedback_analysis.get("common_issues", [])
        for issue in common_issues:
            if issue["count"] > 5:  # Significant issue
                improvements.append(ImprovementItem(
                    id=f"feedback_issue_{issue['keyword']}_{int(time.time())}",
                    type=ImprovementType.USABILITY,
                    title=f"Address {issue['keyword'].title()} Issues",
                    description=f"User feedback indicates {issue['count']} reports of {issue['keyword']} issues",
                    priority=2,
                    effort_estimate=20,
                    impact_score=7.0,
                    user_feedback_count=issue["count"],
                    technical_debt_score=6.0,
                    status=ImprovementStatus.PLANNED,
                    created_at=datetime.now(timezone.utc)
                ))
        
        return improvements
    
    def _generate_optimization_improvements(self, recommendations: List) -> List[ImprovementItem]:
        """Generate improvements based on optimization recommendations"""
        improvements = []
        
        for rec in recommendations:
            if rec.priority.value in ["high", "critical"]:
                improvements.append(ImprovementItem(
                    id=f"opt_{rec.id}",
                    type=ImprovementType.PERFORMANCE,
                    title=rec.title,
                    description=rec.description,
                    priority=1 if rec.priority.value == "critical" else 2,
                    effort_estimate=int(rec.effort_score * 8),  # Convert to hours
                    impact_score=rec.impact_score,
                    user_feedback_count=0,
                    technical_debt_score=rec.effort_score,
                    status=ImprovementStatus.PLANNED,
                    created_at=datetime.now(timezone.utc)
                ))
        
        return improvements
    
    def _generate_metrics_improvements(self) -> List[ImprovementItem]:
        """Generate improvements based on system metrics"""
        improvements = []
        
        try:
            # Get recent metrics
            recent_metrics = post_launch_monitoring.metrics_history
            if not recent_metrics:
                return improvements
            
            # Performance improvements
            performance_metrics = [
                m for m in recent_metrics 
                if m.metric_name in ["response_time", "memory_usage", "cpu_usage"]
                and m.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
            ]
            
            if performance_metrics:
                avg_response_time = sum(
                    m.value for m in performance_metrics if m.metric_name == "response_time"
                ) / len([m for m in performance_metrics if m.metric_name == "response_time"])
                
                if avg_response_time > 1.0:
                    improvements.append(ImprovementItem(
                        id=f"metrics_performance_{int(time.time())}",
                        type=ImprovementType.PERFORMANCE,
                        title="Optimize System Performance",
                        description=f"Average response time is {avg_response_time:.2f}s",
                        priority=2,
                        effort_estimate=32,
                        impact_score=8.0,
                        user_feedback_count=0,
                        technical_debt_score=7.0,
                        status=ImprovementStatus.PLANNED,
                        created_at=datetime.now(timezone.utc)
                    ))
            
            # Security improvements
            security_metrics = [
                m for m in recent_metrics 
                if m.metric_name in ["failed_logins", "security_events"]
                and m.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
            ]
            
            if security_metrics:
                total_security_events = sum(m.value for m in security_metrics)
                if total_security_events > 20:
                    improvements.append(ImprovementItem(
                        id=f"metrics_security_{int(time.time())}",
                        type=ImprovementType.SECURITY,
                        title="Enhance Security Measures",
                        description=f"High number of security events: {total_security_events}",
                        priority=1,
                        effort_estimate=24,
                        impact_score=9.0,
                        user_feedback_count=0,
                        technical_debt_score=8.0,
                        status=ImprovementStatus.PLANNED,
                        created_at=datetime.now(timezone.utc)
                    ))
            
        except Exception as e:
            logger.error(f"Error generating metrics improvements: {e}")
        
        return improvements
    
    def prioritize_improvements(self, improvements: List[ImprovementItem]) -> List[ImprovementItem]:
        """Prioritize improvements based on multiple factors"""
        def calculate_priority_score(improvement: ImprovementItem) -> float:
            # Weighted scoring: impact (30%), user feedback (25%), technical debt (25%), effort (20%)
            impact_weight = 0.30
            feedback_weight = 0.25
            debt_weight = 0.25
            effort_weight = 0.20
            
            # Normalize effort (lower effort = higher score)
            effort_score = 10 - (improvement.effort_estimate / 10)
            
            # Calculate score
            score = (
                improvement.impact_score * impact_weight +
                min(improvement.user_feedback_count / 10, 10) * feedback_weight +
                improvement.technical_debt_score * debt_weight +
                effort_score * effort_weight
            )
            
            return score
        
        # Sort by priority score (descending)
        sorted_improvements = sorted(
            improvements,
            key=calculate_priority_score,
            reverse=True
        )
        
        return sorted_improvements
    
    def create_improvement_cycle(self, name: str, duration_days: int = 30) -> ImprovementCycle:
        """Create a new improvement cycle"""
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=duration_days)
        
        cycle = ImprovementCycle(
            id=f"cycle_{int(time.time())}",
            name=name,
            start_date=start_date,
            end_date=end_date,
            status="active",
            improvements=[],
            metrics={},
            lessons_learned=[]
        )
        
        self.cycles.append(cycle)
        logger.info(f"Created improvement cycle: {name}")
        return cycle
    
    def add_improvement_to_cycle(self, cycle_id: str, improvement_id: str) -> bool:
        """Add an improvement to a cycle"""
        try:
            cycle = next((c for c in self.cycles if c.id == cycle_id), None)
            if not cycle:
                return False
            
            improvement = next((i for i in self.improvements if i.id == improvement_id), None)
            if not improvement:
                return False
            
            cycle.improvements.append(improvement_id)
            improvement.status = ImprovementStatus.IN_PROGRESS
            improvement.planned_start = datetime.now(timezone.utc)
            improvement.planned_end = cycle.end_date
            
            logger.info(f"Added improvement {improvement_id} to cycle {cycle_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding improvement to cycle: {e}")
            return False
    
    def update_improvement_progress(self, improvement_id: str, progress: float, notes: str = None) -> bool:
        """Update improvement progress"""
        try:
            improvement = next((i for i in self.improvements if i.id == improvement_id), None)
            if not improvement:
                return False
            
            improvement.progress = min(progress, 100.0)
            
            if notes:
                if improvement.notes is None:
                    improvement.notes = []
                improvement.notes.append(f"{datetime.now().isoformat()}: {notes}")
            
            # Update status based on progress
            if progress >= 100.0:
                improvement.status = ImprovementStatus.COMPLETED
                improvement.actual_end = datetime.now(timezone.utc)
            elif progress > 0 and improvement.status == ImprovementStatus.PLANNED:
                improvement.status = ImprovementStatus.IN_PROGRESS
                improvement.actual_start = datetime.now(timezone.utc)
            
            logger.info(f"Updated improvement {improvement_id} progress to {progress}%")
            return True
            
        except Exception as e:
            logger.error(f"Error updating improvement progress: {e}")
            return False
    
    def complete_improvement_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Complete an improvement cycle and generate summary"""
        try:
            cycle = next((c for c in self.cycles if c.id == cycle_id), None)
            if not cycle:
                return {"error": "Cycle not found"}
            
            # Update cycle status
            cycle.status = "completed"
            
            # Get cycle improvements
            cycle_improvements = [
                i for i in self.improvements 
                if i.id in cycle.improvements
            ]
            
            # Calculate metrics
            total_improvements = len(cycle_improvements)
            completed_improvements = len([i for i in cycle_improvements if i.status == ImprovementStatus.COMPLETED])
            completion_rate = (completed_improvements / total_improvements * 100) if total_improvements > 0 else 0
            
            total_effort = sum(i.effort_estimate for i in cycle_improvements)
            actual_effort = sum(
                i.effort_estimate for i in cycle_improvements 
                if i.status == ImprovementStatus.COMPLETED
            )
            
            # Generate lessons learned
            lessons_learned = self._generate_lessons_learned(cycle_improvements)
            cycle.lessons_learned = lessons_learned
            
            # Update cycle metrics
            cycle.metrics = {
                "total_improvements": total_improvements,
                "completed_improvements": completed_improvements,
                "completion_rate": completion_rate,
                "total_effort_estimated": total_effort,
                "actual_effort": actual_effort,
                "efficiency": (actual_effort / total_effort * 100) if total_effort > 0 else 0
            }
            
            summary = {
                "cycle_id": cycle_id,
                "cycle_name": cycle.name,
                "start_date": cycle.start_date.isoformat(),
                "end_date": cycle.end_date.isoformat(),
                "duration_days": (cycle.end_date - cycle.start_date).days,
                "metrics": cycle.metrics,
                "lessons_learned": lessons_learned,
                "improvements": [
                    {
                        "id": i.id,
                        "title": i.title,
                        "status": i.status.value,
                        "progress": i.progress,
                        "effort_estimate": i.effort_estimate
                    }
                    for i in cycle_improvements
                ]
            }
            
            logger.info(f"Completed improvement cycle {cycle_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error completing improvement cycle: {e}")
            return {"error": str(e)}
    
    def _generate_lessons_learned(self, improvements: List[ImprovementItem]) -> List[str]:
        """Generate lessons learned from improvements"""
        lessons = []
        
        # Analyze improvement patterns
        completed_improvements = [i for i in improvements if i.status == ImprovementStatus.COMPLETED]
        
        if completed_improvements:
            # Effort estimation accuracy
            effort_accuracy = sum(
                1 for i in completed_improvements 
                if abs(i.effort_estimate - (i.actual_end - i.actual_start).total_seconds() / 3600) < 10
            ) / len(completed_improvements)
            
            if effort_accuracy < 0.5:
                lessons.append("Improve effort estimation accuracy - many improvements took significantly more or less time than estimated")
            
            # High impact improvements
            high_impact = [i for i in completed_improvements if i.impact_score >= 8.0]
            if high_impact:
                lessons.append(f"Focus on high-impact improvements - {len(high_impact)} high-impact items were completed successfully")
            
            # User feedback driven improvements
            feedback_driven = [i for i in completed_improvements if i.user_feedback_count > 0]
            if feedback_driven:
                lessons.append(f"User feedback is valuable - {len(feedback_driven)} improvements were driven by user feedback")
            
            # Technical debt improvements
            debt_improvements = [i for i in completed_improvements if i.technical_debt_score >= 7.0]
            if debt_improvements:
                lessons.append(f"Address technical debt systematically - {len(debt_improvements)} technical debt items were resolved")
        
        return lessons
    
    def get_improvement_dashboard(self) -> Dict[str, Any]:
        """Get improvement dashboard data"""
        return {
            "total_improvements": len(self.improvements),
            "active_improvements": len([i for i in self.improvements if i.status == ImprovementStatus.IN_PROGRESS]),
            "completed_improvements": len([i for i in self.improvements if i.status == ImprovementStatus.COMPLETED]),
            "planned_improvements": len([i for i in self.improvements if i.status == ImprovementStatus.PLANNED]),
            "active_cycles": len([c for c in self.cycles if c.status == "active"]),
            "completed_cycles": len([c for c in self.cycles if c.status == "completed"]),
            "improvements_by_type": self._get_improvements_by_type(),
            "improvements_by_priority": self._get_improvements_by_priority(),
            "recent_improvements": [self._format_improvement(i) for i in self.improvements[-10:]],
            "cycle_summary": [self._format_cycle(c) for c in self.cycles[-5:]]
        }
    
    def _get_improvements_by_type(self) -> Dict[str, int]:
        """Get count of improvements by type"""
        type_counts = {}
        for improvement in self.improvements:
            type_counts[improvement.type.value] = type_counts.get(improvement.type.value, 0) + 1
        return type_counts
    
    def _get_improvements_by_priority(self) -> Dict[str, int]:
        """Get count of improvements by priority"""
        priority_counts = {}
        for improvement in self.improvements:
            priority_counts[str(improvement.priority)] = priority_counts.get(str(improvement.priority), 0) + 1
        return priority_counts
    
    def _format_improvement(self, improvement: ImprovementItem) -> Dict[str, Any]:
        """Format improvement for dashboard"""
        return {
            "id": improvement.id,
            "type": improvement.type.value,
            "title": improvement.title,
            "priority": improvement.priority,
            "status": improvement.status.value,
            "progress": improvement.progress,
            "created_at": improvement.created_at.isoformat()
        }
    
    def _format_cycle(self, cycle: ImprovementCycle) -> Dict[str, Any]:
        """Format cycle for dashboard"""
        return {
            "id": cycle.id,
            "name": cycle.name,
            "status": cycle.status,
            "start_date": cycle.start_date.isoformat(),
            "end_date": cycle.end_date.isoformat(),
            "improvements_count": len(cycle.improvements)
        }
    
    async def start_continuous_improvement(self):
        """Start continuous improvement process"""
        logger.info("Starting continuous improvement process...")
        
        while self.improvement_active:
            try:
                # Analyze for new improvements
                new_improvements = self.analyze_user_feedback_for_improvements()
                
                if new_improvements:
                    logger.info(f"Generated {len(new_improvements)} new improvement items")
                
                # Check for cycle completions
                active_cycles = [c for c in self.cycles if c.status == "active"]
                for cycle in active_cycles:
                    if datetime.now(timezone.utc) >= cycle.end_date:
                        self.complete_improvement_cycle(cycle.id)
                        logger.info(f"Completed improvement cycle: {cycle.name}")
                
                # Wait before next analysis
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Error in continuous improvement: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    def stop_improvement(self):
        """Stop continuous improvement"""
        self.improvement_active = False
        logger.info("Continuous improvement stopped")


# Global instance
continuous_improvement = ContinuousImprovementService()
