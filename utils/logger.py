"""
Logging configuration for the Semantic Search Engine
"""
import logging
import sys
from pathlib import Path
from .config import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)
    
    # File handler (ensure log directory exists)
    log_file_path = Path(LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Create default logger
logger = setup_logger(__name__)
