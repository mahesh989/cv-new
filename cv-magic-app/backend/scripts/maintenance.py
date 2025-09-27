#!/usr/bin/env python3
"""
Production maintenance script
"""
import os
import sys
import subprocess
import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging
import psutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Production maintenance manager"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "deployment_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load deployment configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
    
    def cleanup_logs(self, days: int = 30) -> bool:
        """Clean up old log files"""
        logger.info(f"Cleaning up logs older than {days} days...")
        
        try:
            log_dir = Path(self.config["logging"]["file"]).parent
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cleaned_count = 0
            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} log files")
            return True
            
        except Exception as e:
            logger.error(f"Log cleanup failed: {e}")
            return False
    
    def cleanup_metrics(self, days: int = 30) -> bool:
        """Clean up old metrics data"""
        logger.info(f"Cleaning up metrics older than {days} days...")
        
        try:
            # This would typically clean up metrics from a time-series database
            # For now, we'll just log the action
            logger.info("Metrics cleanup completed (placeholder)")
            return True
            
        except Exception as e:
            logger.error(f"Metrics cleanup failed: {e}")
            return False
    
    def cleanup_temp_files(self) -> bool:
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        
        try:
            temp_dirs = [
                "/tmp/cv-app",
                "/var/tmp/cv-app",
                "temp",
                "uploads/temp"
            ]
            
            cleaned_count = 0
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for file in temp_path.glob("*"):
                        if file.is_file():
                            file.unlink()
                            cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return True
            
        except Exception as e:
            logger.error(f"Temp files cleanup failed: {e}")
            return False
    
    def backup_database(self) -> bool:
        """Backup database"""
        logger.info("Creating database backup...")
        
        try:
            backup_dir = Path("/var/backups/cv-app")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"cv_app_backup_{timestamp}.sql"
            
            # Create database backup
            subprocess.run([
                "pg_dump",
                "-h", self.config["database"]["host"],
                "-p", str(self.config["database"]["port"]),
                "-U", self.config["database"]["user"],
                "-d", self.config["database"]["name"],
                "-f", str(backup_file)
            ], check=True, env={"PGPASSWORD": self.config["database"]["password"]})
            
            # Compress backup
            subprocess.run(["gzip", str(backup_file)], check=True)
            
            logger.info(f"Database backup created: {backup_file}.gz")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def backup_files(self) -> bool:
        """Backup application files"""
        logger.info("Creating files backup...")
        
        try:
            backup_dir = Path("/var/backups/cv-app")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"cv_app_files_{timestamp}.tar.gz"
            
            # Create files backup
            subprocess.run([
                "tar", "-czf", str(backup_file),
                "app/", "uploads/", "logs/", "config/"
            ], check=True)
            
            logger.info(f"Files backup created: {backup_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Files backup failed: {e}")
            return False
    
    def cleanup_old_backups(self, days: int = 30) -> bool:
        """Clean up old backup files"""
        logger.info(f"Cleaning up backups older than {days} days...")
        
        try:
            backup_dir = Path("/var/backups/cv-app")
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cleaned_count = 0
            for backup_file in backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} backup files")
            return True
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return False
    
    def check_disk_space(self) -> bool:
        """Check disk space usage"""
        logger.info("Checking disk space...")
        
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent > 90:
                logger.warning(f"Disk usage is high: {usage_percent:.1f}%")
                return False
            elif usage_percent > 80:
                logger.warning(f"Disk usage is moderate: {usage_percent:.1f}%")
            
            logger.info(f"Disk usage: {usage_percent:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False
    
    def check_memory_usage(self) -> bool:
        """Check memory usage"""
        logger.info("Checking memory usage...")
        
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                logger.warning(f"Memory usage is high: {usage_percent:.1f}%")
                return False
            elif usage_percent > 80:
                logger.warning(f"Memory usage is moderate: {usage_percent:.1f}%")
            
            logger.info(f"Memory usage: {usage_percent:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return False
    
    def check_service_status(self) -> bool:
        """Check service status"""
        logger.info("Checking service status...")
        
        try:
            result = subprocess.run([
                "systemctl", "is-active", self.config['app_name']
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Service is running")
                return True
            else:
                logger.error("Service is not running")
                return False
                
        except Exception as e:
            logger.error(f"Service status check failed: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart service"""
        logger.info("Restarting service...")
        
        try:
            subprocess.run(["sudo", "systemctl", "restart", self.config['app_name']], check=True)
            logger.info("Service restarted successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service restart failed: {e}")
            return False
    
    def update_dependencies(self) -> bool:
        """Update dependencies"""
        logger.info("Updating dependencies...")
        
        try:
            # Update pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Update requirements
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"], check=True)
            
            logger.info("Dependencies updated successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Dependency update failed: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Run health check"""
        logger.info("Running health check...")
        
        try:
            # Check if service is responding
            import requests
            response = requests.get(f"http://localhost:{self.config['server']['port']}/monitoring/health", timeout=10)
            
            if response.status_code == 200:
                logger.info("Health check passed")
                return True
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def run_maintenance(self) -> bool:
        """Run full maintenance routine"""
        logger.info("Starting maintenance routine...")
        
        steps = [
            ("Check Disk Space", self.check_disk_space),
            ("Check Memory Usage", self.check_memory_usage),
            ("Check Service Status", self.check_service_status),
            ("Cleanup Logs", lambda: self.cleanup_logs(30)),
            ("Cleanup Metrics", lambda: self.cleanup_metrics(30)),
            ("Cleanup Temp Files", self.cleanup_temp_files),
            ("Cleanup Old Backups", lambda: self.cleanup_old_backups(30)),
            ("Backup Database", self.backup_database),
            ("Backup Files", self.backup_files),
            ("Run Health Check", self.run_health_check)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            if not step_func():
                logger.error(f"Maintenance failed at: {step_name}")
                return False
        
        logger.info("Maintenance routine completed successfully!")
        return True


def main():
    """Main maintenance function"""
    parser = argparse.ArgumentParser(description="CV Management API Maintenance Script")
    parser.add_argument("--config", help="Configuration file path", default="deployment_config.json")
    parser.add_argument("--action", choices=[
        "maintenance", "cleanup-logs", "cleanup-metrics", "cleanup-temp", 
        "backup-db", "backup-files", "cleanup-backups", "check-disk", 
        "check-memory", "check-service", "restart-service", "update-deps", 
        "health-check"
    ], default="maintenance")
    parser.add_argument("--days", type=int, default=30, help="Days for cleanup operations")
    
    args = parser.parse_args()
    
    maintenance_manager = MaintenanceManager(args.config)
    
    if args.action == "maintenance":
        success = maintenance_manager.run_maintenance()
    elif args.action == "cleanup-logs":
        success = maintenance_manager.cleanup_logs(args.days)
    elif args.action == "cleanup-metrics":
        success = maintenance_manager.cleanup_metrics(args.days)
    elif args.action == "cleanup-temp":
        success = maintenance_manager.cleanup_temp_files()
    elif args.action == "backup-db":
        success = maintenance_manager.backup_database()
    elif args.action == "backup-files":
        success = maintenance_manager.backup_files()
    elif args.action == "cleanup-backups":
        success = maintenance_manager.cleanup_old_backups(args.days)
    elif args.action == "check-disk":
        success = maintenance_manager.check_disk_space()
    elif args.action == "check-memory":
        success = maintenance_manager.check_memory_usage()
    elif args.action == "check-service":
        success = maintenance_manager.check_service_status()
    elif args.action == "restart-service":
        success = maintenance_manager.restart_service()
    elif args.action == "update-deps":
        success = maintenance_manager.update_dependencies()
    elif args.action == "health-check":
        success = maintenance_manager.run_health_check()
    else:
        logger.error("Invalid action")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
