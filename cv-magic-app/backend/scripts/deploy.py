#!/usr/bin/env python3
"""
Production deployment script
"""
import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeploymentManager:
    """Production deployment manager"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "deployment_config.json"
        self.config = self._load_config()
        self.deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _load_config(self) -> dict:
        """Load deployment configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """Create default deployment configuration"""
        config = {
            "environment": "production",
            "app_name": "cv-management-api",
            "version": "1.0.0",
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "cv_app_prod",
                "user": "cv_app_user",
                "password": "secure_password"
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "password": None
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "file": "/var/log/cv-app/app.log"
            },
            "monitoring": {
                "enabled": True,
                "metrics_retention_days": 30
            },
            "backup": {
                "enabled": True,
                "schedule": "0 2 * * *",
                "retention_days": 30
            }
        }
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created default configuration at {self.config_path}")
        return config
    
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        logger.info("Validating deployment environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8+ required")
            return False
        
        # Check required packages
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary",
            "pydantic", "python-jose", "passlib", "python-multipart"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                logger.error(f"Required package not found: {package}")
                return False
        
        # Check database connection
        if not self._check_database_connection():
            logger.error("Database connection failed")
            return False
        
        # Check Redis connection
        if not self._check_redis_connection():
            logger.error("Redis connection failed")
            return False
        
        logger.info("Environment validation passed")
        return True
    
    def _check_database_connection(self) -> bool:
        """Check database connection"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=self.config["database"]["host"],
                port=self.config["database"]["port"],
                database=self.config["database"]["name"],
                user=self.config["database"]["user"],
                password=self.config["database"]["password"]
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def _check_redis_connection(self) -> bool:
        """Check Redis connection"""
        try:
            import redis
            r = redis.Redis(
                host=self.config["redis"]["host"],
                port=self.config["redis"]["port"],
                password=self.config["redis"]["password"]
            )
            r.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install production dependencies"""
        logger.info("Installing production dependencies...")
        
        try:
            # Install from requirements.txt
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            
            # Install additional production packages
            production_packages = [
                "gunicorn", "psutil", "redis", "celery", "flower"
            ]
            
            for package in production_packages:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True)
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Setup production database"""
        logger.info("Setting up production database...")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "DATABASE_URL": f"postgresql://{self.config['database']['user']}:{self.config['database']['password']}@{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['name']}",
                "ENVIRONMENT": "production"
            })
            
            # Run database migration
            subprocess.run([
                sys.executable, "recreate_tables.py"
            ], check=True, env=env)
            
            logger.info("Database setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    def create_systemd_service(self) -> bool:
        """Create systemd service file"""
        logger.info("Creating systemd service...")
        
        service_content = f"""[Unit]
Description=CV Management API
After=network.target

[Service]
Type=exec
User=cv-app
Group=cv-app
WorkingDirectory={os.getcwd()}
Environment=PATH={os.environ.get('PATH')}
Environment=DATABASE_URL=postgresql://{self.config['database']['user']}:{self.config['database']['password']}@{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['name']}
Environment=ENVIRONMENT=production
ExecStart={sys.executable} -m gunicorn app.main:app -w {self.config['server']['workers']} -k uvicorn.workers.UvicornWorker --bind {self.config['server']['host']}:{self.config['server']['port']}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        service_file = f"/etc/systemd/system/{self.config['app_name']}.service"
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", self.config['app_name']], check=True)
            
            logger.info(f"Systemd service created: {service_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
    
    def setup_logging(self) -> bool:
        """Setup production logging"""
        logger.info("Setting up production logging...")
        
        try:
            # Create log directory
            log_dir = Path(self.config["logging"]["file"]).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            subprocess.run(["sudo", "chown", "-R", "cv-app:cv-app", str(log_dir)], check=True)
            
            logger.info("Logging setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Logging setup failed: {e}")
            return False
    
    def setup_monitoring(self) -> bool:
        """Setup monitoring and alerting"""
        logger.info("Setting up monitoring...")
        
        try:
            # Create monitoring directory
            monitoring_dir = Path("/var/lib/cv-app/monitoring")
            monitoring_dir.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            subprocess.run(["sudo", "chown", "-R", "cv-app:cv-app", str(monitoring_dir)], check=True)
            
            logger.info("Monitoring setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Monitoring setup failed: {e}")
            return False
    
    def create_nginx_config(self) -> bool:
        """Create Nginx configuration"""
        logger.info("Creating Nginx configuration...")
        
        nginx_config = f"""
upstream cv_app {{
    server {self.config['server']['host']}:{self.config['server']['port']};
}}

server {{
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location / {{
        proxy_pass http://cv_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias /var/www/cv-app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        
        nginx_file = f"/etc/nginx/sites-available/{self.config['app_name']}"
        
        try:
            with open(nginx_file, 'w') as f:
                f.write(nginx_config)
            
            # Enable site
            subprocess.run(["sudo", "ln", "-sf", nginx_file, f"/etc/nginx/sites-enabled/{self.config['app_name']}"], check=True)
            subprocess.run(["sudo", "nginx", "-t"], check=True)
            
            logger.info(f"Nginx configuration created: {nginx_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create Nginx configuration: {e}")
            return False
    
    def deploy(self) -> bool:
        """Deploy application"""
        logger.info(f"Starting deployment {self.deployment_id}...")
        
        steps = [
            ("Validate Environment", self.validate_environment),
            ("Install Dependencies", self.install_dependencies),
            ("Setup Database", self.setup_database),
            ("Setup Logging", self.setup_logging),
            ("Setup Monitoring", self.setup_monitoring),
            ("Create Systemd Service", self.create_systemd_service),
            ("Create Nginx Config", self.create_nginx_config)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            if not step_func():
                logger.error(f"Deployment failed at: {step_name}")
                return False
        
        logger.info(f"Deployment {self.deployment_id} completed successfully!")
        return True
    
    def start_service(self) -> bool:
        """Start the service"""
        logger.info("Starting service...")
        
        try:
            subprocess.run(["sudo", "systemctl", "start", self.config['app_name']], check=True)
            subprocess.run(["sudo", "systemctl", "status", self.config['app_name']], check=True)
            
            logger.info("Service started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the service"""
        logger.info("Stopping service...")
        
        try:
            subprocess.run(["sudo", "systemctl", "stop", self.config['app_name']], check=True)
            
            logger.info("Service stopped successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop service: {e}")
            return False
    
    def restart_service(self) -> bool:
        """Restart the service"""
        logger.info("Restarting service...")
        
        try:
            subprocess.run(["sudo", "systemctl", "restart", self.config['app_name']], check=True)
            
            logger.info("Service restarted successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart service: {e}")
            return False


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="CV Management API Deployment Script")
    parser.add_argument("--config", help="Configuration file path", default="deployment_config.json")
    parser.add_argument("--action", choices=["deploy", "start", "stop", "restart"], default="deploy")
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager(args.config)
    
    if args.action == "deploy":
        success = deployment_manager.deploy()
    elif args.action == "start":
        success = deployment_manager.start_service()
    elif args.action == "stop":
        success = deployment_manager.stop_service()
    elif args.action == "restart":
        success = deployment_manager.restart_service()
    else:
        logger.error("Invalid action")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
