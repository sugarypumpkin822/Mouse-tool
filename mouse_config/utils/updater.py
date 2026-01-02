"""
Auto-update system for the mouse configuration tool
"""

import os
import sys
import json
import requests
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import threading
from PyQt6.QtCore import QThread, pyqtSignal

from .logger import get_logger
from .helpers import safe_execute


class UpdateChecker(QThread):
    """Background thread for checking updates"""
    
    update_available = pyqtSignal(dict)
    check_complete = pyqtSignal(bool, str)
    
    def __init__(self, repo_url: str = "https://api.github.com/repos/sugarypumpkin822/Mouse-tool"):
        super().__init__()
        self.logger = get_logger(__name__)
        self.repo_url = repo_url
        self.api_url = "https://api.github.com/repos/sugarypumpkin822/Mouse-tool"
        
    def run(self):
        """Check for updates"""
        try:
            self.logger.info("Checking for updates...")
            
            # Get current version
            current_version = self.get_current_version()
            
            # Get latest release info
            release_info = self.get_latest_release()
            
            if release_info:
                latest_version = release_info.get('tag_name', '').lstrip('v')
                
                if self.is_newer_version(latest_version, current_version):
                    update_info = {
                        'current_version': current_version,
                        'latest_version': latest_version,
                        'release_name': release_info.get('name', ''),
                        'release_notes': release_info.get('body', ''),
                        'download_url': release_info.get('zipball_url', ''),
                        'published_at': release_info.get('published_at', ''),
                        'prerelease': release_info.get('prerelease', False)
                    }
                    
                    self.logger.info(f"Update available: {current_version} -> {latest_version}")
                    self.update_available.emit(update_info)
                    self.check_complete.emit(True, "Update available")
                else:
                    self.logger.info(f"Up to date: {current_version}")
                    self.check_complete.emit(False, "Up to date")
            else:
                self.logger.error("Failed to get release information")
                self.check_complete.emit(False, "Failed to check for updates")
                
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            self.check_complete.emit(False, f"Update check failed: {e}")
    
    def get_current_version(self) -> str:
        """Get current application version"""
        try:
            version_file = Path(__file__).parent.parent.parent / "VERSION"
            if version_file.exists():
                return version_file.read_text().strip()
            else:
                # Try to get from __init__.py
                init_file = Path(__file__).parent.parent.parent / "mouse_config" / "__init__.py"
                if init_file.exists():
                    content = init_file.read_text()
                    for line in content.split('\n'):
                        if '__version__' in line:
                            return line.split('=')[1].strip().strip('"\'')
                
                # Fallback version
                return "2.0.0"
        except Exception as e:
            self.logger.error(f"Error getting current version: {e}")
            return "2.0.0"
    
    def get_latest_release(self) -> Optional[Dict]:
        """Get latest release information from GitHub"""
        try:
            # Get releases from GitHub API
            response = requests.get(f"{self.api_url}/releases", timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            
            # Find the latest non-prerelease release
            for release in releases:
                if not release.get('prerelease', False) and not release.get('draft', False):
                    return release
            
            # If no stable release, return the latest
            if releases:
                return releases[0]
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting release info: {e}")
            return None
    
    def is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings"""
        try:
            def version_tuple(v):
                return tuple(map(int, (v.split("."))))
            
            return version_tuple(latest) > version_tuple(current)
            
        except Exception:
            return False


class UpdateDownloader(QThread):
    """Background thread for downloading and installing updates"""
    
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, update_info: Dict):
        super().__init__()
        self.logger = get_logger(__name__)
        self.update_info = update_info
        self.should_stop = False
    
    def run(self):
        """Download and install update"""
        try:
            self.status.emit("Preparing update...")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download update
                self.status.emit("Downloading update...")
                if not self.download_update(temp_path):
                    self.finished.emit(False, "Download failed")
                    return
                
                # Verify download
                self.status.emit("Verifying download...")
                if not self.verify_download(temp_path):
                    self.finished.emit(False, "Download verification failed")
                    return
                
                # Install update
                self.status.emit("Installing update...")
                if not self.install_update(temp_path):
                    self.finished.emit(False, "Installation failed")
                    return
                
                self.status.emit("Update completed successfully!")
                self.finished.emit(True, "Update installed successfully")
                
        except Exception as e:
            self.logger.error(f"Update installation failed: {e}")
            self.finished.emit(False, f"Installation failed: {e}")
    
    def download_update(self, temp_path: Path) -> bool:
        """Download update from GitHub"""
        try:
            download_url = self.update_info.get('download_url')
            if not download_url:
                self.logger.error("No download URL available")
                return False
            
            # Download the zip file
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            zip_path = temp_path / "update.zip"
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.should_stop:
                        return False
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)
            
            self.logger.info(f"Downloaded update to {zip_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False
    
    def verify_download(self, temp_path: Path) -> bool:
        """Verify downloaded update"""
        try:
            zip_path = temp_path / "update.zip"
            
            if not zip_path.exists():
                self.logger.error("Downloaded file not found")
                return False
            
            # Check file size
            file_size = zip_path.stat().st_size
            if file_size < 1024:  # Less than 1KB
                self.logger.error("Downloaded file too small")
                return False
            
            # Check if it's a valid zip file
            import zipfile
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    files = zf.namelist()
                    if not files:
                        self.logger.error("Downloaded file is not a valid zip")
                        return False
            except zipfile.BadZipFile:
                self.logger.error("Downloaded file is not a valid zip")
                return False
            
            self.logger.info("Download verification passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    def install_update(self, temp_path: Path) -> bool:
        """Install the update"""
        try:
            zip_path = temp_path / "update.zip"
            app_dir = Path(__file__).parent.parent.parent
            
            # Extract update
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_path / "extracted")
            
            extracted_path = temp_path / "extracted"
            
            # Find the extracted directory
            extracted_dirs = [d for d in extracted_path.iterdir() if d.is_dir()]
            if not extracted_dirs:
                self.logger.error("No extracted directory found")
                return False
            
            source_dir = extracted_dirs[0]
            
            # Backup current installation
            backup_dir = app_dir.parent / f"{app_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.status.emit("Creating backup...")
            
            if app_dir.exists():
                shutil.copytree(app_dir, backup_dir)
                self.logger.info(f"Created backup at {backup_dir}")
            
            # Copy new files
            self.status.emit("Installing new files...")
            for item in source_dir.iterdir():
                dest_path = app_dir / item.name
                
                if item.is_file():
                    shutil.copy2(item, dest_path)
                elif item.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(item, dest_path)
            
            # Update version file
            version_file = app_dir / "VERSION"
            version_file.write_text(self.update_info['latest_version'])
            
            self.logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return False
    
    def stop(self):
        """Stop the update process"""
        self.should_stop = True


class UpdateManager:
    """Manage application updates"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.update_checker = None
        self.update_downloader = None
        
    def check_for_updates(self) -> UpdateChecker:
        """Start checking for updates"""
        self.update_checker = UpdateChecker()
        return self.update_checker
    
    def download_update(self, update_info: Dict) -> UpdateDownloader:
        """Start downloading and installing update"""
        self.update_downloader = UpdateDownloader(update_info)
        return self.update_downloader
    
    def get_changelog(self, version: str = None) -> Optional[str]:
        """Get changelog information"""
        try:
            response = requests.get("https://api.github.com/repos/sugarypumpkin822/Mouse-tool/releases", timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            
            changelog = "# Changelog\n\n"
            
            for release in releases[:10]:  # Last 10 releases
                release_version = release.get('tag_name', '').lstrip('v')
                release_name = release.get('name', '')
                release_date = release.get('published_at', '')[:10]
                release_notes = release.get('body', '')
                
                changelog += f"## {release_version} - {release_date}\n"
                changelog += f"**{release_name}**\n\n"
                changelog += f"{release_notes}\n\n"
                changelog += "---\n\n"
            
            return changelog
            
        except Exception as e:
            self.logger.error(f"Error getting changelog: {e}")
            return None
    
    def create_backup(self) -> bool:
        """Create a backup of the current installation"""
        try:
            app_dir = Path(__file__).parent.parent.parent
            backup_dir = app_dir.parent / f"{app_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if app_dir.exists():
                shutil.copytree(app_dir, backup_dir)
                self.logger.info(f"Created backup at {backup_dir}")
                return True
            else:
                self.logger.warning("Application directory not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore from backup"""
        try:
            app_dir = Path(__file__).parent.parent.parent
            
            if backup_path.exists() and backup_path.is_dir():
                if app_dir.exists():
                    shutil.rmtree(app_dir)
                
                shutil.copytree(backup_path, app_dir)
                self.logger.info(f"Restored from backup: {backup_path}")
                return True
            else:
                self.logger.error("Backup path does not exist")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            return False
