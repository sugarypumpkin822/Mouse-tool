"""
AI-powered mouse optimization system
"""

import time
import statistics
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger


class OptimizationGoal(Enum):
    """Optimization goals"""
    FPS = "fps"
    PRECISION = "precision"
    COMFORT = "comfort"
    BALANCED = "balanced"
    POWER_SAVING = "power_saving"


@dataclass
class MouseMetrics:
    """Mouse usage metrics"""
    avg_speed: float
    max_speed: float
    acceleration_events: int
    click_frequency: float
    movement_patterns: List[str]
    session_duration: float
    total_distance: float
    right_click_ratio: float
    scroll_usage: float


@dataclass
class OptimizationProfile:
    """Optimization profile configuration"""
    name: str
    goal: OptimizationGoal
    dpi: int
    polling_rate: int
    lift_off_distance: int
    angle_snapping: bool
    debounce_time: int
    rgb_brightness: int
    description: str


class AIOptimizer:
    """AI-powered mouse optimization system"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Optimization profiles
        self.profiles = {
            OptimizationGoal.FPS: OptimizationProfile(
                "FPS Gaming",
                OptimizationGoal.FPS,
                dpi=800,
                polling_rate=1000,
                lift_off_distance=1,
                angle_snapping=True,
                debounce_time=2,
                rgb_brightness=80,
                description="Optimized for competitive FPS gaming with fast reactions"
            ),
            OptimizationGoal.PRECISION: OptimizationProfile(
                "Precision Work",
                OptimizationGoal.PRECISION,
                dpi=1200,
                polling_rate=1000,
                lift_off_distance=1,
                angle_snapping=True,
                debounce_time=2,
                rgb_brightness=60,
                description="Optimized for precise cursor movements"
            ),
            OptimizationGoal.COMFORT: OptimizationProfile(
                "Comfort Use",
                OptimizationGoal.COMFORT,
                dpi=1000,
                polling_rate=500,
                lift_off_distance=2,
                angle_snapping=False,
                debounce_time=8,
                rgb_brightness=50,
                description="Optimized for comfortable everyday use"
            ),
            OptimizationGoal.BALANCED: OptimizationProfile(
                "Balanced",
                OptimizationGoal.BALANCED,
                dpi=800,
                polling_rate=1000,
                lift_off_distance=2,
                angle_snapping=False,
                debounce_time=4,
                rgb_brightness=70,
                description="Balanced settings for general use"
            ),
            OptimizationGoal.POWER_SAVING: OptimizationProfile(
                "Power Saving",
                OptimizationGoal.POWER_SAVING,
                dpi=600,
                polling_rate=250,
                lift_off_distance=3,
                angle_snapping=False,
                debounce_time=16,
                rgb_brightness=30,
                description="Optimized for battery life on wireless mice"
            )
        }
        
        # Learning data
        self.usage_history: List[MouseMetrics] = []
        self.optimization_history: List[Tuple[MouseMetrics, OptimizationProfile]] = []
        
        # AI model parameters
        self.learning_rate = 0.1
        self.history_size = 100
        
    def analyze_usage_pattern(self, metrics: MouseMetrics) -> Dict[str, Any]:
        """Analyze mouse usage patterns"""
        analysis = {
            'usage_type': self.classify_usage_type(metrics),
            'skill_level': self.estimate_skill_level(metrics),
            'recommendations': self.generate_recommendations(metrics),
            'efficiency_score': self.calculate_efficiency_score(metrics),
            'risk_factors': self.identify_risk_factors(metrics)
        }
        
        return analysis
    
    def classify_usage_type(self, metrics: MouseMetrics) -> str:
        """Classify the type of usage based on metrics"""
        try:
            # Calculate usage characteristics
            click_rate = metrics.click_frequency
            avg_speed = metrics.avg_speed
            right_click_ratio = metrics.right_click_ratio
            
            # Classification logic
            if click_rate > 60 and avg_speed > 500 and right_click_ratio < 0.2:
                return "FPS Gaming"
            elif click_rate > 30 and right_click_ratio > 0.3:
                return "Productivity"
            elif avg_speed < 200 and click_rate < 20:
                return "Casual Browsing"
            elif avg_speed > 800 and metrics.acceleration_events > 10:
                return "Creative Work"
            else:
                return "General Use"
                
        except Exception as e:
            self.logger.error(f"Error classifying usage type: {e}")
            return "Unknown"
    
    def estimate_skill_level(self, metrics: MouseMetrics) -> str:
        """Estimate user skill level based on metrics"""
        try:
            # Skill indicators
            speed_consistency = self.calculate_speed_consistency(metrics)
            click_accuracy = self.estimate_click_accuracy(metrics)
            movement_efficiency = self.calculate_movement_efficiency(metrics)
            
            # Calculate overall skill score
            skill_score = (speed_consistency + click_accuracy + movement_efficiency) / 3
            
            if skill_score > 0.8:
                return "Expert"
            elif skill_score > 0.6:
                return "Advanced"
            elif skill_score > 0.4:
                return "Intermediate"
            elif skill_score > 0.2:
                return "Beginner"
            else:
                return "Novice"
                
        except Exception as e:
            self.logger.error(f"Error estimating skill level: {e}")
            return "Unknown"
    
    def calculate_speed_consistency(self, metrics: MouseMetrics) -> float:
        """Calculate how consistent the user's speed is"""
        try:
            # This would normally use speed variance from detailed tracking data
            # For now, use max_speed vs avg_speed ratio
            if metrics.avg_speed > 0:
                consistency = 1 - (metrics.max_speed - metrics.avg_speed) / metrics.avg_speed
                return max(0, min(1, consistency))
            return 0.5
        except:
            return 0.5
    
    def estimate_click_accuracy(self, metrics: MouseMetrics) -> float:
        """Estimate click accuracy based on metrics"""
        try:
            # This would normally use click position data
            # For now, use click frequency and session duration
            if metrics.session_duration > 0:
                clicks_per_minute = metrics.click_frequency
                # Higher click rate with longer sessions suggests better accuracy
                accuracy_score = min(1.0, clicks_per_minute / 60) * min(1.0, metrics.session_duration / 3600)
                return accuracy_score
            return 0.5
        except:
            return 0.5
    
    def calculate_movement_efficiency(self, metrics: MouseMetrics) -> float:
        """Calculate movement efficiency"""
        try:
            if metrics.total_distance > 0 and metrics.session_duration > 0:
                # Efficiency = distance / time with penalty for excessive acceleration
                base_efficiency = metrics.total_distance / metrics.session_duration
                
                # Penalty for too many acceleration events
                acceleration_penalty = metrics.acceleration_events * 0.01
                
                efficiency = base_efficiency * (1 - acceleration_penalty)
                return max(0, min(1, efficiency))
            return 0.5
        except:
            return 0.5
    
    def generate_recommendations(self, metrics: MouseMetrics) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        try:
            usage_type = self.classify_usage_type(metrics)
            skill_level = self.estimate_skill_level(metrics)
            
            # DPI recommendations
            if metrics.avg_speed < 300:
                recommendations.append("Consider increasing DPI for faster cursor movement")
            elif metrics.avg_speed > 1500:
                recommendations.append("Consider decreasing DPI for better precision")
            
            # Polling rate recommendations
            if usage_type == "FPS Gaming" and metrics.session_duration > 3600:
                recommendations.append("1000Hz polling rate recommended for competitive gaming")
            elif usage_type == "Productivity":
                recommendations.append("500-1000Hz polling rate is sufficient for productivity")
            
            # Angle snapping recommendations
            if usage_type == "FPS Gaming" and skill_level in ["Expert", "Advanced"]:
                recommendations.append("Enable angle snapping for improved tracking")
            elif usage_type == "Creative Work":
                recommendations.append("Disable angle snapping for natural movement")
            
            # Debounce recommendations
            if metrics.click_frequency > 80:
                recommendations.append("Consider reducing debounce time for faster response")
            elif metrics.click_frequency < 20:
                recommendations.append("Increase debounce time to prevent accidental clicks")
            
            # Lift-off distance recommendations
            if usage_type == "FPS Gaming":
                recommendations.append("Low lift-off distance (1-2mm) recommended for gaming")
            elif usage_type == "Comfort Use":
                recommendations.append("Higher lift-off distance (2-3mm) recommended for comfort")
            
            # RGB recommendations
            if metrics.session_duration > 7200:  # 2+ hours
                recommendations.append("Consider reducing RGB brightness for extended use")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def calculate_efficiency_score(self, metrics: MouseMetrics) -> float:
        """Calculate overall efficiency score"""
        try:
            # Weighted efficiency factors
            speed_score = min(1.0, metrics.avg_speed / 1000)  # Normalized to 1000px/s
            click_score = min(1.0, metrics.click_frequency / 60)  # Normalized to 60 CPM
            consistency_score = self.calculate_speed_consistency(metrics)
            
            # Weighted average
            efficiency = (speed_score * 0.4 + click_score * 0.4 + consistency_score * 0.2)
            
            return efficiency
            
        except Exception as e:
            self.logger.error(f"Error calculating efficiency score: {e}")
            return 0.5
    
    def identify_risk_factors(self, metrics: MouseMetrics) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        try:
            # High speed risks
            if metrics.max_speed > 2000:
                risks.append("Very high cursor speed may cause fatigue")
            
            # Low polling rate risks
            if metrics.session_duration > 3600:  # 1+ hour
                risks.append("Low polling rate may impact responsiveness")
            
            # High click frequency risks
            if metrics.click_frequency > 120:
                risks.append("Very high click frequency may cause strain")
            
            # Acceleration risks
            if metrics.acceleration_events > 50:
                risks.append("Frequent acceleration may indicate inconsistent movement")
            
            # Session duration risks
            if metrics.session_duration > 14400:  # 4+ hours
                risks.append("Extended session may cause fatigue")
                
        except Exception as e:
            self.logger.error(f"Error identifying risk factors: {e}")
        
        return risks
    
    def optimize_settings(self, metrics: MouseMetrics, goal: OptimizationGoal = OptimizationGoal.BALANCED) -> OptimizationProfile:
        """Optimize settings based on usage metrics and goal"""
        try:
            # Get base profile for goal
            base_profile = self.profiles[goal]
            
            # AI adjustments based on metrics
            optimized_profile = self.ai_optimize_profile(base_profile, metrics)
            
            # Add to learning history
            self.optimization_history.append((metrics, optimized_profile))
            if len(self.optimization_history) > self.history_size:
                self.optimization_history.pop(0)
            
            self.logger.info(f"Optimized settings for {goal.value}: DPI={optimized_profile.dpi}, Polling Rate={optimized_profile.polling_rate}")
            
            return optimized_profile
            
        except Exception as e:
            self.logger.error(f"Error optimizing settings: {e}")
            return self.profiles[goal]
    
    def ai_optimize_profile(self, base_profile: OptimizationProfile, metrics: MouseMetrics) -> OptimizationProfile:
        """Apply AI adjustments to base profile"""
        try:
            # Create optimized profile as copy of base
            optimized = OptimizationProfile(
                name=base_profile.name,
                goal=base_profile.goal,
                dpi=base_profile.dpi,
                polling_rate=base_profile.polling_rate,
                lift_off_distance=base_profile.lift_off_distance,
                angle_snapping=base_profile.angle_snapping,
                debounce_time=base_profile.debounce_time,
                rgb_brightness=base_profile.rgb_brightness,
                description=base_profile.description
            )
            
            # DPI optimization
            optimized.dpi = self.optimize_dpi(base_profile.dpi, metrics, base_profile.goal)
            
            # Polling rate optimization
            optimized.polling_rate = self.optimize_polling_rate(base_profile.polling_rate, metrics, base_profile.goal)
            
            # Lift-off distance optimization
            optimized.lift_off_distance = self.optimize_lift_off_distance(base_profile.lift_off_distance, metrics, base_profile.goal)
            
            # Debounce time optimization
            optimized.debounce_time = self.optimize_debounce_time(base_profile.debounce_time, metrics, base_profile.goal)
            
            # Angle snapping optimization
            optimized.angle_snapping = self.optimize_angle_snapping(base_profile.angle_snapping, metrics, base_profile.goal)
            
            # RGB brightness optimization
            optimized.rgb_brightness = self.optimize_rgb_brightness(base_profile.rgb_brightness, metrics, base_profile.goal)
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error in AI optimization: {e}")
            return base_profile
    
    def optimize_dpi(self, base_dpi: int, metrics: MouseMetrics, goal: OptimizationGoal) -> int:
        """AI-optimized DPI setting"""
        try:
            if goal == OptimizationGoal.FPS:
                # For FPS: prioritize speed and precision
                target_speed = 800 + (metrics.avg_speed - 800) * 0.3
                return max(400, min(1600, int(target_speed)))
            
            elif goal == OptimizationGoal.PRECISION:
                # For precision: moderate speed with high accuracy
                return max(800, min(1600, int(metrics.avg_speed * 1.2)))
            
            elif goal == OptimizationGoal.COMFORT:
                # For comfort: moderate speed
                return max(600, min(1200, int(metrics.avg_speed * 0.8)))
            
            elif goal == OptimizationGoal.POWER_SAVING:
                # For power saving: lower speed
                return max(400, min(800, int(metrics.avg_speed * 0.6)))
            
            else:  # BALANCED
                # Balanced: moderate speed
                return max(600, min(1200, int(metrics.avg_speed)))
                
        except Exception as e:
            self.logger.error(f"Error optimizing DPI: {e}")
            return base_dpi
    
    def optimize_polling_rate(self, base_rate: int, metrics: MouseMetrics, goal: OptimizationGoal) -> int:
        """AI-optimized polling rate"""
        try:
            if goal == OptimizationGoal.FPS:
                return 1000  # Always 1000Hz for FPS
            
            elif goal == OptimizationGoal.POWER_SAVING:
                return 250  # Lower for power saving
            
            elif goal == OptimizationGoal.COMFORT:
                return 500  # Moderate for comfort
            
            else:  # PRECISION, BALANCED
                return 1000  # High for responsiveness
                
        except Exception as e:
            self.logger.error(f"Error optimizing polling rate: {e}")
            return base_rate
    
    def optimize_lift_off_distance(self, base_lod: int, metrics: MouseMetrics, goal: OptimizationGoal) -> int:
        """AI-optimized lift-off distance"""
        try:
            if goal == OptimizationGoal.FPS:
                return 1  # Low for gaming
            
            elif goal == OptimizationGoal.COMFORT:
                return 3  # High for comfort
            
            elif goal == OptimizationGoal.PRECISION:
                return 1  # Low for precision
            
            else:  # BALANCED, POWER_SAVING
                return 2  # Moderate
                
        except Exception as e:
            self.logger.error(f"Error optimizing LOD: {e}")
            return base_lod
    
    def optimize_debounce_time(self, base_time: int, metrics: MouseMetrics, goal: OptimizationGoal) -> int:
        """AI-optimized debounce time"""
        try:
            click_frequency = metrics.click_frequency
            
            if goal == OptimizationGoal.FPS:
                # Fast response for gaming
                return max(2, min(4, int(8 - click_frequency / 20)))
            
            elif goal == OptimizationGoal.POWER_SAVING:
                # Slower response to save power
                return max(8, min(16, int(8 + click_frequency / 10)))
            
            else:  # PRECISION, COMFORT, BALANCED
                return max(4, min(8, int(6 + click_frequency / 15)))
                
        except Exception as e:
            self.logger.error(f"Error optimizing debounce: {e}")
            return base_time
    
    def optimize_angle_snapping(self, base_snapping: bool, metrics: MouseMetrics, goal: OptimizationGoal) -> bool:
        """AI-optimized angle snapping"""
        try:
            if goal == OptimizationGoal.FPS:
                return True  # Enable for gaming
            
            elif goal == OptimizationGoal.PRECISION:
                return True  # Enable for precision
            
            elif goal == OptimizationGoal.COMFORT:
                return False  # Disable for comfort
            
            else:  # BALANCED, POWER_SAVING
                return base_snapping  # Keep base setting
                
        except Exception as e:
            self.logger.error(f"Error optimizing angle snapping: {e}")
            return base_snapping
    
    def optimize_rgb_brightness(self, base_brightness: int, metrics: MouseMetrics, goal: OptimizationGoal) -> int:
        """AI-optimized RGB brightness"""
        try:
            session_hours = metrics.session_duration / 3600
            
            if goal == OptimizationGoal.POWER_SAVING:
                return max(10, min(30, base_brightness // 2))
            
            elif session_hours > 4:
                return max(20, min(50, base_brightness // 2))
            
            else:
                return base_brightness
                
        except Exception as e:
            self.logger.error(f"Error optimizing RGB brightness: {e}")
            return base_brightness
    
    def add_usage_data(self, metrics: MouseMetrics):
        """Add usage data to learning history"""
        self.usage_history.append(metrics)
        
        # Limit history size
        if len(self.usage_history) > self.history_size:
            self.usage_history.pop(0)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning data"""
        if not self.usage_history:
            return {"message": "No usage data available"}
        
        try:
            # Calculate averages
            avg_speed = statistics.mean([m.avg_speed for m in self.usage_history])
            avg_click_freq = statistics.mean([m.click_frequency for m in self.usage_history])
            avg_session = statistics.mean([m.session_duration for m in self.usage_history])
            
            # Find most common usage type
            usage_types = [self.classify_usage_type(m) for m in self.usage_history]
            most_common = max(set(usage_types), key=usage_types.count)
            
            return {
                'total_sessions': len(self.usage_history),
                'average_speed': avg_speed,
                'average_click_frequency': avg_click_freq,
                'average_session_duration': avg_session,
                'most_common_usage_type': most_common,
                'skill_progression': self.calculate_skill_progression(),
                'optimization_effectiveness': self.calculate_optimization_effectiveness()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
            return {"error": str(e)}
    
    def calculate_skill_progression(self) -> str:
        """Calculate skill progression over time"""
        try:
            if len(self.usage_history) < 2:
                return "Insufficient data"
            
            # Compare first and last skill levels
            first_skill = self.estimate_skill_level(self.usage_history[0])
            last_skill = self.estimate_skill_level(self.usage_history[-1])
            
            skill_levels = ["Novice", "Beginner", "Intermediate", "Advanced", "Expert"]
            
            first_index = skill_levels.index(first_skill) if first_skill in skill_levels else 2
            last_index = skill_levels.index(last_skill) if last_skill in skill_levels else 2
            
            if last_index > first_index:
                return f"Improved: {skill_levels[first_index]} → {skill_levels[last_index]}"
            elif last_index < first_index:
                return f"Declined: {skill_levels[first_index]} → {skill_levels[last_index]}"
            else:
                return "Stable"
                
        except Exception as e:
            self.logger.error(f"Error calculating skill progression: {e}")
            return "Unknown"
    
    def calculate_optimization_effectiveness(self) -> float:
        """Calculate how effective optimizations have been"""
        try:
            if len(self.optimization_history) < 2:
                return 0.0
            
            # Compare metrics before and after optimizations
            improvements = []
            
            for i in range(1, len(self.optimization_history)):
                before_metrics = self.optimization_history[i-1][0]
                after_metrics = self.optimization_history[i][0]
                
                before_efficiency = self.calculate_efficiency_score(before_metrics)
                after_efficiency = self.calculate_efficiency_score(after_metrics)
                
                improvement = after_efficiency - before_efficiency
                improvements.append(improvement)
            
            if improvements:
                avg_improvement = statistics.mean(improvements)
                return max(0.0, avg_improvement)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization effectiveness: {e}")
            return 0.0
