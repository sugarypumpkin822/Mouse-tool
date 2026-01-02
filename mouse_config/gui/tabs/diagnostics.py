"""
Advanced diagnostics and troubleshooting tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.utils.helpers import get_system_info
except ImportError:
    get_system_info = lambda: {}


class DiagnosticsTab(QWidget):
    """Advanced diagnostics and troubleshooting tab"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # System Information
        sys_group = QGroupBox("💻 System Information")
        sys_layout = QVBoxLayout()
        
        self.sys_info_text = QTextEdit()
        self.sys_info_text.setReadOnly(True)
        self.sys_info_text.setMaximumHeight(200)
        self.sys_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 5px;
            }
        """)
        sys_layout.addWidget(self.sys_info_text)
        
        refresh_sys_btn = QPushButton("🔄 Refresh System Info")
        refresh_sys_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_sys_btn.clicked.connect(self.refresh_system_info)
        sys_layout.addWidget(refresh_sys_btn)
        
        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)
        
        # Device Diagnostics
        device_group = QGroupBox("🔧 Device Diagnostics")
        device_layout = QVBoxLayout()
        
        self.device_info_text = QTextEdit()
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setMaximumHeight(200)
        self.device_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 5px;
            }
        """)
        device_layout.addWidget(self.device_info_text)
        
        test_device_btn = QPushButton("🧪 Test Device Connection")
        test_device_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        test_device_btn.clicked.connect(self.test_device_connection)
        device_layout.addWidget(test_device_btn)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Performance Monitor
        perf_group = QGroupBox("⚡ Performance Monitor")
        perf_layout = QVBoxLayout()
        
        self.perf_text = QTextEdit()
        self.perf_text.setReadOnly(True)
        self.perf_text.setMaximumHeight(150)
        self.perf_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #00ff00; 
                font-family: 'Courier New'; 
                padding: 5px;
            }
        """)
        perf_layout.addWidget(self.perf_text)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def refresh_system_info(self):
        """Refresh system information display"""
        try:
            info = get_system_info()
            
            # Format system info for display
            sys_text = "SYSTEM INFORMATION\n"
            sys_text += "=" * 50 + "\n\n"
            
            for key, value in info.items():
                if key == 'memory':
                    sys_text += f"{key.upper()}:\n"
                    sys_text += f"  Total: {value['total'] / (1024**3):.1f} GB\n"
                    sys_text += f"  Available: {value['available'] / (1024**3):.1f} GB\n"
                    sys_text += f"  Used: {value['percent']:.1f}%\n"
                elif key == 'cpu_percent':
                    sys_text += f"CPU Usage: {value:.1f}%\n"
                else:
                    sys_text += f"{key}: {value}\n"
            
            # Add library status
            try:
                from mouse_config.utils.config import get_library_status
                library_status = get_library_status()
                
                sys_text += "\nLIBRARY STATUS\n"
                sys_text += "=" * 50 + "\n\n"
                
                for lib_name, available in library_status.items():
                    status = "✅ Available" if available else "❌ Not Available"
                    sys_text += f"{lib_name.upper()}: {status}\n"
            except ImportError:
                sys_text += "\nLIBRARY STATUS\n"
                sys_text += "=" * 50 + "\n\n"
                sys_text += "Unable to get library status\n"
            
            self.sys_info_text.setText(sys_text)
            
        except Exception as e:
            self.logger.error(f"Error refreshing system info: {e}")
            self.sys_info_text.setText(f"Error getting system info: {e}")
    
    def test_device_connection(self):
        """Test device connection and responsiveness"""
        try:
            if not self.controller or not self.controller.connected:
                self.device_info_text.setText("❌ No device connected")
                return
            
            info = []
            info.append(f"🔌 Device: {self.controller.mouse_info['product']}")
            info.append(f"📡 Connection Method: {self.controller.connection_method}")
            info.append(f"🔧 Protocol: {self.controller.vendor}")
            
            # Test connection
            if self.controller.test_connection():
                info.append("✅ Connection Test: PASSED")
            else:
                info.append("❌ Connection Test: FAILED")
            
            # Get connection details
            conn_info = self.controller.get_connection_info()
            info.append("\n🔍 Connection Details:")
            for detail in conn_info:
                info.append(f"  {detail}")
            
            # Test basic commands
            info.append("\n🧪 Command Tests:")
            
            # Test DPI command
            if hasattr(self.controller.protocol, 'set_dpi'):
                try:
                    command = self.controller.protocol.set_dpi(800)
                    if self.controller.send_command(command):
                        info.append("  ✅ DPI Command: SUCCESS")
                    else:
                        info.append("  ❌ DPI Command: FAILED")
                except Exception as e:
                    info.append(f"  ❌ DPI Command: ERROR - {e}")
            
            # Test RGB command
            if hasattr(self.controller.protocol, 'set_rgb'):
                try:
                    command = self.controller.protocol.set_rgb(255, 0, 0, 0)
                    if self.controller.send_command(command):
                        info.append("  ✅ RGB Command: SUCCESS")
                    else:
                        info.append("  ❌ RGB Command: FAILED")
                except Exception as e:
                    info.append(f"  ❌ RGB Command: ERROR - {e}")
            
            self.device_info_text.setText('\n'.join(info))
            
        except Exception as e:
            self.logger.error(f"Error testing device connection: {e}")
            self.device_info_text.setText(f"Error testing device: {e}")
    
    def update_performance_info(self):
        """Update performance monitoring information"""
        try:
            import psutil
            import time
            
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            perf_text = "PERFORMANCE MONITOR\n"
            perf_text += "=" * 50 + "\n\n"
            perf_text += f"CPU Usage: {cpu_percent:.1f}%\n"
            perf_text += f"Memory Usage: {memory.percent:.1f}%\n"
            perf_text += f"Available Memory: {memory.available / (1024**3):.1f} GB\n"
            perf_text += f"Used Memory: {memory.used / (1024**3):.1f} GB\n"
            
            # Get process info
            try:
                process = psutil.Process()
                perf_text += f"\nProcess Info:\n"
                perf_text += f"  PID: {process.pid}\n"
                perf_text += f"  Memory: {process.memory_info().rss / (1024**2):.1f} MB\n"
                perf_text += f"  CPU: {process.cpu_percent():.1f}%\n"
            except:
                perf_text += "\nProcess Info: Unable to get process info\n"
            
            self.perf_text.setText(perf_text)
            
        except Exception as e:
            self.logger.error(f"Error updating performance info: {e}")
            self.perf_text.setText(f"Error getting performance info: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # Diagnostics tab doesn't have settings to load
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Diagnostics tab doesn't have settings to update
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Diagnostics tab doesn't apply device settings
        return {}
