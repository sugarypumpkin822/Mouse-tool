"""
PC optimization tab for gaming performance
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox, QComboBox, QProgressBar,
                             QMessageBox, QCheckBox, QSpinBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from mouse_config.advanced import PCOptimizer, OptimizationLevel, PCSpecs
except ImportError:
    PCOptimizer = None
    OptimizationLevel = None
    PCSpecs = None


class PCOptimizationTab(QWidget):
    """PC optimization tab for gaming performance"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        self.pc_optimizer = PCOptimizer()
        
        # Auto-detection timer
        self.detection_timer = QTimer()
        self.detection_timer.timeout.connect(self.detect_running_game)
        self.detection_timer.start(5000)  # Check every 5 seconds
        
        self.init_ui()
        
        # Initialize display
        self.update_pc_specs_display()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # PC Specs Group
        specs_group = QGroupBox("💻 PC Specifications")
        specs_layout = QVBoxLayout()
        
        self.specs_text = QTextEdit()
        self.specs_text.setReadOnly(True)
        self.specs_text.setMaximumHeight(150)
        self.specs_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        specs_layout.addWidget(self.specs_text)
        
        refresh_specs_btn = QPushButton("🔄 Refresh Specs")
        refresh_specs_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_specs_btn.clicked.connect(self.update_pc_specs_display)
        specs_layout.addWidget(refresh_specs_btn)
        
        specs_group.setLayout(specs_layout)
        layout.addWidget(specs_group)
        
        # Game Detection Group
        detection_group = QGroupBox("🎮 Game Detection")
        detection_layout = QVBoxLayout()
        
        self.game_status_label = QLabel("🔍 Detecting running games...")
        self.game_status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detection_layout.addWidget(self.game_status_label)
        
        detected_game_layout = QHBoxLayout()
        detected_game_layout.addWidget(QLabel("Detected Game:"))
        self.detected_game_label = QLabel("None")
        self.detected_game_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        detected_game_layout.addWidget(self.detected_game_label)
        detected_game_layout.addStretch()
        detection_layout.addLayout(detected_game_layout)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Optimization Group
        opt_group = QGroupBox("⚡ PC Optimization")
        opt_layout = QVBoxLayout()
        
        # Optimization level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Optimization Level:"))
        self.opt_level_combo = QComboBox()
        self.opt_level_combo.addItems(["Minimal", "Balanced", "Aggressive", "Extreme"])
        self.opt_level_combo.setCurrentText("Balanced")
        level_layout.addWidget(self.opt_level_combo)
        opt_layout.addLayout(level_layout)
        
        # Optimize button
        self.optimize_btn = QPushButton("🚀 Optimize for Game")
        self.optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.optimize_btn.clicked.connect(self.optimize_for_game)
        opt_layout.addWidget(self.optimize_btn)
        
        # Restore button
        self.restore_btn = QPushButton("🔄 Restore Defaults")
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.restore_btn.clicked.connect(self.restore_defaults)
        opt_layout.addWidget(self.restore_btn)
        
        opt_group.setLayout(opt_layout)
        layout.addWidget(opt_group)
        
        # Optimization Results Group
        results_group = QGroupBox("📊 Optimization Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Recommendations Group
        rec_group = QGroupBox("💡 Recommendations")
        rec_layout = QVBoxLayout()
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMaximumHeight(100)
        self.recommendations_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        rec_layout.addWidget(self.recommendations_text)
        
        get_rec_btn = QPushButton("💡 Get Recommendations")
        get_rec_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        get_rec_btn.clicked.connect(self.get_recommendations)
        rec_layout.addWidget(get_rec_btn)
        
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        # Performance Metrics Group
        perf_group = QGroupBox("📈 Performance Metrics")
        perf_layout = QVBoxLayout()
        
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(100)
        self.metrics_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa; 
                font-family: 'Courier New'; 
                padding: 10px;
            }
        """)
        perf_layout.addWidget(self.metrics_text)
        
        refresh_metrics_btn = QPushButton("🔄 Refresh Metrics")
        refresh_metrics_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        refresh_metrics_btn.clicked.connect(self.refresh_metrics)
        perf_layout.addWidget(refresh_metrics_btn)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
    
    def update_pc_specs_display(self):
        """Update PC specifications display"""
        try:
            if self.pc_optimizer.pc_specs:
                specs = self.pc_optimizer.pc_specs
                
                specs_text = f"""💻 PC SPECIFICATIONS
{'='*50}
CPU: {specs.cpu_name}
Cores: {specs.cpu_cores} cores, {specs.cpu_threads} threads
Frequency: {specs.cpu_freq:.1f} GHz
RAM: {specs.ram_total} GB total, {specs.ram_available} GB available
GPU: {specs.gpu_name}
GPU Memory: {specs.gpu_memory} MB
Storage: {specs.storage_type}
OS: {specs.os_name} {specs.os_version}
Architecture: {specs.architecture}
"""
            else:
                specs_text = "❌ Unable to detect PC specifications"
            
            self.specs_text.setText(specs_text)
            
        except Exception as e:
            self.logger.error(f"Error updating PC specs display: {e}")
            self.specs_text.setText(f"❌ Error: {e}")
    
    def detect_running_game(self):
        """Detect currently running game"""
        try:
            game_profile = self.pc_optimizer.detect_running_game()
            
            if game_profile:
                self.detected_game_label.setText(game_profile.name)
                self.detected_game_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
                self.game_status_label.setText(f"🎮 {game_profile.name} detected")
                
                # Auto-optimize if enabled
                if hasattr(self, 'auto_optimize_check') and self.auto_optimize_check.isChecked():
                    self.optimize_for_game()
            else:
                self.detected_game_label.setText("None")
                self.detected_game_label.setStyleSheet("font-weight: bold; color: #999;")
                self.game_status_label.setText("🔍 No game detected")
                
        except Exception as e:
            self.logger.error(f"Error detecting running game: {e}")
            self.game_status_label.setText("❌ Detection error")
    
    def optimize_for_game(self):
        """Optimize PC for detected game"""
        try:
            game_profile = self.pc_optimizer.detect_running_game()
            
            if not game_profile:
                QMessageBox.warning(self, "Warning", "No game detected for optimization")
                return
            
            # Get optimization level
            level_text = self.opt_level_combo.currentText()
            level_map = {
                "Minimal": OptimizationLevel.MINIMAL,
                "Balanced": OptimizationLevel.BALANCED,
                "Aggressive": OptimizationLevel.AGGRESSIVE,
                "Extreme": OptimizationLevel.EXTREME
            }
            
            # Update game profile with selected level
            game_profile.optimization_level = level_map.get(level_text, OptimizationLevel.BALANCED)
            
            # Apply optimization
            self.results_text.setText("🚀 Optimizing PC for gaming...")
            
            results = self.pc_optimizer.optimize_for_game(game_profile)
            
            # Display results
            if results['success']:
                result_text = f"""✅ OPTIMIZATION COMPLETE
{'='*50}
Game: {game_profile.name}
Level: {game_profile.optimization_level.value}
Optimizations Applied:
"""
                
                for opt in results['optimizations_applied']:
                    result_text += f"✅ {opt}\n"
                
                if results['warnings']:
                    result_text += "\n⚠️ Warnings:\n"
                    for warning in results['warnings']:
                        result_text += f"⚠️ {warning}\n"
                
                if results['errors']:
                    result_text += "\n❌ Errors:\n"
                    for error in results['errors']:
                        result_text += f"❌ {error}\n"
                
                # Add game recommendations
                result_text += f"\n💡 GAME RECOMMENDATIONS:\n"
                for rec in game_profile.recommendations:
                    result_text += f"💡 {rec}\n"
                
                self.results_text.setText(result_text)
                
                QMessageBox.information(
                    self,
                    "Optimization Complete",
                    f"PC optimized for {game_profile.name}"
                )
                
            else:
                error_msg = results.get('error', 'Unknown error')
                self.results_text.setText(f"❌ OPTIMIZATION FAILED\n\n{error_msg}")
                QMessageBox.critical(self, "Optimization Failed", f"Failed to optimize: {error_msg}")
                
        except Exception as e:
            self.logger.error(f"Error optimizing PC: {e}")
            self.results_text.setText(f"❌ Error: {e}")
            QMessageBox.critical(self, "Optimization Error", f"Optimization error: {e}")
    
    def restore_defaults(self):
        """Restore default Windows settings"""
        try:
            reply = QMessageBox.question(
                self,
                "Restore Defaults",
                "This will restore all Windows settings to their default state.\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.results_text.setText("🔄 Restoring default settings...")
                
                results = self.pc_optimizer.restore_default_settings()
                
                if results['success']:
                    result_text = f"""✅ RESTORATION COMPLETE
{'='*50}
Restorations Applied:
"""
                    
                    for restore in results['restorations_applied']:
                        result_text += f"✅ {restore}\n"
                    
                    if results['warnings']:
                        result_text += "\n⚠️ Warnings:\n"
                        for warning in results['warnings']:
                            result_text += f"⚠️ {warning}\n"
                    
                    if results['errors']:
                        result_text += "\n❌ Errors:\n"
                        for error in results['errors']:
                            result_text += f"❌ {error}\n"
                    
                    self.results_text.setText(result_text)
                    
                    QMessageBox.information(self, "Restore Complete", "Default settings restored")
                    
                else:
                    error_msg = results.get('error', 'Unknown error')
                    self.results_text.setText(f"❌ RESTORATION FAILED\n\n{error_msg}")
                    QMessageBox.critical(self, "Restore Failed", f"Failed to restore: {error_msg}")
                    
        except Exception as e:
            self.logger.error(f"Error restoring defaults: {e}")
            self.results_text.setText(f"❌ Error: {e}")
            QMessageBox.critical(self, "Restore Error", f"Restore error: {e}")
    
    def get_recommendations(self):
        """Get PC optimization recommendations"""
        try:
            recommendations = self.pc_optimizer.get_optimization_recommendations()
            
            if recommendations:
                rec_text = "💡 PC OPTIMIZATION RECOMMENDATIONS\n" + "="*50 + "\n\n"
                for i, rec in enumerate(recommendations, 1):
                    rec_text += f"{i}. {rec}\n"
                
                self.recommendations_text.setText(rec_text)
            else:
                self.recommendations_text.setText("❌ No recommendations available")
                
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            self.recommendations_text.setText(f"❌ Error: {e}")
    
    def refresh_metrics(self):
        """Refresh performance metrics"""
        try:
            metrics = self.pc_optimizer.get_performance_metrics()
            
            if metrics:
                metrics_text = f"""📈 PERFORMANCE METRICS
{'='*50}
CPU Usage: {metrics.get('cpu_usage', 0):.1f}%
Memory Usage: {metrics.get('memory_usage', 0):.1f}%
Disk Usage: {metrics.get('disk_usage', 0):.1f}%
Process Count: {metrics.get('process_count', 0)}
Network I/O: Sent: {metrics.get('network_io', {}).get('bytes_sent', 0):,} bytes, Received: {metrics.get('network_io', {}).get('bytes_recv', 0):,} bytes
Boot Time: {time.ctime(metrics.get('boot_time', 0))}
"""
                
                if metrics.get('current_optimizations'):
                    metrics_text += f"\nCurrent Optimizations: {len(metrics['current_optimizations'])} active"
                
                self.metrics_text.setText(metrics_text)
            else:
                self.metrics_text.setText("❌ Unable to get performance metrics")
                
        except Exception as e:
            self.logger.error(f"Error refreshing metrics: {e}")
            self.metrics_text.setText(f"❌ Error: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # PC optimization doesn't have persistent settings
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # PC optimization doesn't update persistent settings
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        # PC optimization doesn't apply device settings
        return {}
