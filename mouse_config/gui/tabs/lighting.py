"""
RGB lighting settings tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QCheckBox, QComboBox, QSlider, QGroupBox)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
from ..widgets.color_picker import ColorPickerWidget


class LightingTab(QWidget):
    """RGB lighting settings tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        rgb_group = QGroupBox("💡 RGB Lighting Control")
        rgb_layout = QVBoxLayout()
        
        # Enable toggle
        self.rgb_enabled_check = QCheckBox("Enable RGB Lighting")
        self.rgb_enabled_check.setChecked(True)
        self.rgb_enabled_check.stateChanged.connect(self.on_settings_changed)
        rgb_layout.addWidget(self.rgb_enabled_check)
        
        # Mode selection
        rgb_layout.addWidget(QLabel("Lighting Mode:"))
        self.rgb_mode_combo = QComboBox()
        self.rgb_mode_combo.addItems(["Static", "Breathing", "Spectrum", "Wave", "Reactive"])
        self.rgb_mode_combo.currentTextChanged.connect(self.on_settings_changed)
        rgb_layout.addWidget(self.rgb_mode_combo)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_picker = ColorPickerWidget("#00FF00")
        self.color_picker.color_changed.connect(self.on_settings_changed)
        color_layout.addWidget(self.color_picker)
        rgb_layout.addLayout(color_layout)
        
        # Brightness
        rgb_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(100)
        self.brightness_label = QLabel("100%")
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        rgb_layout.addWidget(self.brightness_slider)
        rgb_layout.addWidget(self.brightness_label)
        
        # Speed
        rgb_layout.addWidget(QLabel("Effect Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_label = QLabel("50%")
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        rgb_layout.addWidget(self.speed_slider)
        rgb_layout.addWidget(self.speed_label)
        
        rgb_group.setLayout(rgb_layout)
        layout.addWidget(rgb_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.settings_changed.emit()
    
    def on_brightness_changed(self, value):
        """Handle brightness change"""
        self.brightness_label.setText(f"{value}%")
        self.settings_changed.emit()
    
    def on_speed_changed(self, value):
        """Handle speed change"""
        self.speed_label.setText(f"{value}%")
        self.settings_changed.emit()
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            self.rgb_enabled_check.setChecked(settings.rgb_enabled)
            self.rgb_mode_combo.setCurrentText(settings.rgb_mode)
            self.color_picker.set_color(settings.rgb_color)
            self.brightness_slider.setValue(settings.rgb_brightness)
            self.speed_slider.setValue(settings.rgb_speed)
        except Exception as e:
            self.logger.error(f"Error loading lighting settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        try:
            settings.rgb_enabled = self.rgb_enabled_check.isChecked()
            settings.rgb_mode = self.rgb_mode_combo.currentText()
            settings.rgb_color = self.color_picker.get_color()
            settings.rgb_brightness = self.brightness_slider.value()
            settings.rgb_speed = self.speed_slider.value()
        except Exception as e:
            self.logger.error(f"Error updating lighting settings: {e}")
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            if controller and controller.connected and self.rgb_enabled_check.isChecked():
                color = self.color_picker.get_color()
                mode = self.rgb_mode_combo.currentText()
                brightness = self.brightness_slider.value()
                speed = self.speed_slider.value()
                
                if controller.set_rgb(color, mode, brightness, speed):
                    results['rgb'] = True
                    self.logger.info(f"RGB set to {mode} with color {color}")
                else:
                    results['rgb'] = False
                    self.logger.error("Failed to set RGB")
            else:
                results['rgb'] = None
                
        except Exception as e:
            self.logger.error(f"Error applying lighting settings: {e}")
            results['error'] = str(e)
        
        return results
