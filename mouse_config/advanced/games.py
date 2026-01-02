"""
Game detection and automatic profile switching
"""

import time
from typing import Optional, Dict, List, Set
from ..utils.logger import get_logger


class GameDetector:
    """Detect running games and applications for profile switching"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Extended game database
        self.game_processes = {
            # FPS Games
            'valorant': {
                'processes': ['VALORANT.exe'],
                'category': 'FPS',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'csgo': {
                'processes': ['csgo.exe'],
                'category': 'FPS', 
                'recommended_dpi': 400,
                'recommended_poll_rate': 1000
            },
            'overwatch': {
                'processes': ['Overwatch.exe'],
                'category': 'FPS',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'fortnite': {
                'processes': ['FortniteClient-Win64-Shipping.exe'],
                'category': 'FPS',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 1000
            },
            'apex': {
                'processes': ['r5apex.exe'],
                'category': 'FPS',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'cod': {
                'processes': ['ModernWarfare.exe', 'mw2.exe', 'mw3.exe'],
                'category': 'FPS',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'rainbow6': {
                'processes': ['RainbowSix.exe'],
                'category': 'FPS',
                'recommended_dpi': 400,
                'recommended_poll_rate': 1000
            },
            
            # MOBA Games
            'lol': {
                'processes': ['League of Legends.exe'],
                'category': 'MOBA',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'dota': {
                'processes': ['dota2.exe'],
                'category': 'MOBA',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'heroes': {
                'processes': ['HeroesOfTheStorm.exe'],
                'category': 'MOBA',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            
            # Sandbox/Survival
            'minecraft': {
                'processes': ['Minecraft.exe', 'MinecraftLauncher.exe'],
                'category': 'Sandbox',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 1000
            },
            'rust': {
                'processes': ['Rust.exe'],
                'category': 'Survival',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'valheim': {
                'processes': ['Valheim.exe'],
                'category': 'Survival',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            
            # Strategy Games
            'starcraft': {
                'processes': ['SC2.exe'],
                'category': 'Strategy',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 1000
            },
            'ageofempires': {
                'processes': ['AoE4.exe'],
                'category': 'Strategy',
                'recommended_dpi': 800,
                'recommended_poll_rate': 500
            },
            
            # Battle Royale
            'pubg': {
                'processes': ['TslGame.exe'],
                'category': 'Battle Royale',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            'warzone': {
                'processes': ['cod.exe'],
                'category': 'Battle Royale',
                'recommended_dpi': 800,
                'recommended_poll_rate': 1000
            },
            
            # Creative/Productivity
            'photoshop': {
                'processes': ['Photoshop.exe'],
                'category': 'Creative',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 500
            },
            'illustrator': {
                'processes': ['Illustrator.exe'],
                'category': 'Creative',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 500
            },
            'blender': {
                'processes': ['blender.exe'],
                'category': 'Creative',
                'recommended_dpi': 800,
                'recommended_poll_rate': 500
            },
            
            # Browsers
            'chrome': {
                'processes': ['chrome.exe'],
                'category': 'Browser',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 500
            },
            'firefox': {
                'processes': ['firefox.exe'],
                'category': 'Browser',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 500
            },
            'edge': {
                'processes': ['msedge.exe'],
                'category': 'Browser',
                'recommended_dpi': 1200,
                'recommended_poll_rate': 500
            },
        }
        
        # Custom game profiles
        self.custom_profiles: Dict[str, Dict] = {}
        
        # Detection cache
        self.last_detection: Optional[str] = None
        self.last_detection_time: float = 0
        self.detection_cache_duration: float = 2.0  # Cache for 2 seconds
    
    def get_current_game(self) -> Optional[str]:
        """Detect currently running game/application"""
        current_time = time.time()
        
        # Use cache to avoid excessive polling
        if (self.last_detection and 
            current_time - self.last_detection_time < self.detection_cache_duration):
            return self.last_detection
        
        try:
            # Check if Windows API is available
            try:
                import win32gui
                import win32process
                import psutil
            except ImportError:
                self.logger.warning("Windows API not available for game detection")
                return None
            
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process information
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                window_title = win32gui.GetWindowText(hwnd)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
            
            # Check against game database
            detected_game = self._match_process(process_name, window_title)
            
            # Update cache
            self.last_detection = detected_game
            self.last_detection_time = current_time
            
            if detected_game:
                self.logger.debug(f"Detected: {detected_game} ({process_name})")
            
            return detected_game
            
        except Exception as e:
            self.logger.error(f"Error detecting game: {e}")
            return None
    
    def _match_process(self, process_name: str, window_title: str) -> Optional[str]:
        """Match process against game database"""
        process_name_lower = process_name.lower()
        window_title_lower = window_title.lower()
        
        for game_name, game_info in self.game_processes.items():
            for process in game_info['processes']:
                if process.lower() in process_name_lower:
                    return game_name
        
        # Check custom profiles
        for profile_name, profile_info in self.custom_profiles.items():
            for process in profile_info.get('processes', []):
                if process.lower() in process_name_lower:
                    return profile_name
        
        # Check window title for additional matches
        title_keywords = {
            'valorant': ['valorant'],
            'csgo': ['counter-strike', 'csgo'],
            'lol': ['league of legends'],
            'dota': ['dota 2'],
            'minecraft': ['minecraft'],
            'rust': ['rust'],
            'fortnite': ['fortnite'],
            'apex': ['apex legends'],
            'overwatch': ['overwatch'],
        }
        
        for game_name, keywords in title_keywords.items():
            if any(keyword in window_title_lower for keyword in keywords):
                return game_name
        
        return None
    
    def get_game_info(self, game_name: str) -> Optional[Dict]:
        """Get information about a specific game"""
        if game_name in self.game_processes:
            return self.game_processes[game_name]
        elif game_name in self.custom_profiles:
            return self.custom_profiles[game_name]
        return None
    
    def add_custom_profile(self, name: str, processes: List[str], category: str, 
                         dpi: int = 800, poll_rate: int = 1000) -> bool:
        """Add a custom game profile"""
        try:
            self.custom_profiles[name] = {
                'processes': processes,
                'category': category,
                'recommended_dpi': dpi,
                'recommended_poll_rate': poll_rate,
                'custom': True
            }
            self.logger.info(f"Added custom profile: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding custom profile: {e}")
            return False
    
    def remove_custom_profile(self, name: str) -> bool:
        """Remove a custom game profile"""
        try:
            if name in self.custom_profiles:
                del self.custom_profiles[name]
                self.logger.info(f"Removed custom profile: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing custom profile: {e}")
            return False
    
    def get_supported_games(self) -> List[str]:
        """Get list of all supported games"""
        return list(self.game_processes.keys()) + list(self.custom_profiles.keys())
    
    def get_games_by_category(self, category: str) -> List[str]:
        """Get games filtered by category"""
        games = []
        
        for game_name, game_info in self.game_processes.items():
            if game_info.get('category') == category:
                games.append(game_name)
        
        for profile_name, profile_info in self.custom_profiles.items():
            if profile_info.get('category') == category:
                games.append(profile_name)
        
        return games
    
    def get_categories(self) -> List[str]:
        """Get all game categories"""
        categories = set()
        
        for game_info in self.game_processes.values():
            categories.add(game_info.get('category', 'Unknown'))
        
        for profile_info in self.custom_profiles.values():
            categories.add(profile_info.get('category', 'Unknown'))
        
        return sorted(list(categories))
    
    def get_recommended_settings(self, game_name: str) -> Optional[Dict]:
        """Get recommended settings for a specific game"""
        game_info = self.get_game_info(game_name)
        if not game_info:
            return None
        
        return {
            'dpi': game_info.get('recommended_dpi', 800),
            'poll_rate': game_info.get('recommended_poll_rate', 1000),
            'category': game_info.get('category', 'Unknown')
        }
    
    def export_profiles(self, file_path: str) -> bool:
        """Export custom profiles to file"""
        try:
            import json
            
            data = {
                'custom_profiles': self.custom_profiles,
                'export_time': time.time()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Profiles exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting profiles: {e}")
            return False
    
    def import_profiles(self, file_path: str) -> bool:
        """Import custom profiles from file"""
        try:
            import json
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.custom_profiles.update(data.get('custom_profiles', {}))
            self.logger.info(f"Profiles imported from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing profiles: {e}")
            return False
    
    def get_detection_statistics(self) -> Dict:
        """Get game detection statistics"""
        return {
            'total_games': len(self.game_processes),
            'custom_profiles': len(self.custom_profiles),
            'categories': len(self.get_categories()),
            'last_detection': self.last_detection,
            'cache_duration': self.detection_cache_duration
        }
