"""
Comprehensive logging service for production
"""
import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
import threading
from contextlib import contextmanager


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry, default=str)


class TextFormatter(logging.Formatter):
    """Enhanced text formatter for human-readable logs"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        # Add thread and process info
        record.thread_name = threading.current_thread().name
        return super().format(record)


class LoggingService:
    """Comprehensive logging service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        log_dir = Path(self.config.get('log_directory', '/app/logs'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        if self.config.get('log_format', 'json') == 'json':
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(TextFormatter())
        
        root_logger.addHandler(console_handler)
        
        # File handler
        if self.config.get('log_file'):
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = self._create_error_handler()
        root_logger.addHandler(error_handler)
        
        # Security log handler
        security_handler = self._create_security_handler()
        root_logger.addHandler(security_handler)
    
    def _create_file_handler(self):
        """Create rotating file handler"""
        log_file = self.config.get('log_file', '/app/logs/app.log')
        max_bytes = self.config.get('log_max_bytes', 10 * 1024 * 1024)  # 10MB
        backup_count = self.config.get('log_backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(logging.INFO)
        
        if self.config.get('log_format', 'json') == 'json':
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(TextFormatter())
        
        return handler
    
    def _create_error_handler(self):
        """Create error log handler"""
        error_file = self.config.get('error_log_file', '/app/logs/error.log')
        max_bytes = self.config.get('log_max_bytes', 10 * 1024 * 1024)
        backup_count = self.config.get('log_backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(logging.ERROR)
        
        if self.config.get('log_format', 'json') == 'json':
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(TextFormatter())
        
        return handler
    
    def _create_security_handler(self):
        """Create security log handler"""
        security_file = self.config.get('security_log_file', '/app/logs/security.log')
        max_bytes = self.config.get('log_max_bytes', 10 * 1024 * 1024)
        backup_count = self.config.get('log_backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            security_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(logging.WARNING)
        
        # Security formatter
        security_formatter = JSONFormatter()
        handler.setFormatter(security_formatter)
        
        return handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger for specific module"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, user_id: Optional[int] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log HTTP request"""
        logger = self.get_logger('http')
        
        extra = {
            'type': 'http_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time': response_time,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        logger.info(f"{method} {path} - {status_code} ({response_time:.3f}s)", extra=extra)
    
    def log_security_event(self, event_type: str, severity: str, 
                          user_id: Optional[int] = None, ip_address: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None):
        """Log security event"""
        logger = self.get_logger('security')
        
        extra = {
            'type': 'security_event',
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        if severity in ['high', 'critical']:
            logger.error(f"Security event: {event_type}", extra=extra)
        else:
            logger.warning(f"Security event: {event_type}", extra=extra)
    
    def log_authentication(self, event_type: str, success: bool, 
                          user_id: Optional[int] = None, ip_address: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None):
        """Log authentication event"""
        logger = self.get_logger('auth')
        
        extra = {
            'type': 'authentication',
            'event_type': event_type,
            'success': success,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        if success:
            logger.info(f"Auth success: {event_type}", extra=extra)
        else:
            logger.warning(f"Auth failure: {event_type}", extra=extra)
    
    def log_database_operation(self, operation: str, table: str, 
                              user_id: Optional[int] = None, 
                              details: Optional[Dict[str, Any]] = None):
        """Log database operation"""
        logger = self.get_logger('database')
        
        extra = {
            'type': 'database_operation',
            'operation': operation,
            'table': table,
            'user_id': user_id,
            'details': details or {}
        }
        
        logger.info(f"DB operation: {operation} on {table}", extra=extra)
    
    def log_performance(self, operation: str, duration: float, 
                       user_id: Optional[int] = None,
                       details: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        logger = self.get_logger('performance')
        
        extra = {
            'type': 'performance',
            'operation': operation,
            'duration': duration,
            'user_id': user_id,
            'details': details or {}
        }
        
        if duration > 5.0:  # Log slow operations
            logger.warning(f"Slow operation: {operation} ({duration:.3f}s)", extra=extra)
        else:
            logger.info(f"Operation: {operation} ({duration:.3f}s)", extra=extra)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        logger = self.get_logger('error')
        
        extra = {
            'type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        logger.error(f"Error: {type(error).__name__}: {str(error)}", extra=extra, exc_info=True)
    
    def log_system_event(self, event_type: str, message: str, 
                        details: Optional[Dict[str, Any]] = None):
        """Log system event"""
        logger = self.get_logger('system')
        
        extra = {
            'type': 'system_event',
            'event_type': event_type,
            'details': details or {}
        }
        
        logger.info(f"System: {event_type} - {message}", extra=extra)
    
    @contextmanager
    def log_execution_time(self, operation: str, user_id: Optional[int] = None):
        """Context manager for logging execution time"""
        start_time = datetime.now(timezone.utc)
        try:
            yield
        finally:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.log_performance(operation, duration, user_id)


# Global logging service instance
logging_service = None


def setup_logging(config: Dict[str, Any]):
    """Setup global logging service"""
    global logging_service
    logging_service = LoggingService(config)
    return logging_service


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    if logging_service is None:
        return logging.getLogger(name)
    return logging_service.get_logger(name)
