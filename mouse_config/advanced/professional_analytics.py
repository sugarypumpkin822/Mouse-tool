"""
Professional analytics and performance monitoring system
"""

import time
import json
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import statistics
import math

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute


@dataclass
class PerformanceMetrics:
    """Detailed performance metrics"""
    timestamp: float
    session_id: str
    dpi: int
    polling_rate: int
    avg_speed: float
    max_speed: float
    acceleration: float
    deceleration: float
    jitter: float
    click_frequency: float
    right_click_ratio: float
    scroll_distance: float
    total_distance: float
    session_duration: float
    error_count: int
    efficiency_score: float
    comfort_score: float
    precision_score: float


@dataclass
class DeviceHealthMetrics:
    """Device health and performance metrics"""
    battery_level: float
    battery_health: float
    connection_stability: float
    response_time: float
    error_rate: float
    uptime: float
    temperature: float
    firmware_version: str
    hardware_id: str


class ProfessionalAnalytics:
    """Professional-grade analytics system with database storage"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_path = Path.home() / '.mouse_config' / 'analytics.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Analytics cache
        self.metrics_cache: List[PerformanceMetrics] = []
        self.health_cache: List[DeviceHealthMetrics] = []
        
        # Performance thresholds
        self.thresholds = {
            'speed_optimal': (400, 1200),  # min, max
            'jitter_acceptable': 50.0,
            'response_time_good': 8.0,  # ms
            'battery_warning': 20.0,
            'efficiency_good': 0.7,
            'comfort_good': 0.6
        }
        
        # Analytics lock
        self.analytics_lock = threading.Lock()
    
    def init_database(self):
        """Initialize SQLite database for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        session_id TEXT NOT NULL,
                        dpi INTEGER NOT NULL,
                        polling_rate INTEGER NOT NULL,
                        avg_speed REAL NOT NULL,
                        max_speed REAL NOT NULL,
                        acceleration REAL NOT NULL,
                        deceleration REAL NOT NULL,
                        jitter REAL NOT NULL,
                        click_frequency REAL NOT NULL,
                        right_click_ratio REAL NOT NULL,
                        scroll_distance REAL NOT NULL,
                        total_distance REAL NOT NULL,
                        session_duration REAL NOT NULL,
                        error_count INTEGER NOT NULL,
                        efficiency_score REAL NOT NULL,
                        comfort_score REAL NOT NULL,
                        precision_score REAL NOT NULL
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS device_health (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        battery_level REAL NOT NULL,
                        battery_health REAL NOT NULL,
                        connection_stability REAL NOT NULL,
                        response_time REAL NOT NULL,
                        error_rate REAL NOT NULL,
                        uptime REAL NOT NULL,
                        temperature REAL NOT NULL,
                        firmware_version TEXT NOT NULL,
                        hardware_id TEXT NOT NULL
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        start_time REAL NOT NULL,
                        end_time REAL,
                        duration REAL,
                        device_id TEXT,
                        user_id TEXT,
                        purpose TEXT,
                        notes TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_performance_timestamp 
                    ON performance_metrics(timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_health_timestamp 
                    ON device_health(timestamp)
                ''')
                
                conn.commit()
                
            self.logger.info("Analytics database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def record_performance_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Record performance metrics to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, session_id, dpi, polling_rate, avg_speed, max_speed,
                     acceleration, deceleration, jitter, click_frequency, right_click_ratio,
                     scroll_distance, total_distance, session_duration, error_count,
                     efficiency_score, comfort_score, precision_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp, metrics.session_id, metrics.dpi, metrics.polling_rate,
                    metrics.avg_speed, metrics.max_speed, metrics.acceleration, metrics.deceleration,
                    metrics.jitter, metrics.click_frequency, metrics.right_click_ratio,
                    metrics.scroll_distance, metrics.total_distance, metrics.session_duration,
                    metrics.error_count, metrics.efficiency_score, metrics.comfort_score,
                    metrics.precision_score
                ))
                conn.commit()
            
            # Add to cache
            with self.analytics_lock:
                self.metrics_cache.append(metrics)
                if len(self.metrics_cache) > 1000:
                    self.metrics_cache.pop(0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record performance metrics: {e}")
            return False
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for specified period"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT AVG(avg_speed) as avg_speed,
                           AVG(max_speed) as avg_max_speed,
                           AVG(jitter) as avg_jitter,
                           AVG(click_frequency) as avg_click_freq,
                           AVG(efficiency_score) as avg_efficiency,
                           AVG(comfort_score) as avg_comfort,
                           AVG(precision_score) as avg_precision,
                           COUNT(*) as session_count,
                           SUM(session_duration) as total_duration
                    FROM performance_metrics
                    WHERE timestamp > ?
                ''', (cutoff_time,))
                
                result = cursor.fetchone()
                
                if result and result[0]:
                    return {
                        'period_days': days,
                        'avg_speed': result[0] or 0.0,
                        'avg_max_speed': result[1] or 0.0,
                        'avg_jitter': result[2] or 0.0,
                        'avg_click_frequency': result[3] or 0.0,
                        'avg_efficiency_score': result[4] or 0.0,
                        'avg_comfort_score': result[5] or 0.0,
                        'avg_precision_score': result[6] or 0.0,
                        'session_count': result[7] or 0,
                        'total_duration': result[8] or 0.0,
                        'performance_rating': self._calculate_performance_rating(result[4] or 0.0)
                    }
                else:
                    return {'period_days': days, 'message': 'No data available'}
                    
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_rating(self, efficiency_score: float) -> str:
        """Calculate performance rating based on efficiency score"""
        if efficiency_score >= 0.9:
            return "Excellent"
        elif efficiency_score >= 0.8:
            return "Very Good"
        elif efficiency_score >= 0.7:
            return "Good"
        elif efficiency_score >= 0.6:
            return "Fair"
        elif efficiency_score >= 0.5:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive device health report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT AVG(battery_level) as avg_battery,
                           AVG(battery_health) as avg_health,
                           AVG(connection_stability) as avg_stability,
                           AVG(response_time) as avg_response,
                           AVG(error_rate) as avg_error_rate,
                           AVG(temperature) as avg_temp,
                           MAX(timestamp) as last_update
                    FROM device_health
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (time.time() - 24 * 3600,))  # Last 24 hours
                
                result = cursor.fetchone()
                
                if result and result[0]:
                    return {
                        'battery_level': result[0] or 0.0,
                        'battery_health': result[1] or 0.0,
                        'connection_stability': result[2] or 0.0,
                        'response_time': result[3] or 0.0,
                        'error_rate': result[4] or 0.0,
                        'temperature': result[5] or 0.0,
                        'last_update': result[6] or 0.0,
                        'health_score': self._calculate_health_score(result),
                        'health_status': self._get_health_status(result),
                        'recommendations': self._generate_health_recommendations(result)
                    }
                else:
                    return {'message': 'No health data available'}
                    
        except Exception as e:
            self.logger.error(f"Error getting health report: {e}")
            return {'error': str(e)}
    
    def _calculate_health_score(self, health_data: Tuple) -> float:
        """Calculate overall health score"""
        try:
            battery = health_data[0] or 0.0
            health = health_data[1] or 0.0
            stability = health_data[2] or 0.0
            response = health_data[3] or 0.0
            error_rate = health_data[4] or 0.0
            
            # Weighted health score
            health_score = (
                (battery / 100.0) * 0.2 +
                (health / 100.0) * 0.2 +
                stability * 0.2 +
                max(0.0, 1.0 - response / 20.0) * 0.2 +
                max(0.0, 1.0 - error_rate) * 0.2
            )
            
            return max(0.0, min(1.0, health_score))
            
        except Exception:
            return 0.5
    
    def _get_health_status(self, health_data: Tuple) -> str:
        """Get health status based on metrics"""
        try:
            health_score = self._calculate_health_score(health_data)
            battery = health_data[0] or 0.0
            
            if battery < 10:
                return "Critical - Battery Very Low"
            elif health_score >= 0.8:
                return "Excellent"
            elif health_score >= 0.6:
                return "Good"
            elif health_score >= 0.4:
                return "Fair"
            else:
                return "Poor"
                
        except Exception:
            return "Unknown"
    
    def _generate_health_recommendations(self, health_data: Tuple) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        try:
            battery = health_data[0] or 0.0
            health = health_data[1] or 0.0
            stability = health_data[2] or 0.0
            response = health_data[3] or 0.0
            error_rate = health_data[4] or 0.0
            
            if battery < 20:
                recommendations.append("🔋 Battery level is low - consider charging soon")
            elif health < 70:
                recommendations.append("🔋 Battery health declining - consider replacement")
            
            if stability < 0.8:
                recommendations.append("📡 Connection stability issues - check USB port")
            
            if response > 15:
                recommendations.append("⚡ Response time is high - check for interference")
            
            if error_rate > 0.05:
                recommendations.append("❌ High error rate - check device connection")
            
            if not recommendations:
                recommendations.append("✅ Device health is good")
                
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append("❌ Unable to generate recommendations")
        
        return recommendations
