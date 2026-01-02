"""
Custom LCD display widget for statistics
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class LCDDisplay(QWidget):
    """Custom LCD-style display for statistics"""
    
    def __init__(self, label_text="Value", unit="", parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.label_text = label_text
        self.unit = unit
        self.value = 0
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Arial", 9))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #00ff00;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.value_label)
        
        # Unit label
        if self.unit:
            self.unit_label = QLabel(self.unit)
            self.unit_label.setFont(QFont("Arial", 8))
            self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.unit_label)
    
    def display(self, value):
        """Display a value"""
        try:
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    self.value_label.setText(f"{value:.1f}")
                else:
                    self.value_label.setText(str(value))
                self.value = value
            else:
                self.value_label.setText(str(value))
                
        except Exception as e:
            self.logger.error(f"Error displaying value: {e}")
            self.value_label.setText("Error")
    
    def get_value(self):
        """Get the current value"""
        return self.value
    
    def set_color(self, color):
        """Set the display color"""
        self.value_label.setStyleSheet(f"""
            QLabel {{
                background-color: #1e1e1e;
                color: {color};
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #333;
            }}
        """)
    
    def set_label(self, text):
        """Set the label text"""
        self.label.setText(text)
        self.label_text = text
