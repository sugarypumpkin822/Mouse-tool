"""
Mouse device control and management system
"""

import time
from typing import Optional, List, Dict, Any
from ..utils.helpers import safe_execute, retry_operation
from ..utils.logger import get_logger


class MouseController:
    """Ultra-robust controller with multiple connection methods and bypass capabilities"""
    
    def __init__(self, mouse_info: Dict[str, Any]):
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
        self.logger = get_logger(__name__)
        
    def _get_protocol(self):
        """Get appropriate protocol class"""
        from .protocols import (
            RazerProtocol, LogitechProtocol, SteelSeriesProtocol,
            GenericProtocol, CyberpowerProtocol, IBuyPowerProtocol
        )
        
        protocol_map = {
            "Razer": RazerProtocol,
            "Logitech": LogitechProtocol,
            "SteelSeries": SteelSeriesProtocol,
            "CyberpowerPC": CyberpowerProtocol,
            "iBuyPower": IBuyPowerProtocol,
        }
        
        return protocol_map.get(self.vendor, GenericProtocol)
    
    def connect(self) -> bool:
        """Enhanced multi-method connection with bypass capabilities"""
        self.logger.info(f"Attempting to connect to {self.mouse_info['product']}")
        
        # Check library availability
        if not self._check_libraries():
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
                self.logger.debug(f"Trying {method_name}...")
                if safe_execute(method, default=False):
                    self.connected = True
                    self.connection_method = method_name
                    self.last_error = ""
                    self.logger.info(f"Successfully connected via {method_name}")
                    return True
            except Exception as e:
                self.last_error = f"{method_name} failed: {str(e)[:100]}"
                self.logger.debug(f"{method_name} failed: {e}")
                continue
        
        self.logger.error("All connection methods failed")
        return False
    
    def _check_libraries(self) -> bool:
        """Check if required libraries are available"""
        try:
            import hid
            import usb.core
            return True
        except ImportError as e:
            self.last_error = f"Missing library: {e}"
            return False
    
    def _connect_hid_standard(self) -> bool:
        """Standard HID connection"""
        try:
            import hid
            self.device = hid.Device(
                vid=self.mouse_info['vendor_id'],
                pid=self.mouse_info['product_id']
            )
            self.device.set_nonblocking(1)
            return True
        except Exception as e:
            self.logger.debug(f"HID Standard failed: {e}")
            return False
    
    def _connect_hid_path(self) -> bool:
        """HID connection via path"""
        try:
            import hid
            if not self.mouse_info.get('path'):
                return False
            
            self.device = hid.Device(path=self.mouse_info['path'])
            self.device.set_nonblocking(1)
            return True
        except Exception as e:
            self.logger.debug(f"HID Path failed: {e}")
            return False
    
    def _connect_hid_all_interfaces(self) -> bool:
        """Try all interfaces until one works"""
        try:
            import hid
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
        except Exception as e:
            self.logger.debug(f"HID All Interfaces failed: {e}")
        
        return False
    
    def _connect_usb_direct(self) -> bool:
        """Direct USB connection"""
        try:
            import usb.core
            import usb.util
            
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
        except Exception as e:
            self.logger.debug(f"USB Direct failed: {e}")
            return False
    
    def _connect_usb_detach_driver(self) -> bool:
        """USB connection with kernel driver detachment"""
        try:
            import usb.core
            import usb.util
            
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
        except Exception as e:
            self.logger.debug(f"USB Detach Driver failed: {e}")
            return False
    
    def _connect_usb_raw(self) -> bool:
        """Raw USB control transfer"""
        try:
            import usb.core
            import usb.util
            
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
        except Exception as e:
            self.logger.debug(f"USB Raw failed: {e}")
            return False
    
    def disconnect(self):
        """Clean disconnect with driver reattachment"""
        self.logger.info("Disconnecting device")
        
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None
        
        if self.usb_device:
            try:
                import usb.util
                
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
    
    def send_command(self, command: bytes, retries: int = 3) -> bool:
        """Enhanced send with multiple methods and retry logic"""
        if not self.connected:
            self.logger.error("Device not connected")
            return False
        
        def _send_with_retry():
            return self._attempt_send(command)
        
        try:
            return retry_operation(_send_with_retry, max_retries=retries, delay=0.1)
        except Exception as e:
            self.last_error = f"Send command failed: {e}"
            self.logger.error(f"Send command failed: {e}")
            return False
    
    def _attempt_send(self, command: bytes) -> bool:
        """Attempt to send command using all available methods"""
        # Method 1: HID Feature Report
        if self.device:
            if safe_execute(self.device.send_feature_report, default=False, args=[command]):
                time.sleep(0.05)
                return True
            
            # Method 2: HID Write
            if safe_execute(self.device.write, default=False, args=[command]):
                time.sleep(0.05)
                return True
        
        # Method 3: USB Interrupt Transfer
        if self.usb_device and self.usb_endpoint_out:
            if safe_execute(self.usb_endpoint_out.write, default=False, args=[command], kwargs={'timeout': 1000}):
                time.sleep(0.05)
                return True
        
        # Method 4: USB Control Transfer (HID Set Report)
        if self.usb_device:
            try:
                import usb.core
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
                import usb.core
                interface = self.interface_claimed or 0
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
        
        return False
    
    def test_connection(self) -> bool:
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
    
    def get_connection_info(self) -> List[str]:
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
    
    def set_dpi(self, dpi: int) -> bool:
        """Set DPI with validation"""
        if not self.connected:
            return False
        
        try:
            if not (100 <= dpi <= 20000):
                raise ValueError(f"DPI out of range: {dpi}")
            
            command = self.protocol.set_dpi(dpi)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"DPI error: {e}"
            self.logger.error(f"DPI error: {e}")
            return False
    
    def set_polling_rate(self, rate: int) -> bool:
        """Set polling rate with validation"""
        if not self.connected:
            return False
        
        try:
            if rate not in [125, 250, 500, 1000]:
                raise ValueError(f"Invalid polling rate: {rate}")
            
            command = self.protocol.set_poll_rate(rate)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Polling rate error: {e}"
            self.logger.error(f"Polling rate error: {e}")
            return False
    
    def set_rgb(self, color: str, mode: str, brightness: int = 100, speed: int = 50) -> bool:
        """Set RGB with validation"""
        if not self.connected:
            return False
        
        try:
            color = color.lstrip('#')
            if len(color) != 6:
                raise ValueError(f"Invalid color format: {color}")
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            if not (0 <= brightness <= 100):
                raise ValueError(f"Invalid brightness: {brightness}")
            
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
            self.logger.error(f"RGB error: {e}")
            return False
    
    def set_lod(self, distance: int) -> bool:
        """Set lift-off distance with validation"""
        if not self.connected:
            return False
        
        try:
            if not (1 <= distance <= 3):
                raise ValueError(f"Invalid LOD distance: {distance}")
            
            if hasattr(self.protocol, 'set_lift_off_distance'):
                command = self.protocol.set_lift_off_distance(distance)
            elif hasattr(self.protocol, 'set_lod'):
                command = self.protocol.set_lod(distance)
            else:
                self.logger.warning("LOD not supported by this protocol")
                return False
            
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"LOD error: {e}"
            self.logger.error(f"LOD error: {e}")
            return False
    
    def set_angle_snapping(self, enabled: bool) -> bool:
        """Set angle snapping"""
        if not self.connected or not hasattr(self.protocol, 'set_angle_snapping'):
            return False
        
        try:
            command = self.protocol.set_angle_snapping(enabled)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Angle snap error: {e}"
            self.logger.error(f"Angle snap error: {e}")
            return False
    
    def set_debounce(self, ms: int) -> bool:
        """Set debounce time with validation"""
        if not self.connected or not hasattr(self.protocol, 'set_debounce_time'):
            return False
        
        try:
            if not (2 <= ms <= 16):
                raise ValueError(f"Invalid debounce time: {ms}")
            
            command = self.protocol.set_debounce_time(ms)
            return self.send_command(command)
        except Exception as e:
            self.last_error = f"Debounce error: {e}"
            self.logger.error(f"Debounce error: {e}")
            return False
