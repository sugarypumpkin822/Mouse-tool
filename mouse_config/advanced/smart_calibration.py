"""
Smart calibration system for mouse sensors
"""

import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
import math

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute


class CalibrationMode(Enum):
    """Calibration modes"""
    AUTOMATIC = "automatic"
    PRECISION = "precision"
    GAMING = "gaming"
    COMFORT = "comfort"
    CUSTOM = "custom"


@dataclass
class CalibrationResult:
    """Calibration result data"""
    success: bool
    mode: str
    settings: Dict[str, Any]
    accuracy_improvement: float
    stability_score: float
    recommendations: List[str]
    calibration_data: Dict[str, Any]


@dataclass
class SensorData:
    """Sensor measurement data"""
    raw_values: List[float]
    filtered_values: List[float]
    noise_level: float
    drift_rate: float
    linearity_error: float
    timestamp: float


class SmartCalibrator:
    """Smart calibration system for mouse sensors"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Calibration data
        self.calibration_history: List[CalibrationResult] = []
        self.sensor_data: List[SensorData] = []
        
        # Calibration state
        self.calibrating = False
        self.current_mode = CalibrationMode.AUTOMATIC
        self.progress = 0.0
        
        # Calibration parameters
        self.calibration_params = {
            'sample_count': 100,
            'settle_time': 0.5,
            'measurement_interval': 0.01,
            'noise_threshold': 2.0,
            'drift_threshold': 0.1,
            'linearity_tolerance': 5.0
        }
        
        # Calibration lock
        self.calibration_lock = threading.Lock()
        
        # Sensor models
        self.sensor_models = {
            'dpi': self._create_dpi_model(),
            'angle_snapping': self._create_angle_snapping_model(),
            'lift_off_distance': self._create_lod_model(),
            'debounce': self._create_debounce_model()
        }
    
    def calibrate_sensor(self, sensor_type: str, mode: CalibrationMode = CalibrationMode.AUTOMATIC) -> CalibrationResult:
        """Calibrate a specific sensor"""
        with self.calibration_lock:
            if self.calibrating:
                return CalibrationResult(
                    success=False,
                    mode=mode.value,
                    settings={},
                    accuracy_improvement=0.0,
                    stability_score=0.0,
                    recommendations=["Calibration already in progress"],
                    calibration_data={}
                )
            
            self.calibrating = True
            self.current_mode = mode
            self.progress = 0.0
            
            try:
                self.logger.info(f"Starting {sensor_type} calibration in {mode.value} mode")
                
                # Collect sensor data
                sensor_data = self._collect_sensor_data(sensor_type)
                
                # Analyze sensor characteristics
                analysis = self._analyze_sensor_characteristics(sensor_data)
                
                # Generate calibration settings
                settings = self._generate_calibration_settings(sensor_type, mode, analysis)
                
                # Validate calibration
                validation = self._validate_calibration(sensor_type, settings)
                
                # Apply calibration
                if validation['valid']:
                    applied_settings = self._apply_calibration(sensor_type, settings)
                    success = True
                else:
                    applied_settings = {}
                    success = False
                
                # Calculate improvements
                improvements = self._calculate_improvements(sensor_type, applied_settings)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(sensor_type, analysis, validation)
                
                result = CalibrationResult(
                    success=success,
                    mode=mode.value,
                    settings=applied_settings,
                    accuracy_improvement=improvements.get('accuracy', 0.0),
                    stability_score=improvements.get('stability', 0.0),
                    recommendations=recommendations,
                    calibration_data={
                        'sensor_data': sensor_data,
                        'analysis': analysis,
                        'validation': validation
                    }
                )
                
                # Store result
                self.calibration_history.append(result)
                if len(self.calibration_history) > 50:
                    self.calibration_history.pop(0)
                
                self.logger.info(f"Calibration completed: {'Success' if success else 'Failed'}")
                return result
                
            except Exception as e:
                self.logger.error(f"Calibration failed: {e}")
                return CalibrationResult(
                    success=False,
                    mode=mode.value,
                    settings={},
                    accuracy_improvement=0.0,
                    stability_score=0.0,
                    recommendations=[f"Calibration error: {e}"],
                    calibration_data={}
                )
            finally:
                self.calibrating = False
                self.progress = 0.0
    
    def _collect_sensor_data(self, sensor_type: str) -> SensorData:
        """Collect raw sensor data"""
        try:
            self.progress = 0.1
            
            raw_values = []
            filtered_values = []
            timestamps = []
            
            # Collect samples
            for i in range(self.calibration_params['sample_count']):
                self.progress = 0.1 + (i / self.calibration_params['sample_count']) * 0.4
                
                # Get raw sensor reading
                raw_value = self._read_sensor_value(sensor_type)
                raw_values.append(raw_value)
                
                # Apply simple filter
                filtered_value = self._apply_filter(raw_values, sensor_type)
                filtered_values.append(filtered_value)
                
                timestamps.append(time.time())
                
                # Wait between samples
                time.sleep(self.calibration_params['measurement_interval'])
            
            # Calculate metrics
            noise_level = self._calculate_noise_level(raw_values)
            drift_rate = self._calculate_drift_rate(filtered_values)
            linearity_error = self._calculate_linearity_error(filtered_values)
            
            sensor_data = SensorData(
                raw_values=raw_values,
                filtered_values=filtered_values,
                noise_level=noise_level,
                drift_rate=drift_rate,
                linearity_error=linearity_error,
                timestamp=time.time()
            )
            
            self.sensor_data.append(sensor_data)
            if len(self.sensor_data) > 100:
                self.sensor_data.pop(0)
            
            return sensor_data
            
        except Exception as e:
            self.logger.error(f"Error collecting sensor data: {e}")
            raise
    
    def _read_sensor_value(self, sensor_type: str) -> float:
        """Read raw sensor value"""
        # This would interface with the actual sensor
        # For now, simulate sensor readings
        if sensor_type == 'dpi':
            # Simulate DPI sensor reading
            base_value = 800
            noise = np.random.normal(0, 5)
            return base_value + noise
        elif sensor_type == 'angle_snapping':
            # Simulate angle sensor
            base_value = 0.0
            noise = np.random.normal(0, 2)
            return base_value + noise
        elif sensor_type == 'lift_off_distance':
            # Simulate LOD sensor
            base_value = 2.0
            noise = np.random.normal(0, 0.5)
            return max(0, min(3, base_value + noise))
        elif sensor_type == 'debounce':
            # Simulate debounce sensor
            base_value = 4.0
            noise = np.random.normal(0, 1)
            return max(2, min(16, base_value + noise))
        else:
            return 0.0
    
    def _apply_filter(self, values: List[float], sensor_type: str) -> float:
        """Apply filter to sensor values"""
        if len(values) < 3:
            return values[-1] if values else 0.0
        
        # Use median filter for noise reduction
        return statistics.median(values[-3:])
    
    def _calculate_noise_level(self, values: List[float]) -> float:
        """Calculate noise level in sensor readings"""
        if len(values) < 2:
            return 0.0
        
        # Calculate standard deviation
        return statistics.stdev(values)
    
    def _calculate_drift_rate(self, values: List[float]) -> float:
        """Calculate drift rate"""
        if len(values) < 10:
            return 0.0
        
        # Calculate linear regression slope
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return abs(slope)
    
    def _calculate_linearity_error(self, values: List[float]) -> float:
        """Calculate linearity error"""
        if len(values) < 2:
            return 0.0
        
        # Calculate deviation from linear fit
        x = list(range(len(values)))
        n = len(values)
        
        # Linear regression
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_mean = statistics.mean(values)
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        ss_res = sum((values[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return 1 - r_squared  # Return error (1 - R²)
    
    def _analyze_sensor_characteristics(self, sensor_data: SensorData) -> Dict[str, Any]:
        """Analyze sensor characteristics"""
        try:
            analysis = {
                'noise_level': sensor_data.noise_level,
                'drift_rate': sensor_data.drift_rate,
                'linearity_error': sensor_data.linearity_error,
                'stability': self._calculate_stability(sensor_data),
                'quality_score': self._calculate_quality_score(sensor_data),
                'characteristics': self._classify_characteristics(sensor_data)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing sensor characteristics: {e}")
            return {}
    
    def _calculate_stability(self, sensor_data: SensorData) -> float:
        """Calculate sensor stability score"""
        try:
            # Stability based on noise, drift, and linearity
            noise_score = max(0, 1 - sensor_data.noise_level / 10.0)
            drift_score = max(0, 1 - sensor_data.drift_rate / 5.0)
            linearity_score = max(0, 1 - sensor_data.linearity_error / 20.0)
            
            # Weighted average
            stability = (noise_score * 0.4 + drift_score * 0.3 + linearity_score * 0.3)
            
            return stability
            
        except Exception:
            return 0.5
    
    def _calculate_quality_score(self, sensor_data: SensorData) -> float:
        """Calculate overall sensor quality score"""
        try:
            # Quality based on all metrics
            noise_penalty = min(1.0, sensor_data.noise_level / 5.0)
            drift_penalty = min(1.0, sensor_data.drift_rate / 2.0)
            linearity_penalty = min(1.0, sensor_data.linearity_error / 10.0)
            
            # Combined score
            quality = 1.0 - (noise_penalty + drift_penalty + linearity_penalty) / 3.0
            
            return max(0.0, quality)
            
        except Exception:
            return 0.5
    
    def _classify_characteristics(self, sensor_data: SensorData) -> List[str]:
        """Classify sensor characteristics"""
        characteristics = []
        
        try:
            # Noise characteristics
            if sensor_data.noise_level > 5.0:
                characteristics.append("High noise")
            elif sensor_data.noise_level > 2.0:
                characteristics.append("Moderate noise")
            else:
                characteristics.append("Low noise")
            
            # Drift characteristics
            if sensor_data.drift_rate > 1.0:
                characteristics.append("High drift")
            elif sensor_data.drift_rate > 0.5:
                characteristics.append("Moderate drift")
            else:
                characteristics.append("Low drift")
            
            # Linearity characteristics
            if sensor_data.linearity_error > 10.0:
                characteristics.append("Poor linearity")
            elif sensor_data.linearity_error > 5.0:
                characteristics.append("Moderate linearity")
            else:
                characteristics.append("Good linearity")
            
        except Exception as e:
            self.logger.error(f"Error classifying characteristics: {e}")
            characteristics.append("Unknown")
        
        return characteristics
    
    def _generate_calibration_settings(self, sensor_type: str, mode: CalibrationMode, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal calibration settings"""
        try:
            self.progress = 0.5
            
            settings = {}
            
            if sensor_type == 'dpi':
                settings = self._generate_dpi_settings(mode, analysis)
            elif sensor_type == 'angle_snapping':
                settings = self._generate_angle_snapping_settings(mode, analysis)
            elif sensor_type == 'lift_off_distance':
                settings = self._generate_lod_settings(mode, analysis)
            elif sensor_type == 'debounce':
                settings = self._generate_debounce_settings(mode, analysis)
            else:
                settings = {}
            
            self.progress = 0.8
            return settings
            
        except Exception as e:
            self.logger.error(f"Error generating calibration settings: {e}")
            return {}
    
    def _generate_dpi_settings(self, mode: CalibrationMode, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DPI calibration settings"""
        base_settings = {
            'dpi': 800,
            'dpi_stages': [400, 800, 1600, 3200],
            'dpi_smoothing': False,
            'dpi_acceleration': False,
            'dpi_acceleration_offset': 0
        }
        
        if mode == CalibrationMode.PRECISION:
            # Precision mode: optimize for accuracy
            base_settings['dpi'] = 1200
            base_settings['dpi_stages'] = [600, 1200, 2400]
            base_settings['dpi_smoothing'] = True
            
        elif mode == CalibrationMode.GAMING:
            # Gaming mode: optimize for responsiveness
            base_settings['dpi'] = 800
            base_settings['dpi_stages'] = [400, 800, 1600]
            base_settings['dpi_acceleration'] = True
            base_settings['dpi_acceleration_offset'] = 10
            
        elif mode == CalibrationMode.COMFORT:
            # Comfort mode: optimize for smooth movement
            base_settings['dpi'] = 1000
            base_settings['dpi_stages'] = [800, 1000, 1200]
            base_settings['dpi_smoothing'] = True
        
        # Adjust based on analysis
        if 'characteristics' in analysis:
            if 'High noise' in analysis['characteristics']:
                base_settings['dpi_smoothing'] = True
                base_settings['dpi_acceleration'] = False
            
            if 'High drift' in analysis['characteristics']:
                base_settings['dpi_smoothing'] = True
                base_settings['dpi_stages'] = [400, 800, 1200]  # Fewer stages
        
        return base_settings
    
    def _generate_angle_snapping_settings(self, mode: CalibrationMode, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate angle snapping calibration settings"""
        base_settings = {
            'angle_snapping': False,
            'snap_strength': 0.5,
            'snap_angle': 45.0,
            'snap_distance': 20.0
        }
        
        if mode == CalibrationMode.PRECISION:
            base_settings['angle_snapping'] = True
            base_settings['snap_strength'] = 0.8
            base_settings['snap_angle'] = 30.0
            base_settings['snap_distance'] = 15.0
        
        elif mode == CalibrationMode.GAMING:
            base_settings['angle_snapping'] = True
            base_settings['snap_strength'] = 0.6
            base_settings['snap_angle'] = 45.0
            base_settings['snap_distance'] = 25.0
        
        # Adjust based on analysis
        if 'characteristics' in analysis:
            if 'High noise' in analysis['characteristics']:
                base_settings['snap_strength'] = min(1.0, base_settings['snap_strength'] + 0.2)
            
            if 'Poor linearity' in analysis['characteristics']:
                base_settings['snap_strength'] = max(0.3, base_settings['snap_strength'] - 0.2)
        
        return base_settings
    
    def _generate_lod_settings(self, mode: CalibrationMode, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lift-off distance calibration settings"""
        base_settings = {
            'lift_off_distance': 2,  # mm
            'lod_smoothing': False,
            'lod_hysteresis': 0.5
        }
        
        if mode == CalibrationMode.PRECISION:
            base_settings['lift_off_distance'] = 1
            base_settings['lod_smoothing'] = True
            base_settings['lod_hysteresis'] = 0.2
        
        elif mode == CalibrationMode.GAMING:
            base_settings['lift_off_distance'] = 1
            base_settings['lod_smoothing'] = False
            base_settings['lod_hysteresis'] = 0.1
        
        elif mode == CalibrationMode.COMFORT:
            base_settings['lift_off_distance'] = 3
            base_settings['lod_smoothing'] = True
            base_settings['lod_hysteresis'] = 0.8
        
        return base_settings
    
    def _generate_debounce_settings(self, mode: CalibrationMode, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate debounce calibration settings"""
        base_settings = {
            'debounce_time': 4,  # ms
            'debounce_mode': 'normal',
            'debounce_hysteresis': 1.0
        }
        
        if mode == CalibrationMode.PRECISION:
            base_settings['debounce_time'] = 2
            base_settings['debounce_mode'] = 'fast'
            base_settings['debounce_hysteresis'] = 0.5
        
        elif mode == CalibrationMode.GAMING:
            base_settings['debounce_time'] = 2
            base_settings['debounce_mode'] = 'fast'
            base_settings['debounce_hysteresis'] = 0.3
        
        elif mode == CalibrationMode.COMFORT:
            base_settings['debounce_time'] = 8
            base_settings['debounce_mode'] = 'normal'
            base_settings['debounce_hysteresis'] = 2.0
        
        # Adjust based on analysis
        if 'characteristics' in analysis:
            if 'High noise' in analysis['characteristics']:
                base_settings['debounce_time'] = min(16, base_settings['debounce_time'] + 2)
                base_settings['debounce_hysteresis'] = max(0.5, base_settings['debounce_hysteresis'] - 0.5)
        
        return base_settings
    
    def _validate_calibration(self, sensor_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate calibration settings"""
        try:
            validation = {
                'valid': True,
                'warnings': [],
                'errors': [],
                'score': 0.0
            }
            
            # Validate based on sensor type
            if sensor_type == 'dpi':
                if 'dpi' in settings:
                    if not (100 <= settings['dpi'] <= 20000):
                        validation['errors'].append("DPI out of range (100-20000)")
                        validation['valid'] = False
                
                if 'dpi_stages' in settings:
                    for stage in settings['dpi_stages']:
                        if not (100 <= stage <= 20000):
                            validation['warnings'].append(f"DPI stage {stage} out of range")
            
            elif sensor_type == 'lift_off_distance':
                if 'lift_off_distance' in settings:
                    if not (1 <= settings['lift_off_distance'] <= 3):
                        validation['errors'].append("LOD out of range (1-3mm)")
                        validation['valid'] = False
            
            elif sensor_type == 'debounce':
                if 'debounce_time' in settings:
                    if not (2 <= settings['debounce_time'] <= 16):
                        validation['errors'].append("Debounce time out of range (2-16ms)")
                        validation['valid'] = False
            
            # Calculate validation score
            if validation['valid']:
                validation['score'] = 1.0 - len(validation['warnings']) * 0.1 - len(validation['errors']) * 0.5
            else:
                validation['score'] = 0.0
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Error validating calibration: {e}")
            return {'valid': False, 'errors': [str(e)], 'warnings': [], 'score': 0.0}
    
    def _apply_calibration(self, sensor_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Apply calibration settings to device"""
        try:
            self.progress = 0.9
            
            applied_settings = {}
            
            # This would interface with the actual device
            # For now, simulate application
            if sensor_type == 'dpi':
                applied_settings['dpi'] = settings.get('dpi', 800)
                applied_settings['dpi_stages'] = settings.get('dpi_stages', [400, 800, 1600])
            
            elif sensor_type == 'angle_snapping':
                applied_settings['angle_snapping'] = settings.get('angle_snapping', False)
                applied_settings['snap_strength'] = settings.get('snap_strength', 0.5)
            
            elif sensor_type == 'lift_off_distance':
                applied_settings['lift_off_distance'] = settings.get('lift_off_distance', 2)
            
            elif sensor_type == 'debounce':
                applied_settings['debounce_time'] = settings.get('debounce_time', 4)
            
            self.progress = 1.0
            return applied_settings
            
        except Exception as e:
            self.logger.error(f"Error applying calibration: {e}")
            return {}
    
    def _calculate_improvements(self, sensor_type: str, applied_settings: Dict[str, Any]) -> Dict[str, float]:
        """Calculate calibration improvements"""
        try:
            improvements = {}
            
            # Get baseline metrics from calibration history
            baseline_metrics = self._get_baseline_metrics(sensor_type)
            
            if baseline_metrics:
                # Calculate improvements based on applied settings
                if sensor_type == 'dpi':
                    improvements['accuracy'] = self._calculate_dpi_improvement(applied_settings, baseline_metrics)
                    improvements['stability'] = self._calculate_dpi_stability(applied_settings)
                
                elif sensor_type == 'angle_snapping':
                    improvements['accuracy'] = self._calculate_angle_snapping_improvement(applied_settings, baseline_metrics)
                    improvements['stability'] = self._calculate_angle_snapping_stability(applied_settings)
                
                elif sensor_type == 'lift_off_distance':
                    improvements['consistency'] = self._calculate_lod_improvement(applied_settings, baseline_metrics)
                    improvements['stability'] = self._calculate_lod_stability(applied_settings)
                
                elif sensor_type == 'debounce':
                    improvements['responsiveness'] = self._calculate_debounce_improvement(applied_settings, baseline_metrics)
                    improvements['stability'] = self._calculate_debounce_stability(applied_settings)
            
            return improvements
            
        except Exception as e:
            self.logger.error(f"Error calculating improvements: {e}")
            return {}
    
    def _get_baseline_metrics(self, sensor_type: str) -> Optional[Dict[str, float]]:
        """Get baseline metrics from calibration history"""
        try:
            for result in self.calibration_history[-10:]:  # Last 10 calibrations
                if sensor_type in result.calibration_data.get('validation', {}):
                    # Extract baseline metrics
                    return {
                        'noise_level': result.calibration_data['sensor_data'].noise_level,
                        'drift_rate': result.calibration_data['sensor_data'].drift_rate,
                        'linearity_error': result.calibration_data['sensor_data'].linearity_error
                    }
            
            return None
            
        except Exception:
            return None
    
    def _calculate_dpi_improvement(self, settings: Dict[str, Any], baseline: Dict[str, float]) -> float:
        """Calculate DPI accuracy improvement"""
        try:
            # Simulate improvement calculation
            base_noise = baseline.get('noise_level', 5.0)
            target_noise = 2.0
            
            # Estimate noise reduction from settings
            if settings.get('dpi_smoothing', False):
                estimated_noise = base_noise * 0.7
            else:
                estimated_noise = base_noise
            
            improvement = max(0, (base_noise - estimated_noise) / base_noise) * 0.3
            return improvement
            
        except Exception:
            return 0.0
    
    def _calculate_dpi_stability(self, settings: Dict[str, Any]) -> float:
        """Calculate DPI stability score"""
        try:
            score = 0.5  # Base score
            
            # Add points for features
            if settings.get('dpi_smoothing', False):
                score += 0.2
            
            if not settings.get('dpi_acceleration', False):
                score += 0.2
            
            if len(settings.get('dpi_stages', [])) <= 4:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _calculate_angle_snapping_improvement(self, settings: Dict[str, Any], baseline: Dict[str, float]) -> float:
        """Calculate angle snapping improvement"""
        try:
            base_linearity = baseline.get('linearity_error', 10.0)
            target_linearity = 5.0
            
            # Estimate linearity improvement from settings
            strength = settings.get('snap_strength', 0.5)
            estimated_linearity = base_linearity * (1.0 - strength * 0.3)
            
            improvement = max(0, (base_linearity - estimated_linearity) / base_linearity) * 0.2
            return improvement
            
        except Exception:
            return 0.0
    
    def _calculate_angle_snapping_stability(self, settings: Dict[str, Any]) -> float:
        """Calculate angle snapping stability score"""
        try:
            score = 0.5  # Base score
            
            # Add points for conservative settings
            if settings.get('snap_strength', 0.5) <= 0.7:
                score += 0.2
            
            if settings.get('snap_angle', 45.0) in [30.0, 45.0, 60.0]:
                score += 0.2
            
            if settings.get('snap_distance', 20.0) >= 15.0:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _calculate_lod_improvement(self, settings: Dict[str, Any], baseline: Dict[str, float]) -> float:
        """Calculate LOD improvement"""
        try:
            base_drift = baseline.get('drift_rate', 0.5)
            target_drift = 0.2
            
            # Estimate drift reduction from settings
            if settings.get('lod_smoothing', False):
                estimated_drift = base_drift * 0.7
            else:
                estimated_drift = base_drift * 0.9
            
            improvement = max(0, (base_drift - estimated_drift) / base_drift) * 0.15
            return improvement
            
        except Exception:
            return 0.0
    
    def _calculate_lod_stability(self, settings: Dict[str, Any]) -> float:
        """Calculate LOD stability score"""
        try:
            score = 0.5  # Base score
            
            # Add points for conservative settings
            if settings.get('lift_off_distance', 2) >= 2:
                score += 0.2
            
            if settings.get('lod_smoothing', False):
                score += 0.2
            
            if settings.get('lod_hysteresis', 0.5) >= 0.5:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _calculate_debounce_improvement(self, settings: Dict[str, Any], baseline: Dict[str, float]) -> float:
        """Calculate debounce improvement"""
        try:
            base_noise = baseline.get('noise_level', 5.0)
            target_noise = 2.0
            
            # Estimate noise reduction from settings
            debounce_time = settings.get('debounce_time', 4)
            hysteresis = settings.get('debounce_hysteresis', 1.0)
            
            if debounce_time <= 4 and hysteresis <= 0.5:
                estimated_noise = base_noise * 0.6
            else:
                estimated_noise = base_noise * 0.8
            
            improvement = max(0, (base_noise - estimated_noise) / base_noise) * 0.25
            return improvement
            
        except Exception:
            return 0.0
    
    def _calculate_debounce_stability(self, settings: Dict[str, Any]) -> float:
        """Calculate debounce stability score"""
        try:
            score = 0.5  # Base score
            
            # Add points for reasonable settings
            debounce_time = settings.get('debounce_time', 4)
            if 2 <= debounce_time <= 8:
                score += 0.2
            
            hysteresis = settings.get('debounce_hysteresis', 1.0)
            if 0.5 <= hysteresis <= 2.0:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception:
            return 0.5
    
    def _generate_recommendations(self, sensor_type: str, analysis: Dict[str, Any], validation: Dict[str, Any]) -> List[str]:
        """Generate calibration recommendations"""
        recommendations = []
        
        try:
            # General recommendations
            if not validation['valid']:
                recommendations.append("❌ Calibration failed - check device connection")
                recommendations.append("🔧 Try reducing sensor sensitivity")
                recommendations.append("🔧 Ensure stable surface during calibration")
                return recommendations
            
            if validation['warnings']:
                recommendations.append("⚠️ Calibration completed with warnings")
            
            # Specific recommendations based on analysis
            if 'characteristics' in analysis:
                if 'High noise' in analysis['characteristics']:
                    recommendations.append("🔧 Consider enabling smoothing filters")
                    recommendations.append("🔧 Check for environmental interference")
                
                if 'High drift' in analysis['characteristics']:
                    recommendations.append("🔧 Reduce sensor sensitivity")
                    recommendations.append("🔧 Check for temperature effects")
                
                if 'Poor linearity' in analysis['characteristics']:
                    recommendations.append("🔧 Sensor may need recalibration")
                    recommendations.append("🔧 Check for mechanical issues")
            
            # Mode-specific recommendations
            if self.current_mode == CalibrationMode.PRECISION:
                recommendations.append("🎯 Precision mode optimized for accuracy")
                recommendations.append("📊 Monitor performance metrics")
            
            elif self.current_mode == CalibrationMode.GAMING:
                recommendations.append("🎮 Gaming mode optimized for responsiveness")
                recommendations.append("⚡ Test in actual gaming scenarios")
            
            elif self.current_mode == CalibrationMode.COMFORT:
                recommendations.append("😌 Comfort mode optimized for smooth use")
                recommendations.append("🕒️ Suitable for extended sessions")
            
            if not recommendations:
                recommendations.append("✅ Calibration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append("❌ Unable to generate recommendations")
        
        return recommendations
    
    def get_calibration_progress(self) -> float:
        """Get current calibration progress"""
        return self.progress
    
    def is_calibrating(self) -> bool:
        """Check if calibration is in progress"""
        return self.calibrating
    
    def get_calibration_history(self, sensor_type: Optional[str] = None) -> List[CalibrationResult]:
        """Get calibration history"""
        if sensor_type:
            return [r for r in self.calibration_history if sensor_type in r.settings]
        return self.calibration_history
    
    def get_calibration_summary(self) -> Dict[str, Any]:
        """Get calibration summary"""
        try:
            if not self.calibration_history:
                return {'message': 'No calibration data available'}
            
            # Calculate statistics
            total_calibrations = len(self.calibration_history)
            successful_calibrations = len([r for r in self.calibration_history if r.success])
            
            if successful_calibrations > 0:
                avg_accuracy = statistics.mean([r.accuracy_improvement for r in self.calibration_history if r.success])
                avg_stability = statistics.mean([r.stability_score for r in self.calibration_history if r.success])
            else:
                avg_accuracy = 0.0
                avg_stability = 0.0
            
            # Most recent calibration
            recent = self.calibration_history[-1] if self.calibration_history else None
            
            return {
                'total_calibrations': total_calibrations,
                'successful_calibrations': successful_calibrations,
                'success_rate': successful_calibrations / total_calibrations if total_calibrations > 0 else 0.0,
                'avg_accuracy_improvement': avg_accuracy,
                'avg_stability_score': avg_stability,
                'last_calibration': recent,
                'calibration_trends': self._calculate_calibration_trends()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting calibration summary: {e}")
            return {'error': str(e)}
    
    def _create_dpi_model(self):
        """Create DPI calibration model"""
        return {
            'min_dpi': 100,
            'max_dpi': 25000,
            'optimal_range': (800, 1600),
            'sensitivity_factor': 1.0
        }
    
    def _create_angle_snapping_model(self):
        """Create angle snapping calibration model"""
        return {
            'enabled': False,
            'threshold': 15,
            'strength': 0.5
        }
    
    def _create_lod_model(self):
        """Create lift-off distance calibration model"""
        return {
            'min_distance': 0.5,
            'max_distance': 3.0,
            'optimal_distance': 1.5
        }
    
    def _create_debounce_model(self):
        """Create debounce calibration model"""
        return {
            'enabled': True,
            'delay_ms': 10,
            'threshold': 2
        }
    
    def _calculate_calibration_trends(self) -> Dict[str, str]:
        """Calculate calibration trends"""
        try:
            if len(self.calibration_history) < 2:
                return {'trend': 'Insufficient data'}
            
            recent = self.calibration_history[-5:]
            
            # Compare recent with older calibrations
            if len(recent) >= 2:
                recent_avg_accuracy = statistics.mean([r.accuracy_improvement for r in recent if r.success])
                older_avg_accuracy = statistics.mean([r.accuracy_improvement for r in self.calibration_history[:-5] if r.success])
                
                if recent_avg_accuracy > older_avg_accuracy * 1.1:
                    return {'trend': 'Improving', 'recent': recent_avg_accuracy, 'older': older_avg_accuracy}
                elif recent_avg_accuracy < older_avg_accuracy * 0.9:
                    return {'trend': 'Declining', 'recent': recent_avg_accuracy, 'older': older_avg_accuracy}
                else:
                    return {'trend': 'Stable', 'recent': recent_avg_accuracy, 'older': older_avg_accuracy}
            
            return {'trend': 'Stable', 'recent': 0.0, 'older': 0.0}
            
        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            return {'trend': 'Unknown'}
    
    def export_calibration_data(self, file_path: str) -> bool:
        """Export calibration data to file"""
        try:
            import json
            
            export_data = {
                'export_time': time.time(),
                'calibration_summary': self.get_calibration_summary(),
                'calibration_history': [asdict(r) for r in self.calibration_history],
                'sensor_data': [asdict(s) for s in self.sensor_data],
                'calibration_params': self.calibration_params
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Calibration data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting calibration data: {e}")
            return False
