"""
Cloud synchronization system for settings and profiles
"""

import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute


class CloudSyncManager(QThread):
    """Background thread for cloud synchronization"""
    
    sync_progress = pyqtSignal(int)
    sync_status = pyqtSignal(str)
    sync_complete = pyqtSignal(bool, str)
    
    def __init__(self, api_key: str = None, api_url: str = "https://api.mouseconfig.com"):
        super().__init__()
        self.logger = get_logger(__name__)
        self.api_key = api_key
        self.api_url = api_url
        self.should_stop = False
        self.sync_interval = 300  # 5 minutes
        
        # User account info
        self.user_id = None
        self.user_token = None
        
        # Sync status
        self.last_sync = None
        self.pending_uploads = []
        self.pending_downloads = []
        
    def run(self):
        """Run continuous synchronization"""
        try:
            self.logger.info("Starting cloud sync service")
            
            while not self.should_stop:
                try:
                    # Perform sync
                    self.perform_sync()
                    
                    # Wait for next sync cycle
                    for _ in range(self.sync_interval):
                        if self.should_stop:
                            break
                        self.msleep(1000)
                        
                except Exception as e:
                    self.logger.error(f"Sync error: {e}")
                    self.sync_status.emit(f"Sync error: {e}")
                    self.msleep(10000)  # Wait 10 seconds before retrying
                    
        except Exception as e:
            self.logger.error(f"Cloud sync service error: {e}")
    
    def perform_sync(self):
        """Perform one sync cycle"""
        try:
            if not self.user_token:
                self.sync_status.emit("Not logged in")
                return
            
            self.sync_progress.emit(10)
            self.sync_status.emit("Syncing settings...")
            
            # Upload local changes
            self.upload_settings()
            self.sync_progress.emit(50)
            
            # Download remote changes
            self.download_settings()
            self.sync_progress.emit(90)
            
            # Update last sync time
            self.last_sync = datetime.now()
            self.sync_progress.emit(100)
            self.sync_status.emit("Sync complete")
            self.sync_complete.emit(True, "Sync completed successfully")
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            self.sync_complete.emit(False, f"Sync failed: {e}")
    
    def login(self, email: str, password: str) -> bool:
        """Login to cloud service"""
        try:
            self.sync_status.emit("Logging in...")
            
            # Create user account or login
            login_data = {
                'email': email,
                'password': hashlib.sha256(password.encode()).hexdigest(),
                'device_id': self.get_device_id()
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            response.raise_for_status()
            
            auth_data = response.json()
            
            if auth_data.get('success'):
                self.user_id = auth_data.get('user_id')
                self.user_token = auth_data.get('token')
                self.logger.info(f"Logged in as user {self.user_id}")
                return True
            else:
                self.logger.error(f"Login failed: {auth_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def logout(self):
        """Logout from cloud service"""
        try:
            if self.user_token:
                requests.post(f"{self.api_url}/auth/logout", 
                           headers={'Authorization': f'Bearer {self.user_token}'}, timeout=10)
            
            self.user_id = None
            self.user_token = None
            self.logger.info("Logged out")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
    
    def upload_settings(self) -> bool:
        """Upload settings to cloud"""
        try:
            if not self.user_token:
                return False
            
            # Get settings files
            settings_files = self.get_settings_files()
            
            for file_path, file_data in settings_files.items():
                self.sync_status.emit(f"Uploading {file_path.name}...")
                
                upload_data = {
                    'file_path': str(file_path.relative_to(Path.home())),
                    'content': file_data,
                    'checksum': hashlib.sha256(file_data).hexdigest(),
                    'modified': file_path.stat().st_mtime
                }
                
                response = requests.post(
                    f"{self.api_url}/sync/upload",
                    json=upload_data,
                    headers={'Authorization': f'Bearer {self.user_token}'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.logger.info(f"Uploaded {file_path.name}")
                else:
                    self.logger.error(f"Failed to upload {file_path.name}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Upload error: {e}")
            return False
    
    def download_settings(self) -> bool:
        """Download settings from cloud"""
        try:
            if not self.user_token:
                return False
            
            # Get remote files list
            response = requests.get(
                f"{self.api_url}/sync/files",
                headers={'Authorization': f'Bearer {self.user_token}'},
                timeout=10
            )
            
            if response.status_code != 200:
                return False
            
            remote_files = response.json().get('files', [])
            
            for file_info in remote_files:
                file_path = Path.home() / file_info['file_path']
                
                # Check if local file exists and is newer
                should_download = True
                
                if file_path.exists():
                    local_modified = file_path.stat().st_mtime
                    remote_modified = file_info['modified']
                    
                    if local_modified >= remote_modified:
                        should_download = False
                
                if should_download:
                    self.sync_status.emit(f"Downloading {file_path.name}...")
                    
                    # Download file content
                    file_response = requests.get(
                        f"{self.api_url}/sync/download/{file_info['id']}",
                        headers={'Authorization': f'Bearer {self.user_token}'},
                        timeout=30
                    )
                    
                    if file_response.status_code == 200:
                        # Verify checksum
                        downloaded_content = file_response.content
                        checksum = hashlib.sha256(downloaded_content).hexdigest()
                        
                        if checksum == file_info['checksum']:
                            # Save file
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            file_path.write_bytes(downloaded_content)
                            
                            # Set modification time
                            import os
                            os.utime(file_path, (file_info['modified'], file_info['modified']))
                            
                            self.logger.info(f"Downloaded {file_path.name}")
                        else:
                            self.logger.error(f"Checksum mismatch for {file_path.name}")
                            return False
                    else:
                        self.logger.error(f"Failed to download {file_path.name}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return False
    
    def get_settings_files(self) -> Dict[Path, bytes]:
        """Get all settings files"""
        settings_files = {}
        
        # Main config file
        config_file = Path.home() / '.mouse_config' / 'config.json'
        if config_file.exists():
            settings_files[config_file] = config_file.read_bytes()
        
        # Profiles
        profiles_dir = Path.home() / '.mouse_config' / 'profiles'
        if profiles_dir.exists():
            for profile_file in profiles_dir.glob('*.json'):
                settings_files[profile_file] = profile_file.read_bytes()
        
        # Macros
        macros_dir = Path.home() / '.mouse_config' / 'macros'
        if macros_dir.exists():
            for macro_file in macros_dir.glob('*.json'):
                settings_files[macro_file] = macro_file.read_bytes()
        
        # Logs (recent ones only)
        logs_dir = Path.home() / '.mouse_config' / 'logs'
        if logs_dir.exists():
            for log_file in sorted(logs_dir.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                if log_file.stat().st_size < 1024 * 1024:  # Less than 1MB
                    settings_files[log_file] = log_file.read_bytes()
        
        return settings_files
    
    def get_device_id(self) -> str:
        """Get unique device identifier"""
        try:
            import platform
            import uuid
            
            # Create a unique device ID based on system info
            system_info = f"{platform.system()}-{platform.node()}-{platform.machine()}"
            device_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
            
            return device_id
            
        except Exception:
            return str(uuid.uuid4())
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            'logged_in': self.user_token is not None,
            'user_id': self.user_id,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'pending_uploads': len(self.pending_uploads),
            'pending_downloads': len(self.pending_downloads),
            'sync_interval': self.sync_interval
        }
    
    def set_sync_interval(self, seconds: int):
        """Set sync interval in seconds"""
        self.sync_interval = max(60, seconds)  # Minimum 1 minute
    
    def stop(self):
        """Stop the sync service"""
        self.should_stop = True


class CloudSettingsManager:
    """Manage cloud settings and preferences"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings_file = Path.home() / '.mouse_config' / 'cloud_settings.json'
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load cloud settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                return self.get_default_settings()
        except Exception as e:
            self.logger.error(f"Error loading cloud settings: {e}")
            return self.get_default_settings()
    
    def save_settings(self) -> bool:
        """Save cloud settings"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cloud settings: {e}")
            return False
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default cloud settings"""
        return {
            'enabled': False,
            'auto_sync': True,
            'sync_interval': 300,  # 5 minutes
            'sync_settings': True,
            'sync_profiles': True,
            'sync_macros': True,
            'sync_logs': False,
            'last_sync': None,
            'user_email': '',
            'remember_login': False
        }
    
    def update_setting(self, key: str, value: Any):
        """Update a specific setting"""
        self.settings[key] = value
        self.save_settings()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting"""
        return self.settings.get(key, default)
