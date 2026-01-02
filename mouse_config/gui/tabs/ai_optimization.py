"""
AI optimization tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTextEdit, QGroupBox, QProgressBar)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.advanced import AIOptimizer, OptimizationGoal, MouseMetrics
except ImportError:
    AIOptimizer = None
    OptimizationGoal = None
    MouseMetrics = None


class AIOptimizationTab(QWidget):
    """AI-powered optimization tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        self.ai_optimizer = AIOptimizer()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # AI Analysis Group
        analysis_group = QGroupBox("🤖 AI Usage Analysis")
        analysis_layout = QVBoxLayout()
        
        # Analysis button
        analyze_btn = QPushButton("🔍 Analyze Current Usage")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_usage)
        analysis_layout.addWidget(analyze_btn)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(200)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        analysis_layout.addWidget(self.analysis_text)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # AI Optimization Group
        opt_group = QGroupBox("⚡ AI Optimization")
        opt_layout = QVBoxLayout()
        
        # Goal selection
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel("Optimization Goal:"))
        self.goal_combo = QComboBox()
        self.goal_combo.addItems([
            "Balanced",
            "FPS Gaming", 
            "Precision Work",
            "Comfort Use",
            "Power Saving"
        ])
        self.goal_combo.currentTextChanged.connect(self.on_settings_changed)
        goal_layout.addWidget(self.goal_combo)
        opt_layout.addLayout(goal_layout)
        
        # Optimize button
        optimize_btn = QPushButton("🚀 Optimize Settings")
        optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        optimize_btn.clicked.connect(self.optimize_settings)
        opt_layout.addWidget(optimize_btn)
        
        # Optimization results
        self.opt_results_text = QTextEdit()
        self.opt_results_text.setReadOnly(True)
        self.opt_results_text.setMaximumHeight(150)
        self.opt_results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        opt_layout.addWidget(self.opt_results_text)
        
        opt_group.setLayout(opt_layout)
        layout.addWidget(opt_group)
        
        # Learning Insights Group
        insights_group = QGroupBox("📊 Learning Insights")
        insights_layout = QVBoxLayout()
        
        insights_btn = QPushButton("📈 Get Insights")
        insights_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        insights_btn.clicked.connect(self.get_insights)
        insights_layout.addWidget(insights_btn)
        
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        insights_layout.addWidget(self.insights_text)
        
        insights_group.setLayout(insights_layout)
        layout.addWidget(insights_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def analyze_usage(self):
        """Analyze current usage patterns"""
        try:
            if not self.controller or not self.controller.connected:
                self.analysis_text.setText("❌ No mouse connected for analysis")
                return
            
            # Get current tracking data
            # This would normally get real data from MouseTracker
            # For now, simulate metrics
            metrics = MouseMetrics(
                avg_speed=750.0,
                max_speed=1200.0,
                acceleration_events=15,
                click_frequency=45.0,
                movement_patterns=["circular", "linear"],
                session_duration=3600.0,
                total_distance=2700000.0,
                right_click_ratio=0.25,
                scroll_usage=0.15
            )
            
            # Analyze with AI
            analysis = self.ai_optimizer.analyze_usage_pattern(metrics)
            
            # Format results
            result_text = f"""🤖 AI Usage Analysis
{'='*40}

Usage Type: {analysis['usage_type']}
Skill Level: {analysis['skill_level']}
Efficiency Score: {analysis['efficiency_score']:.2f}

📋 Recommendations:
"""
            for rec in analysis['recommendations']:
                result_text += f"• {rec}\n"
            
            if analysis['risk_factors']:
                result_text += f"\n⚠️ Risk Factors:\n"
                for risk in analysis['risk_factors']:
                    result_text += f"• {risk}\n"
            
            self.analysis_text.setText(result_text)
            self.logger.info("AI usage analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error analyzing usage: {e}")
            self.analysis_text.setText(f"❌ Analysis failed: {e}")
    
    def optimize_settings(self):
        """Optimize settings using AI"""
        try:
            if not self.controller or not self.controller.connected:
                self.opt_results_text.setText("❌ No mouse connected for optimization")
                return
            
            # Get selected goal
            goal_text = self.goal_combo.currentText()
            goal_map = {
                "Balanced": OptimizationGoal.BALANCED,
                "FPS Gaming": OptimizationGoal.FPS,
                "Precision Work": OptimizationGoal.PRECISION,
                "Comfort Use": OptimizationGoal.COMFORT,
                "Power Saving": OptimizationGoal.POWER_SAVING
            }
            
            goal = goal_map.get(goal_text, OptimizationGoal.BALANCED)
            
            # Get current metrics (simulated)
            metrics = MouseMetrics(
                avg_speed=750.0,
                max_speed=1200.0,
                acceleration_events=15,
                click_frequency=45.0,
                movement_patterns=["circular", "linear"],
                session_duration=3600.0,
                total_distance=2700000.0,
                right_click_ratio=0.25,
                scroll_usage=0.15
            )
            
            # Optimize with AI
            profile = self.ai_optimizer.optimize_settings(metrics, goal)
            
            # Format results
            result_text = f"""🚀 AI Optimization Complete
{'='*40}

Profile: {profile.name}
Goal: {goal.value}
Description: {profile.description}

⚙️ Optimized Settings:
• DPI: {profile.dpi}
• Polling Rate: {profile.polling_rate}Hz
• Lift-off Distance: {profile.lift_off_distance}mm
• Angle Snapping: {'Enabled' if profile.angle_snapping else 'Disabled'}
• Debounce Time: {profile.debounce_time}ms
• RGB Brightness: {profile.rgb_brightness}%

💡 Click "Apply All Settings" to apply these optimizations
"""
            
            self.opt_results_text.setText(result_text)
            self.logger.info(f"AI optimization completed for {goal.value}")
            
        except Exception as e:
            self.logger.error(f"Error optimizing settings: {e}")
            self.opt_results_text.setText(f"❌ Optimization failed: {e}")
    
    def get_insights(self):
        """Get learning insights"""
        try:
            insights = self.ai_optimizer.get_learning_insights()
            
            if 'error' in insights:
                self.insights_text.setText(f"❌ Error: {insights['error']}")
                return
            
            # Format insights
            insight_text = f"""📊 Learning Insights
{'='*40}

Total Sessions: {insights.get('total_sessions', 0)}
Average Speed: {insights.get('average_speed', 0):.1f} px/s
Average Click Frequency: {insights.get('average_click_frequency', 0):.1f} CPM
Average Session Duration: {insights.get('average_session_duration', 0):.1f} seconds
Most Common Usage: {insights.get('most_common_usage_type', 'Unknown')}
Skill Progression: {insights.get('skill_progression', 'Unknown')}
Optimization Effectiveness: {insights.get('optimization_effectiveness', 0):.2f}
"""
            
            self.insights_text.setText(insight_text)
            self.logger.info("Learning insights retrieved")
            
        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            self.insights_text.setText(f"❌ Failed to get insights: {e}")
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.settings_changed.emit()
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # AI optimization doesn't have persistent settings
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # AI optimization doesn't update persistent settings
        pass
    
    def apply_settings(self, controller):
        """Apply AI-optimized settings to the device"""
        results = {}
        
        try:
            if controller and controller.connected:
                # Get the optimized profile from the results
                if hasattr(self, 'last_optimized_profile'):
                    profile = self.last_optimized_profile
                    
                    # Apply DPI
                    if controller.set_dpi(profile.dpi):
                        results['ai_dpi'] = True
                    else:
                        results['ai_dpi'] = False
                    
                    # Apply polling rate
                    if controller.set_polling_rate(profile.polling_rate):
                        results['ai_polling_rate'] = True
                    else:
                        results['ai_polling_rate'] = False
                    
                    # Apply other settings
                    if controller.set_lod(profile.lift_off_distance):
                        results['ai_lod'] = True
                    else:
                        results['ai_lod'] = False
                    
                    if controller.set_angle_snapping(profile.angle_snapping):
                        results['ai_angle_snapping'] = True
                    else:
                        results['ai_angle_snapping'] = False
                    
                    if controller.set_debounce(profile.debounce_time):
                        results['ai_debounce'] = True
                    else:
                        results['ai_debounce'] = False
                    
                    self.logger.info("AI-optimized settings applied successfully")
                else:
                    self.logger.warning("No optimized profile available")
                    results['ai_optimization'] = None
            else:
                results['ai_optimization'] = None
                
        except Exception as e:
            self.logger.error(f"Error applying AI settings: {e}")
            results['error'] = str(e)
        
        return results
