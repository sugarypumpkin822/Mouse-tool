"""
Real-time mouse movement tracking and statistics
"""

import time
import threading
import math
from typing import Dict, Any, Optional, List
from ..utils.logger import get_logger
from ..utils.helpers import ThreadSafeCounter


class MouseTracker:
    """Real-time mouse movement tracking and statistics"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.tracking = False
        self.stats = {
            'total_distance': 0.0,
            'click_count': 0,
            'avg_speed': 0.0,
            'max_speed': 0.0,
            'session_time': 0.0,
            'clicks_per_minute': 0.0,
            'total_clicks': 0,
            'right_clicks': 0,
            'middle_clicks': 0,
            'scroll_distance': 0.0,
            'acceleration_events': 0
        }
        self.last_pos: Optional[tuple] = None
        self.last_time: Optional[float] = None
        self.start_time: Optional[float] = None
        self.click_times: List[float] = []
        self.listener: Optional[Any] = None
        self.stats_lock = threading.Lock()
        
        # Performance counters
        self.distance_counter = ThreadSafeCounter()
        self.click_counter = ThreadSafeCounter()
        
    def start_tracking(self) -> bool:
        """Start tracking mouse movement"""
        if self.tracking:
            self.logger.warning("Already tracking")
            return False
        
        try:
            # Try to import pynput
            try:
                from pynput import mouse
            except ImportError:
                self.logger.error("pynput not available for mouse tracking")
                return False
            
            self.tracking = True
            self.start_time = time.time()
            self.last_time = self.start_time
            self.click_times = []
            
            # Reset stats
            with self.stats_lock:
                for key in self.stats:
                    self.stats[key] = 0.0 if isinstance(self.stats[key], float) else 0
            
            def on_move(x, y):
                if self.tracking:
                    current_time = time.time()
                    
                    with self.stats_lock:
                        if self.last_pos:
                            # Calculate distance
                            dx = x - self.last_pos[0]
                            dy = y - self.last_pos[1]
                            distance = math.sqrt(dx**2 + dy**2)
                            
                            # Calculate time difference
                            time_diff = current_time - self.last_time
                            
                            if time_diff > 0:
                                # Calculate speed
                                speed = distance / time_diff
                                
                                # Update statistics
                                self.stats['total_distance'] += distance
                                self.stats['max_speed'] = max(self.stats['max_speed'], speed)
                                self.distance_counter.increment(int(distance))
                        
                        self.last_pos = (x, y)
                        self.last_time = current_time
            
            def on_click(x, y, button, pressed):
                if self.tracking and pressed:
                    current_time = time.time()
                    
                    with self.stats_lock:
                        self.click_times.append(current_time)
                        self.stats['click_count'] += 1
                        self.click_counter.increment()
                        
                        # Track click types
                        if 'Button.left' in str(button):
                            self.stats['total_clicks'] += 1
                        elif 'Button.right' in str(button):
                            self.stats['right_clicks'] += 1
                        elif 'Button.middle' in str(button):
                            self.stats['middle_clicks'] += 1
            
            def on_scroll(x, y, dx, dy):
                if self.tracking:
                    with self.stats_lock:
                        # Track scroll distance
                        self.stats['scroll_distance'] += abs(dy)
            
            self.listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
            self.listener.start()
            
            self.logger.info("Started mouse tracking")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting tracking: {e}")
            self.tracking = False
            return False
    
    def stop_tracking(self) -> Dict[str, Any]:
        """Stop tracking and calculate final stats"""
        if not self.tracking:
            self.logger.warning("Not currently tracking")
            return self.stats.copy()
        
        try:
            self.tracking = False
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            with self.stats_lock:
                if self.start_time:
                    self.stats['session_time'] = time.time() - self.start_time
                    
                    # Calculate average speed and clicks per minute
                    if self.stats['session_time'] > 0:
                        self.stats['avg_speed'] = self.stats['total_distance'] / self.stats['session_time']
                        
                        # Calculate clicks per minute
                        current_time = time.time()
                        recent_clicks = [t for t in self.click_times if current_time - t < 60]
                        self.stats['clicks_per_minute'] = len(recent_clicks)
                
                final_stats = self.stats.copy()
            
            self.logger.info(f"Tracking stopped. Session time: {final_stats['session_time']:.1f}s, "
                           f"Distance: {final_stats['total_distance']:.0f}px, "
                           f"Clicks: {final_stats['click_count']}")
            
            return final_stats
            
        except Exception as e:
            self.logger.error(f"Error stopping tracking: {e}")
            return self.stats.copy()
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current tracking statistics"""
        with self.stats_lock:
            if self.tracking and self.start_time:
                # Update live statistics
                current_time = time.time()
                session_time = current_time - self.start_time
                
                if session_time > 0:
                    self.stats['session_time'] = session_time
                    self.stats['avg_speed'] = self.stats['total_distance'] / session_time
                    
                    # Calculate clicks per minute
                    recent_clicks = [t for t in self.click_times if current_time - t < 60]
                    self.stats['clicks_per_minute'] = len(recent_clicks)
            
            return self.stats.copy()
    
    def reset_stats(self):
        """Reset tracking statistics"""
        with self.stats_lock:
            for key in self.stats:
                self.stats[key] = 0.0 if isinstance(self.stats[key], float) else 0
            
            self.last_pos = None
            self.last_time = None
            self.start_time = None
            self.click_times = []
        
        self.distance_counter.reset()
        self.click_counter.reset()
        
        self.logger.info("Statistics reset")
    
    def get_movement_analysis(self) -> Dict[str, Any]:
        """Get detailed movement analysis"""
        with self.stats_lock:
            if self.stats['session_time'] == 0:
                return {'error': 'No tracking data available'}
            
            analysis = {
                'session_duration': self.stats['session_time'],
                'total_distance': self.stats['total_distance'],
                'average_speed': self.stats['avg_speed'],
                'max_speed': self.stats['max_speed'],
                'total_clicks': self.stats['click_count'],
                'clicks_per_minute': self.stats['clicks_per_minute'],
                'click_distribution': {
                    'left': self.stats['total_clicks'],
                    'right': self.stats['right_clicks'],
                    'middle': self.stats['middle_clicks']
                },
                'scroll_distance': self.stats['scroll_distance']
            }
            
            # Calculate efficiency metrics
            if self.stats['total_distance'] > 0:
                analysis['clicks_per_meter'] = (self.stats['click_count'] / (self.stats['total_distance'] / 1000))
                analysis['pixels_per_second'] = self.stats['total_distance'] / self.stats['session_time']
            
            # Classify user activity
            if self.stats['clicks_per_minute'] > 60:
                activity_level = 'High'
            elif self.stats['clicks_per_minute'] > 30:
                activity_level = 'Medium'
            else:
                activity_level = 'Low'
            
            analysis['activity_level'] = activity_level
            
            return analysis
    
    def export_tracking_data(self, file_path: str) -> bool:
        """Export tracking data to file"""
        try:
            import json
            
            data = {
                'timestamp': time.time(),
                'stats': self.get_current_stats(),
                'analysis': self.get_movement_analysis(),
                'click_times': self.click_times
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Tracking data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting tracking data: {e}")
            return False
    
    def get_heatmap_data(self, grid_size: int = 50) -> List[List[int]]:
        """Generate heatmap data for mouse positions"""
        # This would require storing position history
        # For now, return empty grid
        return [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    
    def is_tracking(self) -> bool:
        """Check if currently tracking"""
        return self.tracking
    
    def get_session_summary(self) -> str:
        """Get a human-readable session summary"""
        stats = self.get_current_stats()
        
        if stats['session_time'] == 0:
            return "No tracking session active"
        
        summary = f"""
Session Summary:
- Duration: {stats['session_time']:.1f} seconds
- Total Distance: {stats['total_distance']:.0f} pixels
- Average Speed: {stats['avg_speed']:.1f} px/s
- Max Speed: {stats['max_speed']:.1f} px/s
- Total Clicks: {stats['click_count']}
- Clicks/Minute: {stats['clicks_per_minute']:.1f}
- Scroll Distance: {stats['scroll_distance']:.0f}
        """.strip()
        
        return summary
