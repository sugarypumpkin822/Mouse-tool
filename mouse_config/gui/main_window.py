"""
Main application window
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette

from ..core import MouseDetector, MouseController, SettingsManager
from ..advanced import (MacroRecorder, GameDetector, MouseTracker, BatteryMonitor, 
                         AdvancedRGBController, CloudSyncManager, AIOptimizer,
                         RobustConnectionManager, SmartCalibrator,
                         ThermalMonitor, PCOptimizer)
from ..utils.updater import UpdateManager
from ..utils.logger import get_logger
from .tabs import *
from .styles.modern import apply_modern_style


class MouseConfigGUI(QMainWindow):
    """Main application window with enhanced error handling"""
    
    # Signals
    device_connected = pyqtSignal(object)
    device_disconnected = pyqtSignal()
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Core components
        self.detector = MouseDetector()
        self.settings_manager = SettingsManager()
        self.controller: Optional[MouseController] = None
        
        # Advanced systems
        self.macro_recorder = MacroRecorder()
        self.game_detector = GameDetector()
        self.mouse_tracker = MouseTracker()
        self.battery_monitor = BatteryMonitor()
        self.rgb_controller = AdvancedRGBController()
        self.cloud_sync_manager = CloudSyncManager()
        self.ai_optimizer = AIOptimizer()
        self.update_manager = UpdateManager()
        
        self.robust_connection_manager = RobustConnectionManager()
        self.smart_calibrator = SmartCalibrator()
        self.thermal_monitor = ThermalMonitor()
        
        # Timers
        self.game_detection_timer = QTimer()
        self.game_detection_timer.timeout.connect(self.check_running_game)
        
        self.stats_update_timer = QTimer()
        self.stats_update_timer.timeout.connect(self.update_statistics)
        
        self.battery_update_timer = QTimer()
        self.battery_update_timer.timeout.connect(self.update_battery_status)
        
        # Initialize UI
        self.init_ui()
        self.apply_modern_style()
        self.load_settings()
        self.setup_timers()
        self.scan_for_mice()
        
        # Connect signals
        self.setup_signal_connections()
        
        self.logger.info("Mouse Config GUI initialized successfully")
    
    def init_ui(self):
        """Initialize the user interface"""
        try:
            self.setWindowTitle("🎮 Gaming Mouse Control Center - Pro Edition")
            self.setGeometry(100, 100, 1200, 900)
            self.setMinimumSize(1000, 700)
            
            # Set window icon (if available)
            # self.setWindowIcon(QIcon("icon.png"))
            
            # Create central widget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            layout.setSpacing(10)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Create header
            self.create_header(layout)
            
            # Create device selection section
            self.create_device_selection(layout)
            
            # Create tab widget
            self.create_tab_widget(layout)
            
            # Create status bar
            self.create_status_bar()
            
            # Create action buttons
            self.create_action_buttons(layout)
            
        except Exception as e:
            self.logger.error(f"Error initializing UI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize UI: {e}")
            sys.exit(1)
    
    def create_header(self, layout):
        """Create application header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #667eea, stop:1 #764ba2); 
                border-radius: 10px;
                margin: 5px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title = QLabel("🎮 GAMING MOUSE CONTROL CENTER")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Professional Edition - Advanced Mouse Configuration")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); padding: 2px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
    
    def create_device_selection(self, layout):
        """Create device selection section"""
        from .widgets.device_selector import DeviceSelector
        
        self.device_selector = DeviceSelector()
        self.device_selector.device_selected.connect(self.on_device_selected)
        self.device_selector.scan_clicked.connect(self.scan_for_mice)
        self.device_selector.debug_clicked.connect(self.show_debug_info)
        
        layout.addWidget(self.device_selector)
    
    def create_tab_widget(self, layout):
        """Create main tab widget"""
        from .tabs.tab_container import TabContainer
        
        self.tab_container = TabContainer()
        self.tab_container.settings_changed.connect(self.on_settings_changed)
        
        layout.addWidget(self.tab_container)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_label = QLabel("🔌 Ready")
        self.status_label.setStyleSheet("padding: 5px; font-weight: bold;")
        self.statusBar().addWidget(self.status_label)
        
        # Add permanent widgets
        self.device_status_label = QLabel("No device")
        self.statusBar().addPermanentWidget(self.device_status_label)
        
        self.library_status_label = QLabel("Libraries: Checking...")
        self.statusBar().addPermanentWidget(self.library_status_label)
    
    def create_action_buttons(self, layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        
        # Apply settings button
        apply_btn = QPushButton("✅ Apply All Settings")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_btn.clicked.connect(self.apply_all_settings)
        button_layout.addWidget(apply_btn)
        
        # Save profile button
        save_btn = QPushButton("💾 Save Profile")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        # Load profile button
        load_btn = QPushButton("📂 Load Profile")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white; 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        load_btn.clicked.connect(self.load_settings)
        button_layout.addWidget(load_btn)
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
    
    def apply_modern_style(self):
        """Apply modern styling to the application"""
        try:
            apply_modern_style(self)
        except Exception as e:
            self.logger.error(f"Error applying style: {e}")
    
    def setup_timers(self):
        """Setup periodic timers"""
        # Game detection (every 2 seconds)
        self.game_detection_timer.start(2000)
        
        # Statistics update (every 1 second)
        self.stats_update_timer.start(1000)
        
        # Battery update (every 30 seconds)
        self.battery_update_timer.start(30000)
        
        # Update library status
        self.update_library_status()
        
        # Check for updates on startup
        self.check_for_updates_on_startup()
    
    def setup_signal_connections(self):
        """Setup signal connections"""
        self.device_connected.connect(self.on_device_connected)
        self.device_disconnected.connect(self.on_device_disconnected)
        self.settings_changed.connect(self.on_settings_changed)
    
    def scan_for_mice(self):
        """Scan for gaming mice"""
        try:
            self.logger.info("Scanning for gaming mice...")
            self.status_label.setText("🔍 Scanning...")
            
            mice = self.detector.scan_devices()
            
            self.device_selector.update_device_list(mice)
            
            if mice:
                self.status_label.setText(f"✅ Found {len(mice)} mouse/mice")
                self.logger.info(f"Found {len(mice)} gaming mice")
                
                for mouse in mice:
                    self.logger.info(f"  - {mouse['vendor']} {mouse['product']}")
            else:
                self.status_label.setText("❌ No gaming mice detected")
                self.logger.warning("No gaming mice detected")
                
        except Exception as e:
            self.logger.error(f"Error scanning for mice: {e}")
            self.status_label.setText("❌ Scan failed")
            QMessageBox.warning(self, "Scan Error", f"Failed to scan for mice: {e}")
    
    def on_device_selected(self, mouse_info):
        """Handle device selection"""
        try:
            # Disconnect current device
            if self.controller:
                self.controller.disconnect()
                self.controller = None
                self.device_disconnected.emit()
            
            if not mouse_info:
                self.status_label.setText("⚠️ No device selected")
                return
            
            self.status_label.setText(f"🔌 Connecting to {mouse_info['product']}...")
            
            # Create controller and connect
            self.controller = MouseController(mouse_info)
            
            if self.controller.connect():
                self.device_connected.emit(self.controller)
                self.status_label.setText(f"✅ Connected: {mouse_info['product']}")
                self.logger.info(f"Connected to {mouse_info['product']} via {self.controller.connection_method}")
            else:
                self.status_label.setText("❌ Connection failed")
                self.logger.error(f"Failed to connect to {mouse_info['product']}: {self.controller.last_error}")
                self.show_connection_error()
                
        except Exception as e:
            self.logger.error(f"Error handling device selection: {e}")
            self.status_label.setText("❌ Selection error")
            QMessageBox.critical(self, "Error", f"Failed to select device: {e}")
    
    def on_device_connected(self, controller):
        """Handle successful device connection"""
        self.device_status_label.setText(f"🖱️ {controller.mouse_info['product']}")
        
        # Update tabs with device info
        self.tab_container.set_device_controller(controller)
        
        # Start battery monitoring for wireless devices
        if "wireless" in controller.mouse_info.get('product', '').lower():
            self.battery_monitor.start_monitoring()
    
    def on_device_disconnected(self):
        """Handle device disconnection"""
        self.device_status_label.setText("No device")
        self.tab_container.set_device_controller(None)
        self.battery_monitor.stop_monitoring()
    
    def apply_all_settings(self):
        """Apply all settings to the device"""
        if not self.controller or not self.controller.connected:
            QMessageBox.warning(self, "Warning", "No mouse connected!")
            return
        
        try:
            settings = self.settings_manager.get_settings()
            success_count = 0
            total_count = 0
            
            # Apply settings through tab container
            results = self.tab_container.apply_settings(self.controller)
            
            for setting_name, success in results.items():
                total_count += 1
                if success:
                    success_count += 1
                    self.logger.info(f"✅ {setting_name} applied successfully")
                else:
                    self.logger.warning(f"❌ {setting_name} failed to apply")
            
            # Show result
            if success_count == total_count:
                QMessageBox.information(self, "Success", "✅ All settings applied successfully!")
            elif success_count > 0:
                QMessageBox.warning(self, "Partial Success", f"⚠️ {success_count}/{total_count} settings applied")
            else:
                QMessageBox.critical(self, "Error", "❌ Failed to apply any settings")
                
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Get settings from tabs
            self.tab_container.update_settings(self.settings_manager.settings)
            
            if self.settings_manager.save_settings():
                self.logger.info("Settings saved successfully")
                QMessageBox.information(self, "Success", "Settings saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings")
                
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Load settings"""
        try:
            if self.settings_manager.load_settings():
                # Update tabs with loaded settings
                self.tab_container.load_settings(self.settings_manager.settings)
                self.logger.info("Settings loaded successfully")
            else:
                self.logger.info("No saved settings found, using defaults")
                
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.settings_manager.reset_to_defaults()
                self.tab_container.load_settings(self.settings_manager.settings)
                self.logger.info("Settings reset to defaults")
                QMessageBox.information(self, "Success", "Settings reset to defaults!")
                
            except Exception as e:
                self.logger.error(f"Error resetting settings: {e}")
                QMessageBox.critical(self, "Error", f"Failed to reset settings: {e}")
    
    def check_running_game(self):
        """Check for running games and switch profiles"""
        try:
            current_game = self.game_detector.get_current_game()
            
            if current_game and self.settings_manager.settings.auto_profile_switch:
                game_profile = f"{current_game.title()} Profile"
                
                if (hasattr(self, 'last_game') and self.last_game != current_game and 
                    game_profile in self.settings_manager.settings.profiles):
                    
                    self.logger.info(f"Detected game: {current_game} - switching profile")
                    self.settings_manager.load_profile(game_profile)
                    self.tab_container.load_settings(self.settings_manager.settings)
                
                self.last_game = current_game
                
        except Exception as e:
            self.logger.error(f"Error checking running game: {e}")
    
    def update_statistics(self):
        """Update statistics displays"""
        try:
            self.tab_container.update_statistics()
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def update_battery_status(self):
        """Update battery status"""
        try:
            if self.controller and self.controller.connected:
                battery_info = self.battery_monitor.get_battery_info()
                self.tab_container.update_battery_status(battery_info)
        except Exception as e:
            self.logger.error(f"Error updating battery status: {e}")
    
    def update_library_status(self):
        """Update library status in status bar"""
        try:
            from ..utils.config import get_library_status
            
            status = get_library_status()
            status_text = "Libraries: "
            
            if status.get('hidapi'):
                status_text += "HID✅ "
            else:
                status_text += "HID❌ "
            
            if status.get('pyusb'):
                status_text += "USB✅ "
            else:
                status_text += "USB❌ "
            
            if status.get('win32'):
                status_text += "Win32✅"
            else:
                status_text += "Win32❌"
            
            self.library_status_label.setText(status_text)
            
        except Exception as e:
            self.logger.error(f"Error updating library status: {e}")
    
    def show_debug_info(self):
        """Show debug information"""
        try:
            from .widgets.debug_dialog import DebugDialog
            
            debug_dialog = DebugDialog(self.detector, self.controller)
            debug_dialog.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing debug info: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show debug info: {e}")
    
    def show_connection_error(self):
        """Show connection error with troubleshooting"""
        error_msg = self.controller.last_error if self.controller else "Unknown error"
        
        troubleshooting = """
Troubleshooting Steps:
1. Close manufacturer software (Razer Synapse, Logitech G HUB, etc.)
2. Try unplugging and replugging the mouse
3. Run as Administrator
4. Install missing dependencies:
   - pip install hidapi pyusb pywin32 psutil pynput
5. Check if mouse is supported
        """.strip()
        
        QMessageBox.warning(self, "Connection Failed", 
                           f"Failed to connect: {error_msg}\n\n{troubleshooting}")
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.settings_changed.emit()
    
    def check_for_updates_on_startup(self):
        """Check for updates on startup if enabled"""
        try:
            from ..utils.config import get_config_path
            import json
            
            config_path = get_config_path()
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if config.get('auto_update', False):
                    # Start update check in background
                    self.update_checker = self.update_manager.check_for_updates()
                    self.update_checker.check_complete.connect(self.on_startup_update_check)
                    self.update_checker.start()
                    
        except Exception as e:
            self.logger.error(f"Error checking startup updates: {e}")
    
    def on_startup_update_check(self, success, message):
        """Handle startup update check"""
        if success and "Update available" in message:
            # Show notification about update
            self.status_label.setText("🔄 Update available!")
            self.logger.info("Update available on startup")
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            self.logger.info("Closing application...")
            
            # Cleanup
            if self.controller:
                self.controller.disconnect()
            
            if self.mouse_tracker.tracking:
                self.mouse_tracker.stop_tracking()
            
            if self.macro_recorder.recording:
                self.macro_recorder.stop_recording()
            
            if self.rgb_controller.animation_running:
                self.rgb_controller.stop_current_animation()
            
            self.battery_monitor.stop_monitoring()
            
            # Save settings
            self.settings_manager.save_settings()
            
            self.logger.info("Application closed successfully")
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            event.accept()  # Still close the application
