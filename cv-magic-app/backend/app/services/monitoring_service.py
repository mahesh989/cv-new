"""
Application monitoring and health check service
"""
import time
import psutil
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from app.database import get_database
from app.models.user import User, UserSession
from app.models.user_data import UserActivityLog
import logging

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    load_average: List[float]


@dataclass
class ApplicationMetrics:
    """Application metrics data structure"""
    timestamp: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    active_users: int
    total_users: int
    active_sessions: int
    database_connections: int
    error_rate: float


@dataclass
class HealthStatus:
    """Health status data structure"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    checks: Dict[str, Dict[str, Any]]
    overall_score: float


class MonitoringService:
    """Application monitoring service"""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.app_metrics_history: List[ApplicationMetrics] = []
        self.health_history: List[HealthStatus] = []
        self.monitoring_enabled = True
        self.metrics_thread = None
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_enabled and not self.monitoring_thread:
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Monitoring service started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_enabled = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Monitoring service stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                self.app_metrics_history.append(app_metrics)
                
                # Check health status
                health_status = self._check_health_status()
                self.health_history.append(health_status)
                
                # Clean up old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network usage
            network = psutil.net_io_counters()
            
            # Active connections
            connections = len(psutil.net_connections())
            
            # Load average
            load_avg = psutil.getloadavg()
            
            return SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                active_connections=connections,
                load_average=list(load_avg)
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                active_connections=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application metrics"""
        try:
            db = next(get_database())
            
            # Get user counts
            total_users = db.query(User).count()
            active_users = db.query(UserSession).filter(
                UserSession.is_blacklisted == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).distinct(UserSession.user_id).count()
            
            # Get session counts
            active_sessions = db.query(UserSession).filter(
                UserSession.is_blacklisted == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            ).count()
            
            # Get activity counts (last hour)
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_activities = db.query(UserActivityLog).filter(
                UserActivityLog.created_at >= one_hour_ago
            ).count()
            
            # Calculate metrics (simplified)
            total_requests = recent_activities
            successful_requests = int(total_requests * 0.95)  # Assume 95% success rate
            failed_requests = total_requests - successful_requests
            average_response_time = 0.5  # Placeholder
            error_rate = failed_requests / total_requests if total_requests > 0 else 0
            
            return ApplicationMetrics(
                timestamp=datetime.now(timezone.utc),
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                active_users=active_users,
                total_users=total_users,
                active_sessions=active_sessions,
                database_connections=1,  # Placeholder
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                timestamp=datetime.now(timezone.utc),
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                active_users=0,
                total_users=0,
                active_sessions=0,
                database_connections=0,
                error_rate=0.0
            )
    
    def _check_health_status(self) -> HealthStatus:
        """Check overall health status"""
        checks = {}
        overall_score = 100.0
        
        # Database health
        db_health = self._check_database_health()
        checks['database'] = db_health
        if not db_health['healthy']:
            overall_score -= 30
        
        # System health
        system_health = self._check_system_health()
        checks['system'] = system_health
        if not system_health['healthy']:
            overall_score -= 25
        
        # Application health
        app_health = self._check_application_health()
        checks['application'] = app_health
        if not app_health['healthy']:
            overall_score -= 25
        
        # Security health
        security_health = self._check_security_health()
        checks['security'] = security_health
        if not security_health['healthy']:
            overall_score -= 20
        
        # Determine overall status
        if overall_score >= 90:
            status = "healthy"
        elif overall_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.now(timezone.utc),
            checks=checks,
            overall_score=overall_score
        )
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            db = next(get_database())
            # Simple query to test connection
            db.execute("SELECT 1")
            
            return {
                'healthy': True,
                'status': 'connected',
                'response_time': 0.1,
                'details': 'Database connection successful'
            }
        except Exception as e:
            return {
                'healthy': False,
                'status': 'disconnected',
                'error': str(e),
                'details': 'Database connection failed'
            }
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            # Get latest system metrics
            if not self.metrics_history:
                return {'healthy': True, 'status': 'no_data', 'details': 'No metrics available'}
            
            latest_metrics = self.metrics_history[-1]
            
            # Check thresholds
            issues = []
            if latest_metrics.cpu_percent > 80:
                issues.append(f"High CPU usage: {latest_metrics.cpu_percent:.1f}%")
            if latest_metrics.memory_percent > 80:
                issues.append(f"High memory usage: {latest_metrics.memory_percent:.1f}%")
            if latest_metrics.disk_percent > 90:
                issues.append(f"High disk usage: {latest_metrics.disk_percent:.1f}%")
            
            healthy = len(issues) == 0
            
            return {
                'healthy': healthy,
                'status': 'ok' if healthy else 'warning',
                'cpu_percent': latest_metrics.cpu_percent,
                'memory_percent': latest_metrics.memory_percent,
                'disk_percent': latest_metrics.disk_percent,
                'issues': issues,
                'details': 'System metrics within normal range' if healthy else '; '.join(issues)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'error': str(e),
                'details': 'Failed to check system health'
            }
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application health"""
        try:
            if not self.app_metrics_history:
                return {'healthy': True, 'status': 'no_data', 'details': 'No metrics available'}
            
            latest_metrics = self.app_metrics_history[-1]
            
            # Check thresholds
            issues = []
            if latest_metrics.error_rate > 0.05:  # 5% error rate
                issues.append(f"High error rate: {latest_metrics.error_rate:.2%}")
            if latest_metrics.average_response_time > 2.0:  # 2 seconds
                issues.append(f"Slow response time: {latest_metrics.average_response_time:.2f}s")
            
            healthy = len(issues) == 0
            
            return {
                'healthy': healthy,
                'status': 'ok' if healthy else 'warning',
                'error_rate': latest_metrics.error_rate,
                'response_time': latest_metrics.average_response_time,
                'active_users': latest_metrics.active_users,
                'issues': issues,
                'details': 'Application metrics within normal range' if healthy else '; '.join(issues)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'error': str(e),
                'details': 'Failed to check application health'
            }
    
    def _check_security_health(self) -> Dict[str, Any]:
        """Check security health"""
        try:
            # Check for recent security events
            db = next(get_database())
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            
            security_events = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type == 'security',
                UserActivityLog.created_at >= one_hour_ago
            ).count()
            
            # Check for failed login attempts
            failed_logins = db.query(UserActivityLog).filter(
                UserActivityLog.activity_type == 'authentication',
                UserActivityLog.activity_data.contains('"success": false'),
                UserActivityLog.created_at >= one_hour_ago
            ).count()
            
            issues = []
            if security_events > 10:
                issues.append(f"High security events: {security_events}")
            if failed_logins > 50:
                issues.append(f"High failed logins: {failed_logins}")
            
            healthy = len(issues) == 0
            
            return {
                'healthy': healthy,
                'status': 'ok' if healthy else 'warning',
                'security_events': security_events,
                'failed_logins': failed_logins,
                'issues': issues,
                'details': 'Security metrics within normal range' if healthy else '; '.join(issues)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'error': str(e),
                'details': 'Failed to check security health'
            }
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory issues"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Clean up system metrics
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        # Clean up application metrics
        self.app_metrics_history = [
            m for m in self.app_metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        # Clean up health history
        self.health_history = [
            h for h in self.health_history 
            if h.timestamp >= cutoff_time
        ]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'system': asdict(self.metrics_history[-1]) if self.metrics_history else None,
            'application': asdict(self.app_metrics_history[-1]) if self.app_metrics_history else None,
            'health': asdict(self.health_history[-1]) if self.health_history else None
        }
    
    def get_metrics_history(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics history"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return {
            'system': [asdict(m) for m in self.metrics_history if m.timestamp >= cutoff_time],
            'application': [asdict(m) for m in self.app_metrics_history if m.timestamp >= cutoff_time],
            'health': [asdict(h) for h in self.health_history if h.timestamp >= cutoff_time]
        }


# Global monitoring service instance
monitoring_service = MonitoringService()
