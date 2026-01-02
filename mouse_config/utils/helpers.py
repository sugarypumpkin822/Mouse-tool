"""
Helper functions and utilities
"""

import time
import threading
import platform
from typing import Any, Dict, List, Optional


def safe_execute(func, default=None, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error executing {func.__name__}: {e}")
        return default


def retry_operation(func, max_retries=3, delay=0.1, *args, **kwargs):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    info = {
        'os': f"{platform.system()} {platform.release()}",
        'python': platform.python_version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
    }
    
    # Add memory info if psutil is available
    try:
        import psutil
        memory = psutil.virtual_memory()
        info['memory'] = {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
        info['cpu_percent'] = psutil.cpu_percent(interval=1)
    except ImportError:
        pass
    
    return info


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def validate_dpi(dpi: int) -> bool:
    """Validate DPI value"""
    return 100 <= dpi <= 20000


def validate_poll_rate(rate: int) -> bool:
    """Validate polling rate value"""
    return rate in [125, 250, 500, 1000]


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color"""
    return f"#{r:02x}{g:02x}{b:02x}"


class ThreadSafeCounter:
    """Thread-safe counter for statistics"""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1):
        """Increment the counter"""
        with self._lock:
            self._value += amount
    
    def get(self) -> int:
        """Get current value"""
        with self._lock:
            return self._value
    
    def reset(self):
        """Reset counter to zero"""
        with self._lock:
            self._value = 0


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def can_proceed(self) -> bool:
        """Check if operation can proceed"""
        with self.lock:
            now = time.time()
            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False


def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of a file"""
    try:
        if file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            backup_path.write_bytes(file_path.read_bytes())
            return backup_path
    except Exception as e:
        print(f"Failed to create backup of {file_path}: {e}")
    return None
