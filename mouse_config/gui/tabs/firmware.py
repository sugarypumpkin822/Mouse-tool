"""
Firmware management tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QMessageBox, QGroupBox)
from PyQt6.QtCore import pyqtSignal, QThread

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.firmware import FirmwareManager, FirmwareScraper
except ImportError:
    FirmwareManager = None
    FirmwareScraper = None


class FirmwareTab(QWidget):
    """Firmware update and management tab"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        # Firmware management
        self.firmware_manager = FirmwareManager()
        self.firmware_scraper = FirmwareScraper()
        self.current_download = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        firmware_group = QGroupBox("🔄 Firmware Management")
        firmware_layout = QVBoxLayout()
        
        # Current firmware info
        firmware_layout.addWidget(QLabel("Current Firmware Version:"))
        self.firmware_version_label = QLabel("Unknown - Connect mouse to check")
        self.firmware_version_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        firmware_layout.addWidget(self.firmware_version_label)
        
        # Check updates button
        check_btn = QPushButton("🔍 Check for Updates")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        check_btn.clicked.connect(self.check_firmware_updates)
        firmware_layout.addWidget(check_btn)
        
        # Progress bar
        self.firmware_progress = QProgressBar()
        self.firmware_progress.setVisible(False)
        firmware_layout.addWidget(self.firmware_progress)
        
        # Status label
        self.firmware_status = QLabel("")
        firmware_layout.addWidget(self.firmware_status)
        
        # Download button
        self.download_btn = QPushButton("⬇️ Download & Install Update")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.download_btn.clicked.connect(self.download_firmware)
        self.download_btn.setEnabled(False)
        firmware_layout.addWidget(self.download_btn)
        
        # Warning
        warning_label = QLabel("⚠️ WARNING: Do not disconnect mouse during firmware update!")
        warning_label.setStyleSheet("""
            QLabel {
                color: red; 
                font-weight: bold; 
                padding: 10px; 
                background-color: #fff3cd; 
                border-radius: 5px;
            }
        """)
        firmware_layout.addWidget(warning_label)
        
        firmware_group.setLayout(firmware_layout)
        layout.addWidget(firmware_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
        if controller:
            self.update_firmware_info()
    
    def update_firmware_info(self):
        """Update firmware information display"""
        try:
            if self.controller and self.controller.connected:
                # Get firmware info from device
                device_info = self.controller.mouse_info
                self.firmware_version_label.setText(f"{device_info['product']} - Connected")
            else:
                self.firmware_version_label.setText("No device connected")
        except Exception as e:
            self.logger.error(f"Error updating firmware info: {e}")
            self.firmware_version_label.setText("Error getting firmware info")
    
    def check_firmware_updates(self):
        """Check for firmware updates"""
        try:
            if not self.controller or not self.controller.connected:
                QMessageBox.warning(self, "Warning", "No mouse connected!")
                return
            
            self.firmware_status.setText("Searching for updates...")
            self.logger.info("Checking for firmware updates...")
            
            # Get device info
            device_info = self.controller.mouse_info
            vendor = device_info['vendor']
            product = device_info['product']
            
            # Search for firmware
            firmware_info = self.firmware_scraper.search_firmware(vendor, product)
            
            if firmware_info:
                self.firmware_status.setText(f"✅ Update available: {firmware_info['version']}")
                self.download_btn.setEnabled(True)
                self.firmware_url = firmware_info['url']
                self.firmware_filename = firmware_info['filename']
                self.logger.info(f"Firmware found: {firmware_info['version']}")
            else:
                self.firmware_status.setText("❌ No updates found or not supported")
                self.download_btn.setEnabled(False)
                self.logger.info("No firmware updates available")
                
        except Exception as e:
            self.logger.error(f"Error checking firmware updates: {e}")
            self.firmware_status.setText(f"❌ Error checking updates: {e}")
    
    def download_firmware(self):
        """Download and install firmware"""
        try:
            reply = QMessageBox.question(
                self,
                "Confirm Update",
                "⚠️ Firmware update will take 2-5 minutes.\nDo NOT disconnect the mouse!\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.logger.info("Starting firmware download...")
                
                from pathlib import Path
                save_path = Path.home() / "Downloads" / self.firmware_filename
                
                # Start download
                self.current_download = self.firmware_manager.download_firmware(
                    self.firmware_url, save_path
                )
                
                # Connect signals
                self.current_download.progress.connect(self.firmware_progress.setValue)
                self.current_download.status.connect(self.firmware_status.setText)
                self.current_download.finished.connect(self.on_firmware_downloaded)
                
                # Show progress bar
                self.firmware_progress.setVisible(True)
                self.firmware_progress.setValue(0)
                
                # Start download thread
                self.current_download.start()
                
        except Exception as e:
            self.logger.error(f"Error starting firmware download: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start download: {e}")
    
    def on_firmware_downloaded(self, success, message):
        """Handle firmware download completion"""
        try:
            self.firmware_progress.setVisible(False)
            
            if success:
                self.logger.info(f"Firmware downloaded: {message}")
                QMessageBox.information(
                    self,
                    "Download Complete",
                    f"Firmware downloaded to:\n{message}\n\nFor safety, please run the firmware updater manually."
                )
            else:
                self.logger.error(f"Firmware download failed: {message}")
                QMessageBox.critical(self, "Download Failed", message)
                
        except Exception as e:
            self.logger.error(f"Error handling firmware download: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # Firmware tab doesn't have settings to load
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Firmware tab doesn't have settings to update
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Firmware tab doesn't apply device settings
        return {}
