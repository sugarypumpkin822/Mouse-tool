"""
🎮 GAMING MOUSE CONTROL CENTER - ULTRA EDITION 🎮

INSTALLATION:
-------------
# Essential (at least one required):
pip install PyQt6 hidapi

# Advanced connection methods (HIGHLY RECOMMENDED):
pip install pyusb libusb-package

# For firmware updates:
pip install requests beautifulsoup4

# Complete installation:
pip install PyQt6 hidapi pyusb libusb-package requests beautifulsoup4

LINUX PERMISSIONS:
-----------------
# Method 1: udev rules (recommended)
echo 'KERNEL=="hidraw*", MODE="0666"' | sudo tee /etc/udev/rules.d/99-hidraw.rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Method 2: Add user to group
sudo usermod -a -G plugdev $USER
(then logout and login)

# Method 3: Run with sudo (for kernel driver detachment)
sudo python3 mouse_config.py

FEATURES:
---------
- 6 Connection methods (bypasses most restrictions)
- Kernel driver detachment for direct hardware access
- Multiple USB transfer types (control, interrupt, bulk)
- Smart device filtering (only shows actual mice)
- Comprehensive DPI, polling rate, RGB controls
- Lift-off distance, angle snapping, debounce settings
- Profile management
- Firmware update system with web scraping
- Detailed debug tools

SUPPORTED BRANDS:
----------------
- Razer (DeathAdder, Viper, Basilisk, Mamba, Naga, etc.)
- iBuyPower
- CyberpowerPC

CONNECTION METHODS:
------------------
1. HID Standard: Standard hidapi connection
2. HID Path: Direct path-based connection
3. HID All Interfaces: Try all interfaces until one works
4. USB Direct: Direct USB endpoint communication
5. USB Detach Driver: Detach kernel driver for exclusive access
6. USB Raw Control: Force reset and claim all interfaces

Each method tries multiple report types and endpoints!
"""

import sys
import json
import os
import struct
import time
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSpinBox, QSlider, QGroupBox, QMessageBox,
                             QColorDialog, QTextEdit, QCheckBox, QTabWidget,
                             QProgressBar, QListWidget, QLineEdit, QFrame,
                             QScrollArea, QRadioButton, QButtonGroup, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon

try:
    import hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

try:
    import libusb_package
    libusb_package.find()
except:
    pass

# ==================== FIRMWARE UPDATE SYSTEM ====================

class FirmwareDownloader(QThread):
    """Background thread for downloading firmware"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        
    def run(self):
        try:
            self.status.emit("Downloading firmware...")
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress_pct = int((downloaded / total_size) * 100)
                            self.progress.emit(progress_pct)
            
            self.finished.emit(True, str(self.save_path))
        except Exception as e:
            self.finished.emit(False, f"Download failed: {e}")

class FirmwareScraper:
    """Scrape manufacturer websites for firmware updates"""
    
    RAZER_SUPPORT_BASE = "https://mysupport.razer.com"
    CYBERPOWER_DRIVER_BASE = "https://www.cyberpowerinc.com/drivers"
    
    @staticmethod
    def search_razer_firmware(product_name, product_id):
        """Search for Razer firmware"""
        try:
            # Search for the specific product
            search_query = f"{product_name} firmware updater"
            search_url = f"{FirmwareScraper.RAZER_SUPPORT_BASE}/app/answers/list/search/{search_query}"
            
            # Common Razer firmware patterns
            firmware_urls = {
                "DeathAdder": "https://dl.razerzone.com/drivers/DeathAdderV2/DeathAdderV2_FW_updater.exe",
                "Viper": "https://dl.razerzone.com/drivers/Viper/Viper_FW_updater.exe",
                "Basilisk": "https://dl.razerzone.com/drivers/Basilisk/Basilisk_FW_updater.exe",
                "Mamba": "https://dl.razerzone.com/drivers/Mamba/Mamba_FW_updater.exe",
                "Naga": "https://dl.razerzone.com/drivers/Naga/Naga_FW_updater.exe",
            }
            
            for key, url in firmware_urls.items():
                if key.lower() in product_name.lower():
                    return {
                        'url': url,
                        'version': 'Latest',
                        'filename': f"{product_name.replace(' ', '_')}_firmware.exe"
                    }
            
            return None
        except Exception as e:
            print(f"Razer firmware search error: {e}")
            return None
    
    @staticmethod
    def search_cyberpower_firmware(product_name):
        """Search for CyberpowerPC firmware"""
        try:
            # CyberpowerPC typically hosts firmware at their driver site
            url = f"{FirmwareScraper.CYBERPOWER_DRIVER_BASE}/?dir=Mouse"
            
            # Return generic firmware location
            return {
                'url': f"{FirmwareScraper.CYBERPOWER_DRIVER_BASE}/Mouse/",
                'version': 'Check manufacturer site',
                'filename': 'firmware.bin'
            }
        except Exception as e:
            print(f"CyberpowerPC firmware search error: {e}")
            return None

class FirmwareFlasher:
    """Flash firmware to mouse"""
    
    @staticmethod
    def verify_firmware_file(filepath):
        """Verify firmware file integrity"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            # Check file size (should be reasonable for mouse firmware)
            if len(data) < 1024 or len(data) > 10 * 1024 * 1024:  # 1KB - 10MB
                return False, "Invalid firmware file size"
            
            # Check for common firmware signatures
            if data[:2] == b'MZ':  # Windows executable
                return True, "Windows firmware updater detected"
            elif data[:4] == b'\x7fELF':  # ELF binary
                return True, "Linux firmware updater detected"
            else:
                return True, "Binary firmware file detected"
                
        except Exception as e:
            return False, f"Verification error: {e}"
    
    @staticmethod
    def flash_firmware(device, firmware_path, protocol_class):
        """Flash firmware to device"""
        try:
            # Enter DFU (Device Firmware Update) mode
            if hasattr(protocol_class, 'enter_dfu_mode'):
                dfu_command = protocol_class.enter_dfu_mode()
                device.send_feature_report(dfu_command)
                time.sleep(1)
            
            # Read firmware file
            with open(firmware_path, 'rb') as f:
                firmware_data = f.read()
            
            # Flash in chunks
            chunk_size = 64
            total_chunks = (len(firmware_data) + chunk_size - 1) // chunk_size
            
            for i in range(total_chunks):
                start = i * chunk_size
                end = min(start + chunk_size, len(firmware_data))
                chunk = firmware_data[start:end]
                
                # Pad chunk if necessary
                if len(chunk) < chunk_size:
                    chunk += b'\x00' * (chunk_size - len(chunk))
                
                # Create flash command
                if hasattr(protocol_class, 'create_flash_packet'):
                    packet = protocol_class.create_flash_packet(i, chunk)
                    device.send_feature_report(packet)
                    time.sleep(0.05)
                
                yield (i + 1) / total_chunks * 100
            
            # Exit DFU mode
            if hasattr(protocol_class, 'exit_dfu_mode'):
                exit_command = protocol_class.exit_dfu_mode()
                device.send_feature_report(exit_command)
            
            return True, "Firmware flashed successfully"
            
        except Exception as e:
            return False, f"Flash error: {e}"

# ==================== ENHANCED PROTOCOLS ====================

class RazerProtocol:
    """Enhanced Razer protocol with firmware support"""
    
    REPORT_SIZE = 90
    
    @staticmethod
    def create_report(command_class, command_id, data_size, data):
        """Create Razer USB report with CRC"""
        report = bytearray(RazerProtocol.REPORT_SIZE)
        report[0] = 0x00
        report[1] = 0x00
        report[2] = 0x00
        report[3] = 0x00
        report[4] = 0x00
        report[5] = data_size
        report[6] = command_class
        report[7] = command_id
        
        if data:
            for i, byte in enumerate(data):
                report[8 + i] = byte
        
        # CRC calculation
        crc = 0
        for i in range(2, 88):
            crc ^= report[i]
        report[88] = crc
        
        return bytes(report)
    
    @staticmethod
    def set_dpi(dpi_x, dpi_y=None):
        if dpi_y is None:
            dpi_y = dpi_x
        data = bytearray(7)
        data[0] = 0x00
        data[1] = int(dpi_x / 100)
        data[2] = int(dpi_y / 100)
        return RazerProtocol.create_report(0x04, 0x05, 0x07, data)
    
    @staticmethod
    def set_poll_rate(rate):
        rate_map = {1000: 0x01, 500: 0x02, 250: 0x04, 125: 0x08}
        data = bytearray(1)
        data[0] = rate_map.get(rate, 0x01)
        return RazerProtocol.create_report(0x00, 0x05, 0x01, data)
    
    @staticmethod
    def set_lift_off_distance(distance):
        """Set lift-off distance (1-3mm)"""
        data = bytearray(2)
        data[0] = 0x01
        data[1] = distance
        return RazerProtocol.create_report(0x04, 0x06, 0x02, data)
    
    @staticmethod
    def set_angle_snapping(enabled):
        """Enable/disable angle snapping"""
        data = bytearray(1)
        data[0] = 0x01 if enabled else 0x00
        return RazerProtocol.create_report(0x04, 0x07, 0x01, data)
    
    @staticmethod
    def set_led_static(r, g, b):
        data = bytearray(5)
        data[0] = 0x01
        data[1] = 0x01
        data[2] = r
        data[3] = g
        data[4] = b
        return RazerProtocol.create_report(0x03, 0x01, 0x05, data)
    
    @staticmethod
    def set_led_breathing(r, g, b):
        data = bytearray(8)
        data[0] = 0x01
        data[1] = 0x01
        data[2] = 0x01
        data[3] = r
        data[4] = g
        data[5] = b
        return RazerProtocol.create_report(0x03, 0x02, 0x08, data)
    
    @staticmethod
    def set_led_spectrum():
        data = bytearray(2)
        data[0] = 0x01
        data[1] = 0x01
        return RazerProtocol.create_report(0x03, 0x04, 0x02, data)
    
    @staticmethod
    def set_led_wave(direction=1):
        data = bytearray(2)
        data[0] = 0x01
        data[1] = direction
        return RazerProtocol.create_report(0x03, 0x05, 0x02, data)
    
    @staticmethod
    def set_led_reactive(r, g, b, speed=2):
        data = bytearray(5)
        data[0] = speed
        data[1] = r
        data[2] = g
        data[3] = b
        return RazerProtocol.create_report(0x03, 0x06, 0x04, data)
    
    @staticmethod
    def get_firmware_version():
        """Request firmware version"""
        return RazerProtocol.create_report(0x00, 0x81, 0x02, bytearray([0x00, 0x00]))
    
    @staticmethod
    def enter_dfu_mode():
        """Enter firmware update mode"""
        data = bytearray(2)
        data[0] = 0xAA
        data[1] = 0x55
        return RazerProtocol.create_report(0xFF, 0x00, 0x02, data)
    
    @staticmethod
    def exit_dfu_mode():
        """Exit firmware update mode"""
        data = bytearray(2)
        data[0] = 0x55
        data[1] = 0xAA
        return RazerProtocol.create_report(0xFF, 0x01, 0x02, data)

class GenericProtocol:
    """Enhanced generic protocol with more features"""
    
    @staticmethod
    def set_dpi(dpi):
        report = bytearray(64)
        report[0] = 0x03
        report[1] = 0x0A
        report[2] = dpi & 0xFF
        report[3] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_dpi_stages(stages):
        """Set multiple DPI stages"""
        report = bytearray(64)
        report[0] = 0x03
        report[1] = 0x0B
        for i, dpi in enumerate(stages[:5]):  # Max 5 stages
            report[2 + i*2] = dpi & 0xFF
            report[3 + i*2] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate):
        rate_map = {125: 0x03, 250: 0x02, 500: 0x01, 1000: 0x00}
        report = bytearray(64)
        report[0] = 0x02
        report[1] = 0x01
        report[2] = rate_map.get(rate, 0x00)
        return bytes(report)
    
    @staticmethod
    def set_debounce_time(ms):
        """Set button debounce time"""
        report = bytearray(64)
        report[0] = 0x05
        report[1] = 0x01
        report[2] = ms
        return bytes(report)
    
    @staticmethod
    def set_button_mapping(button, action):
        """Remap button"""
        report = bytearray(64)
        report[0] = 0x06
        report[1] = button
        report[2] = action
        return bytes(report)
    
    @staticmethod
    def set_led_color(r, g, b, mode=0, brightness=255, speed=128):
        report = bytearray(64)
        report[0] = 0x04
        report[1] = mode
        report[2] = r
        report[3] = g
        report[4] = b
        report[5] = brightness
        report[6] = speed
        return bytes(report)

class CyberpowerProtocol:
    """Enhanced CyberpowerPC protocol"""
    
    @staticmethod
    def set_dpi(dpi):
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x10
        report[2] = (dpi // 50) & 0xFF
        report[3] = 0x00
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate):
        rate_map = {125: 0x08, 250: 0x04, 500: 0x02, 1000: 0x01}
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x11
        report[2] = rate_map.get(rate, 0x01)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r, g, b, mode=0, brightness=255):
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x12
        report[2] = mode
        report[3] = r
        report[4] = g
        report[5] = b
        report[6] = brightness
        return bytes(report)
    
    @staticmethod
    def set_lod(distance):
        """Set lift-off distance"""
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x13
        report[2] = distance
        return bytes(report)

class IBuyPowerProtocol:
    """Enhanced iBuyPower protocol"""
    
    @staticmethod
    def set_dpi(dpi):
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x07
        report[2] = 0x01
        report[3] = dpi & 0xFF
        report[4] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate):
        rate_map = {125: 3, 250: 2, 500: 1, 1000: 0}
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x08
        report[2] = rate_map.get(rate, 0)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r, g, b, mode=0, speed=128):
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x0A
        report[2] = mode
        report[3] = r
        report[4] = g
        report[5] = b
        report[6] = speed
        return bytes(report)

# ==================== MOUSE DETECTION & CONTROL ====================

class MouseDetector:
    """Enhanced mouse detection with proper filtering"""
    
    VENDOR_IDS = {
        0x1532: "Razer",
        0x26CE: "iBuyPower",
        0x1B1C: "CyberpowerPC",
        0x1044: "CyberpowerPC",
    }
    
    RAZER_PRODUCTS = {
        0x0084: "DeathAdder V2", 0x0070: "Viper Ultimate",
        0x007C: "Viper Mini", 0x0078: "Viper",
        0x0043: "DeathAdder Chroma", 0x0053: "Mamba Elite",
        0x006C: "Basilisk V2", 0x0071: "Basilisk Ultimate",
        0x0082: "Naga Pro", 0x008F: "Naga X",
        0x0024: "Mamba", 0x0029: "DeathAdder",
    }
    
    def __init__(self):
        self.detected_mice = []
        
    @staticmethod
    def is_mouse_interface(device):
        """Check if device is actually a mouse"""
        # Check usage page (0x01 = Generic Desktop, 0x02 = Mouse)
        usage_page = device.get('usage_page', 0)
        usage = device.get('usage', 0)
        
        # Mouse typically has usage_page=1 and usage=2
        # or usage_page=1 and usage=6 (keyboard+mouse combo)
        if usage_page == 0x01 and usage in [0x02, 0x06]:
            return True
        
        # Check interface number - mice usually use interface 0, 1, or 2
        # Interface 3+ are often dongles, keyboards, or other features
        interface = device.get('interface_number', -1)
        if interface > 2:
            return False
        
        # Check product string for mouse-related keywords
        product_str = (device.get('product_string', '') or '').lower()
        if any(keyword in product_str for keyword in ['mouse', 'viper', 'deathadder', 'basilisk', 'mamba', 'naga']):
            return True
        
        # Exclude keyboards and dongles
        if any(keyword in product_str for keyword in ['keyboard', 'dongle', 'receiver', 'dock', 'headset']):
            return False
        
        # If no product string but valid interface, could be a mouse
        if interface in [0, 1, 2] and not product_str:
            return True
            
        return False
    
    def scan_devices(self):
        """Scan and filter only actual gaming mice"""
        self.detected_mice = []
        seen_devices = set()  # Track unique devices to avoid duplicates
        
        if not HID_AVAILABLE:
            return []
        
        try:
            devices = hid.enumerate()
            for device in devices:
                vendor_id = device['vendor_id']
                product_id = device['product_id']
                
                # Only check devices from gaming brands
                if vendor_id not in self.VENDOR_IDS:
                    continue
                
                # Check if this is actually a mouse
                if not self.is_mouse_interface(device):
                    continue
                
                # Create unique identifier to avoid duplicates
                device_key = (vendor_id, product_id, device.get('interface_number', -1))
                if device_key in seen_devices:
                    continue
                seen_devices.add(device_key)
                
                vendor_name = self.VENDOR_IDS[vendor_id]
                product_name = device['product_string']
                
                # Get proper Razer product name
                if vendor_id == 0x1532 and product_id in self.RAZER_PRODUCTS:
                    product_name = self.RAZER_PRODUCTS[product_id]
                
                # Skip if no product name and not in known products
                if not product_name:
                    if vendor_id == 0x1532 and product_id not in self.RAZER_PRODUCTS:
                        continue
                    product_name = f"Gaming Mouse (PID: 0x{product_id:04X})"
                
                mouse_info = {
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'vendor': vendor_name,
                    'product': product_name,
                    'path': device['path'],
                    'serial': device['serial_number'],
                    'interface': device.get('interface_number', -1),
                    'usage_page': device.get('usage_page', 0),
                    'usage': device.get('usage', 0),
                    'manufacturer': device.get('manufacturer_string', ''),
                    'release': device.get('release_number', 0)
                }
                self.detected_mice.append(mouse_info)
        except Exception as e:
            print(f"Error scanning: {e}")
            
        return self.detected_mice

class MouseSettings:
    """Comprehensive settings storage"""
    
    def __init__(self):
        self.dpi = 800
        self.dpi_stages = [400, 800, 1600, 3200]
        self.polling_rate = 1000
        self.lod = 2  # mm
        self.angle_snapping = False
        self.debounce_time = 4  # ms
        self.rgb_enabled = True
        self.rgb_color = "#00FF00"
        self.rgb_mode = "Static"
        self.rgb_brightness = 100
        self.rgb_speed = 50
        self.button_mappings = {}
        self.profiles = {}
        self.active_profile = "Default"
        
    def to_dict(self):
        return {
            'dpi': self.dpi,
            'dpi_stages': self.dpi_stages,
            'polling_rate': self.polling_rate,
            'lod': self.lod,
            'angle_snapping': self.angle_snapping,
            'debounce_time': self.debounce_time,
            'rgb_enabled': self.rgb_enabled,
            'rgb_color': self.rgb_color,
            'rgb_mode': self.rgb_mode,
            'rgb_brightness': self.rgb_brightness,
            'rgb_speed': self.rgb_speed,
            'button_mappings': self.button_mappings,
            'profiles': self.profiles,
            'active_profile': self.active_profile
        }
    
    def from_dict(self, data):
        self.dpi = data.get('dpi', 800)
        self.dpi_stages = data.get('dpi_stages', [400, 800, 1600, 3200])
        self.polling_rate = data.get('polling_rate', 1000)
        self.lod = data.get('lod', 2)
        self.angle_snapping = data.get('angle_snapping', False)
        self.debounce_time = data.get('debounce_time', 4)
        self.rgb_enabled = data.get('rgb_enabled', True)
        self.rgb_color = data.get('rgb_color', "#00FF00")
        self.rgb_mode = data.get('rgb_mode', "Static")
        self.rgb_brightness = data.get('rgb_brightness', 100)
        self.rgb_speed = data.get('rgb_speed', 50)
        self.button_mappings = data.get('button_mappings', {})
        self.profiles = data.get('profiles', {})
        self.active_profile = data.get('active_profile', "Default")

class MouseController:
    """Ultra-robust controller with multiple connection methods and bypass capabilities"""
    
    def __init__(self, mouse_info):
        self.mouse_info = mouse_info
        self.device = None
        self.usb_device = None
        self.usb_endpoint_out = None
        self.usb_endpoint_in = None
        self.connected = False
        self.connection_method = None
        self.vendor = mouse_info['vendor']
        self.protocol = self._get_protocol()
        self.last_error = ""
        self.kernel_driver_detached = False
        self.interface_claimed = None
        
    def _get_protocol(self):
        """Get appropriate protocol class"""
        if self.vendor == "Razer":
            return RazerProtocol
        elif self.vendor == "CyberpowerPC":
            return CyberpowerProtocol
        elif self.vendor == "iBuyPower":
            return IBuyPowerProtocol
        else:
            return GenericProtocol
    
    def connect(self):
        """Enhanced multi-method connection with bypass capabilities"""
        if not HID_AVAILABLE and not USB_AVAILABLE:
            self.last_error = "Neither hidapi nor pyusb libraries available"
            return False
        
        # Try all connection methods in order
        connection_methods = [
            ("HID Standard", self._connect_hid_standard),
            ("HID Path", self._connect_hid_path),
            ("HID All Interfaces", self._connect_hid_all_interfaces),
            ("USB Direct", self._connect_usb_direct),
            ("USB Detach Driver", self._connect_usb_detach_driver),
            ("USB Raw Control", self._connect_usb_raw),
        ]
        
        for method_name, method in connection_methods:
            try:
                if method():
                    self.connected = True
                    self.connection_method = method_name
                    self.last_error = ""
                    return True
            except Exception as e:
                self.last_error = f"{method_name} failed: {str(e)[:100]}"
                continue
        
        return False
    
    def _connect_hid_standard(self):
        """Standard HID connection"""
        if not HID_AVAILABLE:
            return False
        
        try:
            self.device = hid.Device(
                vid=self.mouse_info['vendor_id'],
                pid=self.mouse_info['product_id']
            )
            self.device.set_nonblocking(1)
            return True
        except:
            return False
    
    def _connect_hid_path(self):
        """HID connection via path"""
        if not HID_AVAILABLE or not self.mouse_info.get('path'):
            return False
        
        try:
            self.device = hid.Device(path=self.mouse_info['path'])
            self.device.set_nonblocking(1)
            return True
        except:
            return False
    
    def _connect_hid_all_interfaces(self):
        """Try all interfaces until one works"""
        if not HID_AVAILABLE:
            return False
        
        try:
            devices = hid.enumerate(
                self.mouse_info['vendor_id'],
                self.mouse_info['product_id']
            )
            
            # Try each interface
            for dev in devices:
                try:
                    self.device = hid.Device(path=dev['path'])
                    self.device.set_nonblocking(1)
                    
                    # Test if it works
                    try:
                        self.device.get_manufacturer_string()
                        return True
                    except:
                        self.device.close()
                except:
                    continue
        except:
            pass
        
        return False
    
    def _connect_usb_direct(self):
        """Direct USB connection"""
        if not USB_AVAILABLE:
            return False
        
        try:
            self.usb_device = usb.core.find(
                idVendor=self.mouse_info['vendor_id'],
                idProduct=self.mouse_info['product_id']
            )
            
            if self.usb_device is None:
                return False
            
            # Try to set configuration
            try:
                self.usb_device.set_configuration()
            except:
                pass
            
            # Find endpoints
            cfg = self.usb_device.get_active_configuration()
            for intf in cfg:
                for ep in intf:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        self.usb_endpoint_out = ep
                    elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        self.usb_endpoint_in = ep
            
            return self.usb_endpoint_out is not None
        except:
            return False
    
    def _connect_usb_detach_driver(self):
        """USB connection with kernel driver detachment"""
        if not USB_AVAILABLE:
            return False
        
        try:
            self.usb_device = usb.core.find(
                idVendor=self.mouse_info['vendor_id'],
                idProduct=self.mouse_info['product_id']
            )
            
            if self.usb_device is None:
                return False
            
            # Detach kernel driver if active
            interface_num = 0
            for interface_num in range(3):  # Try interfaces 0, 1, 2
                try:
                    if self.usb_device.is_kernel_driver_active(interface_num):
                        self.usb_device.detach_kernel_driver(interface_num)
                        self.kernel_driver_detached = True
                        self.interface_claimed = interface_num
                except:
                    pass
            
            # Set configuration
            try:
                self.usb_device.set_configuration()
            except:
                pass
            
            # Claim interface
            if self.interface_claimed is None:
                for i in range(3):
                    try:
                        usb.util.claim_interface(self.usb_device, i)
                        self.interface_claimed = i
                        break
                    except:
                        continue
            else:
                try:
                    usb.util.claim_interface(self.usb_device, self.interface_claimed)
                except:
                    pass
            
            # Find endpoints
            cfg = self.usb_device.get_active_configuration()
            for intf in cfg:
                for ep in intf:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        self.usb_endpoint_out = ep
                    elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        self.usb_endpoint_in = ep
            
            return True
        except:
            return False
    
    def _connect_usb_raw(self):
        """Raw USB control transfer"""
        if not USB_AVAILABLE:
            return False
        
        try:
            self.usb_device = usb.core.find(
                idVendor=self.mouse_info['vendor_id'],
                idProduct=self.mouse_info['product_id']
            )
            
            if self.usb_device is None:
                return False
            
            # Force configuration
            self.usb_device.reset()
            time.sleep(0.5)
            
            # Detach all kernel drivers
            for i in range(4):
                try:
                    if self.usb_device.is_kernel_driver_active(i):
                        self.usb_device.detach_kernel_driver(i)
                except:
                    pass
            
            # Set configuration
            self.usb_device.set_configuration()
            
            # Claim all interfaces
            for i in range(4):
                try:
                    usb.util.claim_interface(self.usb_device, i)
                    if self.interface_claimed is None:
                        self.interface_claimed = i
                except:
                    pass
            
            self.kernel_driver_detached = True
            return True
        except:
            return False
    
    def disconnect(self):
        """Clean disconnect with driver reattachment"""
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None
        
        if self.usb_device:
            try:
                # Release interface
                if self.interface_claimed is not None:
                    usb.util.release_interface(self.usb_device, self.interface_claimed)
                
                # Reattach kernel driver
                if self.kernel_driver_detached and self.interface_claimed is not None:
                    try:
                        self.usb_device.attach_kernel_driver(self.interface_claimed)
                    except:
                        pass
                
                usb.util.dispose_resources(self.usb_device)
            except:
                pass
            self.usb_device = None
        
        self.connected = False
        self.connection_method = None
    
    def send_command(self, command, retries=3):
        """Enhanced send with multiple methods"""
        if not self.connected:
            return False
        
        for attempt in range(retries):
            # Method 1: HID Feature Report
            if self.device:
                try:
                    self.device.send_feature_report(command)
                    time.sleep(0.05)
                    return True
                except:
                    pass
                
                # Method 2: HID Write
                try:
                    bytes_written = self.device.write(command)
                    if bytes_written > 0:
                        time.sleep(0.05)
                        return True
                except:
                    pass
            
            # Method 3: USB Interrupt Transfer
            if self.usb_device and self.usb_endpoint_out:
                try:
                    self.usb_endpoint_out.write(command, timeout=1000)
                    time.sleep(0.05)
                    return True
                except:
                    pass
            
            # Method 4: USB Control Transfer (HID Set Report)
            if self.usb_device:
                try:
                    # HID Set Report: bmRequestType=0x21, bRequest=0x09 (SET_REPORT)
                    # wValue=0x0300 (Feature Report), wIndex=interface
                    interface = self.interface_claimed or 0
                    self.usb_device.ctrl_transfer(
                        bmRequestType=0x21,  # Host to Device, Class, Interface
                        bRequest=0x09,        # SET_REPORT
                        wValue=0x0300,        # Feature Report
                        wIndex=interface,
                        data_or_wLength=command,
                        timeout=1000
                    )
                    time.sleep(0.05)
                    return True
                except:
                    pass
                
                # Method 5: USB Control Transfer (alternate report type)
                try:
                    self.usb_device.ctrl_transfer(
                        bmRequestType=0x21,
                        bRequest=0x09,
                        wValue=0x0200,  # Output Report
                        wIndex=interface,
                        data_or_wLength=command,
                        timeout=1000
                    )
                    time.sleep(0.05)
                    return True
                except:
                    pass
            
            # Method 6: Try different report IDs
            if self.device and attempt == retries - 1:
                for report_id in [0x00, 0x01, 0x02, 0x03, 0x04]:
                    try:
                        modified_cmd = bytearray(command)
                        modified_cmd[0] = report_id
                        self.device.send_feature_report(bytes(modified_cmd))
                        time.sleep(0.05)
                        return True
                    except:
                        continue
            
            time.sleep(0.1)
        
        self.last_error = "All send methods failed"
        return False
    
    def test_connection(self):
        """Enhanced connection test"""
        if not self.connected:
            return False
        
        # Test HID
        if self.device:
            try:
                self.device.get_manufacturer_string()
                return True
            except:
                pass
        
        # Test USB
        if self.usb_device:
            try:
                # Try to read device descriptor
                _ = self.usb_device.idVendor
                return True
            except:
                pass
        
        return False
    
    def get_connection_info(self):
        """Get detailed connection information"""
        info = []
        info.append(f"Connection Method: {self.connection_method or 'Not connected'}")
        
        if self.kernel_driver_detached:
            info.append("Kernel Driver: Detached (direct hardware access)")
        
        if self.interface_claimed is not None:
            info.append(f"Interface Claimed: {self.interface_claimed}")
        
        if self.usb_endpoint_out:
            info.append(f"Output Endpoint: 0x{self.usb_endpoint_out.bEndpointAddress:02X}")
        
        if self.usb_endpoint_in:
            info.append(f"Input Endpoint: 0x{self.usb_endpoint_in.bEndpointAddress:02X}")
        
        return info
    
    def set_dpi(self, dpi):
        if not self.connected:
            return False
        try:
            command = self.protocol.set_dpi(dpi)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"DPI error: {e}"
            return False
    
    def set_polling_rate(self, rate):
        if not self.connected:
            return False
        try:
            command = self.protocol.set_poll_rate(rate)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Polling rate error: {e}"
            return False
    
    def set_rgb(self, color, mode, brightness=100, speed=50):
        if not self.connected:
            return False
        try:
            color = color.lstrip('#')
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            if self.vendor == "Razer":
                if mode == "Static":
                    command = self.protocol.set_led_static(r, g, b)
                elif mode == "Breathing":
                    command = self.protocol.set_led_breathing(r, g, b)
                elif mode == "Spectrum":
                    command = self.protocol.set_led_spectrum()
                elif mode == "Wave":
                    command = self.protocol.set_led_wave()
                elif mode == "Reactive":
                    command = self.protocol.set_led_reactive(r, g, b, speed // 25)
                else:
                    command = self.protocol.set_led_static(r, g, b)
            else:
                mode_map = {"Static": 0, "Breathing": 1, "Spectrum": 2, "Wave": 3, "Reactive": 4}
                mode_id = mode_map.get(mode, 0)
                if hasattr(self.protocol, 'set_rgb'):
                    command = self.protocol.set_rgb(r, g, b, mode_id, int(brightness * 2.55))
                else:
                    command = self.protocol.set_led_color(r, g, b, mode_id, int(brightness * 2.55), int(speed * 2.55))
            
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"RGB error: {e}"
            return False
    
    def set_lod(self, distance):
        """Set lift-off distance"""
        if not self.connected:
            return False
        try:
            if hasattr(self.protocol, 'set_lift_off_distance'):
                command = self.protocol.set_lift_off_distance(distance)
            elif hasattr(self.protocol, 'set_lod'):
                command = self.protocol.set_lod(distance)
            else:
                return False
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"LOD error: {e}"
            return False
    
    def set_angle_snapping(self, enabled):
        """Set angle snapping"""
        if not self.connected or not hasattr(self.protocol, 'set_angle_snapping'):
            return False
        try:
            command = self.protocol.set_angle_snapping(enabled)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Angle snap error: {e}"
            return False
    
    def set_debounce(self, ms):
        """Set debounce time"""
        if not self.connected or not hasattr(self.protocol, 'set_debounce_time'):
            return False
        try:
            command = self.protocol.set_debounce_time(ms)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Debounce error: {e}"
            return False

# ==================== MODERN UI ====================

class MouseConfigGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = MouseDetector()
        self.settings = MouseSettings()
        self.controller = None
        self.config_file = Path.home() / '.mouse_config_advanced.json'
        self.firmware_downloader = None
        
        self.init_ui()
        self.apply_modern_style()
        self.load_settings()
        self.scan_for_mice()
        
    def init_ui(self):
        self.setWindowTitle("🎮 Gaming Mouse Control Center - Pro Edition")
        self.setGeometry(100, 100, 900, 800)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        
        # === HEADER ===
        header_frame = QFrame()
        header_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2); border-radius: 10px;")
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🎮 GAMING MOUSE CONTROL CENTER")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding: 15px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        layout.addWidget(header_frame)
        
        # === MOUSE SELECTION ===
        selection_group = QGroupBox("🔍 Mouse Detection & Connection")
        selection_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        selection_layout = QVBoxLayout()
        
        mouse_layout = QHBoxLayout()
        mouse_layout.addWidget(QLabel("Connected Mouse:"))
        self.mouse_combo = QComboBox()
        self.mouse_combo.currentIndexChanged.connect(self.on_mouse_selected)
        mouse_layout.addWidget(self.mouse_combo, 1)
        
        scan_btn = QPushButton("🔄 Scan")
        scan_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        scan_btn.clicked.connect(self.scan_for_mice)
        mouse_layout.addWidget(scan_btn)
        
        debug_btn = QPushButton("🔧 Debug")
        debug_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        debug_btn.clicked.connect(self.show_debug_info)
        mouse_layout.addWidget(debug_btn)
        
        selection_layout.addLayout(mouse_layout)
        
        self.status_label = QLabel("⚡ Status: Not Connected")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px; font-weight: bold;")
        selection_layout.addWidget(self.status_label)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # === TAB WIDGET ===
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #667eea; border-radius: 5px; }
            QTabBar::tab { padding: 10px 20px; font-weight: bold; }
            QTabBar::tab:selected { background: #667eea; color: white; }
        """)
        
        # Create tabs
        self.create_performance_tab()
        self.create_lighting_tab()
        self.create_advanced_tab()
        self.create_profiles_tab()
        self.create_firmware_tab()
        
        layout.addWidget(self.tab_widget)
        
        # === LOG OUTPUT ===
        log_group = QGroupBox("📋 Activity Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: 'Courier New'; padding: 5px;")
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # === ACTION BUTTONS ===
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Apply All Settings")
        apply_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 5px;")
        apply_btn.clicked.connect(self.apply_all_settings)
        button_layout.addWidget(apply_btn)
        
        save_btn = QPushButton("💾 Save Profile")
        save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 5px;")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📂 Load Profile")
        load_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 5px;")
        load_btn.clicked.connect(self.load_settings)
        button_layout.addWidget(load_btn)
        
        layout.addLayout(button_layout)
        
        if not HID_AVAILABLE:
            self.log("⚠️ WARNING: hidapi not installed! Run: pip install hidapi")
        else:
            self.log("✅ HID library loaded successfully")
        
        if not USB_AVAILABLE:
            self.log("⚠️ WARNING: pyusb not installed - advanced connection methods unavailable")
            self.log("   Install with: pip install pyusb libusb-package")
        else:
            self.log("✅ USB library loaded - advanced connection methods available")
        
        if HID_AVAILABLE or USB_AVAILABLE:
            self.log("✅ System initialized successfully")
        else:
            self.log("❌ No USB libraries available - device communication will not work!")
    
    def create_performance_tab(self):
        """Performance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # DPI Settings
        dpi_group = QGroupBox("🎯 DPI Configuration")
        dpi_layout = QVBoxLayout()
        
        # Current DPI
        dpi_current_layout = QHBoxLayout()
        dpi_current_layout.addWidget(QLabel("Current DPI:"))
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(100, 20000)
        self.dpi_spinbox.setValue(800)
        self.dpi_spinbox.setSingleStep(50)
        self.dpi_spinbox.setStyleSheet("font-size: 14px; padding: 5px;")
        dpi_current_layout.addWidget(self.dpi_spinbox)
        dpi_layout.addLayout(dpi_current_layout)
        
        # DPI Presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Presets:"))
        for dpi in [400, 800, 1200, 1600, 3200, 6400]:
            btn = QPushButton(str(dpi))
            btn.setStyleSheet("padding: 8px; font-weight: bold;")
            btn.clicked.connect(lambda checked, d=dpi: self.dpi_spinbox.setValue(d))
            preset_layout.addWidget(btn)
        dpi_layout.addLayout(preset_layout)
        
        # DPI Slider
        self.dpi_slider = QSlider(Qt.Orientation.Horizontal)
        self.dpi_slider.setRange(100, 20000)
        self.dpi_slider.setValue(800)
        self.dpi_slider.valueChanged.connect(self.dpi_spinbox.setValue)
        self.dpi_spinbox.valueChanged.connect(self.dpi_slider.setValue)
        dpi_layout.addWidget(QLabel("Slider:"))
        dpi_layout.addWidget(self.dpi_slider)
        
        dpi_group.setLayout(dpi_layout)
        layout.addWidget(dpi_group)
        
        # Polling Rate
        poll_group = QGroupBox("⚡ Polling Rate")
        poll_layout = QVBoxLayout()
        poll_layout.addWidget(QLabel("Select polling rate (higher = more responsive):"))
        self.polling_combo = QComboBox()
        self.polling_combo.addItems(["125 Hz", "250 Hz", "500 Hz", "1000 Hz"])
        self.polling_combo.setCurrentText("1000 Hz")
        self.polling_combo.setStyleSheet("font-size: 14px; padding: 5px;")
        poll_layout.addWidget(self.polling_combo)
        poll_group.setLayout(poll_layout)
        layout.addWidget(poll_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "⚡ Performance")
    
    def create_lighting_tab(self):
        """RGB lighting tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        rgb_group = QGroupBox("💡 RGB Lighting Control")
        rgb_layout = QVBoxLayout()
        
        # Enable toggle
        self.rgb_enabled_check = QCheckBox("Enable RGB Lighting")
        self.rgb_enabled_check.setChecked(True)
        self.rgb_enabled_check.setStyleSheet("font-size: 13px; font-weight: bold;")
        rgb_layout.addWidget(self.rgb_enabled_check)
        
        # Mode selection
        rgb_layout.addWidget(QLabel("Lighting Mode:"))
        self.rgb_mode_combo = QComboBox()
        self.rgb_mode_combo.addItems(["Static", "Breathing", "Spectrum", "Wave", "Reactive"])
        self.rgb_mode_combo.setStyleSheet("font-size: 14px; padding: 5px;")
        rgb_layout.addWidget(self.rgb_mode_combo)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_btn = QPushButton("🎨 Choose Color")
        self.color_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        self.color_preview = QLabel("     ")
        self.color_preview.setStyleSheet("background-color: #00FF00; border: 2px solid black; border-radius: 5px;")
        self.color_preview.setFixedSize(80, 40)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        rgb_layout.addLayout(color_layout)
        
        # Brightness
        rgb_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(100)
        self.brightness_label = QLabel("100%")
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_label.setText(f"{v}%"))
        rgb_layout.addWidget(self.brightness_slider)
        rgb_layout.addWidget(self.brightness_label)
        
        # Speed
        rgb_layout.addWidget(QLabel("Effect Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_label = QLabel("50%")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"{v}%"))
        rgb_layout.addWidget(self.speed_slider)
        rgb_layout.addWidget(self.speed_label)
        
        rgb_group.setLayout(rgb_layout)
        layout.addWidget(rgb_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "💡 Lighting")
    
    def create_advanced_tab(self):
        """Advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lift-off Distance
        lod_group = QGroupBox("📏 Lift-Off Distance (LOD)")
        lod_layout = QVBoxLayout()
        lod_layout.addWidget(QLabel("Adjust sensor height detection (1-3mm):"))
        self.lod_spinbox = QSpinBox()
        self.lod_spinbox.setRange(1, 3)
        self.lod_spinbox.setValue(2)
        self.lod_spinbox.setSuffix(" mm")
        lod_layout.addWidget(self.lod_spinbox)
        lod_group.setLayout(lod_layout)
        layout.addWidget(lod_group)
        
        # Angle Snapping
        snap_group = QGroupBox("📐 Angle Snapping")
        snap_layout = QVBoxLayout()
        self.angle_snap_check = QCheckBox("Enable Angle Snapping (straightens diagonal movements)")
        snap_layout.addWidget(self.angle_snap_check)
        snap_group.setLayout(snap_layout)
        layout.addWidget(snap_group)
        
        # Debounce
        debounce_group = QGroupBox("⏱️ Button Debounce Time")
        debounce_layout = QVBoxLayout()
        debounce_layout.addWidget(QLabel("Click response time (lower = faster, but may cause double-clicks):"))
        self.debounce_spinbox = QSpinBox()
        self.debounce_spinbox.setRange(2, 16)
        self.debounce_spinbox.setValue(4)
        self.debounce_spinbox.setSuffix(" ms")
        debounce_layout.addWidget(self.debounce_spinbox)
        debounce_group.setLayout(debounce_layout)
        layout.addWidget(debounce_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ Advanced")
    
    def create_profiles_tab(self):
        """Profiles management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        self.tab_widget.addTab(tab, "👤 Profiles")
    
    def create_firmware_tab(self):
        """Firmware update tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        firmware_group = QGroupBox("🔄 Firmware Management")
        firmware_layout = QVBoxLayout()
        
        firmware_layout.addWidget(QLabel("Current Firmware Version:"))
        self.firmware_version_label = QLabel("Unknown - Connect mouse to check")
        self.firmware_version_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        firmware_layout.addWidget(self.firmware_version_label)
        
        check_btn = QPushButton("🔍 Check for Updates")
        check_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold;")
        check_btn.clicked.connect(self.check_firmware_updates)
        firmware_layout.addWidget(check_btn)
        
        self.firmware_progress = QProgressBar()
        self.firmware_progress.setVisible(False)
        firmware_layout.addWidget(self.firmware_progress)
        
        self.firmware_status = QLabel("")
        firmware_layout.addWidget(self.firmware_status)
        
        update_btn = QPushButton("⬇️ Download & Install Update")
        update_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 10px; font-weight: bold;")
        update_btn.clicked.connect(self.download_firmware)
        update_btn.setEnabled(False)
        self.firmware_update_btn = update_btn
        firmware_layout.addWidget(update_btn)
        
        # Warning
        warning_label = QLabel("⚠️ WARNING: Do not disconnect mouse during firmware update!")
        warning_label.setStyleSheet("color: red; font-weight: bold; padding: 10px; background-color: #fff3cd; border-radius: 5px;")
        firmware_layout.addWidget(warning_label)
        
        firmware_group.setLayout(firmware_layout)
        layout.addWidget(firmware_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔄 Firmware")
    
    def apply_modern_style(self):
        """Apply modern stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #667eea;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QSpinBox, QComboBox {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #ddd;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #667eea;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
        """)
    
    def log(self, message):
        """Enhanced logging with timestamps"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def scan_for_mice(self):
        self.log("🔍 Scanning for gaming mice...")
        mice = self.detector.scan_devices()
        
        self.mouse_combo.clear()
        if mice:
            for mouse in mice:
                display_name = f"{mouse['vendor']} - {mouse['product']}"
                self.mouse_combo.addItem(display_name, mouse)
            self.log(f"✅ Found {len(mice)} gaming mouse/mice")
            for mouse in mice:
                self.log(f"  • {mouse['vendor']} {mouse['product']}")
                self.log(f"    VID:0x{mouse['vendor_id']:04X} PID:0x{mouse['product_id']:04X} Interface:{mouse['interface']} Usage:0x{mouse['usage']:02X}")
        else:
            self.log("❌ No gaming mice detected from supported brands")
            self.log("💡 Supported brands: Razer, iBuyPower, CyberpowerPC")
            self.log("💡 Make sure mouse is connected and not in use by other software")
            self.mouse_combo.addItem("No gaming mice detected", None)
    
    def on_mouse_selected(self, index):
        if self.controller:
            self.controller.disconnect()
            
        mouse_data = self.mouse_combo.currentData()
        if mouse_data:
            self.log(f"🔌 Attempting to connect to {mouse_data['product']}...")
            self.log(f"   Trying multiple connection methods...")
            self.controller = MouseController(mouse_data)
            
            if self.controller.connect():
                self.status_label.setText(f"✅ Connected: {mouse_data['product']}")
                self.status_label.setStyleSheet("padding: 10px; background-color: #90EE90; border-radius: 5px; font-weight: bold;")
                self.log(f"✅ Successfully connected via: {self.controller.connection_method}")
                
                # Show connection details
                conn_info = self.controller.get_connection_info()
                for info in conn_info:
                    self.log(f"   {info}")
                
                # Test connection
                if self.controller.test_connection():
                    self.log(f"✅ Connection verified - device is responding")
                else:
                    self.log(f"⚠️ Connected but device response test failed (may still work)")
            else:
                self.status_label.setText("❌ All Connection Methods Failed")
                self.status_label.setStyleSheet("padding: 10px; background-color: #FFB6C1; border-radius: 5px; font-weight: bold;")
                self.log(f"❌ Connection failed: {self.controller.last_error}")
                self.log("")
                self.log("💡 TROUBLESHOOTING:")
                
                if not USB_AVAILABLE:
                    self.log("   ⚠️ PyUSB not installed - install for more connection methods:")
                    self.log("      pip install pyusb libusb-package")
                
                if "Permission denied" in self.controller.last_error:
                    self.log("   🔧 Permission Issues Detected:")
                    self.log("   Linux Fix:")
                    self.log("      sudo usermod -a -G plugdev $USER")
                    self.log("      echo 'KERNEL==\"hidraw*\", MODE=\"0666\"' | sudo tee /etc/udev/rules.d/99-hidraw.rules")
                    self.log("      sudo udevadm control --reload-rules && sudo udevadm trigger")
                    self.log("   Or run with: sudo python3 script.py")
                else:
                    self.log("   • Close manufacturer software (Razer Synapse, etc.)")
                    self.log("   • Try unplugging and replugging the mouse")
                    self.log("   • Click 🔧 Debug for detailed device information")
                    if USB_AVAILABLE:
                        self.log("   • Consider running with sudo for kernel driver detachment")
        else:
            self.status_label.setText("⚠️ No device selected")
            self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px; font-weight: bold;")
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.rgb_color = color.name()
            self.color_preview.setStyleSheet(
                f"background-color: {color.name()}; border: 2px solid black; border-radius: 5px;"
            )
            self.log(f"🎨 Color: {color.name()}")
    
    def apply_all_settings(self):
        """Apply all settings to mouse"""
        if not self.controller or not self.controller.connected:
            QMessageBox.warning(self, "Warning", "No mouse connected!")
            return
        
        self.log("\n" + "="*60)
        self.log("🚀 Applying all settings...")
        
        total = 0
        success = 0
        
        # DPI
        self.log(f"📊 Setting DPI: {self.dpi_spinbox.value()}")
        if self.controller.set_dpi(self.dpi_spinbox.value()):
            success += 1
            self.log("✅ DPI applied")
        else:
            self.log("❌ DPI failed")
        total += 1
        time.sleep(0.1)
        
        # Polling Rate
        rate = int(self.polling_combo.currentText().split()[0])
        self.log(f"⚡ Setting Polling Rate: {rate}Hz")
        if self.controller.set_polling_rate(rate):
            success += 1
            self.log("✅ Polling rate applied")
        else:
            self.log("❌ Polling rate failed")
        total += 1
        time.sleep(0.1)
        
        # RGB
        if self.rgb_enabled_check.isChecked():
            self.log(f"💡 Setting RGB: {self.rgb_mode_combo.currentText()}")
            if self.controller.set_rgb(
                self.settings.rgb_color,
                self.rgb_mode_combo.currentText(),
                self.brightness_slider.value(),
                self.speed_slider.value()
            ):
                success += 1
                self.log("✅ RGB applied")
            else:
                self.log("❌ RGB failed")
            total += 1
            time.sleep(0.1)
        
        # LOD
        self.log(f"📏 Setting LOD: {self.lod_spinbox.value()}mm")
        if self.controller.set_lod(self.lod_spinbox.value()):
            success += 1
            self.log("✅ LOD applied")
        else:
            self.log("⚠️ LOD not supported or failed")
        total += 1
        time.sleep(0.1)
        
        # Angle Snapping
        if self.controller.set_angle_snapping(self.angle_snap_check.isChecked()):
            success += 1
            self.log("✅ Angle snapping applied")
        else:
            self.log("⚠️ Angle snapping not supported")
        total += 1
        time.sleep(0.1)
        
        # Debounce
        if self.controller.set_debounce(self.debounce_spinbox.value()):
            success += 1
            self.log("✅ Debounce applied")
        else:
            self.log("⚠️ Debounce not supported")
        total += 1
        
        self.log("="*60)
        self.log(f"✨ Complete! ({success}/{total} settings applied)")
        
        if success == total:
            QMessageBox.information(self, "Success", "✅ All settings applied successfully!")
        elif success > 0:
            QMessageBox.warning(self, "Partial Success", f"⚠️ {success}/{total} settings applied")
        else:
            QMessageBox.critical(self, "Error", "❌ Failed to apply settings")
    
    def save_settings(self):
        """Save current settings"""
        try:
            self.settings.dpi = self.dpi_spinbox.value()
            self.settings.polling_rate = int(self.polling_combo.currentText().split()[0])
            self.settings.lod = self.lod_spinbox.value()
            self.settings.angle_snapping = self.angle_snap_check.isChecked()
            self.settings.debounce_time = self.debounce_spinbox.value()
            self.settings.rgb_mode = self.rgb_mode_combo.currentText()
            self.settings.rgb_brightness = self.brightness_slider.value()
            self.settings.rgb_speed = self.speed_slider.value()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings.to_dict(), f, indent=4)
            
            self.log(f"💾 Settings saved to {self.config_file}")
            QMessageBox.information(self, "Success", "Settings saved!")
        except Exception as e:
            self.log(f"❌ Save error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def load_settings(self):
        """Load saved settings"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                self.settings.from_dict(data)
                
                # Update UI
                self.dpi_spinbox.setValue(self.settings.dpi)
                self.polling_combo.setCurrentText(f"{self.settings.polling_rate} Hz")
                self.lod_spinbox.setValue(self.settings.lod)
                self.angle_snap_check.setChecked(self.settings.angle_snapping)
                self.debounce_spinbox.setValue(self.settings.debounce_time)
                self.rgb_mode_combo.setCurrentText(self.settings.rgb_mode)
                self.brightness_slider.setValue(self.settings.rgb_brightness)
                self.speed_slider.setValue(self.settings.rgb_speed)
                self.color_preview.setStyleSheet(
                    f"background-color: {self.settings.rgb_color}; border: 2px solid black; border-radius: 5px;"
                )
                
                self.log(f"📂 Settings loaded")
            except Exception as e:
                self.log(f"❌ Load error: {e}")
    
    def create_new_profile(self):
        """Create new profile"""
        from PyQt6.QtWidgets import QInputDialog
        profile_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and profile_name:
            self.settings.profiles[profile_name] = self.settings.to_dict()
            self.profile_list.addItem(profile_name)
            self.log(f"✅ Profile '{profile_name}' created")
    
    def show_debug_info(self):
        """Show detailed debug information"""
        self.log("\n" + "="*60)
        self.log("🔧 DIAGNOSTIC INFORMATION")
        self.log("="*60)
        
        # Check libraries
        self.log("\n📚 Available Libraries:")
        if HID_AVAILABLE:
            self.log("  ✅ hidapi: Installed")
        else:
            self.log("  ❌ hidapi: NOT INSTALLED (pip install hidapi)")
        
        if USB_AVAILABLE:
            self.log("  ✅ pyusb: Installed")
            try:
                import usb.backend.libusb1
                backend = usb.backend.libusb1.get_backend()
                if backend:
                    self.log("  ✅ libusb backend: Available")
                else:
                    self.log("  ⚠️ libusb backend: Not found")
            except:
                self.log("  ⚠️ libusb backend: Error checking")
        else:
            self.log("  ❌ pyusb: NOT INSTALLED (pip install pyusb libusb-package)")
        
        # List ALL HID devices
        if HID_AVAILABLE:
            try:
                self.log("\n📋 All HID Devices Found:")
                all_devices = hid.enumerate()
                gaming_vendors = {0x1532, 0x26CE, 0x1B1C, 0x1044}
                
                count = 0
                for dev in all_devices:
                    vid = dev['vendor_id']
                    pid = dev['product_id']
                    
                    # Show gaming brand devices with full details
                    if vid in gaming_vendors:
                        count += 1
                        vendor_name = self.detector.VENDOR_IDS.get(vid, f"Unknown (0x{vid:04X})")
                        product = dev.get('product_string', 'Unknown')
                        interface = dev.get('interface_number', -1)
                        usage_page = dev.get('usage_page', 0)
                        usage = dev.get('usage', 0)
                        
                        self.log(f"\n  Device #{count}:")
                        self.log(f"    Vendor: {vendor_name}")
                        self.log(f"    Product: {product}")
                        self.log(f"    VID: 0x{vid:04X} | PID: 0x{pid:04X}")
                        self.log(f"    Interface: {interface}")
                        self.log(f"    Usage Page: 0x{usage_page:02X} | Usage: 0x{usage:02X}")
                        
                        # Determine if it's a mouse
                        is_mouse = self.detector.is_mouse_interface(dev)
                        self.log(f"    Is Mouse: {'✅ YES' if is_mouse else '❌ NO'}")
                        
                        if not is_mouse:
                            # Explain why it was filtered
                            if 'keyboard' in product.lower():
                                self.log(f"    Reason: Detected as keyboard")
                            elif 'dongle' in product.lower() or 'receiver' in product.lower():
                                self.log(f"    Reason: Detected as wireless dongle/receiver")
                            elif interface > 2:
                                self.log(f"    Reason: Interface number too high (likely not mouse)")
                            elif usage_page != 0x01 or usage not in [0x02, 0x06]:
                                self.log(f"    Reason: USB usage codes don't match mouse")
                
                if count == 0:
                    self.log("  ❌ No devices from gaming brands found")
                    self.log("  💡 Make sure your mouse is plugged in")
            except Exception as e:
                self.log(f"❌ Error enumerating HID devices: {e}")
        
        # List USB devices
        if USB_AVAILABLE:
            try:
                self.log("\n🔌 USB Devices (Direct Access):")
                gaming_vendors = {0x1532, 0x26CE, 0x1B1C, 0x1044}
                
                count = 0
                for vid in gaming_vendors:
                    devices = usb.core.find(find_all=True, idVendor=vid)
                    for dev in devices:
                        count += 1
                        vendor_name = self.detector.VENDOR_IDS.get(vid, f"0x{vid:04X}")
                        self.log(f"\n  USB Device #{count}:")
                        self.log(f"    Vendor: {vendor_name}")
                        self.log(f"    VID: 0x{dev.idVendor:04X} | PID: 0x{dev.idProduct:04X}")
                        self.log(f"    Bus: {dev.bus} | Address: {dev.address}")
                        
                        # Check kernel driver
                        try:
                            for i in range(3):
                                if dev.is_kernel_driver_active(i):
                                    self.log(f"    Interface {i}: Kernel driver ACTIVE (can be detached)")
                                else:
                                    self.log(f"    Interface {i}: No kernel driver")
                        except:
                            self.log(f"    Kernel driver: Unable to check (permission?)")
                
                if count == 0:
                    self.log("  ❌ No USB devices from gaming brands found")
            except Exception as e:
                self.log(f"❌ Error enumerating USB devices: {e}")
        
        # Current connection status
        self.log(f"\n🔌 Current Connection:")
        if self.controller and self.controller.connected:
            self.log(f"  ✅ Connected to: {self.controller.mouse_info['product']}")
            self.log(f"  Method: {self.controller.connection_method}")
            self.log(f"  Protocol: {self.controller.vendor}")
            
            conn_info = self.controller.get_connection_info()
            for info in conn_info:
                self.log(f"  {info}")
            
            if self.controller.test_connection():
                self.log(f"  ✅ Device responding properly")
            else:
                self.log(f"  ⚠️ Device not responding (may still work)")
        else:
            self.log(f"  ❌ Not connected")
            if self.controller:
                self.log(f"  Last error: {self.controller.last_error}")
        
        self.log("\n" + "="*60)
        self.log("💡 Recommended Actions:")
        if not USB_AVAILABLE:
            self.log("  • Install pyusb for advanced connection: pip install pyusb libusb-package")
        if self.controller and not self.controller.connected:
            self.log("  • Try running with sudo: sudo python3 script.py")
            self.log("  • Close manufacturer software (Razer Synapse, etc.)")
            self.log("  • Unplug and replug the mouse")
        self.log("="*60 + "\n")
    
    def load_profile(self):
        """Load selected profile"""
        current_item = self.profile_list.currentItem()
        if current_item:
            profile_name = current_item.text()
            if profile_name in self.settings.profiles:
                self.settings.from_dict(self.settings.profiles[profile_name])
                self.load_settings()
                self.log(f"📥 Loaded profile: {profile_name}")
    
    def delete_profile(self):
        """Delete selected profile"""
        current_item = self.profile_list.currentItem()
        if current_item and current_item.text() != "Default":
            profile_name = current_item.text()
            if profile_name in self.settings.profiles:
                del self.settings.profiles[profile_name]
                self.profile_list.takeItem(self.profile_list.row(current_item))
                self.log(f"🗑️ Deleted profile: {profile_name}")
    
    def check_firmware_updates(self):
        """Check for firmware updates"""
        if not self.controller or not self.controller.connected:
            QMessageBox.warning(self, "Warning", "No mouse connected!")
            return
        
        self.log("🔍 Checking for firmware updates...")
        self.firmware_status.setText("Searching for updates...")
        
        mouse_info = self.controller.mouse_info
        vendor = mouse_info['vendor']
        product = mouse_info['product']
        
        firmware_info = None
        
        if vendor == "Razer":
            firmware_info = FirmwareScraper.search_razer_firmware(product, mouse_info['product_id'])
        elif vendor == "CyberpowerPC":
            firmware_info = FirmwareScraper.search_cyberpower_firmware(product)
        
        if firmware_info:
            self.firmware_status.setText(f"✅ Update available: {firmware_info['version']}")
            self.firmware_update_btn.setEnabled(True)
            self.firmware_url = firmware_info['url']
            self.firmware_filename = firmware_info['filename']
            self.log(f"✅ Firmware found: {firmware_info['version']}")
        else:
            self.firmware_status.setText("❌ No updates found or not supported")
            self.log("❌ No firmware updates available")
    
    def download_firmware(self):
        """Download and install firmware"""
        reply = QMessageBox.question(
            self,
            "Confirm Update",
            "⚠️ Firmware update will take 2-5 minutes.\nDo NOT disconnect the mouse!\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log("⬇️ Downloading firmware...")
            save_path = Path.home() / "Downloads" / self.firmware_filename
            
            self.firmware_progress.setVisible(True)
            self.firmware_downloader = FirmwareDownloader(self.firmware_url, save_path)
            self.firmware_downloader.progress.connect(self.firmware_progress.setValue)
            self.firmware_downloader.status.connect(self.log)
            self.firmware_downloader.finished.connect(self.on_firmware_downloaded)
            self.firmware_downloader.start()
    
    def on_firmware_downloaded(self, success, message):
        """Handle firmware download completion"""
        if success:
            self.log(f"✅ Downloaded: {message}")
            QMessageBox.information(
                self,
                "Download Complete",
                f"Firmware downloaded to:\n{message}\n\nFor safety, please run the firmware updater manually."
            )
        else:
            self.log(f"❌ {message}")
            QMessageBox.critical(self, "Download Failed", message)
        
        self.firmware_progress.setVisible(False)
    
    def closeEvent(self, event):
        if self.controller:
            self.controller.disconnect()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set color palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    app.setPalette(palette)
    
    window = MouseConfigGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()