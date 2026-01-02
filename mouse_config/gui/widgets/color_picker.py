"""
Custom color picker widget
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QColorDialog, QFrame)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class ColorPickerWidget(QWidget):
    """Custom color picker with preview"""
    
    color_changed = pyqtSignal(str)
    
    def __init__(self, initial_color="#00FF00", parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.current_color = initial_color
        
        self.init_ui()
        self.set_color(initial_color)
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        layout.addWidget(QLabel("Color:"))
        
        # Color button
        self.color_btn = QPushButton("🎨 Choose Color")
        self.color_btn.setStyleSheet("""
            QPushButton {
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.color_btn.clicked.connect(self.choose_color)
        layout.addWidget(self.color_btn)
        
        # Color preview
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(60, 30)
        self.color_preview.setStyleSheet("border: 2px solid black; border-radius: 5px;")
        layout.addWidget(self.color_preview)
        
        # Color value label
        self.color_label = QLabel(self.current_color)
        self.color_label.setStyleSheet("font-family: monospace; font-weight: bold;")
        layout.addWidget(self.color_label)
        
        layout.addStretch()
    
    def choose_color(self):
        """Open color dialog"""
        try:
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name()
                self.set_color(hex_color)
                self.color_changed.emit(hex_color)
                
        except Exception as e:
            self.logger.error(f"Error choosing color: {e}")
    
    def set_color(self, color):
        """Set the current color"""
        try:
            self.current_color = color
            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}; 
                    border: 2px solid black; 
                    border-radius: 5px;
                }}
            """)
            self.color_label.setText(color.upper())
            
        except Exception as e:
            self.logger.error(f"Error setting color: {e}")
    
    def get_color(self):
        """Get the current color"""
        return self.current_color
    
    def set_enabled(self, enabled):
        """Enable/disable the widget"""
        self.color_btn.setEnabled(enabled)
        self.color_preview.setEnabled(enabled)
        
        if not enabled:
            self.color_preview.setStyleSheet("""
                QFrame {
                    background-color: #cccccc; 
                    border: 2px solid #999999; 
                    border-radius: 5px;
                }
            """)
        else:
            self.set_color(self.current_color)
