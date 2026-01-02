"""
Thermal monitoring and protection system
"""

import time
import threading
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute


class ThermalState(Enum):
    """Thermal state enumeration"""
    NORMAL = "normal"
    WARM = "warm"
    HOT = "hot"
    CRITICAL = "critical"
    OVERHEATED = "overheated"


@dataclass
class ThermalReading:
    """Thermal sensor reading"""
    timestamp: float
    temperature: float
    humidity: Optional[float]
    ambient_temp: Optional[float]
    sensor_location: str
    thermal_state: ThermalState
    warning_level: float
    recommendations: List[str]


@dataclass
class ThermalAlert:
    """Thermal alert configuration"""
    temperature_threshold: float
    alert_type: str
    message: str
    action_required: bool
    auto_action: Optional[str]


class ThermalMonitor:
    """Advanced thermal monitoring system"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Thermal data
        self.thermal_readings: List[ThermalReading] = []
        self.alerts: List[ThermalAlert] = []
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        # Configuration
        self.config = {
            'monitoring_interval': 5.0,  # seconds
            'max_readings': 1000,
            'warning_threshold': 45.0,  # °C
            'critical_threshold': 60.0,  # °C
            'shutdown_threshold': 75.0,  # °C
            'ambient_compensation': True,
            'sensor_locations': ['sensor_1', 'sensor_2', 'sensor_3']
        }
        
        # Thermal models
        self.thermal_models = {
            'sensor_1': self._create_sensor_model('sensor_1', 'DPI Sensor'),
            'sensor_2': self._create_sensor_model('sensor_2', 'RGB Controller'),
            'sensor_3': self._create_sensor_model('sensor_3', 'Main Processor')
        }
        
        # Callbacks
        self.thermal_callbacks: List[Callable[[ThermalReading], None]] = []
        self.alert_callbacks: List[Callable[[ThermalAlert], None]] = []
        
        # Protection state
        self.protection_active = False
        self.protection_actions = []
        
        # Statistics
        self.stats = {
            'max_temperature': 0.0,
            'avg_temperature': 0.0,
            'alert_count': 0,
            'protection_activations': 0,
            'uptime': 0.0
        }
        
        # Monitoring lock
        self.monitor_lock = threading.Lock()
    
    def _create_sensor_model(self, sensor_id: str, description: str) -> Dict[str, Any]:
        """Create sensor model configuration"""
        return {
            'id': sensor_id,
            'description': description,
            'location': description,
            'calibration_offset': 0.0,
            'accuracy': 0.5,
            'min_temp': -20.0,
            'max_temp': 100.0,
            'optimal_range': (20.0, 40.0),
            'response_time': 2.0,
            'drift_rate': 0.1
        }
    
    def start_monitoring(self) -> bool:
        """Start thermal monitoring"""
        with self.monitor_lock:
            if self.monitoring:
                return False
            
            self.monitoring = True
            self.stop_monitoring.clear()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("Thermal monitoring started")
            return True
    
    def stop_monitoring(self):
        """Stop thermal monitoring"""
        with self.monitor_lock:
            if not self.monitoring:
                return
            
            self.monitoring = False
            self.stop_monitoring.set()
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5.0)
            
            self.logger.info("Thermal monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.stats['uptime'] = time.time()
        
        while not self.stop_monitoring.wait(self.config['monitoring_interval']):
            try:
                # Collect thermal readings from all sensors
                readings = self._collect_thermal_readings()
                
                # Process readings
                for reading in readings:
                    self._process_thermal_reading(reading)
                
                # Update statistics
                self._update_statistics()
                
                # Check for alerts
                self._check_thermal_alerts()
                
                # Apply protection if needed
                self._apply_thermal_protection()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)  # Prevent tight error loop
    
    def _collect_thermal_readings(self) -> List[ThermalReading]:
        """Collect thermal readings from all sensors"""
        readings = []
        
        for sensor_id in self.config['sensor_locations']:
            try:
                reading = self._read_sensor_temperature(sensor_id)
                if reading:
                    readings.append(reading)
            except Exception as e:
                self.logger.error(f"Error reading sensor {sensor_id}: {e}")
        
        return readings
    
    def _read_sensor_temperature(self, sensor_id: str) -> Optional[ThermalReading]:
        """Read temperature from a specific sensor"""
        try:
            # Get sensor model
            model = self.thermal_models.get(sensor_id)
            if not model:
                return None
            
            # Simulate sensor reading
            # In real implementation, this would interface with actual thermal sensors
            raw_temp = self._simulate_sensor_reading(model)
            
            # Apply calibration
            calibrated_temp = raw_temp + model['calibration_offset']
            
            # Get ambient temperature for compensation
            ambient_temp = self._get_ambient_temperature() if self.config['ambient_compensation'] else None
            
            # Determine thermal state
            thermal_state = self._determine_thermal_state(calibrated_temp)
            
            # Calculate warning level
            warning_level = self._calculate_warning_level(calibrated_temp)
            
            # Generate recommendations
            recommendations = self._generate_thermal_recommendations(calibrated_temp, thermal_state)
            
            reading = ThermalReading(
                timestamp=time.time(),
                temperature=calibrated_temp,
                humidity=None,  # Could be added later
                ambient_temp=ambient_temp,
                sensor_location=sensor_id,
                thermal_state=thermal_state,
                warning_level=warning_level,
                recommendations=recommendations
            )
            
            return reading
            
        except Exception as e:
            self.logger.error(f"Error reading sensor {sensor_id}: {e}")
            return None
    
    def _simulate_sensor_reading(self, model: Dict[str, Any]) -> float:
        """Simulate sensor reading for testing"""
        try:
            # Base temperature with time-based variation
            base_temp = 35.0
            time_factor = math.sin(time.time() * 0.1) * 2.0  # 2°C variation
            noise_factor = np.random.normal(0, 0.5)  # 0.5°C noise
            
            # Add load-based temperature increase
            load_factor = math.sin(time.time() * 0.05) * 5.0  # 5°C variation
            
            raw_temp = base_temp + time_factor + noise_factor + load_factor
            
            # Clamp to sensor range
            return max(model['min_temp'], min(model['max_temp'], raw_temp))
            
        except Exception:
            return 35.0  # Default temperature
    
    def _get_ambient_temperature(self) -> float:
        """Get ambient temperature"""
        try:
            # In real implementation, this would read from ambient temperature sensor
            # For now, simulate ambient temperature
            return 22.0 + math.sin(time.time() * 0.001) * 5.0
        except Exception:
            return 22.0
    
    def _determine_thermal_state(self, temperature: float) -> ThermalState:
        """Determine thermal state based on temperature"""
        if temperature >= self.config['shutdown_threshold']:
            return ThermalState.OVERHEATED
        elif temperature >= self.config['critical_threshold']:
            return ThermalState.CRITICAL
        elif temperature >= self.config['warning_threshold']:
            return ThermalState.HOT
        elif temperature >= 35.0:
            return ThermalState.WARM
        else:
            return ThermalState.NORMAL
    
    def _calculate_warning_level(self, temperature: float) -> float:
        """Calculate warning level (0-1)"""
        if temperature < self.config['warning_threshold']:
            return 0.0
        elif temperature < self.config['critical_threshold']:
            return (temperature - self.config['warning_threshold']) / (
                self.config['critical_threshold'] - self.config['warning_threshold']
            )
        elif temperature < self.config['shutdown_threshold']:
            return 0.5 + (temperature - self.config['critical_threshold']) / (
                self.config['shutdown_threshold'] - self.config['critical_threshold']
            )
        else:
            return 1.0
    
    def _generate_thermal_recommendations(self, temperature: float, state: ThermalState) -> List[str]:
        """Generate thermal recommendations"""
        recommendations = []
        
        try:
            if state == ThermalState.NORMAL:
                recommendations.append("✅ Temperature is normal")
                recommendations.append("🌡 Optimal performance range")
            
            elif state == ThermalState.WARM:
                recommendations.append("⚠️ Temperature is elevated")
                recommendations.append("🌡 Ensure good ventilation")
                recommendations.append("🌡 Consider reducing load")
            
            elif state == ThermalState.HOT:
                recommendations.append("🔥 Temperature is high")
                recommendations.append("⚡ Immediate action required")
                recommendations.append("🌡 Check for obstructions")
                recommendations.append("🌡 Reduce device load")
            
            elif state == ThermalState.CRITICAL:
                recommendations.append("🚨 CRITICAL TEMPERATURE")
                recommendations.append("🛑️ SHUTDOWN REQUIRED")
                recommendations.append("🌡 Cool down immediately")
                recommendations.append("🌡 Check for damage")
            
            elif state == ThermalState.OVERHEATED:
                recommendations.append("🔥 OVERHEATED")
                recommendations.append("🛑️ EMERGENCY SHUTDOWN")
                recommendations.append("🌡 Power off immediately")
                recommendations.append("🔥 Check for damage")
            
            # Specific temperature-based recommendations
            if temperature > 70:
                recommendations.append("🔥 Risk of damage - Immediate action required")
            elif temperature > 60:
                recommendations.append("⚠️ Performance may be affected")
            elif temperature > 50:
                recommendations.append("🌡 Consider reducing usage")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append("❌ Unable to generate recommendations")
        
        return recommendations
    
    def _process_thermal_reading(self, reading: ThermalReading):
        """Process thermal reading"""
        try:
            # Add to readings list
            with self.monitor_lock:
                self.thermal_readings.append(reading)
                
                # Limit readings
                if len(self.thermal_readings) > self.config['max_readings']:
                    self.thermal_readings.pop(0)
            
            # Notify callbacks
            for callback in self.thermal_callbacks:
                try:
                    callback(reading)
                except Exception as e:
                    self.logger.error(f"Thermal callback error: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing thermal reading: {e}")
    
    def _update_statistics(self):
        """Update thermal statistics"""
        try:
            if self.thermal_readings:
                temps = [r.temperature for r in self.thermal_readings]
                self.stats['max_temperature'] = max(temps)
                self.stats['avg_temperature'] = sum(temps) / len(temps)
            
            # Update uptime
            if self.monitoring:
                self.stats['uptime'] = time.time() - self.stats['uptime']
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def _check_thermal_alerts(self) -> None:
        """Check for thermal alerts"""
        try:
            if not self.thermal_readings:
                return
            
            latest_reading = self.thermal_readings[-1]
            
            # Check against alert thresholds
            alerts_to_check = [
                ThermalAlert(
                    temperature_threshold=self.config['warning_threshold'],
                    alert_type="warning",
                    message="Temperature elevated",
                    action_required=False,
                    auto_action=None
                ),
                ThermalAlert(
                    temperature_threshold=self.config['critical_threshold'],
                    alert_type="critical",
                    message="Critical temperature",
                    action_required=True,
                    auto_notify=True,
                    auto_action="reduce_performance"
                ),
                ThermalAlert(
                    temperature_threshold=self.config['shutdown_threshold'],
                    alert_type="shutdown",
                    message="Emergency shutdown required",
                    action_required=True,
                    auto_notify=True,
                    auto_action="shutdown"
                )
            ]
            
            for alert in alerts_to_check:
                if latest_reading.temperature >= alert.temperature_threshold:
                    self._trigger_thermal_alert(alert, latest_reading)
                    
        except Exception as e:
            self.logger.error(f"Error checking thermal alerts: {e}")
    
    def _trigger_thermal_alert(self, alert: ThermalAlert, reading: ThermalReading):
        """Trigger thermal alert"""
        try:
            self.alerts.append(alert)
            self.stats['alert_count'] += 1
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
            
            self.logger.warning(f"Thermal alert: {alert.message} - {reading.temperature:.1f}°C")
            
            # Apply auto-action if specified
            if alert.auto_action:
                self._apply_thermal_action(alert.auto_action)
                
        except Exception as e:
            self.logger.error(f"Error triggering thermal alert: {e}")
    
    def _apply_thermal_action(self, action: str) -> bool:
        """Apply automatic thermal protection action"""
        try:
            success = False
            
            if action == "reduce_performance":
                success = self._reduce_performance()
            elif action == "shutdown":
                success = self._emergency_shutdown()
            elif action == "notify_user":
                success = self._notify_user_thermal_warning()
            
            if success:
                self.protection_activations += 1
                self.logger.info(f"Applied thermal protection action: {action}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying thermal action {action}: {e}")
            return False
    
    def _reduce_performance(self) -> bool:
        """Reduce performance to lower temperature"""
        try:
            self.logger.info("Applying thermal protection - reducing performance")
            
            # This would interface with the device controller
            # For now, simulate the action
            self.protection_active = True
            self.protection_actions.append("reduce_performance")
            
            # In real implementation:
            # - Reduce polling rate
            # - Lower RGB brightness
            # - Disable non-essential features
            # - Lower DPI if needed
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error reducing performance: {e}")
            return False
    
    def _emergency_shutdown(self) -> bool:
        """Emergency shutdown due to overheating"""
        try:
            self.logger.critical("EMERGENCY SHUTDOWN - Temperature too high!")
            
            # This would interface with the device controller
            # For now, simulate the action
            self.protection_active = True
            self.protection_actions.append("emergency_shutdown")
            
            # In real implementation:
            # - Save current state
            # - Disconnect device
            # - Show emergency message
            # - Power down if possible
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in emergency shutdown: {e}")
            return False
    
    def _notify_user_thermal_warning(self) -> bool:
        """Notify user of thermal warning"""
        try:
            self.logger.warning("Thermal warning - User notification")
            
            # This would show a user notification
            # For now, simulate the action
            self.protection_actions.append("notify_user")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error notifying user: {e}")
            return False
    
    def _apply_thermal_protection(self):
        """Apply thermal protection based on current state"""
        try:
            if not self.thermal_readings:
                return
            
            latest_reading = self.thermal_readings[-1]
            
            # Check if protection is needed
            if latest_reading.thermal_state in [ThermalState.CRITICAL, ThermalState.OVERHEATED]:
                if not self.protection_active:
                    self._initiate_protection()
            elif self.protection_active and latest_reading.thermal_state in [ThermalState.WARM, ThermalState.NORMAL]:
                self._disable_protection()
                
        except Exception as e:
            self.logger.error(f"Error applying thermal protection: {e}")
    
    def _initiate_protection(self):
        """Initiate thermal protection"""
        try:
            self.logger.warning("Initiating thermal protection")
            
            # Determine appropriate action
            latest_reading = self.thermal_readings[-1]
            
            if latest_reading.thermal_state == ThermalState.OVERHEATED:
                self._apply_thermal_action("shutdown")
            elif latest_reading.thermal_state == ThermalState.CRITICAL:
                self._apply_thermal_action("reduce_performance")
            elif latest_reading.thermal_state == ThermalState.HOT:
                self._apply_thermal_action("reduce_performance")
            
        except Exception as e:
            self.logger.error(f"Error initiating protection: {e}")
    
    def _disable_protection(self):
        """Disable thermal protection"""
        try:
            if self.protection_active:
                self.logger.info("Disabling thermal protection")
            
            self.protection_active = False
            self.protection_actions = []
            
            # Restore normal performance
            # In real implementation:
            # - Restore original settings
            # - Re-enable features
            # - Restore polling rate
            
        except Exception as e:
            self.logger.error(f"Error disabling protection: {e}")
    
    def add_thermal_callback(self, callback: Callable[[ThermalReading], None]):
        """Add thermal callback"""
        self.thermal_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable[[ThermalAlert], None]):
        """Add alert callback"""
        self.alert_callbacks.append(callback)
    
    def get_thermal_status(self) -> Dict[str, Any]:
        """Get current thermal status"""
        try:
            if not self.thermal_readings:
                return {
                    'monitoring': self.monitoring,
                    'current_temperature': None,
                    'thermal_state': 'unknown',
                    'protection_active': self.protection_active,
                    'stats': self.stats
                }
            
            latest_reading = self.thermal_readings[-1]
            
            return {
                'monitoring': self.monitoring,
                'current_temperature': latest_reading.temperature,
                'thermal_state': latest_reading.thermal_state.value,
                'protection_active': self.protection_active,
                'stats': self.stats,
                'recommendations': latest_reading.recommendations,
                'alert_count': len(self.alerts),
                'last_update': latest_reading.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error getting thermal status: {e}")
            return {'error': str(e)}
    
    def get_thermal_history(self, hours: int = 24) -> List[ThermalReading]:
        """Get thermal history for specified period"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            return [
                reading for reading in self.thermal_readings
                if reading.timestamp > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting thermal history: {e}")
            return []
    
    def get_thermal_summary(self) -> Dict[str, Any]:
        """Get thermal summary statistics"""
        try:
            if not self.thermal_readings:
                return {'message': 'No thermal data available'}
            
            temps = [r.temperature for r in self.thermal_readings]
            
            return {
                'monitoring': self.monitoring,
                'total_readings': len(self.thermal_readings),
                'min_temperature': min(temps),
                'max_temperature': max(temps),
                'avg_temperature': sum(thermal_readings) / len(thermal_readings),
                'thermal_trends': self._calculate_thermal_trends(),
                'protection_stats': {
                    'active': self.protection_active,
                    'total_activations': self.protection_activations,
                    'last_actions': self.protection_actions.copy()
                },
                'stats': self.stats
            }
            
        except Exception as e:
            self.logger.error(f"Error getting thermal summary: {e}")
            return {'error': str(e)}
    
    def _calculate_thermal_trends(self) -> Dict[str, Any]:
        """Calculate thermal trends"""
        try:
            if len(self.thermal_readings) < 10:
                return {'trend': 'Insufficient data'}
            
            # Calculate trends over last hour
            recent_readings = self._get_thermal_history(1)
            older_readings = self._get_thermal_history(24)
            
            if recent_readings and older_readings:
                recent_avg = sum(r.temperature for r in recent_readings) / len(recent_readings)
                older_avg = sum(r.temperature for r in older_readings) / len(older_readings)
                
                if recent_avg > older_avg * 1.05:
                    return {'trend': 'Increasing', 'recent': recent_avg, 'older': older_avg}
                elif recent_avg < older_avg * 0.95:
                    return {'trend': 'Decreasing', 'recent': recent_avg, 'older': older_avg}
                else:
                    return {'trend': 'Stable', 'recent': recent_avg, 'older': older_avg}
            
            return {'trend': 'Stable', 'recent': 0.0, 'older': 0.0}
            
        except Exception as e:
            self.logger.error(f"Error calculating thermal trends: {e}")
            return {'trend': 'Unknown'}
    
    def set_config(self, **kwargs):
        """Update thermal monitoring configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated thermal config {key} = {value}")
    
    def export_thermal_data(self, file_path: str) -> bool:
        """Export thermal data to file"""
        try:
            import json
            
            export_data = {
                'export_time': time.time(),
                'config': self.config,
                'thermal_summary': self.get_thermal_summary(),
                'thermal_history': [asdict(r) for r in self.thermal_readings],
                'alerts': [asdict(a) for a in self.alerts],
                'stats': self.stats
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Thermal data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting thermal data: {e}")
            return False
    
    def create_thermal_report(self) -> str:
        """Create comprehensive thermal report"""
        try:
            if not self.thermal_readings:
                return "No thermal data available for report generation."
            
            temps = [r.temperature for r in self.thermal_readings]
            
            report = f"""
🌡️ THERMAL MONITORING REPORT
{'='*60}

Generated: {datetime.fromtimestamp(self.thermal_readings[-1].timestamp).strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

OVERVIEW
{'='*60}
Monitoring Status: {'Active' if self.monitoring else 'Inactive'}
Current Temperature: {self.thermal_readings[-1].temperature:.1f}°C
Thermal State: {self.temperature_state}
Protection Active: {'Yes' if self.protection_active else 'No'}
Protection Actions: {len(self.protection_actions)} actions performed

TEMPERATURE ANALYSIS
{'='*60}
Current: {self.thermal_readings[-1].temperature:.2f}°C
Average: {sum(temps) / len(temps):.2f}°C
Minimum: {min(temps):.2f}°C
Maximum: {max(temps):.2f}°C
Range: {max(temps) - min(temps):.2f}°C

TRENDS
{'='*60}
{'='*60}
{self._calculate_thermal_trends()}

ALERT HISTORY
{'='*60}
Total Alerts: {len(self.alerts)}
Last Alert: {self.alerts[-1].message if self.alerts else 'No alerts'}
Critical Alerts: {len([a for a in self.alerts if a.alert_type == 'critical'])}
Warning Alerts: {len([a for a in self.alerts if a.alert_type == 'warning'])}

RECOMMENDATIONS
{'='*60}
{self.thermal_readings[-1].recommendations[0] if self.thermal_readings[-1].recommendations else 'No recommendations'}

PROTECTION STATISTICS
{'='*60}
Total Protection Activations: {self.protection_activations}
Protection Actions: {', '.join(self.protection_actions) if self.protection_actions else 'None'}
Current Protection: {'Active' if self.protection_active else 'Inactive'}
"""
            
        except Exception as e:
            self.logger.error(f"Error creating thermal report: {e}")
            return f"Error creating thermal report: {e}"
        
        return report
