"""
Post-Launch Monitoring Service for CV Management API
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
import aiohttp
from sqlalchemy.orm import Session
from app.database import get_database
from app.models.user import User
from app.models.user_data import UserActivityLog
import requests

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to monitor"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    USAGE = "usage"
    ERROR = "error"
    BUSINESS = "business"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_name: str
    threshold_value: float
    comparison: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    alert_level: AlertLevel
    description: str


@dataclass
class PerformanceMetric:
    """Performance metric data"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    labels: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class UserFeedback:
    """User feedback data"""
    user_id: int
    feedback_type: str
    rating: int
    comment: str
    timestamp: datetime
    metadata: Dict[str, Any]


class PostLaunchMonitoringService:
    """Post-launch monitoring and optimization service"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.user_feedback: List[UserFeedback] = []
        self.optimization_recommendations: List[Dict[str, Any]] = []
        self.thresholds = self._initialize_thresholds()
        self.monitoring_active = True
        self.optimization_enabled = True
        
        logger.info("PostLaunchMonitoringService initialized")
    
    def _initialize_thresholds(self) -> List[MetricThreshold]:
        """Initialize monitoring thresholds"""
        return [
            MetricThreshold(
                metric_name="response_time",
                threshold_value=2.0,
                comparison="gt",
                alert_level=AlertLevel.WARNING,
                description="Response time exceeds 2 seconds"
            ),
            MetricThreshold(
                metric_name="error_rate",
                threshold_value=5.0,
                comparison="gt",
                alert_level=AlertLevel.CRITICAL,
                description="Error rate exceeds 5%"
            ),
            MetricThreshold(
                metric_name="memory_usage",
                threshold_value=80.0,
                comparison="gt",
                alert_level=AlertLevel.WARNING,
                description="Memory usage exceeds 80%"
            ),
            MetricThreshold(
                metric_name="cpu_usage",
                threshold_value=80.0,
                comparison="gt",
                alert_level=AlertLevel.WARNING,
                description="CPU usage exceeds 80%"
            ),
            MetricThreshold(
                metric_name="disk_usage",
                threshold_value=90.0,
                comparison="gt",
                alert_level=AlertLevel.CRITICAL,
                description="Disk usage exceeds 90%"
            ),
            MetricThreshold(
                metric_name="active_users",
                threshold_value=1000.0,
                comparison="gt",
                alert_level=AlertLevel.INFO,
                description="Active users exceed 1000"
            ),
            MetricThreshold(
                metric_name="cache_hit_rate",
                threshold_value=70.0,
                comparison="lt",
                alert_level=AlertLevel.WARNING,
                description="Cache hit rate below 70%"
            )
        ]
    
    async def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Collect comprehensive system metrics"""
        logger.info("Collecting system metrics...")
        
        metrics = []
        current_time = datetime.now(timezone.utc)
        
        try:
            # Performance metrics
            metrics.extend(await self._collect_performance_metrics(current_time))
            
            # Security metrics
            metrics.extend(await self._collect_security_metrics(current_time))
            
            # Usage metrics
            metrics.extend(await self._collect_usage_metrics(current_time))
            
            # Error metrics
            metrics.extend(await self._collect_error_metrics(current_time))
            
            # Business metrics
            metrics.extend(await self._collect_business_metrics(current_time))
            
            # Store metrics
            self.metrics_history.extend(metrics)
            
            # Keep only last 24 hours of metrics
            cutoff_time = current_time - timedelta(hours=24)
            self.metrics_history = [
                m for m in self.metrics_history 
                if m.timestamp > cutoff_time
            ]
            
            logger.info(f"Collected {len(metrics)} metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return []
    
    async def _collect_performance_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect performance metrics"""
        metrics = []
        
        try:
            # Response time metrics
            response_times = await self._measure_response_times()
            for endpoint, avg_time in response_times.items():
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="response_time",
                    value=avg_time,
                    unit="seconds",
                    labels={"endpoint": endpoint},
                    metadata={"type": "performance"}
                ))
            
            # Memory usage
            memory_usage = await self._get_memory_usage()
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="memory_usage",
                value=memory_usage,
                unit="percent",
                labels={},
                metadata={"type": "performance"}
            ))
            
            # CPU usage
            cpu_usage = await self._get_cpu_usage()
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="cpu_usage",
                value=cpu_usage,
                unit="percent",
                labels={},
                metadata={"type": "performance"}
            ))
            
            # Disk usage
            disk_usage = await self._get_disk_usage()
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="disk_usage",
                value=disk_usage,
                unit="percent",
                labels={},
                metadata={"type": "performance"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
        
        return metrics
    
    async def _collect_security_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect security metrics"""
        metrics = []
        
        try:
            db = next(get_database())
            
            # Failed login attempts
            failed_logins = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type == "login_failed",
                UserActivityLog.created_at >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="failed_logins",
                value=failed_logins,
                unit="count",
                labels={},
                metadata={"type": "security"}
            ))
            
            # Security events
            security_events = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type.like("security_%"),
                UserActivityLog.created_at >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="security_events",
                value=security_events,
                unit="count",
                labels={},
                metadata={"type": "security"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting security metrics: {e}")
        
        return metrics
    
    async def _collect_usage_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect usage metrics"""
        metrics = []
        
        try:
            db = next(get_database())
            
            # Active users
            active_users = db.query(User).filter(
                User.last_login >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="active_users",
                value=active_users,
                unit="count",
                labels={},
                metadata={"type": "usage"}
            ))
            
            # Total users
            total_users = db.query(User).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="total_users",
                value=total_users,
                unit="count",
                labels={},
                metadata={"type": "usage"}
            ))
            
            # File operations
            file_operations = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type.like("file_%"),
                UserActivityLog.created_at >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="file_operations",
                value=file_operations,
                unit="count",
                labels={},
                metadata={"type": "usage"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting usage metrics: {e}")
        
        return metrics
    
    async def _collect_error_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect error metrics"""
        metrics = []
        
        try:
            # Calculate error rate
            total_requests = await self._get_total_requests(timestamp)
            error_requests = await self._get_error_requests(timestamp)
            
            if total_requests > 0:
                error_rate = (error_requests / total_requests) * 100
                
                metrics.append(PerformanceMetric(
                    timestamp=timestamp,
                    metric_name="error_rate",
                    value=error_rate,
                    unit="percent",
                    labels={},
                    metadata={"type": "error"}
                ))
            
        except Exception as e:
            logger.error(f"Error collecting error metrics: {e}")
        
        return metrics
    
    async def _collect_business_metrics(self, timestamp: datetime) -> List[PerformanceMetric]:
        """Collect business metrics"""
        metrics = []
        
        try:
            db = next(get_database())
            
            # User registrations
            new_registrations = db.query(User).filter(
                User.created_at >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="new_registrations",
                value=new_registrations,
                unit="count",
                labels={},
                metadata={"type": "business"}
            ))
            
            # File uploads
            file_uploads = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type == "file_upload",
                UserActivityLog.created_at >= timestamp - timedelta(hours=1)
            ).count()
            
            metrics.append(PerformanceMetric(
                timestamp=timestamp,
                metric_name="file_uploads",
                value=file_uploads,
                unit="count",
                labels={},
                metadata={"type": "business"}
            ))
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
        
        return metrics
    
    async def _measure_response_times(self) -> Dict[str, float]:
        """Measure response times for key endpoints"""
        endpoints = [
            "/",
            "/api/auth/login",
            "/api/user/cv/list",
            "/api/monitoring/health"
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:8000{endpoint}", timeout=10) as response:
                        response_time = time.time() - start_time
                        response_times[endpoint] = response_time
            except Exception as e:
                logger.warning(f"Could not measure response time for {endpoint}: {e}")
                response_times[endpoint] = 0.0
        
        return response_times
    
    async def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            logger.warning("psutil not available, using default memory usage")
            return 50.0
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            logger.warning("psutil not available, using default CPU usage")
            return 50.0
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return 0.0
    
    async def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except ImportError:
            logger.warning("psutil not available, using default disk usage")
            return 50.0
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return 0.0
    
    async def _get_total_requests(self, timestamp: datetime) -> int:
        """Get total requests in the last hour"""
        # This would integrate with your logging system
        # For now, return a default value
        return 1000
    
    async def _get_error_requests(self, timestamp: datetime) -> int:
        """Get error requests in the last hour"""
        # This would integrate with your logging system
        # For now, return a default value
        return 50
    
    def check_thresholds(self, metrics: List[PerformanceMetric]) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        for metric in metrics:
            for threshold in self.thresholds:
                if metric.metric_name == threshold.metric_name:
                    if self._evaluate_threshold(metric.value, threshold):
                        alert = {
                            "timestamp": metric.timestamp.isoformat(),
                            "metric_name": metric.metric_name,
                            "value": metric.value,
                            "threshold": threshold.threshold_value,
                            "level": threshold.alert_level.value,
                            "description": threshold.description,
                            "labels": metric.labels,
                            "metadata": metric.metadata
                        }
                        alerts.append(alert)
                        logger.warning(f"Threshold alert: {alert}")
        
        return alerts
    
    def _evaluate_threshold(self, value: float, threshold: MetricThreshold) -> bool:
        """Evaluate if a metric value exceeds its threshold"""
        if threshold.comparison == "gt":
            return value > threshold.threshold_value
        elif threshold.comparison == "lt":
            return value < threshold.threshold_value
        elif threshold.comparison == "eq":
            return value == threshold.threshold_value
        elif threshold.comparison == "gte":
            return value >= threshold.threshold_value
        elif threshold.comparison == "lte":
            return value <= threshold.threshold_value
        return False
    
    def collect_user_feedback(self, user_id: int, feedback_type: str, rating: int, 
                            comment: str, metadata: Dict[str, Any] = None) -> UserFeedback:
        """Collect user feedback"""
        feedback = UserFeedback(
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.user_feedback.append(feedback)
        
        # Keep only last 30 days of feedback
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
        self.user_feedback = [
            f for f in self.user_feedback 
            if f.timestamp > cutoff_time
        ]
        
        logger.info(f"Collected user feedback: {feedback}")
        return feedback
    
    def analyze_user_feedback(self) -> Dict[str, Any]:
        """Analyze user feedback and generate insights"""
        if not self.user_feedback:
            return {"message": "No user feedback available"}
        
        # Calculate average rating
        avg_rating = sum(f.rating for f in self.user_feedback) / len(self.user_feedback)
        
        # Group by feedback type
        feedback_by_type = {}
        for feedback in self.user_feedback:
            if feedback.feedback_type not in feedback_by_type:
                feedback_by_type[feedback.feedback_type] = []
            feedback_by_type[feedback.feedback_type].append(feedback)
        
        # Calculate ratings by type
        ratings_by_type = {}
        for feedback_type, feedbacks in feedback_by_type.items():
            ratings_by_type[feedback_type] = {
                "count": len(feedbacks),
                "average_rating": sum(f.rating for f in feedbacks) / len(feedbacks),
                "ratings": [f.rating for f in feedbacks]
            }
        
        # Identify common issues
        common_issues = self._identify_common_issues()
        
        return {
            "total_feedback": len(self.user_feedback),
            "average_rating": avg_rating,
            "ratings_by_type": ratings_by_type,
            "common_issues": common_issues,
            "recommendations": self._generate_feedback_recommendations()
        }
    
    def _identify_common_issues(self) -> List[Dict[str, Any]]:
        """Identify common issues from user feedback"""
        issues = []
        
        # Analyze comments for common keywords
        common_keywords = ["slow", "error", "bug", "problem", "issue", "difficult", "confusing"]
        
        for keyword in common_keywords:
            keyword_feedback = [
                f for f in self.user_feedback 
                if keyword.lower() in f.comment.lower()
            ]
            
            if keyword_feedback:
                issues.append({
                    "keyword": keyword,
                    "count": len(keyword_feedback),
                    "average_rating": sum(f.rating for f in keyword_feedback) / len(keyword_feedback),
                    "examples": [f.comment for f in keyword_feedback[:3]]  # First 3 examples
                })
        
        return issues
    
    def _generate_feedback_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on user feedback"""
        recommendations = []
        
        # Analyze low ratings
        low_ratings = [f for f in self.user_feedback if f.rating <= 3]
        
        if len(low_ratings) > len(self.user_feedback) * 0.2:  # More than 20% low ratings
            recommendations.append({
                "type": "user_experience",
                "priority": "high",
                "description": "High number of low ratings detected",
                "action": "Review user experience and identify pain points"
            })
        
        # Analyze feedback types
        feedback_types = {}
        for feedback in self.user_feedback:
            if feedback.feedback_type not in feedback_types:
                feedback_types[feedback.feedback_type] = []
            feedback_types[feedback.feedback_type].append(feedback)
        
        for feedback_type, feedbacks in feedback_types.items():
            avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
            if avg_rating < 3.0:
                recommendations.append({
                    "type": "feature_improvement",
                    "priority": "medium",
                    "description": f"Low ratings for {feedback_type}",
                    "action": f"Improve {feedback_type} functionality"
                })
        
        return recommendations
    
    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        # Analyze recent metrics (last hour)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > datetime.now(timezone.utc) - timedelta(hours=1)
        ]
        
        # Performance recommendations
        performance_metrics = [m for m in recent_metrics if m.metric_name == "response_time"]
        if performance_metrics:
            avg_response_time = sum(m.value for m in performance_metrics) / len(performance_metrics)
            if avg_response_time > 1.0:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "description": f"Average response time is {avg_response_time:.2f}s",
                    "action": "Optimize database queries and implement caching",
                    "impact": "High"
                })
        
        # Memory recommendations
        memory_metrics = [m for m in recent_metrics if m.metric_name == "memory_usage"]
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            if avg_memory > 70:
                recommendations.append({
                    "type": "infrastructure",
                    "priority": "medium",
                    "description": f"Memory usage is {avg_memory:.1f}%",
                    "action": "Consider increasing memory or optimizing memory usage",
                    "impact": "Medium"
                })
        
        # Cache recommendations
        cache_metrics = [m for m in recent_metrics if m.metric_name == "cache_hit_rate"]
        if cache_metrics:
            avg_cache_hit = sum(m.value for m in cache_metrics) / len(cache_metrics)
            if avg_cache_hit < 80:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "description": f"Cache hit rate is {avg_cache_hit:.1f}%",
                    "action": "Optimize cache configuration and increase cache size",
                    "impact": "Medium"
                })
        
        # User growth recommendations
        user_metrics = [m for m in recent_metrics if m.metric_name == "active_users"]
        if user_metrics:
            max_users = max(m.value for m in user_metrics)
            if max_users > 500:
                recommendations.append({
                    "type": "scalability",
                    "priority": "low",
                    "description": f"Peak active users: {max_users}",
                    "action": "Monitor for scaling needs and prepare for increased load",
                    "impact": "Low"
                })
        
        return recommendations
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        if not self.metrics_history:
            return {"score": 0, "status": "unknown", "message": "No metrics available"}
        
        # Get recent metrics (last hour)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > datetime.now(timezone.utc) - timedelta(hours=1)
        ]
        
        if not recent_metrics:
            return {"score": 0, "status": "unknown", "message": "No recent metrics available"}
        
        # Calculate health score based on key metrics
        health_factors = []
        
        # Response time factor
        response_metrics = [m for m in recent_metrics if m.metric_name == "response_time"]
        if response_metrics:
            avg_response_time = sum(m.value for m in response_metrics) / len(response_metrics)
            if avg_response_time < 1.0:
                health_factors.append(1.0)
            elif avg_response_time < 2.0:
                health_factors.append(0.8)
            elif avg_response_time < 5.0:
                health_factors.append(0.6)
            else:
                health_factors.append(0.3)
        
        # Error rate factor
        error_metrics = [m for m in recent_metrics if m.metric_name == "error_rate"]
        if error_metrics:
            avg_error_rate = sum(m.value for m in error_metrics) / len(error_metrics)
            if avg_error_rate < 1.0:
                health_factors.append(1.0)
            elif avg_error_rate < 5.0:
                health_factors.append(0.8)
            elif avg_error_rate < 10.0:
                health_factors.append(0.6)
            else:
                health_factors.append(0.2)
        
        # Memory usage factor
        memory_metrics = [m for m in recent_metrics if m.metric_name == "memory_usage"]
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            if avg_memory < 50:
                health_factors.append(1.0)
            elif avg_memory < 70:
                health_factors.append(0.8)
            elif avg_memory < 85:
                health_factors.append(0.6)
            else:
                health_factors.append(0.3)
        
        # Calculate overall score
        if health_factors:
            overall_score = sum(health_factors) / len(health_factors) * 100
        else:
            overall_score = 0
        
        # Determine status
        if overall_score >= 90:
            status = "excellent"
        elif overall_score >= 80:
            status = "good"
        elif overall_score >= 70:
            status = "fair"
        elif overall_score >= 50:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "score": round(overall_score, 1),
            "status": status,
            "factors": len(health_factors),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting post-launch monitoring...")
        
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self.collect_system_metrics()
                
                # Check thresholds
                alerts = self.check_thresholds(metrics)
                
                # Process alerts
                for alert in alerts:
                    await self._process_alert(alert)
                
                # Generate optimization recommendations
                if self.optimization_enabled:
                    recommendations = self.generate_optimization_recommendations()
                    if recommendations:
                        logger.info(f"Generated {len(recommendations)} optimization recommendations")
                
                # Wait before next collection
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _process_alert(self, alert: Dict[str, Any]):
        """Process an alert"""
        logger.warning(f"Processing alert: {alert}")
        
        # Here you would integrate with your alerting system
        # For now, just log the alert
        if alert["level"] in ["critical", "emergency"]:
            logger.critical(f"CRITICAL ALERT: {alert}")
        elif alert["level"] == "warning":
            logger.warning(f"WARNING ALERT: {alert}")
        else:
            logger.info(f"INFO ALERT: {alert}")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Post-launch monitoring stopped")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        return {
            "monitoring_active": self.monitoring_active,
            "optimization_enabled": self.optimization_enabled,
            "metrics_collected": len(self.metrics_history),
            "user_feedback_count": len(self.user_feedback),
            "optimization_recommendations": len(self.optimization_recommendations),
            "health_score": self.get_system_health_score(),
            "feedback_analysis": self.analyze_user_feedback(),
            "recommendations": self.generate_optimization_recommendations()
        }


# Global instance - lazy initialization
post_launch_monitoring = None

def get_post_launch_monitoring():
    """Get or create the post-launch monitoring service instance"""
    global post_launch_monitoring
    if post_launch_monitoring is None:
        post_launch_monitoring = PostLaunchMonitoringService()
    return post_launch_monitoring
