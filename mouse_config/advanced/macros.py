"""
Advanced macro recording and playback system
"""

import time
import threading
from typing import List, Dict, Any, Optional
from ..utils.logger import get_logger
from ..utils.helpers import ThreadSafeCounter


class MacroRecorder:
    """Advanced macro recording and playback system"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.recording = False
        self.recorded_actions: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.listener: Optional[Any] = None
        self.recording_lock = threading.Lock()
        
        # Statistics
        self.total_macros = ThreadSafeCounter()
        self.total_actions = ThreadSafeCounter()
    
    def start_recording(self) -> bool:
        """Start recording mouse and keyboard actions"""
        with self.recording_lock:
            if self.recording:
                self.logger.warning("Already recording")
                return False
            
            try:
                self.recording = True
                self.recorded_actions = []
                self.start_time = time.time()
                
                # Try to import pynput
                try:
                    from pynput import mouse
                except ImportError:
                    self.logger.error("pynput not available for macro recording")
                    self.recording = False
                    return False
                
                def on_click(x, y, button, pressed):
                    if self.recording:
                        action_time = time.time() - self.start_time
                        self.recorded_actions.append({
                            'type': 'mouse_click',
                            'x': x, 'y': y,
                            'button': str(button),
                            'pressed': pressed,
                            'time': action_time
                        })
                
                def on_move(x, y):
                    if self.recording:
                        action_time = time.time() - self.start_time
                        self.recorded_actions.append({
                            'type': 'mouse_move',
                            'x': x, 'y': y,
                            'time': action_time
                        })
                
                def on_scroll(x, y, dx, dy):
                    if self.recording:
                        action_time = time.time() - self.start_time
                        self.recorded_actions.append({
                            'type': 'mouse_scroll',
                            'x': x, 'y': y,
                            'dx': dx, 'dy': dy,
                            'time': action_time
                        })
                
                self.listener = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)
                self.listener.start()
                
                self.logger.info("Started macro recording")
                return True
                
            except Exception as e:
                self.logger.error(f"Error starting recording: {e}")
                self.recording = False
                return False
    
    def stop_recording(self) -> List[Dict[str, Any]]:
        """Stop recording and return macro data"""
        with self.recording_lock:
            if not self.recording:
                self.logger.warning("Not currently recording")
                return []
            
            try:
                self.recording = False
                if self.listener:
                    self.listener.stop()
                    self.listener = None
                
                # Update statistics
                self.total_macros.increment()
                self.total_actions.increment(len(self.recorded_actions))
                
                self.logger.info(f"Stopped recording. Captured {len(self.recorded_actions)} actions")
                return self.recorded_actions.copy()
                
            except Exception as e:
                self.logger.error(f"Error stopping recording: {e}")
                return []
    
    def play_macro(self, actions: List[Dict[str, Any]], repeat_count: int = 1, delay_factor: float = 1.0) -> bool:
        """Play back recorded macro with error handling"""
        if not actions:
            self.logger.warning("No actions to play")
            return False
        
        try:
            # Try to import required modules
            try:
                import win32api
                import win32con
            except ImportError:
                self.logger.error("win32api not available for macro playback")
                return False
            
            self.logger.info(f"Playing macro with {len(actions)} actions, {repeat_count} repeats")
            
            for repeat in range(repeat_count):
                last_time = 0
                
                for action in actions:
                    # Calculate delay from timing
                    if last_time > 0:
                        delay = (action['time'] - last_time) * delay_factor
                        if delay > 0:
                            time.sleep(delay)
                    
                    last_time = action['time']
                    
                    # Execute action
                    try:
                        if action['type'] == 'mouse_click':
                            if action['pressed']:
                                win32api.SetCursorPos((action['x'], action['y']))
                                if 'Button.left' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                elif 'Button.right' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                                elif 'Button.middle' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
                            else:
                                if 'Button.left' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                elif 'Button.right' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                                elif 'Button.middle' in action['button']:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
                        
                        elif action['type'] == 'mouse_move':
                            win32api.SetCursorPos((action['x'], action['y']))
                        
                        elif action['type'] == 'mouse_scroll':
                            win32api.SetCursorPos((action['x'], action['y']))
                            scroll_data = action['dy'] * 120  # Windows scroll units
                            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, scroll_data, 0)
                    
                    except Exception as e:
                        self.logger.error(f"Error executing action: {e}")
                        continue
            
            self.logger.info("Macro playback completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing macro: {e}")
            return False
    
    def save_macro(self, actions: List[Dict[str, Any]], name: str, file_path: Optional[str] = None) -> bool:
        """Save macro to file"""
        try:
            import json
            
            if not file_path:
                from pathlib import Path
                macro_dir = Path.home() / '.mouse_config' / 'macros'
                macro_dir.mkdir(parents=True, exist_ok=True)
                file_path = macro_dir / f"{name}.json"
            
            macro_data = {
                'name': name,
                'created': time.time(),
                'actions': actions,
                'duration': actions[-1]['time'] if actions else 0,
                'action_count': len(actions)
            }
            
            with open(file_path, 'w') as f:
                json.dump(macro_data, f, indent=2)
            
            self.logger.info(f"Macro saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving macro: {e}")
            return False
    
    def load_macro(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Load macro from file"""
        try:
            import json
            
            with open(file_path, 'r') as f:
                macro_data = json.load(f)
            
            actions = macro_data.get('actions', [])
            self.logger.info(f"Loaded macro with {len(actions)} actions from {file_path}")
            return actions
            
        except Exception as e:
            self.logger.error(f"Error loading macro: {e}")
            return None
    
    def get_macro_list(self) -> List[str]:
        """Get list of saved macros"""
        try:
            from pathlib import Path
            
            macro_dir = Path.home() / '.mouse_config' / 'macros'
            if not macro_dir.exists():
                return []
            
            macros = []
            for file_path in macro_dir.glob('*.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    macros.append(data.get('name', file_path.stem))
                except:
                    continue
            
            return sorted(macros)
            
        except Exception as e:
            self.logger.error(f"Error getting macro list: {e}")
            return []
    
    def delete_macro(self, name: str) -> bool:
        """Delete saved macro"""
        try:
            from pathlib import Path
            
            macro_dir = Path.home() / '.mouse_config' / 'macros'
            file_path = macro_dir / f"{name}.json"
            
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Deleted macro: {name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting macro: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """Get macro recording statistics"""
        return {
            'total_macros': self.total_macros.get(),
            'total_actions': self.total_actions.get(),
            'is_recording': self.recording,
            'current_actions': len(self.recorded_actions)
        }
    
    def optimize_macro(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize macro by removing redundant actions"""
        if not actions:
            return actions
        
        optimized = []
        last_move = None
        
        for action in actions:
            if action['type'] == 'mouse_move':
                # Skip redundant moves
                if last_move and abs(action['x'] - last_move['x']) < 2 and abs(action['y'] - last_move['y']) < 2:
                    continue
                last_move = action
            
            # Remove actions with very short delays
            if optimized and action['time'] - optimized[-1]['time'] < 0.01:
                continue
            
            optimized.append(action)
        
        self.logger.info(f"Optimized macro: {len(actions)} -> {len(optimized)} actions")
        return optimized
