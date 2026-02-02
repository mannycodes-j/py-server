"""
Logging Configuration
Production-ready logging setup with structured logging support.
"""

import sys
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from .config import settings


# ============== LOG FORMATTERS ==============

class ColoredFormatter(logging.Formatter):
    """Colored console output for development."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatted output for production."""
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data
        
        return json.dumps(log_data)


# ============== LOGGING SETUP ==============

def setup_logging(
    log_level: str = None,
    log_file: Optional[str] = None,
    json_format: bool = None,
) -> logging.Logger:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_format: Use JSON formatting (default: True in production)
    
    Returns:
        Configured root logger
    """
    level = log_level or settings.LOG_LEVEL
    use_json = json_format if json_format is not None else settings.is_production
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# ============== APPLICATION LOGGER ==============

class AppLogger:
    """
    Application-specific logger with context support.
    
    Usage:
        logger = AppLogger("my_module")
        logger.info("User logged in", user_id=123)
        logger.error("Database error", exc_info=True, query="SELECT...")
    """
    
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
    
    def _log(
        self,
        level: int,
        message: str,
        exc_info: bool = False,
        **kwargs
    ):
        """Internal log method with extra data support."""
        extra = {"extra_data": kwargs} if kwargs else {}
        self._logger.log(level, message, exc_info=exc_info, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)


# Initialize logging on import (can be reconfigured later)
_logger = setup_logging()
