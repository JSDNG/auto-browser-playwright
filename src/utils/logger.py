"""
Logger utility for structured logging.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path


class PlaywrightLogger:
    """Custom logger for Playwright automation."""
    
    def __init__(self, name: str = "playwright-automation"):
        """Initialize logger."""
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Set log level
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create stderr handler (for debugging, not stdout)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(stderr_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def add_file_handler(self, log_file: str, level: int = logging.INFO):
        """Add file handler for logging."""
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.logger.error(f"Failed to add file handler: {e}")
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log(logging.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log(logging.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log(logging.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self._log(logging.ERROR, message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra)
    
    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal log method."""
        if extra:
            # Format extra data
            extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
            message = f"{message} | {extra_str}"
        
        self.logger.log(level, message)
    
    def log_automation_start(self, url: str, actions_count: int = 0, extract_count: int = 0):
        """Log automation start."""
        self.info(
            "Automation started",
            {
                "url": url,
                "actions_count": actions_count,
                "extract_count": extract_count
            }
        )
    
    def log_automation_end(self, success: bool, execution_time: float, data_count: int = 0):
        """Log automation end."""
        status = "success" if success else "failed"
        self.info(
            f"Automation {status}",
            {
                "execution_time": f"{execution_time:.2f}s",
                "data_count": data_count
            }
        )
    
    def log_action(self, action_type: str, selector: str, success: bool, duration: float = 0):
        """Log action execution."""
        status = "success" if success else "failed"
        self.info(
            f"Action {action_type} {status}",
            {
                "selector": selector,
                "duration": f"{duration:.3f}s"
            }
        )
    
    def log_extraction(self, name: str, selector: str, result_count: int = 0):
        """Log data extraction."""
        self.info(
            f"Data extracted: {name}",
            {
                "selector": selector,
                "result_count": result_count
            }
        )
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        self.error(
            f"[{error_type}] {error_message}",
            context or {}
        )
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        self.info(
            f"Performance: {operation}",
            {
                "duration": f"{duration:.3f}s",
                **(details or {})
            }
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events."""
        self.warning(
            f"Security event: {event_type}",
            details
        )


# Global logger instance
_logger_instance: Optional[PlaywrightLogger] = None


def get_logger(name: str = "playwright-automation") -> PlaywrightLogger:
    """Get logger instance."""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = PlaywrightLogger(name)
    
    return _logger_instance


def configure_logger(log_file: Optional[str] = None, level: int = logging.INFO):
    """Configure global logger."""
    logger = get_logger()
    
    if log_file:
        logger.add_file_handler(log_file, level)
    
    # Set logger level
    logger.logger.setLevel(level)


def log_automation_start(url: str, actions_count: int = 0, extract_count: int = 0):
    """Log automation start (convenience function)."""
    logger = get_logger()
    logger.log_automation_start(url, actions_count, extract_count)


def log_automation_end(success: bool, execution_time: float, data_count: int = 0):
    """Log automation end (convenience function)."""
    logger = get_logger()
    logger.log_automation_end(success, execution_time, data_count)


def log_action(action_type: str, selector: str, success: bool, duration: float = 0):
    """Log action execution (convenience function)."""
    logger = get_logger()
    logger.log_action(action_type, selector, success, duration)


def log_extraction(name: str, selector: str, result_count: int = 0):
    """Log data extraction (convenience function)."""
    logger = get_logger()
    logger.log_extraction(name, selector, result_count)


def log_error(error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
    """Log error with context (convenience function)."""
    logger = get_logger()
    logger.log_error(error_type, error_message, context)


def log_performance(operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
    """Log performance metrics (convenience function)."""
    logger = get_logger()
    logger.log_performance(operation, duration, details)


def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events (convenience function)."""
    logger = get_logger()
    logger.log_security_event(event_type, details)


# Context manager for logging operations
class LoggingContext:
    """Context manager for logging operations."""
    
    def __init__(self, operation: str, logger: Optional[PlaywrightLogger] = None):
        """Initialize logging context."""
        self.operation = operation
        self.logger = logger or get_logger()
        self.start_time = None
        self.success = False
    
    def __enter__(self):
        """Enter context."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.success = True
            self.logger.info(f"Completed {self.operation} successfully", {"duration": f"{duration:.3f}s"})
        else:
            self.logger.error(f"Failed {self.operation}", {"error": str(exc_val), "duration": f"{duration:.3f}s"})
        
        return False  # Don't suppress exceptions
    
    def log_progress(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log progress within context."""
        self.logger.info(f"{self.operation}: {message}", details or {}) 