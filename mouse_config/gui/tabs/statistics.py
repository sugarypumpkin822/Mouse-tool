"""
Real-time statistics and tracking tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QProgressBar)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
from ..widgets.lcd_display import LCDDisplay


class StatisticsTab(QWidget):
    """Real-time statistics and tracking tab"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        self.mouse_tracker = None
        self.battery_monitor = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Tracking controls
        tracking_group = QGroupBox("📊 Mouse Tracking")
        tracking_layout = QVBoxLayout()
        
        control_layout = QHBoxLayout()
        self.start_tracking_btn = QPushButton("▶️ Start Tracking")
        self.start_tracking_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.start_tracking_btn.clicked.connect(self.start_tracking)
        control_layout.addWidget(self.start_tracking_btn)
        
        self.stop_tracking_btn = QPushButton("⏹️ Stop Tracking")
        self.stop_tracking_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.stop_tracking_btn.clicked.connect(self.stop_tracking)
        self.stop_tracking_btn.setEnabled(False)
        control_layout.addWidget(self.stop_tracking_btn)
        
        self.reset_stats_btn = QPushButton("🔄 Reset Stats")
        self.reset_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.reset_stats_btn.clicked.connect(self.reset_stats)
        control_layout.addWidget(self.reset_stats_btn)
        
        tracking_layout.addLayout(control_layout)
        tracking_group.setLayout(tracking_layout)
        layout.addWidget(tracking_group)
        
        # Statistics display
        stats_group = QGroupBox("📈 Real-time Statistics")
        stats_layout = QVBoxLayout()
        
        # Create LCD displays
        displays_layout = QHBoxLayout()
        
        # Distance display
        distance_widget = QWidget()
        distance_layout = QVBoxLayout(distance_widget)
        distance_layout.addWidget(QLabel("Total Distance (px)"))
        self.distance_lcd = LCDDisplay("Distance", "px")
        distance_layout.addWidget(self.distance_lcd)
        displays_layout.addWidget(distance_widget)
        
        # Clicks display
        clicks_widget = QWidget()
        clicks_layout = QVBoxLayout(clicks_widget)
        clicks_layout.addWidget(QLabel("Total Clicks"))
        self.clicks_lcd = LCDDisplay("Clicks", "")
        clicks_layout.addWidget(self.clicks_lcd)
        displays_layout.addWidget(clicks_widget)
        
        # Speed display
        speed_widget = QWidget()
        speed_layout = QVBoxLayout(speed_widget)
        speed_layout.addWidget(QLabel("Avg Speed (px/s)"))
        self.speed_lcd = LCDDisplay("Speed", "px/s")
        speed_layout.addWidget(self.speed_lcd)
        displays_layout.addWidget(speed_widget)
        
        # Max speed display
        max_speed_widget = QWidget()
        max_speed_layout = QVBoxLayout(max_speed_widget)
        max_speed_layout.addWidget(QLabel("Max Speed (px/s)"))
        self.max_speed_lcd = LCDDisplay("Max Speed", "px/s")
        max_speed_layout.addWidget(self.max_speed_lcd)
        displays_layout.addWidget(max_speed_widget)
        
        # CPM display
        cpm_widget = QWidget()
        cpm_layout = QVBoxLayout(cpm_widget)
        cpm_layout.addWidget(QLabel("Clicks/Min"))
        self.cpm_lcd = LCDDisplay("CPM", "")
        cpm_layout.addWidget(self.cpm_lcd)
        displays_layout.addWidget(cpm_widget)
        
        # Session time display
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.addWidget(QLabel("Session Time (s)"))
        self.session_time_lcd = LCDDisplay("Time", "s")
        time_layout.addWidget(self.session_time_lcd)
        displays_layout.addWidget(time_widget)
        
        stats_layout.addLayout(displays_layout)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Battery status
        battery_group = QGroupBox("🔋 Battery Status")
        battery_layout = QVBoxLayout()
        
        self.battery_level_label = QLabel("Battery Level: N/A")
        self.battery_level_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        battery_layout.addWidget(self.battery_level_label)
        
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        battery_layout.addWidget(self.battery_progress)
        
        self.estimated_time_label = QLabel("Estimated Time: N/A")
        battery_layout.addWidget(self.estimated_time_label)
        
        battery_group.setLayout(battery_layout)
        layout.addWidget(battery_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
        if controller:
            # Initialize tracking and monitoring
            try:
                from mouse_config.advanced import MouseTracker, BatteryMonitor
                self.mouse_tracker = MouseTracker()
                self.battery_monitor = BatteryMonitor()
            except ImportError:
                self.mouse_tracker = None
                self.battery_monitor = None
    
    def start_tracking(self):
        """Start mouse tracking"""
        try:
            if self.mouse_tracker:
                if self.mouse_tracker.start_tracking():
                    self.start_tracking_btn.setEnabled(False)
                    self.stop_tracking_btn.setEnabled(True)
                    self.logger.info("Started mouse tracking")
                else:
                    QMessageBox.warning(self, "Warning", "Failed to start tracking!")
            else:
                QMessageBox.warning(self, "Warning", "No mouse tracker available!")
                
        except Exception as e:
            self.logger.error(f"Error starting tracking: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start tracking: {e}")
    
    def stop_tracking(self):
        """Stop mouse tracking"""
        try:
            if self.mouse_tracker:
                stats = self.mouse_tracker.stop_tracking()
                self.start_tracking_btn.setEnabled(True)
                self.stop_tracking_btn.setEnabled(False)
                self.logger.info(f"Tracking stopped. Total clicks: {stats['click_count']}, Distance: {stats['total_distance']:.0f}px")
            else:
                QMessageBox.warning(self, "Warning", "No mouse tracker available!")
                
        except Exception as e:
            self.logger.error(f"Error stopping tracking: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop tracking: {e}")
    
    def reset_stats(self):
        """Reset tracking statistics"""
        try:
            if self.mouse_tracker:
                self.mouse_tracker.reset_stats()
                self.update_display()
                self.logger.info("Statistics reset")
            else:
                QMessageBox.warning(self, "Warning", "No mouse tracker available!")
                
        except Exception as e:
            self.logger.error(f"Error resetting stats: {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset stats: {e}")
    
    def update_display(self):
        """Update statistics displays"""
        try:
            if self.mouse_tracker:
                stats = self.mouse_tracker.get_current_stats()
                
                self.distance_lcd.display(int(stats['total_distance']))
                self.clicks_lcd.display(stats['click_count'])
                self.speed_lcd.display(stats['avg_speed'])
                self.max_speed_lcd.display(stats['max_speed'])
                self.cpm_lcd.display(stats['clicks_per_minute'])
                self.session_time_lcd.display(int(stats['session_time']))
                
        except Exception as e:
            self.logger.error(f"Error updating display: {e}")
    
    def update_battery_status(self, battery_info):
        """Update battery status displays"""
        try:
            if battery_info:
                level = battery_info.get('level', 0)
                charging = battery_info.get('charging', False)
                estimated_hours = battery_info.get('estimated_hours', 0)
                
                self.battery_level_label.setText(f"Battery Level: {level}%")
                self.battery_progress.setValue(level)
                
                if charging:
                    self.estimated_time_label.setText(f"Charging...")
                else:
                    self.estimated_time_label.setText(f"Estimated Time: {estimated_hours:.1f} hours")
                    
        except Exception as e:
            self.logger.error(f"Error updating battery status: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # Statistics tab doesn't have settings to load
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Statistics tab doesn't have settings to update
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Statistics tab doesn't apply device settings
        return {}
