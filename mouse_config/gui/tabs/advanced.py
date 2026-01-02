"""
Advanced settings tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QCheckBox, QGroupBox)
from PyQt6.QtCore import pyqtSignal

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class AdvancedTab(QWidget):
    """Advanced settings tab for LOD, angle snapping, etc."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Lift-off Distance
        lod_group = QGroupBox("📏 Lift-Off Distance (LOD)")
        lod_layout = QVBoxLayout()
        lod_layout.addWidget(QLabel("Adjust sensor height detection (1-3mm):"))
        self.lod_spinbox = QSpinBox()
        self.lod_spinbox.setRange(1, 3)
        self.lod_spinbox.setValue(2)
        self.lod_spinbox.setSuffix(" mm")
        self.lod_spinbox.valueChanged.connect(self.on_settings_changed)
        lod_layout.addWidget(self.lod_spinbox)
        lod_group.setLayout(lod_layout)
        layout.addWidget(lod_group)
        
        # Angle Snapping
        snap_group = QGroupBox("📐 Angle Snapping")
        snap_layout = QVBoxLayout()
        self.angle_snap_check = QCheckBox("Enable Angle Snapping (straightens diagonal movements)")
        self.angle_snap_check.stateChanged.connect(self.on_settings_changed)
        snap_layout.addWidget(self.angle_snap_check)
        snap_group.setLayout(snap_layout)
        layout.addWidget(snap_group)
        
        # Debounce
        debounce_group = QGroupBox("⏱️ Button Debounce Time")
        debounce_layout = QVBoxLayout()
        debounce_layout.addWidget(QLabel("Click response time (lower = faster, but may cause double-clicks):"))
        self.debounce_spinbox = QSpinBox()
        self.debounce_spinbox.setRange(2, 16)
        self.debounce_spinbox.setValue(4)
        self.debounce_spinbox.setSuffix(" ms")
        self.debounce_spinbox.valueChanged.connect(self.on_settings_changed)
        debounce_layout.addWidget(self.debounce_spinbox)
        debounce_group.setLayout(debounce_layout)
        layout.addWidget(debounce_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.settings_changed.emit()
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            self.lod_spinbox.setValue(settings.lod)
            self.angle_snap_check.setChecked(settings.angle_snapping)
            self.debounce_spinbox.setValue(settings.debounce_time)
        except Exception as e:
            self.logger.error(f"Error loading advanced settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        try:
            settings.lod = self.lod_spinbox.value()
            settings.angle_snapping = self.angle_snap_check.isChecked()
            settings.debounce_time = self.debounce_spinbox.value()
        except Exception as e:
            self.logger.error(f"Error updating advanced settings: {e}")
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            if controller and controller.connected:
                # Apply LOD
                if controller.set_lod(self.lod_spinbox.value()):
                    results['lod'] = True
                    self.logger.info(f"LOD set to {self.lod_spinbox.value()}mm")
                else:
                    results['lod'] = False
                    self.logger.error("Failed to set LOD")
                
                # Apply angle snapping
                if controller.set_angle_snapping(self.angle_snap_check.isChecked()):
                    results['angle_snapping'] = True
                    self.logger.info(f"Angle snapping set to {self.angle_snap_check.isChecked()}")
                else:
                    results['angle_snapping'] = False
                    self.logger.error("Failed to set angle snapping")
                
                # Apply debounce
                if controller.set_debounce(self.debounce_spinbox.value()):
                    results['debounce'] = True
                    self.logger.info(f"Debounce set to {self.debounce_spinbox.value()}ms")
                else:
                    results['debounce'] = False
                    self.logger.error("Failed to set debounce")
            else:
                results['lod'] = None
                results['angle_snapping'] = None
                results['debounce'] = None
                
        except Exception as e:
            self.logger.error(f"Error applying advanced settings: {e}")
            results['error'] = str(e)
        
        return results
