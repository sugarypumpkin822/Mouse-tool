"""
Robust settings management with validation and recovery
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QSpinBox, QSlider,
                             QMessageBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
from ...core.settings import MouseSettings
from ...advanced.robust_connection import RobustConnectionManager


class RobustSettingsTab(QWidget):
    """Robust settings management with validation and recovery"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        self.connection_manager = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Connection Robustness Group
        robust_group = QGroupBox("🔧 Connection Robustness")
        robust_layout = QVBoxLayout()
        
        # Auto-reconnect
        self.auto_reconnect_check = QCheckBox("Enable automatic reconnection")
        self.auto_reconnect_check.setChecked(True)
        self.auto_reconnect_check.stateChanged.connect(self.on_settings_changed)
        robust_layout.addWidget(self.auto_reconnect_check)
        
        # Reconnection attempts
        reconnect_layout = QHBoxLayout()
        reconnect_layout.addWidget(QLabel("Max Reconnect Attempts:"))
        self.max_reconnect_spinbox = QSpinBox()
        self.max_reconnect_spinbox.setRange(1, 10)
        self.max_reconnect_spinbox.setValue(5)
        reconnect_layout.addWidget(self.max_reconnect_spinbox)
        robust_layout.addStretch()
        robust_layout.addWidget(QLabel("attempts"))
        robust_layout.addStretch()
        robust_layout.addLayout(reconnect_layout)
        
        robust_layout.addLayout(robust_layout)
        robust_group.setLayout(robust_layout)
        layout.addWidget(robust_group)
        
        # Error Recovery Group
        error_group = QGroupBox("🔧 Error Recovery")
        error_layout = QVBoxLayout()
        
        # Auto-retry on error
        self.auto_retry_check = QCheckBox("Auto-retry on errors")
        self.auto_retry_check.setChecked(True)
        self.auto_retry_check.stateChanged.connect(self.on_settings_changed)
        error_layout.addWidget(self.auto_retry_check)
        
        # Retry attempts
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("Max Retry Attempts:"))
        self.max_retry_spinbox = QSpinBox()
        self.max_retry_spinbox.setRange(1, 10)
        self.max_retry_spinbox.setValue(3)
        retry_layout.addWidget(self.max_retry_spinbox)
        retry_layout.addWidget(QLabel("attempts"))
        retry_layout.addStretch()
        retry_layout.addLayout(retry_layout)
        
        error_layout.addLayout(error_layout)
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        # Connection Methods Priority
        methods_group = QGroupBox("📡 Connection Methods Priority")
        methods_layout = QVBoxLayout()
        
        self.method_priorities = {
            'hid_standard': 1,
            'hid_path': 2,
            'hid_all_interfaces': 3,
            'usb_direct': 4,
            'usb_detach_driver': 5,
            'usb_raw': 6
        }
        
        for method, priority in self.method_priorities.items():
            method_layout.addWidget(QLabel(f"{priority}. {method.replace('_', ' ').title()}"))
            method_layout.addStretch()
        
        methods_layout.addLayout(methods_layout)
        methods_group.setLayout(methods_layout)
        layout.addWidget(methods_group)
        
        # Test Connection Button
        test_btn = QPushButton("🧪 Test Robustness")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        test_btn.clicked.connect(self.test_robustness)
        robust_layout.addWidget(test_btn)
        
        methods_layout.addLayout(methods_layout)
        methods_group.setLayout(methods_layout)
        layout.addWidget(methods_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
        
        # Create robust connection manager
        if controller:
            self.connection_manager = RobustConnectionManager()
            self.connection_manager.set_controller(controller)
            
            # Add state change callback
            self.connection_manager.add_state_change_callback(self.on_connection_state_change)
            self.connection_manager.add_error_callback(self.on_connection_error)
    
    def on_connection_state_change(self, state):
        """Handle connection state changes"""
        state_names = {
            'disconnected': 'Disconnected',
            'connecting': 'Connecting',
            'connected': 'Connected',
            'error': 'Error',
            'reconnecting': 'Reconnecting'
        }
        
        state_name = state_names.get(state.value, state.value)
        self.logger.info(f"Connection state changed to: {state_name}")
        
        # Update UI
        if hasattr(self, 'auto_reconnect_check'):
            if state == ConnectionState.DISCONNECTED and self.auto_reconnect_check.isChecked():
                self.auto_reconnect_check.setChecked(True)
            elif state == ConnectionState.CONNECTED:
                self.auto_reconnect_check.setChecked(False)
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Connection: {state_name}")
    
    def on_connection_error(self, error_message: str):
        """Handle connection errors"""
        self.logger.error(f"Connection error: {error_message}")
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Connection Error: {error_message}")
        
        # Show error dialog
        QMessageBox.warning(self, "Connection Error", f"Connection error occurred: {error_message}")
    
    def test_robustness(self):
        """Test robust connection features"""
        try:
            if not self.connection_manager:
                QMessageBox.warning(self, "Warning", "No controller available for testing")
                return
            
            # Get current status
            status = self.connection_manager.get_connection_status()
            
            # Test reconnection
            self.connection_manager.force_reconnect()
            
            # Show test results
            QMessageBox.information(
                self,
                "Robustness Test",
                f"Connection test completed.\n\nStatus: {status['state']}\nMethod: {status['method']}\nSuccess Rate: {status['metrics'].success_rate:.2f}\nReconnect Count: {status['metrics'].reconnect_count}\nUptime: {status['metrics'].uptime:.1f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Error testing robustness: {e}")
            QMessageBox.critical(self, "Test Failed", f"Robustness test failed: {e}")
    
    def on_settings_changed(self):
        """Handle settings changes"""
        try:
            # Update connection manager config
            if self.connection_manager:
                self.connection_manager.set_config(
                    auto_reconnect=self.auto_reconnect_check.isChecked(),
                    max_reconnect_attempts=self.max_reconnect_spinbox.value(),
                    max_retry_attempts=self.max_retry_spinbox.value()
                )
            
            self.settings_changed.emit()
            
        except Exception as e:
            self.logger.error(f"Error updating settings: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            # Load robust settings
            self.auto_reconnect_check.setChecked(settings.get('auto_reconnect', True))
            self.max_reconnect_spinbox.setValue(settings.get('max_reconnect_attempts', 5))
            self.max_retry_spinbox.setValue(settings.get('max_retry_attempts', 3))
            
        except Exception as e:
            self.logger.error(f"Error loading robust settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        try:
            # Save robust settings
            settings['auto_reconnect'] = self.auto_reconnect_check.isChecked()
            settings['max_reconnect_attempts'] = self.max_reconnect_spinbox.value()
            settings['max_retry_attempts'] = self.max_retry_spinbox.value()
            
        except Exception as e:
            self.logger.error(f"Error updating robust settings: {e}")
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            # Apply robust settings to connection manager
            if self.connection_manager:
                # The connection manager will handle robust connection automatically
                results['robust_connection'] = True
                
                # Force reconnection if needed
                if self.auto_reconnect_check.isChecked():
                    self.connection_manager.force_reconnect()
            
            self.logger.info("Robust settings applied")
            
        except Exception as e:
            self.logger.error(f"Error applying robust settings: {e}")
            results['robust_connection'] = False
        
        return results
