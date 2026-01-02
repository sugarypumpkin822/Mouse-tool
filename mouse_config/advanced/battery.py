"""
Battery monitoring for wireless mice
"""

import time
import threading
from typing import Dict, Any, Optional
from ..utils.logger import get_logger


class BatteryMonitor:
    """Monitor wireless mouse battery level"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.battery_level = 100
        self.charging = False
        self.last_update = time.time()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        # Battery statistics
        self.battery_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # Device-specific settings
        self.device_type = "unknown"
        self.battery_curve = "linear"  # linear, exponential, custom
        
    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information for wireless mice"""
        try:
            # This would need device-specific implementation
            # For now, return simulated data with realistic patterns
            
            current_time = time.time()
            
            # Simulate battery drain
            if not self.charging and current_time - self.last_update > 60:  # Update every minute
                # Simulate battery drain based on usage
                drain_rate = 0.1 if self.device_type == "gaming" else 0.05
                self.battery_level = max(0, self.battery_level - drain_rate)
                self.last_update = current_time
                
                # Add to history
                self._add_battery_reading()
            
            # Calculate estimated time remaining
            if self.charging:
                estimated_hours = (100 - self.battery_level) * 0.1  # 10 minutes per percent
            else:
                # Use device-specific consumption rate
                consumption_rate = 0.5 if self.device_type == "gaming" else 0.2  # % per hour
                estimated_hours = self.battery_level / consumption_rate if consumption_rate > 0 else 0
            
            return {
                'level': self.battery_level,
                'charging': self.charging,
                'estimated_hours': max(0, estimated_hours),
                'voltage': self._simulate_voltage(),
                'temperature': self._simulate_temperature(),
                'health': self._calculate_battery_health(),
                'cycles': self._estimate_charge_cycles(),
                'last_update': self.last_update
            }
            
        except Exception as e:
            self.logger.error(f"Error getting battery info: {e}")
            return {
                'level': 100,
                'charging': False,
                'estimated_hours': 0,
                'error': str(e)
            }
    
    def start_monitoring(self, device_type: str = "unknown") -> bool:
        """Start continuous battery monitoring"""
        if self.monitoring:
            self.logger.warning("Battery monitoring already active")
            return False
        
        try:
            self.device_type = device_type
            self.monitoring = True
            self.stop_monitoring.clear()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_battery,
                daemon=True
            )
            self.monitor_thread.start()
            
            self.logger.info(f"Started battery monitoring for {device_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting battery monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop_monitoring(self):
        """Stop battery monitoring"""
        if self.monitoring:
            self.stop_monitoring.set()
            self.monitoring = False
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2.0)
            
            self.logger.info("Stopped battery monitoring")
    
    def _monitor_battery(self):
        """Monitor battery in background thread"""
        while not self.stop_monitoring.is_set():
            try:
                # Update battery info
                battery_info = self.get_battery_info()
                
                # Check for low battery warning
                if battery_info['level'] < 20 and not self.charging:
                    self.logger.warning(f"Low battery: {battery_info['level']:.1f}%")
                
                # Check for charging status change
                if self.charging != battery_info['charging']:
                    self.charging = battery_info['charging']
                    status = "charging" if self.charging else "discharging"
                    self.logger.info(f"Battery status changed to: {status}")
                
                # Sleep for update interval
                self.stop_monitoring.wait(60)  # Update every minute
                
            except Exception as e:
                self.logger.error(f"Error in battery monitoring: {e}")
                self.stop_monitoring.wait(10)
    
    def _add_battery_reading(self):
        """Add battery reading to history"""
        reading = {
            'timestamp': time.time(),
            'level': self.battery_level,
            'charging': self.charging,
            'voltage': self._simulate_voltage(),
            'temperature': self._simulate_temperature()
        }
        
        self.battery_history.append(reading)
        
        # Limit history size
        if len(self.battery_history) > self.max_history_size:
            self.battery_history.pop(0)
    
    def _simulate_voltage(self) -> float:
        """Simulate battery voltage based on level"""
        # Typical Li-ion battery: 3.0V (empty) to 4.2V (full)
        voltage = 3.0 + (self.battery_level / 100) * 1.2
        return round(voltage, 2)
    
    def _simulate_temperature(self) -> float:
        """Simulate battery temperature"""
        # Simulate temperature based on charging state and usage
        base_temp = 25.0  # Room temperature
        
        if self.charging:
            temp_increase = 5.0 + (self.battery_level / 100) * 10.0
        else:
            temp_increase = 2.0 if self.device_type == "gaming" else 1.0
        
        return round(base_temp + temp_increase, 1)
    
    def _calculate_battery_health(self) -> str:
        """Calculate battery health based on history"""
        if len(self.battery_history) < 10:
            return "Unknown"
        
        # Analyze discharge rate
        recent_readings = self.battery_history[-10:]
        discharge_rates = []
        
        for i in range(1, len(recent_readings)):
            if not recent_readings[i]['charging'] and not recent_readings[i-1]['charging']:
                time_diff = recent_readings[i]['timestamp'] - recent_readings[i-1]['timestamp']
                level_diff = recent_readings[i-1]['level'] - recent_readings[i]['level']
                
                if time_diff > 0:
                    rate = level_diff / (time_diff / 3600)  # % per hour
                    discharge_rates.append(rate)
        
        if discharge_rates:
            avg_rate = sum(discharge_rates) / len(discharge_rates)
            
            # Determine health based on discharge rate
            if avg_rate < 1.0:
                return "Excellent"
            elif avg_rate < 2.0:
                return "Good"
            elif avg_rate < 3.0:
                return "Fair"
            else:
                return "Poor"
        
        return "Unknown"
    
    def _estimate_charge_cycles(self) -> int:
        """Estimate number of charge cycles"""
        # This is a rough estimation based on usage patterns
        # In a real implementation, this would come from device data
        
        if len(self.battery_history) < 2:
            return 0
        
        # Count charging cycles from history
        cycles = 0
        was_charging = False
        
        for reading in self.battery_history:
            if reading['charging'] and not was_charging:
                cycles += 1
            was_charging = reading['charging']
        
        return cycles
    
    def get_battery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive battery statistics"""
        if not self.battery_history:
            return {'error': 'No battery data available'}
        
        # Calculate statistics
        levels = [reading['level'] for reading in self.battery_history]
        voltages = [reading['voltage'] for reading in self.battery_history]
        temperatures = [reading['temperature'] for reading in self.battery_history]
        
        # Find min/max values
        min_level = min(levels)
        max_level = max(levels)
        avg_level = sum(levels) / len(levels)
        
        min_voltage = min(voltages)
        max_voltage = max(voltages)
        avg_voltage = sum(voltages) / len(voltages)
        
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)
        
        # Calculate usage time
        if len(self.battery_history) > 1:
            usage_time = self.battery_history[-1]['timestamp'] - self.battery_history[0]['timestamp']
        else:
            usage_time = 0
        
        return {
            'current_level': self.battery_level,
            'charging': self.charging,
            'health': self._calculate_battery_health(),
            'cycles': self._estimate_charge_cycles(),
            'usage_time_hours': usage_time / 3600,
            'readings_count': len(self.battery_history),
            'level_stats': {
                'min': min_level,
                'max': max_level,
                'avg': avg_level
            },
            'voltage_stats': {
                'min': min_voltage,
                'max': max_voltage,
                'avg': avg_voltage
            },
            'temperature_stats': {
                'min': min_temp,
                'max': max_temp,
                'avg': avg_temp
            }
        }
    
    def export_battery_data(self, file_path: str) -> bool:
        """Export battery data to file"""
        try:
            import json
            
            data = {
                'export_time': time.time(),
                'device_type': self.device_type,
                'current_info': self.get_battery_info(),
                'statistics': self.get_battery_statistics(),
                'history': self.battery_history
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Battery data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting battery data: {e}")
            return False
    
    def set_battery_level(self, level: int, charging: bool = False):
        """Manually set battery level (for testing)"""
        self.battery_level = max(0, min(100, level))
        self.charging = charging
        self.last_update = time.time()
        self._add_battery_reading()
    
    def clear_battery_history(self):
        """Clear battery history"""
        self.battery_history = []
        self.logger.info("Battery history cleared")
    
    def is_monitoring(self) -> bool:
        """Check if battery monitoring is active"""
        return self.monitoring
