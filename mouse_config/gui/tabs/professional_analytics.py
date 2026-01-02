"""
Professional analytics tab for advanced metrics and insights
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox, QProgressBar,
                             QMessageBox, QComboBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.advanced import ProfessionalAnalytics, PerformanceMetrics, DeviceHealthMetrics
except ImportError:
    ProfessionalAnalytics = None
    PerformanceMetrics = None
    DeviceHealthMetrics = None


class ProfessionalAnalyticsTab(QWidget):
    """Professional analytics tab for detailed metrics and insights"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        # Initialize analytics if available
        if ProfessionalAnalytics is not None:
            self.analytics = ProfessionalAnalytics()
        else:
            self.analytics = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Analytics Overview Group
        overview_group = QGroupBox("📊 Analytics Overview")
        overview_layout = QVBoxLayout()
        
        # Summary display
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setMaximumHeight(150)
        self.overview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        overview_layout.addWidget(self.overview_text)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Analytics")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_analytics)
        overview_layout.addWidget(refresh_btn)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        
        # Performance Metrics Group
        perf_group = QGroupBox("📈 Performance Metrics")
        perf_layout = QVBoxLayout()
        
        # Time period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Time Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        self.period_combo.setCurrentText("Last 7 Days")
        period_layout.addWidget(self.period_combo)
        perf_layout.addLayout(period_layout)
        
        # Export button
        export_btn = QPushButton("📊 Export Data")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        export_btn.clicked.connect(self.export_analytics_data)
        perf_layout.addWidget(export_btn)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Device Health Group
        health_group = QGroupBox("🏥️ Device Health")
        health_layout = QVBoxLayout()
        
        # Health status display
        self.health_text = QTextEdit()
        self.health_text.setReadOnly(True)
        self.health_text.setMaximumHeight(150)
        self.health_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        health_layout.addWidget(self.health_text)
        
        # Health check button
        health_check_btn = QPushButton("🔍 Check Health")
        health_check_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: self; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        health_check_btn.clicked.connect(self.check_device_health)
        health_layout.addWidget(health_check_btn)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Insights Group
        insights_group = QGroupBox("🔍 Insights & Recommendations")
        insights_layout = QVBoxLayout()
        
        insights_text = QTextEdit()
        insights_text.setReadOnly(True)
        insights_text.setMaximumHeight(200)
        insights_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        insights_layout.addWidget(insights_text)
        
        insights_btn = QPushButton("🔍 Get Insights")
        insights_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        insights_btn.clicked.connect(self.get_insights)
        insights_layout.addWidget(insights_btn)
        
        insights_group.setLayout(insights_layout)
        layout.addWidget(insights_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def refresh_analytics(self):
        """Refresh analytics display"""
        try:
            period_text = self.period_combo.currentText()
            if "7 Days" in period_text:
                days = 7
            elif "30 Days" in period_text:
                days = 30
            elif "90 Days" in period_text:
                days = 90
            else:
                days = 365
            
            # Get performance summary
            perf_summary = self.analytics.get_performance_summary(days)
            
            # Format overview text
            if 'error' in perf_summary:
                self.overview_text.setText(f"❌ Error getting analytics: {perf_summary['error']}")
            else:
                overview_text = f"""📊 PERFORMANCE ANALYTICS - {perf_summary['period_days']} Days
{'='*50}
Performance Rating: {perf_summary['performance_rating']}
Average Speed: {perf_summary['avg_speed']:.1f} px/s
Max Speed: {perf_summary['avg_max_speed']:.1f} px/s
Average Jitter: {perf_summary['avg_jitter']:.2f}
Average Click Frequency: {perf_summary['avg_click_frequency']:.1f} CPM
Average Efficiency Score: {perf_summary['avg_efficiency_score']:.2f}
Average Comfort Score: {perf_summary['avg_comfort_score']:.2f}
Average Precision Score: {perf_summary['avg_precision_score']:.2f}
Total Sessions: {perf_summary['session_count']}
Total Duration: {perf_summary['total_duration']:.1f} hours
"""
            
            self.overview_text.setText(overview_text)
            
        except Exception as e:
            self.logger.error(f"Error refreshing analytics: {e}")
            self.overview_text.setText(f"❌ Error refreshing analytics: {e}")
    
    def check_device_health(self):
        """Check device health"""
        try:
            health_report = self.analytics.get_health_report()
            
            if 'error' in health_report:
                self.health_text.setText(f"❌ Error checking health: {health_report['error']}")
                return
            
            # Format health text
            health_text = f"""🏥️ DEVICE HEALTH STATUS
{'='*50}
Battery Level: {health_report['battery_level']:.1f}%
Battery Health: {health_report['battery_health']:.1f}%
Connection Stability: {health_report['connection_stability']:.2f}
Response Time: {health_report['response_time']:.1f}ms
Error Rate: {health_report['error_rate']:.2f}
Temperature: {health_report['temperature']:.1f}°C
Health Score: {health_report['health_score']:.2f}
Status: {health_report['health_status']}
Last Update: {datetime.fromtimestamp(health_report['last_update']).strftime('%Y-%m-%d %H:%M:%S')}

RECOMMENDATIONS:
{'='*50}
"""
            
            for rec in health_report['recommendations']:
                health_text.append(f"• {rec}\n")
            
            self.health_text.setText(health_text)
            
        except Exception as e:
            self.logger.error(f"Error checking device health: {e}")
            self.health_text.setText(f"❌ Error checking health: {e}")
    
    def get_insights(self):
        """Get analytics insights"""
        try:
            insights = self.analytics.get_analytics_insights()
            
            if 'error' in insights:
                self.insights_text.setText(f"❌ Error getting insights: {insights['error']}")
                return
            
            # Format insights text
            insights_text = f"""🔍 ANALYTICS INSIGHTS
{'='*50}
PERFORMANCE TRENDS:
{'='*50}
Speed Trend: {insights['performance_trends'].get('trend', 'Unknown')}
Recent Avg: {insights['performance_trends'].get('recent', 0):.1f} px/s
Older Avg: {insights['performance_trends'].get('older', 0):.1f} px/s

DEVICE HEALTH:
{'='*50}
Status: {insights['device_health'].get('health_status', 'Unknown')}
Health Score: {insights['device_health'].get('health_score', 0.0):.2f}
Battery Level: {insights['device_health'].get('battery_level', 0.0):.1f}%

RECOMMENDATIONS:
{'='*50}
"""
            
            for rec in insights.get('recommendations', []):
                insights_text.append(f"• {rec}\n")
            
            self.insights_text.setText(insights_text)
            
        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            self.insights_text.setText(f"❌ Error getting insights: {e}")
    
    def export_analytics_data(self):
        """Export analytics data"""
        try:
            # Get current period
            period_text = self.period_combo.currentText()
            if "7 Days" in period_text:
                days = 7
            elif "30 Days" in period_text:
                days = 30
            elif "90 Days" in period_text:
                days = 90
            else:
                days = 365
            
            # Generate filename
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analytics_{timestamp}.json"
            
            # Export data
            success = self.analytics.export_analytics_data(filename)
            
            if success:
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Analytics data exported to {filename}"
                )
            else:
                QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export analytics data"
                    )
                
        except Exception as e:
            self.logger.error(f"Error exporting analytics data: {e}")
            QMessageBox.critical(self, "Export Failed", f"Failed to export analytics data: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # Analytics tab doesn't have persistent settings
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Analytics tab doesn't update persistent settings
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # Analytics tab doesn't apply device settings
        return {}
