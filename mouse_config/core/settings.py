"""
Settings and profile management system
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import get_logger
from ..utils.helpers import create_backup


class MouseSettings:
    """Comprehensive settings storage with validation"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Performance settings
        self.dpi = 800
        self.dpi_stages = [400, 800, 1600, 3200]
        self.polling_rate = 1000
        
        # Advanced settings
        self.lod = 2  # mm
        self.angle_snapping = False
        self.debounce_time = 4  # ms
        
        # RGB settings
        self.rgb_enabled = True
        self.rgb_color = "#00FF00"
        self.rgb_mode = "Static"
        self.rgb_brightness = 100
        self.rgb_speed = 50
        
        # Button mappings
        self.button_mappings = {}
        
        # Profiles
        self.profiles = {}
        self.active_profile = "Default"
        
        # Advanced features
        self.macro_enabled = True
        self.tracking_enabled = False
        self.game_detection_enabled = True
        self.auto_profile_switch = True
        
        # UI settings
        self.window_geometry = ""
        self.last_tab = 0
        self.theme = "modern"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            # Performance
            'dpi': self.dpi,
            'dpi_stages': self.dpi_stages,
            'polling_rate': self.polling_rate,
            
            # Advanced
            'lod': self.lod,
            'angle_snapping': self.angle_snapping,
            'debounce_time': self.debounce_time,
            
            # RGB
            'rgb_enabled': self.rgb_enabled,
            'rgb_color': self.rgb_color,
            'rgb_mode': self.rgb_mode,
            'rgb_brightness': self.rgb_brightness,
            'rgb_speed': self.rgb_speed,
            
            # Buttons
            'button_mappings': self.button_mappings,
            
            # Profiles
            'profiles': self.profiles,
            'active_profile': self.active_profile,
            
            # Features
            'macro_enabled': self.macro_enabled,
            'tracking_enabled': self.tracking_enabled,
            'game_detection_enabled': self.game_detection_enabled,
            'auto_profile_switch': self.auto_profile_switch,
            
            # UI
            'window_geometry': self.window_geometry,
            'last_tab': self.last_tab,
            'theme': self.theme,
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load settings from dictionary with validation"""
        try:
            # Performance settings
            self.dpi = self._validate_dpi(data.get('dpi', 800))
            self.dpi_stages = self._validate_dpi_stages(data.get('dpi_stages', [400, 800, 1600, 3200]))
            self.polling_rate = self._validate_poll_rate(data.get('polling_rate', 1000))
            
            # Advanced settings
            self.lod = self._validate_lod(data.get('lod', 2))
            self.angle_snapping = bool(data.get('angle_snapping', False))
            self.debounce_time = self._validate_debounce(data.get('debounce_time', 4))
            
            # RGB settings
            self.rgb_enabled = bool(data.get('rgb_enabled', True))
            self.rgb_color = self._validate_color(data.get('rgb_color', "#00FF00"))
            self.rgb_mode = self._validate_rgb_mode(data.get('rgb_mode', "Static"))
            self.rgb_brightness = self._validate_brightness(data.get('rgb_brightness', 100))
            self.rgb_speed = self._validate_speed(data.get('rgb_speed', 50))
            
            # Button mappings
            self.button_mappings = data.get('button_mappings', {})
            
            # Profiles
            self.profiles = data.get('profiles', {})
            self.active_profile = data.get('active_profile', "Default")
            
            # Features
            self.macro_enabled = bool(data.get('macro_enabled', True))
            self.tracking_enabled = bool(data.get('tracking_enabled', False))
            self.game_detection_enabled = bool(data.get('game_detection_enabled', True))
            self.auto_profile_switch = bool(data.get('auto_profile_switch', True))
            
            # UI settings
            self.window_geometry = data.get('window_geometry', "")
            self.last_tab = data.get('last_tab', 0)
            self.theme = data.get('theme', "modern")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            # Keep default values on error
    
    def _validate_dpi(self, value: int) -> int:
        """Validate DPI value"""
        return max(100, min(20000, value))
    
    def _validate_dpi_stages(self, stages: list) -> list:
        """Validate DPI stages"""
        validated = []
        for stage in stages:
            validated.append(self._validate_dpi(stage))
        return validated[:5]  # Max 5 stages
    
    def _validate_poll_rate(self, value: int) -> int:
        """Validate polling rate"""
        if value not in [125, 250, 500, 1000]:
            return 1000
        return value
    
    def _validate_lod(self, value: int) -> int:
        """Validate lift-off distance"""
        return max(1, min(3, value))
    
    def _validate_debounce(self, value: int) -> int:
        """Validate debounce time"""
        return max(2, min(16, value))
    
    def _validate_color(self, color: str) -> str:
        """Validate color hex code"""
        if not color.startswith('#'):
            color = '#' + color
        
        try:
            int(color.lstrip('#'), 16)
            return color
        except:
            return "#00FF00"
    
    def _validate_rgb_mode(self, mode: str) -> str:
        """Validate RGB mode"""
        valid_modes = ["Static", "Breathing", "Spectrum", "Wave", "Reactive"]
        return mode if mode in valid_modes else "Static"
    
    def _validate_brightness(self, value: int) -> int:
        """Validate brightness value"""
        return max(0, min(100, value))
    
    def _validate_speed(self, value: int) -> int:
        """Validate speed value"""
        return max(1, min(100, value))
    
    def save_profile(self, name: str) -> bool:
        """Save current settings as a profile"""
        try:
            if not name or name.strip() == "":
                return False
            
            profile_data = self.to_dict()
            profile_data.pop('profiles', None)  # Don't nest profiles
            profile_data.pop('active_profile', None)
            
            self.profiles[name] = profile_data
            self.logger.info(f"Saved profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving profile {name}: {e}")
            return False
    
    def load_profile(self, name: str) -> bool:
        """Load settings from a profile"""
        try:
            if name not in self.profiles:
                self.logger.error(f"Profile not found: {name}")
                return False
            
            profile_data = self.profiles[name].copy()
            profile_data['active_profile'] = name
            
            self.from_dict(profile_data)
            self.logger.info(f"Loaded profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading profile {name}: {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        try:
            if name in self.profiles:
                del self.profiles[name]
                self.logger.info(f"Deleted profile: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting profile {name}: {e}")
            return False
    
    def get_profile_list(self) -> list:
        """Get list of all profile names"""
        return list(self.profiles.keys())
    
    def export_settings(self, file_path: Path) -> bool:
        """Export settings to file"""
        try:
            # Create backup
            backup_path = create_backup(file_path)
            
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            
            self.logger.info(f"Settings exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.from_dict(data)
            self.logger.info(f"Settings imported from {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False


class SettingsManager:
    """Manage settings persistence"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.logger = get_logger(__name__)
        self.config_file = config_file or (Path.home() / '.mouse_config' / 'config.json')
        self.settings = MouseSettings()
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self) -> bool:
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self.settings.from_dict(data)
                self.logger.info("Settings loaded successfully")
                return True
            else:
                self.logger.info("No settings file found, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            # Create backup
            create_backup(self.config_file)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings.to_dict(), f, indent=4)
            
            self.logger.info("Settings saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    def get_settings(self) -> MouseSettings:
        """Get current settings"""
        return self.settings
    
    def reset_to_defaults(self) -> bool:
        """Reset settings to defaults"""
        try:
            self.settings = MouseSettings()
            return self.save_settings()
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            return False
