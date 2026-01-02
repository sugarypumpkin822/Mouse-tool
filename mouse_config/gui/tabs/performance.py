"""
Performance settings tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QSlider, QGroupBox, QPushButton, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.utils.helpers import validate_dpi, validate_poll_rate
except ImportError:
    validate_dpi = lambda x: x
    validate_poll_rate = lambda x: x


class PerformanceTab(QWidget):
    """Performance settings tab for DPI and polling rate"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # DPI Settings
        dpi_group = QGroupBox("🎯 DPI Configuration")
        dpi_layout = QVBoxLayout()
        
        # Current DPI
        dpi_current_layout = QHBoxLayout()
        dpi_current_layout.addWidget(QLabel("Current DPI:"))
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(100, 20000)
        self.dpi_spinbox.setValue(800)
        self.dpi_spinbox.setSingleStep(50)
        self.dpi_spinbox.valueChanged.connect(self.on_dpi_changed)
        dpi_current_layout.addWidget(self.dpi_spinbox)
        dpi_layout.addLayout(dpi_current_layout)
        
        # DPI Presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Presets:"))
        for dpi in [400, 800, 1200, 1600, 3200, 6400]:
            btn = QPushButton(str(dpi))
            btn.setStyleSheet("padding: 8px; font-weight: bold;")
            btn.clicked.connect(lambda checked, d=dpi: self.dpi_spinbox.setValue(d))
            preset_layout.addWidget(btn)
        dpi_layout.addLayout(preset_layout)
        
        # DPI Slider
        self.dpi_slider = QSlider(Qt.Orientation.Horizontal)
        self.dpi_slider.setRange(100, 20000)
        self.dpi_slider.setValue(800)
        self.dpi_slider.valueChanged.connect(self.dpi_spinbox.setValue)
        self.dpi_spinbox.valueChanged.connect(self.dpi_slider.setValue)
        dpi_layout.addWidget(QLabel("Slider:"))
        dpi_layout.addWidget(self.dpi_slider)
        
        dpi_group.setLayout(dpi_layout)
        layout.addWidget(dpi_group)
        
        # Polling Rate
        poll_group = QGroupBox("⚡ Polling Rate")
        poll_layout = QVBoxLayout()
        poll_layout.addWidget(QLabel("Select polling rate (higher = more responsive):"))
        self.polling_combo = QComboBox()
        self.polling_combo.addItems(["125 Hz", "250 Hz", "500 Hz", "1000 Hz"])
        self.polling_combo.setCurrentText("1000 Hz")
        self.polling_combo.currentTextChanged.connect(self.on_polling_changed)
        poll_layout.addWidget(self.polling_combo)
        poll_group.setLayout(poll_layout)
        layout.addWidget(poll_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def on_dpi_changed(self, value):
        """Handle DPI change"""
        if validate_dpi(value):
            self.settings_changed.emit()
    
    def on_polling_changed(self, text):
        """Handle polling rate change"""
        rate = int(text.split()[0])
        if validate_poll_rate(rate):
            self.settings_changed.emit()
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            self.dpi_spinbox.setValue(settings.dpi)
            self.polling_combo.setCurrentText(f"{settings.polling_rate} Hz")
        except Exception as e:
            self.logger.error(f"Error loading performance settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        try:
            settings.dpi = self.dpi_spinbox.value()
            settings.polling_rate = int(self.polling_combo.currentText().split()[0])
        except Exception as e:
            self.logger.error(f"Error updating performance settings: {e}")
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            # Apply DPI
            if controller and controller.connected:
                dpi = self.dpi_spinbox.value()
                if controller.set_dpi(dpi):
                    results['dpi'] = True
                    self.logger.info(f"DPI set to {dpi}")
                else:
                    results['dpi'] = False
                    self.logger.error("Failed to set DPI")
            else:
                results['dpi'] = None
            
            # Apply polling rate
            if controller and controller.connected:
                rate = int(self.polling_combo.currentText().split()[0])
                if controller.set_polling_rate(rate):
                    results['polling_rate'] = True
                    self.logger.info(f"Polling rate set to {rate}Hz")
                else:
                    results['polling_rate'] = False
                    self.logger.error("Failed to set polling rate")
            else:
                results['polling_rate'] = None
                
        except Exception as e:
            self.logger.error(f"Error applying performance settings: {e}")
            results['error'] = str(e)
        
        return results
