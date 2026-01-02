"""
Logging system for the mouse configuration tool
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path.home() / '.mouse_config' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f"mouse_config_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
    logging.getLogger('usb').setLevel(logging.WARNING)
    logging.getLogger('hid').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)
