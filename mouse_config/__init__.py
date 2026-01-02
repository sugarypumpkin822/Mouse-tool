"""
🎮 Gaming Mouse Control Center - Pro Edition

A comprehensive, professional-grade mouse configuration tool with advanced features
for gaming mice from multiple manufacturers.
"""

__version__ = "2.0.0"
__author__ = "Mouse Control Center Team"
__description__ = "Advanced Gaming Mouse Configuration Tool"

# Import main components
from .core import *
from .advanced import *
from .gui import *
from .utils import *

# Export main classes
__all__ = [
    'MouseConfigGUI',
    'MouseController',
    'MouseDetector',
    'MacroRecorder',
    'GameDetector',
    'MouseTracker',
    'BatteryMonitor',
    'AdvancedRGBController',
]
