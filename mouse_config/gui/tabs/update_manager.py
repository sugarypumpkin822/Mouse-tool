"""
Update manager tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox, QProgressBar,
                             QMessageBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.utils.updater import UpdateManager, UpdateChecker, UpdateDownloader
except ImportError:
    UpdateManager = None
    UpdateChecker = None
    UpdateDownloader = None


class UpdateManagerTab(QWidget):
    """Update manager tab for auto-updates"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        # Update management
        self.update_manager = UpdateManager()
        self.update_checker = None
        self.update_downloader = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Current Version Group
        version_group = QGroupBox("📦 Current Version")
        version_layout = QVBoxLayout()
        
        self.current_version_label = QLabel("Loading version...")
        version_layout.addWidget(self.current_version_label)
        
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)
        
        # Update Check Group
        check_group = QGroupBox("🔍 Update Check")
        check_layout = QVBoxLayout()
        
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
        check_btn.clicked.connect(self.check_for_updates)
        check_layout.addWidget(check_btn)
        
        # Auto-update checkbox
        self.auto_update_check = QCheckBox("Automatically check for updates on startup")
        self.auto_update_check.stateChanged.connect(self.on_auto_update_changed)
        check_layout.addWidget(self.auto_update_check)
        
        check_group.setLayout(check_layout)
        layout.addWidget(check_group)
        
        # Update Status Group
        status_group = QGroupBox("📊 Update Status")
        status_layout = QVBoxLayout()
        
        self.update_status_text = QTextEdit()
        self.update_status_text.setReadOnly(True)
        self.update_status_text.setMaximumHeight(200)
        self.update_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        status_layout.addWidget(self.update_status_text)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Download Group
        download_group = QGroupBox("⬇️ Update Download")
        download_layout = QVBoxLayout()
        
        # Progress bar
        self.update_progress = QProgressBar()
        self.update_progress.setVisible(False)
        download_layout.addWidget(self.update_progress)
        
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
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setEnabled(False)
        download_layout.addWidget(self.download_btn)
        
        # Warning
        warning_label = QLabel("⚠️ The application will restart after update installation")
        warning_label.setStyleSheet("""
            QLabel {
                color: #FF5722; 
                font-weight: bold; 
                padding: 10px; 
                background-color: #FFF3E0; 
                border-radius: 5px;
            }
        """)
        download_layout.addWidget(warning_label)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # Changelog Group
        changelog_group = QGroupBox("📝 Changelog")
        changelog_layout = QVBoxLayout()
        
        changelog_btn = QPushButton("📋 View Changelog")
        changelog_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        changelog_btn.clicked.connect(self.show_changelog)
        changelog_layout.addWidget(changelog_btn)
        
        self.changelog_text = QTextEdit()
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setMaximumHeight(150)
        self.changelog_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        changelog_layout.addWidget(self.changelog_text)
        
        changelog_group.setLayout(changelog_layout)
        layout.addWidget(changelog_group)
        
        # Initialize version display
        self.update_current_version()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def update_current_version(self):
        """Update current version display"""
        try:
            from mouse_config.utils.updater import UpdateChecker
            checker = UpdateChecker()
            current_version = checker.get_current_version()
            self.current_version_label.setText(f"Current Version: {current_version}")
        except ImportError:
            self.current_version_label.setText("Current Version: Unknown")
        except Exception as e:
            self.logger.error(f"Error getting current version: {e}")
            self.current_version_label.setText("Version: Unknown")
    
    def check_for_updates(self):
        """Check for updates"""
        try:
            self.update_status_text.setText("🔍 Checking for updates...")
            self.logger.info("Checking for updates...")
            
            # Start update checker
            self.update_checker = self.update_manager.check_for_updates()
            
            # Connect signals
            self.update_checker.update_available.connect(self.on_update_available)
            self.update_checker.check_complete.connect(self.on_check_complete)
            
            # Start checking
            self.update_checker.start()
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            self.update_status_text.setText(f"❌ Check failed: {e}")
    
    def on_update_available(self, update_info):
        """Handle update available"""
        try:
            self.current_update_info = update_info
            
            status_text = f"""✅ Update Available!
{'='*40}

Current Version: {update_info['current_version']}
Latest Version: {update_info['latest_version']}
Release: {update_info['release_name']}
Published: {update_info['published_at']}

📋 Release Notes:
{update_info['release_notes']}

Click "Download & Install Update" to proceed
"""
            
            self.update_status_text.setText(status_text)
            self.download_btn.setEnabled(True)
            
            self.logger.info(f"Update available: {update_info['current_version']} -> {update_info['latest_version']}")
            
        except Exception as e:
            self.logger.error(f"Error handling update available: {e}")
    
    def on_check_complete(self, success, message):
        """Handle check complete"""
        if not success and not hasattr(self, 'current_update_info'):
            self.update_status_text.setText(f"❌ {message}")
            self.download_btn.setEnabled(False)
    
    def download_update(self):
        """Download and install update"""
        try:
            if not hasattr(self, 'current_update_info'):
                QMessageBox.warning(self, "Warning", "No update available to download!")
                return
            
            reply = QMessageBox.question(
                self,
                "Confirm Update",
                f"⚠️ This will download and install version {self.current_update_info['latest_version']}\n"
                "The application will restart after installation.\n\n"
                "Continue with update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.logger.info("Starting update download...")
                
                # Start download
                self.update_downloader = self.update_manager.download_update(self.current_update_info)
                
                # Connect signals
                self.update_downloader.progress.connect(self.update_progress.setValue)
                self.update_downloader.status.connect(self.update_status_text.setText)
                self.update_downloader.finished.connect(self.on_update_finished)
                
                # Show progress bar
                self.update_progress.setVisible(True)
                self.update_progress.setValue(0)
                self.download_btn.setEnabled(False)
                
                # Start download
                self.update_downloader.start()
                
        except Exception as e:
            self.logger.error(f"Error starting update download: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start download: {e}")
    
    def on_update_finished(self, success, message):
        """Handle update download completion"""
        try:
            self.update_progress.setVisible(False)
            self.download_btn.setEnabled(True)
            
            if success:
                self.logger.info(f"Update completed: {message}")
                QMessageBox.information(
                    self,
                    "Update Complete",
                    f"✅ Update installed successfully!\n\n"
                    f"The application will now restart to apply the update."
                )
                
                # Restart application
                import subprocess
                import sys
                from pathlib import Path
                
                # Get current script path
                script_path = Path(__file__).parent.parent.parent.parent / "main.py"
                
                # Restart the application
                subprocess.Popen([sys.executable, str(script_path)])
                sys.exit(0)
                
            else:
                self.logger.error(f"Update failed: {message}")
                QMessageBox.critical(self, "Update Failed", f"❌ {message}")
                
        except Exception as e:
            self.logger.error(f"Error handling update completion: {e}")
    
    def show_changelog(self):
        """Show changelog"""
        try:
            self.changelog_text.setText("📋 Loading changelog...")
            
            changelog = self.update_manager.get_changelog()
            
            if changelog:
                self.changelog_text.setText(changelog)
            else:
                self.changelog_text.setText("❌ Failed to load changelog")
                
        except Exception as e:
            self.logger.error(f"Error showing changelog: {e}")
            self.changelog_text.setText(f"❌ Error: {e}")
    
    def on_auto_update_changed(self, state):
        """Handle auto-update checkbox change"""
        try:
            enabled = state == Qt.CheckState.Checked.value
            # Save setting
            try:
                from mouse_config.utils.config import get_config_path
                import json
                
                config_path = get_config_path()
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                else:
                    config = {}
                
                config['auto_update'] = enabled
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                    
            except ImportError:
                pass
            except Exception as e:
                self.logger.error(f"Error saving auto-update setting: {e}")
                
        except Exception as e:
            self.logger.error(f"Error handling auto-update change: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            try:
                from mouse_config.utils.config import get_config_path
                import json
                
                config_path = get_config_path()
                
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    # Load auto-update setting
                    auto_update = config.get('auto_update', False)
                    self.auto_update_checkbox.setChecked(auto_update)
                    
            except ImportError:
                pass
            except Exception as e:
                self.logger.error(f"Error loading settings: {e}")
                
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Update settings are handled separately
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Update tab doesn't apply device settings
        return {}
