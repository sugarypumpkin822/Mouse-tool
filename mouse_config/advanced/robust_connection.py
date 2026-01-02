"""
Robust connection management with multiple fallback methods
"""

import time
import threading
import queue
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum
import traceback

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute, retry_operation


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    success_rate: float
    avg_response_time: float
    error_count: int
    reconnect_count: int
    uptime: float
    last_error: str
    connection_method: str


class RobustConnectionManager:
    """Robust connection manager with automatic failover and recovery"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Connection state
        self.state = ConnectionState.DISCONNECTED
        self.controller = None
        self.current_method = None
        
        # Connection methods (ordered by preference)
        self.connection_methods = [
            "hid_standard",
            "hid_path", 
            "hid_all_interfaces",
            "usb_direct",
            "usb_detach_driver",
            "usb_raw"
        ]
        
        # Connection metrics
        self.metrics = ConnectionMetrics(
            success_rate=0.0,
            avg_response_time=0.0,
            error_count=0,
            reconnect_count=0,
            uptime=0.0,
            last_error="",
            connection_method=""
        )
        
        # Connection management
        self.connection_lock = threading.Lock()
        self.reconnect_timer = None
        self.health_check_timer = None
        self.command_queue = queue.Queue()
        
        # Configuration
        self.config = {
            'max_reconnect_attempts': 5,
            'reconnect_delay': 2.0,
            'health_check_interval': 30.0,
            'command_timeout': 5.0,
            'max_consecutive_errors': 3,
            'auto_reconnect': True
        }
        
        # Callbacks
        self.state_change_callbacks: List[Callable[[ConnectionState], None]] = []
        self.error_callbacks: List[Callable[[str], None]] = []
        
        # Statistics
        self.connection_start_time = None
        self.total_commands_sent = 0
        self.total_commands_succeeded = 0
    
    def set_controller(self, controller):
        """Set the controller instance"""
        with self.connection_lock:
            self.controller = controller
            if controller and controller.connected:
                self.state = ConnectionState.CONNECTED
                self.current_method = controller.connection_method
                self.connection_start_time = time.time()
                self._notify_state_change()
    
    def connect(self) -> bool:
        """Establish connection with automatic failover"""
        with self.connection_lock:
            if self.state in [ConnectionState.CONNECTED, ConnectionState.CONNECTING]:
                return True
            
            self.state = ConnectionState.CONNECTING
            self._notify_state_change()
            
            for method in self.connection_methods:
                try:
                    self.logger.info(f"Attempting connection via {method}")
                    
                    if self._try_connection_method(method):
                        self.state = ConnectionState.CONNECTED
                        self.current_method = method
                        self.connection_start_time = time.time()
                        self.metrics.connection_method = method
                        self._notify_state_change()
                        
                        # Start health monitoring
                        self._start_health_monitoring()
                        
                        self.logger.info(f"Successfully connected via {method}")
                        return True
                    
                except Exception as e:
                    self.logger.error(f"Connection method {method} failed: {e}")
                    self.metrics.last_error = str(e)
                    self.metrics.error_count += 1
                    self._notify_error(f"Connection failed: {method} - {e}")
                    continue
            
            # All methods failed
            self.state = ConnectionState.ERROR
            self._notify_state_change()
            self._notify_error("All connection methods failed")
            return False
    
    def _try_connection_method(self, method: str) -> bool:
        """Try a specific connection method"""
        if not self.controller:
            return False
        
        try:
            if method == "hid_standard":
                return self._connect_hid_standard()
            elif method == "hid_path":
                return self._connect_hid_path()
            elif method == "hid_all_interfaces":
                return self._connect_hid_all_interfaces()
            elif method == "usb_direct":
                return self._connect_usb_direct()
            elif method == "usb_detach_driver":
                return self._connect_usb_detach_driver()
            elif method == "usb_raw":
                return self._connect_usb_raw()
            else:
                self.logger.error(f"Unknown connection method: {method}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in {method}: {e}")
            raise
    
    def _connect_hid_standard(self) -> bool:
        """Standard HID connection"""
        try:
            import hid
            self.controller.device = hid.Device(
                vid=self.controller.mouse_info['vendor_id'],
                pid=self.controller.mouse_info['product_id']
            )
            self.controller.device.set_nonblocking(1)
            return True
        except Exception as e:
            raise Exception(f"HID standard failed: {e}")
    
    def _connect_hid_path(self) -> bool:
        """HID connection via path"""
        try:
            import hid
            if not self.controller.mouse_info.get('path'):
                raise Exception("No path available")
            
            self.controller.device = hid.Device(path=self.controller.mouse_info['path'])
            self.controller.device.set_nonblocking(1)
            return True
        except Exception as e:
            raise Exception(f"HID path failed: {e}")
    
    def _connect_hid_all_interfaces(self) -> bool:
        """Try all interfaces until one works"""
        try:
            import hid
            devices = hid.enumerate(
                self.controller.mouse_info['vendor_id'],
                self.controller.mouse_info['product_id']
            )
            
            for dev in devices:
                try:
                    self.controller.device = hid.Device(path=dev['path'])
                    self.controller.device.set_nonblocking(1)
                    
                    # Test if it works
                    self.controller.device.get_manufacturer_string()
                    return True
                except:
                    continue
            
            raise Exception("No working HID interface found")
        except Exception as e:
            raise Exception(f"HID all interfaces failed: {e}")
    
    def _connect_usb_direct(self) -> bool:
        """Direct USB connection"""
        try:
            import usb.core
            import usb.util
            
            self.controller.usb_device = usb.core.find(
                idVendor=self.controller.mouse_info['vendor_id'],
                idProduct=self.controller.mouse_info['product_id']
            )
            
            if self.controller.usb_device is None:
                raise Exception("USB device not found")
            
            # Try to set configuration
            try:
                self.controller.usb_device.set_configuration()
            except:
                pass
            
            # Find endpoints
            cfg = self.controller.usb_device.get_active_configuration()
            for intf in cfg:
                for ep in intf:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        self.controller.usb_endpoint_out = ep
                    elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        self.controller.usb_endpoint_in = ep
            
            if self.controller.usb_endpoint_out is None:
                raise Exception("No USB endpoint found")
            
            return True
        except Exception as e:
            raise Exception(f"USB direct failed: {e}")
    
    def _connect_usb_detach_driver(self) -> bool:
        """USB connection with kernel driver detachment"""
        try:
            import usb.core
            import usb.util
            
            self.controller.usb_device = usb.core.find(
                idVendor=self.controller.mouse_info['vendor_id'],
                idProduct=self.controller.mouse_info['product_id']
            )
            
            if self.controller.usb_device is None:
                raise Exception("USB device not found")
            
            # Detach kernel driver if active
            interface_num = 0
            for interface_num in range(3):
                try:
                    if self.controller.usb_device.is_kernel_driver_active(interface_num):
                        self.controller.usb_device.detach_kernel_driver(interface_num)
                        self.controller.kernel_driver_detached = True
                        self.controller.interface_claimed = interface_num
                except:
                    pass
            
            # Set configuration
            try:
                self.controller.usb_device.set_configuration()
            except:
                pass
            
            # Claim interface
            if self.controller.interface_claimed is None:
                for i in range(3):
                    try:
                        usb.util.claim_interface(self.controller.usb_device, i)
                        self.controller.interface_claimed = i
                        break
                    except:
                        continue
            else:
                try:
                    usb.util.claim_interface(self.controller.usb_device, self.controller.interface_claimed)
                except:
                    pass
            
            # Find endpoints
            cfg = self.controller.usb_device.get_active_configuration()
            for intf in cfg:
                for ep in intf:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        self.controller.usb_endpoint_out = ep
                    elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        self.controller.usb_endpoint_in = ep
            
            return True
        except Exception as e:
            raise Exception(f"USB detach driver failed: {e}")
    
    def _connect_usb_raw(self) -> bool:
        """Raw USB control transfer"""
        try:
            import usb.core
            import usb.util
            
            self.controller.usb_device = usb.core.find(
                idVendor=self.controller.mouse_info['vendor_id'],
                idProduct=self.controller.mouse_info['product_id']
            )
            
            if self.controller.usb_device is None:
                raise Exception("USB device not found")
            
            # Force configuration
            self.controller.usb_device.reset()
            time.sleep(0.5)
            
            # Detach all kernel drivers
            for i in range(4):
                try:
                    if self.controller.usb_device.is_kernel_driver_active(i):
                        self.controller.usb_device.detach_kernel_driver(i)
                except:
                    pass
            
            # Set configuration
            self.controller.usb_device.set_configuration()
            
            # Claim all interfaces
            for i in range(4):
                try:
                    usb.util.claim_interface(self.controller.usb_device, i)
                    if self.controller.interface_claimed is None:
                        self.controller.interface_claimed = i
                except:
                    pass
            
            self.controller.kernel_driver_detached = True
            return True
        except Exception as e:
            raise Exception(f"USB raw failed: {e}")
    
    def disconnect(self):
        """Disconnect with cleanup"""
        with self.connection_lock:
            if self.state == ConnectionState.DISCONNECTED:
                return
            
            self.state = ConnectionState.DISCONNECTED
            self._notify_state_change()
            
            # Stop monitoring
            self._stop_health_monitoring()
            self._stop_reconnect_timer()
            
            # Cleanup controller
            if self.controller:
                self.controller.disconnect()
                self.controller = None
            
            self.current_method = None
    
    def send_command(self, command: bytes, retries: int = 3) -> bool:
        """Send command with robust error handling"""
        if self.state != ConnectionState.CONNECTED:
            return False
        
        start_time = time.time()
        success = False
        
        try:
            # Use retry operation with exponential backoff
            success = retry_operation(
                self._send_command_internal,
                max_retries=retries,
                delay=0.1,
                args=(command,)
            )
            
            # Update metrics
            self.total_commands_sent += 1
            if success:
                self.total_commands_succeeded += 1
            else:
                self.metrics.error_count += 1
                self._handle_command_failure()
            
            # Update response time
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Command send failed: {e}")
            self.metrics.error_count += 1
            self._handle_command_failure()
            return False
    
    def _send_command_internal(self, command: bytes) -> bool:
        """Internal command sending with multiple methods"""
        if not self.controller:
            return False
        
        # Method 1: HID Feature Report
        if self.controller.device:
            try:
                self.controller.device.send_feature_report(command)
                time.sleep(0.05)
                return True
            except:
                pass
        
        # Method 2: HID Write
        if self.controller.device:
            try:
                self.controller.device.write(command)
                time.sleep(0.05)
                return True
            except:
                pass
        
        # Method 3: USB Interrupt Transfer
        if self.controller.usb_device and self.controller.usb_endpoint_out:
            try:
                self.controller.usb_endpoint_out.write(command, timeout=1000)
                time.sleep(0.05)
                return True
            except:
                pass
        
        # Method 4: USB Control Transfer (HID Set Report)
        if self.controller.usb_device:
            try:
                import usb.core
                interface = self.controller.interface_claimed or 0
                self.controller.usb_device.ctrl_transfer(
                    bmRequestType=0x21,  # Host to Device, Class, Interface
                    bRequest=0x09,        # SET_REPORT
                    wValue=0x0300,      # Feature Report
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
                interface = self.controller.interface_claimed or 0
                self.controller.usb_device.ctrl_transfer(
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
    
    def _handle_command_failure(self):
        """Handle command failure"""
        self.metrics.error_count += 1
        
        # Check if we need to reconnect
        if self.metrics.error_count >= self.config['max_consecutive_errors']:
            self.logger.warning("Too many consecutive errors, initiating reconnection")
            self._initiate_reconnect()
    
    def _initiate_reconnect(self):
        """Initiate automatic reconnection"""
        if not self.config['auto_reconnect']:
            return
        
        if self.reconnect_timer:
            return
        
        self.state = ConnectionState.RECONNECTING
        self._notify_state_change()
        
        self.reconnect_timer = threading.Timer(
            self.config['reconnect_delay'],
            self._attempt_reconnect
        )
        self.reconnect_timer.start()
    
    def _attempt_reconnect(self):
        """Attempt to reconnect"""
        self.logger.info("Attempting to reconnect...")
        
        # Disconnect first
        if self.controller:
            self.controller.disconnect()
        
        # Try to reconnect
        if self.connect():
            self.metrics.reconnect_count += 1
            self.logger.info(f"Successfully reconnected (attempt {self.metrics.reconnect_count})")
        else:
            self.logger.error("Reconnection failed")
            self._schedule_reconnect_retry()
    
    def _schedule_reconnect_retry(self):
        """Schedule another reconnection attempt"""
        if self.metrics.reconnect_count < self.config['max_reconnect_attempts']:
            delay = self.config['reconnect_delay'] * (2 ** min(self.metrics.reconnect_count, 3))
            
            self.reconnect_timer = threading.Timer(delay, self._attempt_reconnect)
            self.reconnect_timer.start()
        else:
            self.logger.error("Max reconnection attempts reached")
            self.state = ConnectionState.ERROR
            self._notify_state_change()
    
    def _stop_reconnect_timer(self):
        """Stop reconnection timer"""
        if self.reconnect_timer:
            self.reconnect_timer.cancel()
            self.reconnect_timer = None
    
    def _start_health_monitoring(self):
        """Start periodic health checks"""
        if self.health_check_timer:
            return
        
        self.health_check_timer = threading.Timer(
            self.config['health_check_interval'],
            self._health_check
        )
        self.health_check_timer.start()
    
    def _stop_health_monitoring(self):
        """Stop health monitoring"""
        if self.health_check_timer:
            self.health_check_timer.cancel()
            self.health_check_timer = None
    
    def _health_check(self):
        """Perform health check"""
        if self.state != ConnectionState.CONNECTED:
            return
        
        try:
            # Test connection
            if self.controller and self.controller.test_connection():
                # Schedule next health check
                self._start_health_monitoring()
            else:
                self.logger.warning("Health check failed, initiating reconnection")
                self._initiate_reconnect()
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            self._initiate_reconnect()
    
    def _update_response_time(self, response_time: float):
        """Update average response time"""
        if self.metrics.avg_response_time == 0:
            self.metrics.avg_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_response_time = (
                alpha * response_time + 
                (1 - alpha) * self.metrics.avg_response_time
            )
    
    def _update_success_rate(self):
        """Update success rate metric"""
        if self.total_commands_sent > 0:
            self.metrics.success_rate = (
                self.total_commands_succeeded / self.total_commands_sent
            )
    
    def _update_uptime(self):
        """Update uptime metric"""
        if self.connection_start_time:
            self.metrics.uptime = time.time() - self.connection_start_time
    
    def _notify_state_change(self):
        """Notify state change callbacks"""
        for callback in self.state_change_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")
    
    def _notify_error(self, error_message: str):
        """Notify error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_message)
            except Exception as e:
                self.logger.error(f"Error callback error: {e}")
    
    def add_state_change_callback(self, callback: Callable[[ConnectionState], None]):
        """Add state change callback"""
        self.state_change_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str], None]):
        """Add error callback"""
        self.error_callbacks.append(callback)
    
    def get_connection_metrics(self) -> ConnectionMetrics:
        """Get current connection metrics"""
        self._update_success_rate()
        self._update_uptime()
        return self.metrics
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get comprehensive connection status"""
        return {
            'state': self.state.value,
            'method': self.current_method,
            'metrics': self.get_connection_metrics(),
            'config': self.config.copy(),
            'controller_connected': self.controller is not None and self.controller.connected
        }
    
    def set_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated config {key} = {value}")
    
    def force_reconnect(self):
        """Force immediate reconnection"""
        self.logger.info("Forcing reconnection...")
        self._initiate_reconnect()
