"""
Device selection widget
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QFrame)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class DeviceSelector(QFrame):
    """Widget for selecting and connecting to mouse devices"""
    
    device_selected = pyqtSignal(object)
    scan_clicked = pyqtSignal()
    debug_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.detected_mice = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #667eea;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        
        # Device selection
        layout.addWidget(QLabel("🖱️ Connected Mouse:"))
        
        self.mouse_combo = QComboBox()
        self.mouse_combo.setFont(QFont("Arial", 10))
        self.mouse_combo.currentIndexChanged.connect(self.on_device_changed)
        layout.addWidget(self.mouse_combo, 1)
        
        # Scan button
        self.scan_btn = QPushButton("🔄 Scan")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.scan_btn.clicked.connect(self.scan_clicked.emit)
        layout.addWidget(self.scan_btn)
        
        # Debug button
        self.debug_btn = QPushButton("🔧 Debug")
        self.debug_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.debug_btn.clicked.connect(self.debug_clicked.emit)
        layout.addWidget(self.debug_btn)
        
        # Status label
        self.status_label = QLabel("⚡ Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px; 
                background-color: #f0f0f0; 
                border-radius: 5px; 
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
    
    def update_device_list(self, mice):
        """Update the device list"""
        self.detected_mice = mice
        
        self.mouse_combo.clear()
        
        if mice:
            for mouse in mice:
                display_name = f"{mouse['vendor']} - {mouse['product']}"
                self.mouse_combo.addItem(display_name, mouse)
            
            self.status_label.setText(f"✅ Found {len(mice)} mouse/mice")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px; 
                    background-color: #90EE90; 
                    border-radius: 5px; 
                    font-weight: bold;
                }
            """)
        else:
            self.mouse_combo.addItem("No gaming mice detected", None)
            self.status_label.setText("❌ No gaming mice detected")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px; 
                    background-color: #FFB6C1; 
                    border-radius: 5px; 
                    font-weight: bold;
                }
            """)
    
    def on_device_changed(self, index):
        """Handle device selection change"""
        mouse_data = self.mouse_combo.currentData()
        self.device_selected.emit(mouse_data)
    
    def get_selected_device(self):
        """Get the currently selected device"""
        return self.mouse_combo.currentData()
    
    def set_status(self, text, color=None):
        """Set the status text"""
        self.status_label.setText(text)
        
        if color:
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    padding: 8px; 
                    background-color: {color}; 
                    border-radius: 5px; 
                    font-weight: bold;
                }}
            """)
