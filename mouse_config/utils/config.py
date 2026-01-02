"""
Configuration management and dependency checking
"""

import sys
import platform
import psutil
from pathlib import Path


def get_config_path() -> Path:
    """Get the configuration file path"""
    return Path.home() / '.mouse_config' / 'config.json'


def get_system_info() -> dict:
    """Get system information"""
    try:
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free
            }
        }
        return info
    except Exception as e:
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu': platform.processor(),
            'cpu_count': 0,
            'memory': {'total': 0, 'available': 0, 'percent': 0},
            'disk': {'total': 0, 'used': 0, 'free': 0},
            'error': str(e)
        }


def check_dependencies() -> list:
    """Check if all required dependencies are available"""
    missing = []
    
    # Check core dependencies
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    try:
        import hid
    except ImportError:
        missing.append("hidapi")
    
    try:
        import usb.core
    except ImportError:
        missing.append("pyusb")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing.append("beautifulsoup4")
    
    # Check Windows-specific dependencies
    if sys.platform == "win32":
        try:
            import win32gui
        except ImportError:
            missing.append("pywin32")
        
        try:
            import psutil
        except ImportError:
            missing.append("psutil")
        
        try:
            import pynput
        except ImportError:
            missing.append("pynput")
    
    return missing


def get_library_status() -> dict:
    """Get status of all libraries"""
    status = {}
    
    # Check HID API
    try:
        import hid
        status['hidapi'] = True
    except ImportError:
        status['hidapi'] = False
    
    # Check USB API
    try:
        import usb.core
        status['pyusb'] = True
    except ImportError:
        status['pyusb'] = False
    
    # Check Windows API
    try:
        import win32gui
        import psutil
        import pynput
        status['win32'] = True
    except ImportError:
        status['win32'] = False
    
    return status
