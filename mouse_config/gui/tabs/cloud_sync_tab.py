"""
Cloud synchronization tab for settings and profiles
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox, QLineEdit,
                             QMessageBox, QCheckBox, QProgressBar)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.advanced import CloudSyncManager, CloudSettingsManager
except ImportError:
    CloudSyncManager = None
    CloudSettingsManager = None


class CloudSyncTab(QWidget):
    """Cloud synchronization tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        # Cloud systems
        self.cloud_sync_manager = CloudSyncManager()
        self.cloud_settings_manager = CloudSettingsManager()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Login Section
        login_group = QGroupBox("Login")
        login_layout = QVBoxLayout()
        
        # Email input
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        email_layout.addWidget(self.email_input)
        login_layout.addStretch()
        login_layout.addLayout(email_layout)
        login_layout.addLayout(login_layout)
        
        # Password input
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        login_layout.addStretch()
        login_layout.addLayout(password_layout)
        
        login_layout.addLayout(login_layout)
        
        # Login button
        self.login_btn = QPushButton("🔐 Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.login_btn.clicked.connect(self.login_to_cloud)
        login_layout.addWidget(self.login_btn)
        
        login_layout.addLayout(login_layout)
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Sync Settings
        sync_group = QGroupBox("⚙ Sync Settings")
        sync_layout = QVBoxLayout()
        
        # Auto-sync checkbox
        self.auto_sync_check = QCheckBox("Enable automatic synchronization")
        self.auto_sync_check.setChecked(True)
        self.auto_sync_check.stateChanged.connect(self.on_settings_changed)
        sync_layout.addWidget(self.auto_sync_check)
        
        # Sync interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Sync Interval:"))
        self.sync_interval_spinbox = QSpinBox()
        self.sync_interval_spinbox.setRange(1, 60)  # 1-60 minutes
        self.sync_interval_spinbox.setValue(5)  # Default 5 minutes
        interval_layout.addWidget(self.sync_interval_spinbox)
        interval_layout.addWidget(QLabel("minutes"))
        interval_layout.addStretch()
        interval_layout.addLayout(interval_layout)
        sync_layout.addLayout(interval_layout)
        
        sync_layout.addLayout(sync_layout)
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)
        
        # Cloud Storage
        storage_group = QGroupBox("☁️ Cloud Storage")
        storage_layout = QVBoxLayout()
        
        # Storage info
        self.storage_info_text = QTextEdit()
        self.storage_info_text.setReadOnly(True)
        self.storage_info_text.setMaximumHeight(100)
        self.storage_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        storage_layout.addWidget(self.storage_info_text)
        
        # Refresh storage info
        refresh_btn = QPushButton("🔄 Refresh Storage Info")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_storage_info)
        storage_layout.addWidget(refresh_btn)
        
        storage_layout.addLayout(storage_layout)
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Sync Status
        status_group = QGroupBox("📊 Sync Status")
        status_layout = QVBoxLayout()
        
        self.sync_status_text = QTextEdit()
        self.sync_status_text.setReadOnly(True)
        self.sync_status_text.setMaximumHeight(100)
        self.sync_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        status_layout.addWidget(self.sync_status_text)
        
        status_layout.addLayout(status_layout)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
        
        # Initialize cloud systems with controller
        if controller:
            self.cloud_sync_manager = CloudSyncManager()
            self.cloud_settings_manager = CloudSettingsManager()
    
    def login_to_cloud(self):
        """Login to cloud service"""
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text()
            
            if not email or not password:
                QMessageBox.warning(self, "Warning", "Please enter both email and password")
                return
            
            # Attempt login
            if self.cloud_sync_manager.login(email, password):
                self.email_input.clear()
                self.password_input.clear()
                
                # Update UI
                self.update_sync_status("✅ Logged in successfully")
                self.logger.info(f"Logged in as {email}")
                
                # Enable sync features
                self.auto_sync_check.setEnabled(True)
                self.sync_interval_spinbox.setEnabled(True)
                
                # Load cloud settings
                self.cloud_settings_manager.load_settings()
                
                QMessageBox.information(self, "Login Successful", f"Successfully logged in as {email}")
                
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid email or password")
                self.logger.error(f"Login failed for {email}")
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Login Error", f"Login failed: {e}")
    
    def logout_from_cloud(self):
        """Logout from cloud service"""
        try:
            self.cloud_sync_manager.logout()
            
            # Update UI
            self.email_input.clear()
            self.password_input.clear()
            self.auto_sync_check.setChecked(False)
            self.sync_interval_spinbox.setEnabled(False)
            self.update_sync_status("🔴 Logged out")
            
            self.logger.info("Logged out from cloud service")
            
            QMessageBox.information(self, "Logout Successful", "Successfully logged out")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            QMessageBox.critical(self, "Logout Error", f"Logout failed: {e}")
    
    def refresh_storage_info(self):
        """Refresh storage information display"""
        try:
            # Get storage statistics
            stats = self.cloud_sync_manager.get_sync_status()
            
            info_text = f"""☁️ Cloud Storage Information
{'='*50}
User Status: {'Logged In' if stats['logged_in'] else 'Logged Out'}
Last Sync: {stats.get('last_sync', 'Never')}
Pending Uploads: {stats.get('pending_uploads', 0)}
Pending Downloads: {stats.get('pending_downloads', 0)}
Sync Interval: {stats.get('sync_interval', 5)} minutes
Total Sessions: {stats.get('total_sessions', 0)}
"""
            
            self.storage_info_text.setText(info_text)
            
        except Exception as e:
            self.logger.error(f"Error refreshing storage info: {e}")
            self.storage_info.setText(f"❌ Error: {e}")
    
    def update_sync_status(self, message: str = ""):
        """Update sync status display"""
        if message:
            self.sync_status_text.setText(message)
    
    def on_settings_changed(self):
        """Handle settings changes"""
        try:
            # Update cloud settings
            self.cloud_settings_manager.update_setting(
                'auto_sync', self.auto_sync_check.isChecked(),
                'sync_interval', self.sync_interval_spinbox.value()
            )
            
            self.settings_changed.emit()
            
        except Exception as e:
            self.logger.error(f"Error updating cloud settings: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            # Load cloud settings
            self.cloud_settings_manager.load_settings()
            
            # Update UI
            self.auto_sync_check.setChecked(settings.get('auto_sync', False))
            self.sync_interval_spinbox.setValue(settings.get('sync_interval', 5))
            
        except Exception as e:
            self.logger.error(f"Error loading cloud settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        try:
            # Save cloud settings
            self.cloud_settings_manager.save_settings()
            
        except Exception as e:
            self.logger.error(f"Error saving cloud settings: {e}")
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            # Cloud sync doesn't apply device settings directly
            results['cloud_sync'] = True
            
        except Exception as e:
            self.logger.error(f"Error applying cloud settings: {e}")
            results['cloud_sync'] = False
        
        return results
    
    def export_cloud_data(self):
        """Export cloud data"""
        try:
            # Get cloud data
            cloud_data = {
                'sync_status': self.cloud_sync_manager.get_sync_status(),
                'cloud_settings': self.cloud_settings.get_settings(),
                'available_features': [
                    'Settings synchronization',
                    'Profile synchronization',
                    'Macro storage',
                    'Analytics backup'
                ]
            }
            
            # Export to file
            from pathlib import Path
            timestamp = time.time()
            filename = f"cloud_data_{timestamp}.json"
            
            import json
            with open(filename, 'w') as f:
                json.dump(cloud_data, f, indent=2)
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Cloud data exported to {filename}"
            )
            
        except Exception as e:
            self.logger.error(f"Error exporting cloud data: {e}")
            QMessageBox.critical(self, "Export Failed", f"Failed to export cloud data: {e}")
    
    def load_cloud_data(self):
        """Import cloud data"""
        try:
            from pathlib import Path
            import json
            
            # Find most recent cloud data file
            cloud_dir = Path.home() / '.mouse_config' / 'cloud_sync'
            cloud_dir.mkdir(parents=True, exist_ok=True)
            
            cloud_files = sorted(cloud_dir.glob('cloud_data_*.json'), reverse=True)
            
            if cloud_files:
                latest_file = cloud_files[0]
                
                with open(latest_file, 'r') as f:
                    cloud_data = json.load(f)
                
                # Import cloud data
                if 'cloud_settings' in cloud_data:
                    self.cloud_settings_manager.from_dict(cloud_data['cloud_settings'])
                
                if 'sync_status' in cloud_data:
                    status = cloud_data['sync_status']
                    self.update_sync_status(f"Last sync: {status.get('last_sync', 'Never')}")
                
                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Cloud data imported from {latest_file.name}"
                )
                
            else:
                QMessageBox.information(self, "Import Failed", "No cloud data files found")
                
        except Exception as e:
            self.logger.error(f"Error importing cloud data: {e}")
            QMessageBox.critical(self, "Import Failed", f"Failed to import cloud data: {e}")
    
    def get_cloud_status(self) -> Dict[str, Any]:
        """Get current cloud status"""
        return self.cloud_sync_manager.get_sync_status()
