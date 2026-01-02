"""
Profile management tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QPushButton, QGroupBox, 
                             QInputDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class ProfilesTab(QWidget):
    """Profile management tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        profiles_group = QGroupBox("👤 Profile Management")
        profiles_layout = QVBoxLayout()
        
        profiles_layout.addWidget(QLabel("Save different configurations for various games/applications:"))
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.addItem("Default")
        self.profile_list.setCurrentRow(0)
        profiles_layout.addWidget(self.profile_list)
        
        # Profile buttons
        profile_btn_layout = QHBoxLayout()
        
        new_profile_btn = QPushButton("➕ New Profile")
        new_profile_btn.clicked.connect(self.create_new_profile)
        profile_btn_layout.addWidget(new_profile_btn)
        
        load_profile_btn = QPushButton("📥 Load Selected")
        load_profile_btn.clicked.connect(self.load_profile)
        profile_btn_layout.addWidget(load_profile_btn)
        
        delete_profile_btn = QPushButton("🗑️ Delete")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_btn_layout.addWidget(delete_profile_btn)
        
        profiles_layout.addLayout(profile_btn_layout)
        
        profiles_group.setLayout(profiles_layout)
        layout.addWidget(profiles_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def create_new_profile(self):
        """Create new profile"""
        try:
            profile_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
            if ok and profile_name:
                # This would be handled by the main window
                self.settings_changed.emit()
                self.logger.info(f"Created new profile: {profile_name}")
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
    
    def load_profile(self):
        """Load selected profile"""
        try:
            current_item = self.profile_list.currentItem()
            if current_item:
                profile_name = current_item.text()
                self.settings_changed.emit()
                self.logger.info(f"Loaded profile: {profile_name}")
        except Exception as e:
            self.logger.error(f"Error loading profile: {e}")
    
    def delete_profile(self):
        """Delete selected profile"""
        try:
            current_item = self.profile_list.currentItem()
            if current_item and current_item.text() != "Default":
                profile_name = current_item.text()
                reply = QMessageBox.question(
                    self, "Confirm Delete",
                    f"Are you sure you want to delete profile '{profile_name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.profile_list.takeItem(self.profile_list.row(current_item))
                    self.settings_changed.emit()
                    self.logger.info(f"Deleted profile: {profile_name}")
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        try:
            # Update profile list
            self.profile_list.clear()
            self.profile_list.addItem("Default")
            
            for profile_name in settings.get_profile_list():
                if profile_name != "Default":
                    self.profile_list.addItem(profile_name)
                    
        except Exception as e:
            self.logger.error(f"Error loading profile settings: {e}")
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Profile management is handled by the main window
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Profile management doesn't directly apply device settings
        return {}
