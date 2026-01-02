"""
PC optimization system for gaming performance
"""

import psutil
import platform
import subprocess
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import threading
import os
import shutil

from ..utils.logger import get_logger
from ..utils.helpers import safe_execute


class OptimizationLevel(Enum):
    """Optimization levels"""
    MINIMAL = "minimal"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"


@dataclass
class PCSpecs:
    """PC specifications"""
    cpu_name: str
    cpu_cores: int
    cpu_threads: int
    cpu_freq: float
    ram_total: int  # GB
    ram_available: int  # GB
    gpu_name: str
    gpu_memory: int  # MB
    storage_type: str
    os_name: str
    os_version: str
    architecture: str


@dataclass
class GameProfile:
    """Game optimization profile"""
    name: str
    executable: str
    optimization_level: OptimizationLevel
    settings: Dict[str, Any]
    requirements: Dict[str, Any]
    recommendations: List[str]


class PCOptimizer:
    """PC optimization system for gaming performance"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # PC specifications
        self.pc_specs: Optional[PCSpecs] = None
        
        # Game profiles
        self.game_profiles: List[GameProfile] = []
        
        # Current optimizations
        self.current_optimizations: Dict[str, Any] = {}
        
        # Optimization history
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Initialize game profiles
        self._init_game_profiles()
        
        # Get PC specs
        self.pc_specs = self._get_pc_specs()
    
    def _init_game_profiles(self):
        """Initialize game optimization profiles"""
        self.game_profiles = [
            GameProfile(
                name="Fortnite",
                executable="FortniteClient-Win64-Shipping.exe",
                optimization_level=OptimizationLevel.AGGRESSIVE,
                settings={
                    "power_plan": "High Performance",
                    "priority_class": "HIGH",
                    "cpu_affinity": "auto",
                    "gpu_priority": "HIGH",
                    "disable_services": ["Windows Search", "Windows Update"],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "DisableScreenSaver": True,
                        "OptimizeNetwork": True
                    }
                },
                requirements={
                    "cpu_cores": 4,
                    "ram_gb": 8,
                    "gpu_memory_mb": 2048
                },
                recommendations=[
                    "Use DirectX 12",
                    "Enable DLSS if available",
                    "Set texture quality to Medium",
                    "Disable shadows for better FPS"
                ]
            ),
            GameProfile(
                name="CS:GO",
                executable="csgo.exe",
                optimization_level=OptimizationLevel.EXTREME,
                settings={
                    "power_plan": "Ultimate Performance",
                    "priority_class": "HIGH",
                    "cpu_affinity": "auto",
                    "gpu_priority": "HIGH",
                    "disable_services": ["Windows Search", "Windows Update", "Superfetch"],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "DisableScreenSaver": True,
                        "OptimizeNetwork": True,
                        "DisableVSync": True
                    }
                },
                requirements={
                    "cpu_cores": 2,
                    "ram_gb": 4,
                    "gpu_memory_mb": 1024
                },
                recommendations=[
                    "Use -high launch option",
                    "Disable all unnecessary background apps",
                    "Set launch options: -novidia -high -threads 4"
                ]
            ),
            GameProfile(
                name="Valorant",
                executable="VALORANT-Win64-Shipping.exe",
                optimization_level=OptimizationLevel.AGGRESSIVE,
                settings={
                    "power_plan": "High Performance",
                    "priority_class": "HIGH",
                    "cpu_affinity": "auto",
                    "gpu_priority": "HIGH",
                    "disable_services": ["Windows Search"],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "DisableScreenSaver": True,
                        "OptimizeNetwork": True
                    }
                },
                requirements={
                    "cpu_cores": 4,
                    "ram_gb": 8,
                    "gpu_memory_mb": 1024
                },
                recommendations=[
                    "Enable Multithreaded Rendering",
                    "Set Material Quality to Medium",
                    "Use NVIDIA Reflex if available"
                ]
            ),
            GameProfile(
                name="Apex Legends",
                executable="r5apex.exe",
                optimization_level=OptimizationLevel.BALANCED,
                settings={
                    "power_plan": "High Performance",
                    "priority_class": "ABOVE_NORMAL",
                    "cpu_affinity": "auto",
                    "gpu_priority": "HIGH",
                    "disable_services": ["Windows Search"],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "DisableScreenSaver": True
                    }
                },
                requirements={
                    "cpu_cores": 4,
                    "ram_gb": 8,
                    "gpu_memory_mb": 2048
                },
                recommendations=[
                    "Use Adaptive Sync",
                    "Set Texture Streaming Budget to Low",
                    "Disable TAA for better performance"
                ]
            ),
            GameProfile(
                name="Call of Duty: Warzone",
                executable="cod.exe",
                optimization_level=OptimizationLevel.EXTREME,
                settings={
                    "power_plan": "Ultimate Performance",
                    "priority_class": "HIGH",
                    "cpu_affinity": "auto",
                    "gpu_priority": "HIGH",
                    "disable_services": ["Windows Search", "Windows Update", "Superfetch"],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "DisableScreenSaver": True,
                        "OptimizeNetwork": True,
                        "DisableVSync": True
                    }
                },
                requirements={
                    "cpu_cores": 6,
                    "ram_gb": 12,
                    "gpu_memory_mb": 4096
                },
                recommendations=[
                    "Set Texture Resolution to Low",
                    "Enable DLSS Performance Mode",
                    "Disable Ray Tracing"
                ]
            ),
            GameProfile(
                name="Minecraft",
                executable="Minecraft.exe",
                optimization_level=OptimizationLevel.BALANCED,
                settings={
                    "power_plan": "High Performance",
                    "priority_class": "NORMAL",
                    "cpu_affinity": "auto",
                    "gpu_priority": "NORMAL",
                    "disable_services": [],
                    "registry_tweaks": {
                        "DisableMouseAcceleration": True,
                        "OptimizeJava": True
                    }
                },
                requirements={
                    "cpu_cores": 2,
                    "ram_gb": 4,
                    "gpu_memory_mb": 512
                },
                recommendations=[
                    "Allocate 4GB RAM to Java",
                    "Use OptiFine mod",
                    "Set render distance to 8 chunks"
                ]
            )
        ]
    
    def _get_pc_specs(self) -> PCSpecs:
        """Get PC specifications"""
        try:
            # CPU information
            cpu_info = platform.processor()
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0.0
            
            # Memory information
            memory = psutil.virtual_memory()
            ram_total = int(memory.total / (1024**3))  # GB
            ram_available = int(memory.available / (1024**3))  # GB
            
            # GPU information
            gpu_name, gpu_memory = self._get_gpu_info()
            
            # Storage information
            storage_type = self._get_storage_type()
            
            # OS information
            os_name = platform.system()
            os_version = platform.version()
            architecture = platform.architecture()[0]
            
            specs = PCSpecs(
                cpu_name=cpu_info,
                cpu_cores=cpu_cores,
                cpu_threads=cpu_threads,
                cpu_freq=cpu_freq,
                ram_total=ram_total,
                ram_available=ram_available,
                gpu_name=gpu_name,
                gpu_memory=gpu_memory,
                storage_type=storage_type,
                os_name=os_name,
                os_version=os_version,
                architecture=architecture
            )
            
            self.logger.info(f"PC Specs: {specs.cpu_name}, {specs.ram_total}GB RAM, {specs.gpu_name}")
            return specs
            
        except Exception as e:
            self.logger.error(f"Error getting PC specs: {e}")
            return None
    
    def _get_gpu_info(self) -> Tuple[str, int]:
        """Get GPU information"""
        try:
            # Try to get GPU info using wmic
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name", "AdapterRAM"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpu_name = lines[1].strip() if len(lines) > 1 else "Unknown"
                
                # Parse GPU memory
                if len(lines) > 2:
                    memory_str = lines[2].strip()
                    if memory_str.isdigit():
                        gpu_memory = int(memory_str) // 1024  # Convert KB to MB
                    else:
                        gpu_memory = 0
                else:
                    gpu_memory = 0
                
                return gpu_name, gpu_memory
            else:
                # Fallback to generic detection
                return "Unknown GPU", 0
                
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {e}")
            return "Unknown GPU", 0
    
    def _get_storage_type(self) -> str:
        """Get storage type (SSD/HDD)"""
        try:
            # Try to detect SSD
            result = subprocess.run(
                ["wmic", "diskdrive", "get", "MediaType"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    media_type = lines[1].strip().lower()
                    if "ssd" in media_type:
                        return "SSD"
                    else:
                        return "HDD"
            
            return "Unknown"
            
        except Exception as e:
            self.logger.error(f"Error detecting storage type: {e}")
            return "Unknown"
    
    def detect_running_game(self) -> Optional[GameProfile]:
        """Detect currently running game"""
        try:
            running_processes = psutil.process_iter(['name'])
            
            for process in running_processes:
                process_name = process.info['name'].lower()
                
                for profile in self.game_profiles:
                    if profile.executable.lower() in process_name:
                        self.logger.info(f"Detected running game: {profile.name}")
                        return profile
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting running game: {e}")
            return None
    
    def optimize_for_game(self, game_profile: GameProfile) -> Dict[str, Any]:
        """Optimize PC for specific game"""
        try:
            self.logger.info(f"Optimizing PC for {game_profile.name}")
            
            optimization_results = {
                'success': True,
                'optimizations_applied': [],
                'warnings': [],
                'errors': []
            }
            
            # Check requirements
            if not self._check_requirements(game_profile):
                optimization_results['warnings'].append("PC may not meet minimum requirements")
            
            # Apply power plan optimization
            if self._set_power_plan(game_profile.settings['power_plan']):
                optimization_results['optimizations_applied'].append(f"Power plan: {game_profile.settings['power_plan']}")
            else:
                optimization_results['errors'].append("Failed to set power plan")
            
            # Disable services
            for service in game_profile.settings.get('disable_services', []):
                if self._disable_service(service):
                    optimization_results['optimizations_applied'].append(f"Disabled service: {service}")
                else:
                    optimization_results['warnings'].append(f"Could not disable service: {service}")
            
            # Apply registry tweaks
            for tweak, enabled in game_profile.settings.get('registry_tweaks', {}).items():
                if self._apply_registry_tweak(tweak, enabled):
                    optimization_results['optimizations_applied'].append(f"Registry tweak: {tweak}")
                else:
                    optimization_results['warnings'].append(f"Could not apply registry tweak: {tweak}")
            
            # Set game process priority
            self._set_game_priority(game_profile)
            
            # Store current optimizations
            self.current_optimizations = game_profile.settings
            self.optimization_history.append({
                'timestamp': time.time(),
                'game': game_profile.name,
                'optimizations': optimization_results
            })
            
            self.logger.info(f"Optimization completed for {game_profile.name}")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error optimizing for game: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_requirements(self, game_profile: GameProfile) -> bool:
        """Check if PC meets game requirements"""
        if not self.pc_specs:
            return False
        
        requirements = game_profile.requirements
        
        # Check CPU cores
        if self.pc_specs.cpu_cores < requirements.get('cpu_cores', 1):
            return False
        
        # Check RAM
        if self.pc_specs.ram_total < requirements.get('ram_gb', 1):
            return False
        
        # Check GPU memory
        if self.pc_specs.gpu_memory < requirements.get('gpu_memory_mb', 0):
            return False
        
        return True
    
    def _set_power_plan(self, plan_name: str) -> bool:
        """Set Windows power plan"""
        try:
            # Get available power plans
            result = subprocess.run(
                ["powercfg", "/list"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if plan_name.lower() in line.lower():
                        # Extract plan GUID
                        parts = line.split(':')
                        if len(parts) > 0:
                            guid = parts[0].strip().split('(')[0].strip()
                            
                            # Set power plan
                            set_result = subprocess.run(
                                ["powercfg", "/setactive", guid],
                                capture_output=True, text=True, timeout=10
                            )
                            
                            return set_result.returncode == 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting power plan: {e}")
            return False
    
    def _disable_service(self, service_name: str) -> bool:
        """Disable Windows service"""
        try:
            # Check if service exists
            result = subprocess.run(
                ["sc", "query", service_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Stop service
                stop_result = subprocess.run(
                    ["sc", "stop", service_name],
                    capture_output=True, text=True, timeout=10
                )
                
                # Disable service
                disable_result = subprocess.run(
                    ["sc", "config", service_name, "start=disabled"],
                    capture_output=True, text=True, timeout=10
                )
                
                return stop_result.returncode == 0 and disable_result.returncode == 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error disabling service {service_name}: {e}")
            return False
    
    def _apply_registry_tweak(self, tweak_name: str, enabled: bool) -> bool:
        """Apply registry tweak"""
        try:
            import winreg
            
            registry_tweaks = {
                "DisableMouseAcceleration": {
                    "key": r"Control Panel\Mouse",
                    "value": "MouseSpeed",
                    "type": winreg.REG_SZ,
                    "data": "10" if not enabled else "20"
                },
                "DisableScreenSaver": {
                    "key": r"Control Panel\Desktop",
                    "value": "ScreenSaveActive",
                    "type": winreg.REG_SZ,
                    "data": "0" if enabled else "1"
                },
                "OptimizeNetwork": {
                    "key": r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    "value": "TcpAckFrequency",
                    "type": winreg.REG_DWORD,
                    "data": 13 if enabled else 1
                },
                "DisableVSync": {
                    "key": r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "value": "DwmComposition",
                    "type": winreg.REG_DWORD,
                    "data": 0 if enabled else 1
                },
                "OptimizeJava": {
                    "key": r"SOFTWARE\JavaSoft\Java Runtime Environment",
                    "value": "JvmMx",
                    "type": winreg.REG_SZ,
                    "data": "4096" if enabled else "1024"
                }
            }
            
            if tweak_name not in registry_tweaks:
                return False
            
            tweak = registry_tweaks[tweak_name]
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                tweak["key"],
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value
            winreg.SetValueEx(
                key,
                tweak["value"],
                0,
                tweak["type"],
                tweak["data"]
            )
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying registry tweak {tweak_name}: {e}")
            return False
    
    def _set_game_priority(self, game_profile: GameProfile):
        """Set game process priority"""
        try:
            priority_class = game_profile.settings.get('priority_class', 'NORMAL')
            
            # This would need to be applied when the game is running
            # For now, just log the intended priority
            self.logger.info(f"Intended priority for {game_profile.name}: {priority_class}")
            
        except Exception as e:
            self.logger.error(f"Error setting game priority: {e}")
    
    def restore_default_settings(self) -> Dict[str, Any]:
        """Restore default Windows settings"""
        try:
            self.logger.info("Restoring default settings")
            
            restore_results = {
                'success': True,
                'restorations_applied': [],
                'warnings': [],
                'errors': []
            }
            
            # Restore power plan to Balanced
            if self._set_power_plan("Balanced"):
                restore_results['restorations_applied'].append("Power plan: Balanced")
            else:
                restore_results['errors'].append("Failed to restore power plan")
            
            # Re-enable services
            services_to_enable = ["Windows Search", "Windows Update", "Superfetch"]
            for service in services_to_enable:
                if self._enable_service(service):
                    restore_results['restorations_applied'].append(f"Re-enabled service: {service}")
                else:
                    restore_results['warnings'].append(f"Could not re-enable service: {service}")
            
            # Restore registry tweaks
            for tweak in ["DisableMouseAcceleration", "DisableScreenSaver", "OptimizeNetwork"]:
                if self._apply_registry_tweak(tweak, False):
                    restore_results['restorations_applied'].append(f"Restored registry: {tweak}")
                else:
                    restore_results['warnings'].append(f"Could not restore registry: {tweak}")
            
            # Clear current optimizations
            self.current_optimizations = {}
            
            self.logger.info("Default settings restored")
            return restore_results
            
        except Exception as e:
            self.logger.error(f"Error restoring default settings: {e}")
            return {'success': False, 'error': str(e)}
    
    def _enable_service(self, service_name: str) -> bool:
        """Enable Windows service"""
        try:
            # Enable service
            enable_result = subprocess.run(
                ["sc", "config", service_name, "start=auto"],
                capture_output=True, text=True, timeout=10
            )
            
            # Start service
            start_result = subprocess.run(
                ["sc", "start", service_name],
                capture_output=True, text=True, timeout=10
            )
            
            return enable_result.returncode == 0 and start_result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error enabling service {service_name}: {e}")
            return False
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on PC specs"""
        recommendations = []
        
        if not self.pc_specs:
            return ["Unable to analyze PC specs"]
        
        # CPU recommendations
        if self.pc_specs.cpu_cores < 4:
            recommendations.append("Consider upgrading CPU for better gaming performance")
        elif self.pc_specs.cpu_cores >= 8:
            recommendations.append("High-end CPU detected - can handle demanding games")
        
        # RAM recommendations
        if self.pc_specs.ram_total < 8:
            recommendations.append("Consider upgrading RAM to at least 16GB for modern games")
        elif self.pc_specs.ram_total >= 32:
            recommendations.append("High RAM capacity - can handle multitasking while gaming")
        
        # GPU recommendations
        if self.pc_specs.gpu_memory < 2048:
            recommendations.append("Consider upgrading GPU for better gaming experience")
        elif self.pc_specs.gpu_memory >= 8192:
            recommendations.append("High-end GPU detected - can handle 4K gaming")
        
        # Storage recommendations
        if self.pc_specs.storage_type == "HDD":
            recommendations.append("Consider upgrading to SSD for faster load times")
        
        # General recommendations
        recommendations.append("Keep drivers updated for optimal performance")
        recommendations.append("Close background applications while gaming")
        recommendations.append("Use high performance power plan while gaming")
        
        return recommendations
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            metrics = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'process_count': len(psutil.pids()),
                'boot_time': psutil.boot_time(),
                'current_optimizations': self.current_optimizations
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def export_optimization_data(self, file_path: str) -> bool:
        """Export optimization data to file"""
        try:
            export_data = {
                'pc_specs': self.pc_specs.__dict__ if self.pc_specs else None,
                'game_profiles': [profile.__dict__ for profile in self.game_profiles],
                'optimization_history': self.optimization_history,
                'current_optimizations': self.current_optimizations,
                'performance_metrics': self.get_performance_metrics()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Optimization data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting optimization data: {e}")
            return False
