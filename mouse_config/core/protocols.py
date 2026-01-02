"""
Device communication protocols for different mouse manufacturers
"""

import struct
import time
from typing import Optional


class RazerProtocol:
    """Enhanced Razer protocol with firmware support"""
    
    REPORT_SIZE = 90
    
    @staticmethod
    def create_report(command_class: int, command_id: int, data_size: int, data: bytes) -> bytes:
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
    def set_dpi(dpi_x: int, dpi_y: Optional[int] = None) -> bytes:
        """Set DPI for Razer mice"""
        if dpi_y is None:
            dpi_y = dpi_x
        data = bytearray(7)
        data[0] = 0x00
        data[1] = int(dpi_x / 100)
        data[2] = int(dpi_y / 100)
        return RazerProtocol.create_report(0x04, 0x05, 0x07, data)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for Razer mice"""
        rate_map = {1000: 0x01, 500: 0x02, 250: 0x04, 125: 0x08}
        data = bytearray(1)
        data[0] = rate_map.get(rate, 0x01)
        return RazerProtocol.create_report(0x00, 0x05, 0x01, data)
    
    @staticmethod
    def set_lift_off_distance(distance: int) -> bytes:
        """Set lift-off distance (1-3mm)"""
        data = bytearray(2)
        data[0] = 0x01
        data[1] = distance
        return RazerProtocol.create_report(0x04, 0x06, 0x02, data)
    
    @staticmethod
    def set_angle_snapping(enabled: bool) -> bytes:
        """Enable/disable angle snapping"""
        data = bytearray(1)
        data[0] = 0x01 if enabled else 0x00
        return RazerProtocol.create_report(0x04, 0x07, 0x01, data)
    
    @staticmethod
    def set_led_static(r: int, g: int, b: int) -> bytes:
        """Set static LED color"""
        data = bytearray(5)
        data[0] = 0x01
        data[1] = 0x01
        data[2] = r
        data[3] = g
        data[4] = b
        return RazerProtocol.create_report(0x03, 0x01, 0x05, data)
    
    @staticmethod
    def set_led_breathing(r: int, g: int, b: int) -> bytes:
        """Set breathing LED effect"""
        data = bytearray(8)
        data[0] = 0x01
        data[1] = 0x01
        data[2] = 0x01
        data[3] = r
        data[4] = g
        data[5] = b
        return RazerProtocol.create_report(0x03, 0x02, 0x08, data)
    
    @staticmethod
    def set_led_spectrum() -> bytes:
        """Set spectrum cycling effect"""
        data = bytearray(2)
        data[0] = 0x01
        data[1] = 0x01
        return RazerProtocol.create_report(0x03, 0x04, 0x02, data)
    
    @staticmethod
    def set_led_wave(direction: int = 1) -> bytes:
        """Set wave effect"""
        data = bytearray(2)
        data[0] = 0x01
        data[1] = direction
        return RazerProtocol.create_report(0x03, 0x05, 0x02, data)
    
    @staticmethod
    def set_led_reactive(r: int, g: int, b: int, speed: int = 2) -> bytes:
        """Set reactive effect"""
        data = bytearray(5)
        data[0] = speed
        data[1] = r
        data[2] = g
        data[3] = b
        return RazerProtocol.create_report(0x03, 0x06, 0x04, data)
    
    @staticmethod
    def get_firmware_version() -> bytes:
        """Request firmware version"""
        return RazerProtocol.create_report(0x00, 0x81, 0x02, bytearray([0x00, 0x00]))
    
    @staticmethod
    def enter_dfu_mode() -> bytes:
        """Enter firmware update mode"""
        data = bytearray(2)
        data[0] = 0xAA
        data[1] = 0x55
        return RazerProtocol.create_report(0xFF, 0x00, 0x02, data)
    
    @staticmethod
    def exit_dfu_mode() -> bytes:
        """Exit firmware update mode"""
        data = bytearray(2)
        data[0] = 0x55
        data[1] = 0xAA
        return RazerProtocol.create_report(0xFF, 0x01, 0x02, data)


class LogitechProtocol:
    """Enhanced Logitech protocol for G-series mice"""
    
    @staticmethod
    def set_dpi(dpi: int) -> bytes:
        """Set DPI for Logitech mice"""
        report = bytearray(64)
        report[0] = 0x11  # Set DPI command
        report[1] = 0xFF  
        report[2] = 0x04  # DPI report ID
        report[3] = dpi & 0xFF
        report[4] = (dpi >> 8) & 0xFF
        report[5] = 0x00  # Y DPI (same as X)
        report[6] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_dpi_stages(stages: list) -> bytes:
        """Set multiple DPI stages (Logitech G-series)"""
        report = bytearray(64)
        report[0] = 0x12  # Set DPI stages command
        report[1] = 0xFF
        report[2] = 0x05  # DPI stages report ID
        
        for i, dpi in enumerate(stages[:5]):  # Max 5 stages
            report[3 + i*2] = dpi & 0xFF
            report[4 + i*2] = (dpi >> 8) & 0xFF
        
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for Logitech mice"""
        rate_map = {125: 0x08, 250: 0x04, 500: 0x02, 1000: 0x01}
        report = bytearray(64)
        report[0] = 0x10  # Set polling rate command
        report[1] = 0xFF
        report[2] = rate_map.get(rate, 0x01)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r: int, g: int, b: int, mode: int = 0, brightness: int = 255, speed: int = 128) -> bytes:
        """Set RGB color for Logitech mice"""
        report = bytearray(64)
        report[0] = 0x13  # RGB command
        report[1] = 0xFF
        report[2] = mode  # 0=static, 1=breathing, 2=rainbow, etc.
        report[3] = r
        report[4] = g
        report[5] = b
        report[6] = brightness
        report[7] = speed
        return bytes(report)
    
    @staticmethod
    def set_button_mapping(button: int, action: int) -> bytes:
        """Remap button (Logitech G-series)"""
        report = bytearray(64)
        report[0] = 0x14  # Button mapping command
        report[1] = 0xFF
        report[2] = button  # Button ID
        report[3] = action  # Action ID
        return bytes(report)


class SteelSeriesProtocol:
    """Enhanced SteelSeries protocol"""
    
    @staticmethod
    def set_dpi(dpi: int) -> bytes:
        """Set DPI for SteelSeries mice"""
        report = bytearray(64)
        report[0] = 0x20  # SteelSeries DPI command
        report[1] = 0x01
        report[2] = dpi & 0xFF
        report[3] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for SteelSeries mice"""
        rate_map = {125: 0x03, 250: 0x02, 500: 0x01, 1000: 0x00}
        report = bytearray(64)
        report[0] = 0x21  # Polling rate command
        report[1] = rate_map.get(rate, 0x00)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r: int, g: int, b: int, mode: int = 0, brightness: int = 255, speed: int = 128) -> bytes:
        """Set RGB color for SteelSeries mice"""
        report = bytearray(64)
        report[0] = 0x22  # RGB command
        report[1] = mode  # 0=static, 1=breathing, 2=rainbow, 3=reactive
        report[2] = r
        report[3] = g
        report[4] = b
        report[5] = brightness
        report[6] = speed
        return bytes(report)
    
    @staticmethod
    def set_lod(distance: int) -> bytes:
        """Set lift-off distance"""
        report = bytearray(64)
        report[0] = 0x23  # LOD command
        report[1] = distance  # 1-3mm
        return bytes(report)


class GenericProtocol:
    """Enhanced generic protocol with more features"""
    
    @staticmethod
    def set_dpi(dpi: int) -> bytes:
        """Set DPI for generic mice"""
        report = bytearray(64)
        report[0] = 0x03
        report[1] = 0x0A
        report[2] = dpi & 0xFF
        report[3] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_dpi_stages(stages: list) -> bytes:
        """Set multiple DPI stages"""
        report = bytearray(64)
        report[0] = 0x03
        report[1] = 0x0B
        for i, dpi in enumerate(stages[:5]):  # Max 5 stages
            report[2 + i*2] = dpi & 0xFF
            report[3 + i*2] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for generic mice"""
        rate_map = {125: 0x03, 250: 0x02, 500: 0x01, 1000: 0x00}
        report = bytearray(64)
        report[0] = 0x02
        report[1] = 0x01
        report[2] = rate_map.get(rate, 0x00)
        return bytes(report)
    
    @staticmethod
    def set_debounce_time(ms: int) -> bytes:
        """Set button debounce time"""
        report = bytearray(64)
        report[0] = 0x05
        report[1] = 0x01
        report[2] = ms
        return bytes(report)
    
    @staticmethod
    def set_button_mapping(button: int, action: int) -> bytes:
        """Remap button"""
        report = bytearray(64)
        report[0] = 0x06
        report[1] = button
        report[2] = action
        return bytes(report)
    
    @staticmethod
    def set_led_color(r: int, g: int, b: int, mode: int = 0, brightness: int = 255, speed: int = 128) -> bytes:
        """Set LED color"""
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
    def set_dpi(dpi: int) -> bytes:
        """Set DPI for CyberpowerPC mice"""
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x10
        report[2] = (dpi // 50) & 0xFF
        report[3] = 0x00
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for CyberpowerPC mice"""
        rate_map = {125: 0x08, 250: 0x04, 500: 0x02, 1000: 0x01}
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x11
        report[2] = rate_map.get(rate, 0x01)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r: int, g: int, b: int, mode: int = 0, brightness: int = 255) -> bytes:
        """Set RGB color for CyberpowerPC mice"""
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
    def set_lod(distance: int) -> bytes:
        """Set lift-off distance"""
        report = bytearray(8)
        report[0] = 0x00
        report[1] = 0x13
        report[2] = distance
        return bytes(report)


class IBuyPowerProtocol:
    """Enhanced iBuyPower protocol"""
    
    @staticmethod
    def set_dpi(dpi: int) -> bytes:
        """Set DPI for iBuyPower mice"""
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x07
        report[2] = 0x01
        report[3] = dpi & 0xFF
        report[4] = (dpi >> 8) & 0xFF
        return bytes(report)
    
    @staticmethod
    def set_poll_rate(rate: int) -> bytes:
        """Set polling rate for iBuyPower mice"""
        rate_map = {125: 3, 250: 2, 500: 1, 1000: 0}
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x08
        report[2] = rate_map.get(rate, 0)
        return bytes(report)
    
    @staticmethod
    def set_rgb(r: int, g: int, b: int, mode: int = 0, speed: int = 128) -> bytes:
        """Set RGB color for iBuyPower mice"""
        report = bytearray(65)
        report[0] = 0x00
        report[1] = 0x0A
        report[2] = mode
        report[3] = r
        report[4] = g
        report[5] = b
        report[6] = speed
        return bytes(report)
