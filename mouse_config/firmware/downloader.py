"""
Firmware download system
"""

import requests
import time
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    import logging
    get_logger = lambda name: logging.getLogger(name)


class FirmwareDownloader(QThread):
    """Background thread for downloading firmware"""
    
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url: str, save_path: Path):
        super().__init__()
        self.logger = get_logger(__name__)
        self.url = url
        self.save_path = save_path
        self.should_stop = False
        
    def run(self):
        """Download firmware file"""
        try:
            self.status.emit("Downloading firmware...")
            self.logger.info(f"Starting download from {self.url}")
            
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Ensure directory exists
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.should_stop:
                        self.status.emit("Download cancelled")
                        self.finished.emit(False, "Download cancelled by user")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size:
                            progress_pct = int((downloaded / total_size) * 100)
                            self.progress.emit(progress_pct)
            
            self.logger.info(f"Firmware downloaded successfully to {self.save_path}")
            self.finished.emit(True, str(self.save_path))
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            self.logger.error(f"Download failed: {error_msg}")
            self.finished.emit(False, error_msg)
        except Exception as e:
            error_msg = f"Download error: {e}"
            self.logger.error(f"Download failed: {error_msg}")
            self.finished.emit(False, error_msg)
    
    def stop(self):
        """Stop the download"""
        self.should_stop = True


class FirmwareManager:
    """Manage firmware downloads and updates"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.current_download: Optional[FirmwareDownloader] = None
        
    def download_firmware(self, url: str, save_path: Path) -> FirmwareDownloader:
        """Start firmware download"""
        try:
            self.logger.info(f"Starting firmware download: {url}")
            
            # Cancel any existing download
            if self.current_download and self.current_download.isRunning():
                self.current_download.stop()
                self.current_download.wait()
            
            # Start new download
            self.current_download = FirmwareDownloader(url, save_path)
            return self.current_download
            
        except Exception as e:
            self.logger.error(f"Error starting firmware download: {e}")
            raise
    
    def verify_firmware_file(self, file_path: Path) -> tuple[bool, str]:
        """Verify firmware file integrity"""
        try:
            if not file_path.exists():
                return False, "File does not exist"
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size < 1024:  # Less than 1KB
                return False, "File too small to be valid firmware"
            elif file_size > 50 * 1024 * 1024:  # More than 50MB
                return False, "File too large to be valid firmware"
            
            # Check file signature
            with open(file_path, 'rb') as f:
                header = f.read(4)
            
            # Check for common firmware signatures
            if header.startswith(b'MZ'):  # Windows executable
                return True, "Windows firmware updater detected"
            elif header.startswith(b'\x7fELF'):  # ELF binary
                return True, "Linux firmware updater detected"
            elif header.startswith(b'\xfe\xed\xfa'):  # Mach-O binary
                return True, "macOS firmware updater detected"
            elif header.startswith(b'FW'):  # Generic firmware
                return True, "Generic firmware file detected"
            else:
                return True, "Binary firmware file detected"
                
        except Exception as e:
            error_msg = f"Verification error: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_download_info(self, url: str) -> dict:
        """Get information about a firmware download"""
        try:
            response = requests.head(url, timeout=10)
            response.raise_for_status()
            
            return {
                'url': url,
                'size': int(response.headers.get('content-length', 0)),
                'type': response.headers.get('content-type', 'unknown'),
                'available': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting download info: {e}")
            return {
                'url': url,
                'size': 0,
                'type': 'unknown',
                'available': False,
                'error': str(e)
            }
    
    def cancel_download(self):
        """Cancel current download"""
        if self.current_download and self.current_download.isRunning():
            self.logger.info("Cancelling firmware download")
            self.current_download.stop()
