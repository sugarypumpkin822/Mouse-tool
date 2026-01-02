"""
Debug information dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton, 
                             QTabWidget, QWidget, QLabel, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.utils.config import get_library_status, get_system_info
except ImportError:
    get_library_status = lambda: {}
    get_system_info = lambda: {}


class DebugDialog(QDialog):
    """Dialog showing detailed debug information"""
    
    def __init__(self, detector, controller, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.detector = detector
        self.controller = controller
        
        self.init_ui()
        self.refresh_info()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("🔧 Debug Information")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_system_tab()
        self.create_library_tab()
        self.create_device_tab()
        self.create_connection_tab()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_info)
        layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def create_system_tab(self):
        """Create system information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.system_text = QTextEdit()
        self.system_text.setReadOnly(True)
        self.system_text.setFont(QFont("Courier New", 9))
        self.system_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        layout.addWidget(self.system_text)
        
        self.tab_widget.addTab(tab, "💻 System")
    
    def create_library_tab(self):
        """Create library status tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.library_text = QTextEdit()
        self.library_text.setReadOnly(True)
        self.library_text.setFont(QFont("Courier New", 9))
        self.library_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        layout.addWidget(self.library_text)
        
        self.tab_widget.addTab(tab, "📚 Libraries")
    
    def create_device_tab(self):
        """Create device information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.device_text = QTextEdit()
        self.device_text.setReadOnly(True)
        self.device_text.setFont(QFont("Courier New", 9))
        self.device_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        layout.addWidget(self.device_text)
        
        self.tab_widget.addTab(tab, "🖱️ Devices")
    
    def create_connection_tab(self):
        """Create connection information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.connection_text = QTextEdit()
        self.connection_text.setReadOnly(True)
        self.connection_text.setFont(QFont("Courier New", 9))
        self.connection_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        layout.addWidget(self.connection_text)
        
        self.tab_widget.addTab(tab, "🔌 Connection")
    
    def refresh_info(self):
        """Refresh all debug information"""
        try:
            # Update system info
            system_info = get_system_info()
            system_text = "SYSTEM INFORMATION\n"
            system_text += "=" * 50 + "\n\n"
            
            for key, value in system_info.items():
                if key == 'memory':
                    system_text += f"{key.upper()}:\n"
                    system_text += f"  Total: {value['total'] / (1024**3):.1f} GB\n"
                    system_text += f"  Available: {value['available'] / (1024**3):.1f} GB\n"
                    system_text += f"  Used: {value['percent']:.1f}%\n"
                elif key == 'cpu_percent':
                    system_text += f"CPU Usage: {value:.1f}%\n"
                else:
                    system_text += f"{key}: {value}\n"
            
            self.system_text.setText(system_text)
            
            # Update library info
            library_status = get_library_status()
            library_text = "LIBRARY STATUS\n"
            library_text += "=" * 50 + "\n\n"
            
            for lib_name, available in library_status.items():
                status = "✅ Available" if available else "❌ Not Available"
                library_text += f"{lib_name.upper()}: {status}\n"
            
            library_text += "\nINSTALLATION COMMANDS:\n"
            library_text += "pip install hidapi pyusb pywin32 psutil pynput requests beautifulsoup4\n"
            
            self.library_text.setText(library_text)
            
            # Update device info
            device_text = "DEVICE INFORMATION\n"
            device_text += "=" * 50 + "\n\n"
            
            mice = self.detector.scan_devices()
            if mice:
                device_text += f"Found {len(mice)} gaming mice:\n\n"
                
                for i, mouse in enumerate(mice, 1):
                    device_text += f"Device #{i}:\n"
                    device_text += f"  Vendor: {mouse['vendor']}\n"
                    device_text += f"  Product: {mouse['product']}\n"
                    device_text += f"  VID: 0x{mouse['vendor_id']:04X}\n"
                    device_text += f"  PID: 0x{mouse['product_id']:04X}\n"
                    device_text += f"  Interface: {mouse['interface']}\n"
                    device_text += f"  Usage Page: 0x{mouse['usage_page']:02X}\n"
                    device_text += f"  Usage: 0x{mouse['usage']:02X}\n"
                    device_text += f"  Path: {mouse['path']}\n\n"
            else:
                device_text += "No gaming mice detected\n"
                device_text += "\nSUPPORTED BRANDS:\n"
                for brand in self.detector.get_supported_brands():
                    device_text += f"  - {brand}\n"
            
            self.device_text.setText(device_text)
            
            # Update connection info
            connection_text = "CONNECTION INFORMATION\n"
            connection_text += "=" * 50 + "\n\n"
            
            if self.controller and self.controller.connected:
                connection_text += f"Device: {self.controller.mouse_info['product']}\n"
                connection_text += f"Connection Method: {self.controller.connection_method}\n"
                connection_text += f"Protocol: {self.controller.vendor}\n"
                connection_text += f"Test Result: {'✅ PASSED' if self.controller.test_connection() else '❌ FAILED'}\n\n"
                
                connection_text += "Connection Details:\n"
                for info in self.controller.get_connection_info():
                    connection_text += f"  {info}\n"
                
                if self.controller.last_error:
                    connection_text += f"\nLast Error: {self.controller.last_error}\n"
            else:
                connection_text += "No device connected\n"
            
            self.connection_text.setText(connection_text)
            
        except Exception as e:
            self.logger.error(f"Error refreshing debug info: {e}")
            
            # Show error in all tabs
            error_text = f"Error refreshing debug information:\n{e}"
            self.system_text.setText(error_text)
            self.library_text.setText(error_text)
            self.device_text.setText(error_text)
            self.connection_text.setText(error_text)
