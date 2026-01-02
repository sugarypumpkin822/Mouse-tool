"""
Main tab container that manages all application tabs
"""

from PyQt6.QtWidgets import QTabWidget, QWidget
from PyQt6.QtCore import pyqtSignal

from .performance import PerformanceTab
from .lighting import LightingTab
from .advanced import AdvancedTab
from .profiles import ProfilesTab
from .firmware import FirmwareTab
from .macros import MacrosTab
from .statistics import StatisticsTab
from .diagnostics import DiagnosticsTab

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class TabContainer(QTabWidget):
    """Main tab container with all application tabs"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        
        # Create tabs
        self.create_tabs()
        
        # Apply styling
        self.setStyleSheet("""
            QTabWidget::pane { 
                border: 2px solid #667eea; 
                border-radius: 5px; 
                background: white;
            }
            QTabBar::tab { 
                padding: 10px 20px; 
                font-weight: bold; 
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #667eea; 
                color: white; 
                border-color: #667eea;
            }
            QTabBar::tab:hover:!selected {
                background: #e0e0e0;
            }
        """)
    
    def create_tabs(self):
        """Create all application tabs"""
        try:
            # Performance tab
            self.performance_tab = PerformanceTab()
            self.performance_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.performance_tab, "⚡ Performance")
            
            # Lighting tab
            self.lighting_tab = LightingTab()
            self.lighting_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.lighting_tab, "💡 Lighting")
            
            # Advanced tab
            self.advanced_tab = AdvancedTab()
            self.advanced_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.advanced_tab, "⚙️ Advanced")
            
            # Profiles tab
            self.profiles_tab = ProfilesTab()
            self.profiles_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.profiles_tab, "👤 Profiles")
            
            # Macros tab
            self.macros_tab = MacrosTab()
            self.macros_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.macros_tab, "🎬 Macros")
            
            # Statistics tab
            self.statistics_tab = StatisticsTab()
            self.addTab(self.statistics_tab, "📊 Statistics")
            
            # Professional Analytics tab
            self.professional_analytics_tab = ProfessionalAnalyticsTab()
            self.professional_analytics_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.professional_analytics_tab, "📊 Analytics")
            
            # AI Optimization tab
            self.ai_optimization_tab = AIOptimizationTab()
            self.ai_optimization_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.ai_optimization_tab, "🤖 AI Optimization")
            
            # Robust Settings tab
            self.robust_settings_tab = RobustSettingsTab()
            self.robust_settings_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.robust_settings_tab, "🔧 Robust Settings")
            
            # Cloud Sync tab
            self.cloud_sync_tab = CloudSyncTab()
            self.cloud_sync_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.cloud_sync_tab, "☁️ Cloud Sync")
            
            # PC Optimization tab
            self.pc_optimization_tab = PCOptimizationTab()
            self.pc_optimization_tab.settings_changed.connect(self.settings_changed.emit)
            self.addTab(self.pc_optimization_tab, "💻 PC Optimization")
            
            # Update Manager tab
            self.update_manager_tab = UpdateManagerTab()
            self.addTab(self.update_manager_tab, "🔄 Updates")
            
            # Firmware tab
            self.firmware_tab = FirmwareTab()
            self.addTab(self.firmware_tab, "🔧 Firmware")
            
            # Diagnostics tab
            self.diagnostics_tab = DiagnosticsTab()
            self.addTab(self.diagnostics_tab, "🔧 Diagnostics")
            
            self.logger.info("All tabs created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating tabs: {e}")
            raise
    
    def set_device_controller(self, controller):
        """Set the device controller for all tabs"""
        self.controller = controller
        
        # Update all tabs with the new controller
        self.performance_tab.set_controller(controller)
        self.lighting_tab.set_controller(controller)
        self.advanced_tab.set_controller(controller)
        self.profiles_tab.set_controller(controller)
        self.macros_tab.set_controller(controller)
        self.statistics_tab.set_controller(controller)
        self.professional_analytics_tab.set_controller(controller)
        self.ai_optimization_tab.set_controller(controller)
        self.robust_settings_tab.set_controller(controller)
        self.cloud_sync_tab.set_controller(controller)
        self.pc_optimization_tab.set_controller(controller)
        self.update_manager_tab.set_controller(controller)
        self.firmware_tab.set_controller(controller)
        self.diagnostics_tab.set_controller(controller)
    
    def load_settings(self, settings):
        """Load settings into all tabs"""
        try:
            self.performance_tab.load_settings(settings)
            self.lighting_tab.load_settings(settings)
            self.advanced_tab.load_settings(settings)
            self.profiles_tab.load_settings(settings)
            self.macros_tab.load_settings(settings)
            self.statistics_tab.load_settings(settings)
            self.professional_analytics_tab.load_settings(settings)
            self.ai_optimization_tab.load_settings(settings)
            self.robust_settings_tab.load_settings(settings)
            self.cloud_sync_tab.load_settings(settings)
            self.pc_optimization_tab.load_settings(settings)
            self.update_manager_tab.load_settings(settings)
            self.firmware_tab.load_settings(settings)
            self.diagnostics_tab.load_settings(settings)
            
            self.logger.info("Settings loaded into all tabs")
            
        except Exception as e:
            self.logger.error(f"Error loading settings into tabs: {e}")
    
    def update_settings(self, settings):
        """Update settings from all tabs"""
        try:
            self.performance_tab.update_settings(settings)
            self.lighting_tab.update_settings(settings)
            self.advanced_tab.update_settings(settings)
            self.profiles_tab.update_settings(settings)
            self.macros_tab.update_settings(settings)
            
            self.logger.info("Settings updated from all tabs")
            
        except Exception as e:
            self.logger.error(f"Error updating settings from tabs: {e}")
    
    def apply_settings(self, controller):
        """Apply settings from all tabs and return results"""
        results = {}
        
        try:
            # Apply settings from each tab
            results.update(self.performance_tab.apply_settings(controller))
            results.update(self.lighting_tab.apply_settings(controller))
            results.update(self.advanced_tab.apply_settings(controller))
            results.update(self.macros_tab.apply_settings(controller))
            results.update(self.ai_optimization_tab.apply_settings(controller))
            results.update(self.robust_settings_tab.apply_settings(controller))
            results.update(self.cloud_sync_tab.apply_settings(controller))
            results.update(self.pc_optimization_tab.apply_settings(controller))
            
            self.logger.info("Settings applied from all tabs")
            
        except Exception as e:
            self.logger.error(f"Error applying settings from tabs: {e}")
            results['error'] = str(e)
        
        return results
    
    def update_statistics(self):
        """Update statistics displays"""
        try:
            self.statistics_tab.update_display()
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def update_battery_status(self, battery_info):
        """Update battery status displays"""
        try:
            self.statistics_tab.update_battery_status(battery_info)
        except Exception as e:
            self.logger.error(f"Error updating battery status: {e}")
    
    def get_current_tab_name(self):
        """Get the name of the currently active tab"""
        current_index = self.currentIndex()
        return self.tabText(current_index)
    
    def set_tab_by_name(self, tab_name):
        """Set the active tab by name"""
        for i in range(self.count()):
            if self.tabText(i) == tab_name:
                self.setCurrentIndex(i)
                return True
        return False
