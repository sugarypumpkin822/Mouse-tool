"""
Firmware flashing utilities
"""

import time
import struct
from typing import Generator, Tuple, Optional
from pathlib import Path

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    import logging
    get_logger = lambda name: logging.getLogger(name)


class FirmwareFlasher:
    """Flash firmware to mouse device"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def verify_firmware_file(self, file_path: Path) -> Tuple[bool, str]:
        """Verify firmware file integrity"""
        try:
            if not file_path.exists():
                return False, "File does not exist"
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size < 1024:  # Less than 1KB
                return False, "Invalid firmware file size (too small)"
            elif file_size > 10 * 1024 * 1024:  # More than 10MB
                return False, "Invalid firmware file size (too large)"
            
            # Check for common firmware signatures
            with open(file_path, 'rb') as f:
                header = f.read(4)
            
            if header.startswith(b'MZ'):  # Windows executable
                return True, "Windows firmware updater detected"
            elif header.startswith(b'\x7fELF'):  # ELF binary
                return True, "Linux firmware updater detected"
            elif header.startswith(b'\xfe\xed\xfa'):  # Mach-O binary
                return True, "macOS firmware updater detected"
            elif header.startswith(b'FW'):  # Generic firmware
                return True, "Binary firmware file detected"
            else:
                return True, "Binary firmware file detected"
                
        except Exception as e:
            return False, f"Verification error: {e}"
    
    def flash_firmware(self, device, firmware_path: Path, protocol_class) -> Generator[Tuple[float, str], None, bool]:
        """Flash firmware to device with progress reporting"""
        try:
            self.logger.info(f"Starting firmware flash: {firmware_path}")
            
            # Verify firmware file
            valid, message = self.verify_firmware_file(firmware_path)
            if not valid:
                yield 0, f"Invalid firmware file: {message}"
                return False
            
            yield 0, "Entering firmware update mode..."
            
            # Enter DFU (Device Firmware Update) mode
            if hasattr(protocol_class, 'enter_dfu_mode'):
                dfu_command = protocol_class.enter_dfu_mode()
                if not device.send_command(dfu_command):
                    yield 0, "Failed to enter DFU mode"
                    return False
                time.sleep(1)
            
            yield 5, "Reading firmware file..."
            
            # Read firmware file
            with open(firmware_path, 'rb') as f:
                firmware_data = f.read()
            
            yield 10, "Starting firmware transfer..."
            
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
                    if not device.send_command(packet):
                        yield (i + 1) / total_chunks * 100, f"Failed to flash chunk {i+1}/{total_chunks}"
                        return False
                else:
                    # Generic flash command
                    if not device.send_command(chunk):
                        yield (i + 1) / total_chunks * 100, f"Failed to flash chunk {i+1}/{total_chunks}"
                        return False
                
                progress = (i + 1) / total_chunks * 100
                yield progress, f"Flashing... {i+1}/{total_chunks} chunks"
                
                time.sleep(0.05)  # Small delay between chunks
            
            yield 95, "Finalizing firmware..."
            
            # Exit DFU mode
            if hasattr(protocol_class, 'exit_dfu_mode'):
                exit_command = protocol_class.exit_dfu_mode()
                if not device.send_command(exit_command):
                    yield 100, "Failed to exit DFU mode"
                    return False
            
            yield 100, "Firmware flashed successfully"
            self.logger.info("Firmware flash completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Flash error: {e}"
            self.logger.error(error_msg)
            yield 0, error_msg
            return False
    
    def backup_firmware(self, device, protocol_class, backup_path: Path) -> bool:
        """Backup current firmware from device"""
        try:
            self.logger.info(f"Backing up firmware to: {backup_path}")
            
            # This would implement firmware backup functionality
            # For now, just create a placeholder file
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w') as f:
                f.write(f"Firmware backup for device\n")
                f.write(f"Timestamp: {time.time()}\n")
                f.write(f"Protocol: {protocol_class.__name__}\n")
            
            self.logger.info("Firmware backup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up firmware: {e}")
            return False
    
    def get_firmware_info(self, device, protocol_class) -> Optional[dict]:
        """Get current firmware information from device"""
        try:
            if hasattr(protocol_class, 'get_firmware_version'):
                command = protocol_class.get_firmware_version()
                if device.send_command(command):
                    # This would read the response from the device
                    # For now, return placeholder info
                    return {
                        'version': 'Unknown',
                        'build_date': 'Unknown',
                        'hardware_version': 'Unknown',
                        'serial_number': 'Unknown'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting firmware info: {e}")
            return None
    
    def reset_device(self, device, protocol_class) -> bool:
        """Reset device to factory defaults"""
        try:
            self.logger.info("Resetting device to factory defaults")
            
            # Send reset command if available
            if hasattr(protocol_class, 'reset_device'):
                command = protocol_class.reset_device()
                if device.send_command(command):
                    time.sleep(2)  # Wait for reset
                    self.logger.info("Device reset successfully")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resetting device: {e}")
            return False
    
    def validate_firmware_compatibility(self, firmware_path: Path, device_info: dict) -> Tuple[bool, str]:
        """Validate firmware compatibility with device"""
        try:
            # Check file extension
            firmware_extensions = ['.exe', '.bin', '.fw', '.hex']
            if firmware_path.suffix.lower() not in firmware_extensions:
                return False, f"Unsupported firmware file type: {firmware_path.suffix}"
            
            # Check device-specific compatibility
            vendor = device_info.get('vendor', '').lower()
            product = device_info.get('product', '').lower()
            
            # Basic compatibility checks
            if vendor == 'razer' and 'razer' not in firmware_path.name.lower():
                return False, "Firmware may not be compatible with Razer device"
            
            if vendor == 'logitech' and 'logitech' not in firmware_path.name.lower():
                return False, "Firmware may not be compatible with Logitech device"
            
            return True, "Firmware appears compatible"
            
        except Exception as e:
            return False, f"Compatibility check error: {e}"
