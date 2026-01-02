"""
Advanced RGB effects and animations system
"""

import time
import threading
import colorsys
from typing import Dict, List, Any, Optional, Callable
from ..utils.logger import get_logger


class AdvancedRGBController:
    """Advanced RGB effects with custom animations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.animations = {
            'rainbow': self.rainbow_effect,
            'pulse': self.pulse_effect,
            'wave': self.wave_effect,
            'reactive': self.reactive_effect,
            'custom': self.custom_effect,
            'breathing': self.breathing_effect,
            'spectrum': self.spectrum_effect,
            'fading': self.fading_effect,
            'strobe': self.strobe_effect,
            'ripple': self.ripple_effect
        }
        
        self.animation_running = False
        self.animation_thread: Optional[threading.Thread] = None
        self.stop_animation = threading.Event()
        
        # Animation settings
        self.animation_speed = 50
        self.animation_brightness = 100
        self.current_color = "#00FF00"
        
        # Custom keyframes
        self.custom_keyframes: List[Dict[str, Any]] = []
        
    def rainbow_effect(self, controller, speed: int = 50, brightness: int = 100) -> bool:
        """Rainbow color cycling effect"""
        try:
            self.logger.info("Starting rainbow effect")
            
            for i in range(360):
                if self.stop_animation.is_set():
                    break
                
                rgb = colorsys.hsv_to_rgb(i/360, 1.0, brightness/100)
                color = '#{:02x}{:02x}{:02x}'.format(
                    int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
                )
                
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", brightness, speed)
                
                time.sleep(0.1 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rainbow effect error: {e}")
            return False
    
    def pulse_effect(self, controller, color: str, speed: int = 50, brightness: int = 100) -> bool:
        """Pulsing brightness effect"""
        try:
            self.logger.info(f"Starting pulse effect with color {color}")
            
            # Convert hex to RGB
            color = color.lstrip('#')
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Pulse up
            for brightness_level in range(0, brightness + 1, 2):
                if self.stop_animation.is_set():
                    break
                
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", brightness_level, speed)
                time.sleep(0.05 / (speed / 50))
            
            # Pulse down
            for brightness_level in range(brightness, -1, -2):
                if self.stop_animation.is_set():
                    break
                
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", brightness_level, speed)
                time.sleep(0.05 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pulse effect error: {e}")
            return False
    
    def wave_effect(self, controller, colors: List[str], speed: int = 50) -> bool:
        """Wave effect with multiple colors"""
        try:
            self.logger.info(f"Starting wave effect with {len(colors)} colors")
            
            for color in colors:
                if self.stop_animation.is_set():
                    break
                
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", 100, speed)
                time.sleep(0.5 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Wave effect error: {e}")
            return False
    
    def reactive_effect(self, controller, color: str, speed: int = 50) -> bool:
        """Reactive effect that responds to clicks"""
        try:
            self.logger.info(f"Starting reactive effect with color {color}")
            
            if controller and hasattr(controller, 'set_rgb'):
                controller.set_rgb(color, "Reactive", 100, speed)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Reactive effect error: {e}")
            return False
    
    def breathing_effect(self, controller, color: str, speed: int = 50, brightness: int = 100) -> bool:
        """Smooth breathing effect"""
        try:
            self.logger.info(f"Starting breathing effect with color {color}")
            
            # Convert hex to RGB
            color = color.lstrip('#')
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Smooth breathing using sine wave
            import math
            
            while not self.stop_animation.is_set():
                for i in range(360):
                    if self.stop_animation.is_set():
                        break
                    
                    # Calculate brightness using sine wave
                    brightness_level = int((math.sin(math.radians(i)) + 1) * brightness / 2)
                    
                    if controller and hasattr(controller, 'set_rgb'):
                        controller.set_rgb(color, "Static", brightness_level, speed)
                    
                    time.sleep(0.02 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Breathing effect error: {e}")
            return False
    
    def spectrum_effect(self, controller, speed: int = 50) -> bool:
        """Spectrum cycling effect"""
        try:
            self.logger.info("Starting spectrum effect")
            
            if controller and hasattr(controller, 'set_rgb'):
                controller.set_rgb("#FFFFFF", "Spectrum", 100, speed)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Spectrum effect error: {e}")
            return False
    
    def fading_effect(self, controller, colors: List[str], speed: int = 50) -> bool:
        """Fade between multiple colors"""
        try:
            self.logger.info(f"Starting fading effect with {len(colors)} colors")
            
            for i in range(len(colors)):
                if self.stop_animation.is_set():
                    break
                
                current_color = colors[i]
                next_color = colors[(i + 1) % len(colors)]
                
                # Fade from current to next
                for step in range(0, 101, 2):
                    if self.stop_animation.is_set():
                        break
                    
                    # Interpolate between colors
                    fade_color = self._interpolate_color(current_color, next_color, step / 100)
                    
                    if controller and hasattr(controller, 'set_rgb'):
                        controller.set_rgb(fade_color, "Static", 100, speed)
                    
                    time.sleep(0.02 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fading effect error: {e}")
            return False
    
    def strobe_effect(self, controller, color: str, speed: int = 50) -> bool:
        """Strobe flashing effect"""
        try:
            self.logger.info(f"Starting strobe effect with color {color}")
            
            while not self.stop_animation.is_set():
                # Flash on
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", 100, speed)
                time.sleep(0.1 / (speed / 50))
                
                if self.stop_animation.is_set():
                    break
                
                # Flash off
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb("#000000", "Static", 0, speed)
                time.sleep(0.1 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Strobe effect error: {e}")
            return False
    
    def ripple_effect(self, controller, base_color: str, ripple_color: str, speed: int = 50) -> bool:
        """Ripple effect (simulated)"""
        try:
            self.logger.info(f"Starting ripple effect")
            
            # Simulate ripple by alternating colors
            while not self.stop_animation.is_set():
                # Base color
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(base_color, "Static", 100, speed)
                time.sleep(1.0 / (speed / 50))
                
                if self.stop_animation.is_set():
                    break
                
                # Ripple color
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(ripple_color, "Static", 100, speed)
                time.sleep(0.5 / (speed / 50))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ripple effect error: {e}")
            return False
    
    def custom_effect(self, controller, keyframes: List[Dict[str, Any]]) -> bool:
        """Custom animation from keyframes"""
        try:
            self.logger.info(f"Starting custom effect with {len(keyframes)} keyframes")
            
            for keyframe in keyframes:
                if self.stop_animation.is_set():
                    break
                
                color = keyframe.get('color', '#FFFFFF')
                brightness = keyframe.get('brightness', 100)
                duration = keyframe.get('duration', 1.0)
                
                if controller and hasattr(controller, 'set_rgb'):
                    controller.set_rgb(color, "Static", brightness, 50)
                
                time.sleep(duration)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Custom effect error: {e}")
            return False
    
    def start_animation(self, controller, effect_name: str, **kwargs) -> bool:
        """Start an animation in a separate thread"""
        if self.animation_running:
            self.logger.warning("Animation already running")
            return False
        
        if effect_name not in self.animations:
            self.logger.error(f"Unknown animation: {effect_name}")
            return False
        
        try:
            self.stop_animation.clear()
            self.animation_running = True
            
            # Start animation in separate thread
            self.animation_thread = threading.Thread(
                target=self._run_animation,
                args=(controller, effect_name, kwargs),
                daemon=True
            )
            self.animation_thread.start()
            
            self.logger.info(f"Started animation: {effect_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting animation: {e}")
            self.animation_running = False
            return False
    
    def stop_current_animation(self):
        """Stop the current animation"""
        if self.animation_running:
            self.stop_animation.set()
            self.animation_running = False
            
            if self.animation_thread and self.animation_thread.is_alive():
                self.animation_thread.join(timeout=2.0)
            
            self.logger.info("Animation stopped")
    
    def _run_animation(self, controller, effect_name: str, kwargs: Dict[str, Any]):
        """Run animation in thread"""
        try:
            effect_func = self.animations[effect_name]
            effect_func(controller, **kwargs)
        except Exception as e:
            self.logger.error(f"Animation error: {e}")
        finally:
            self.animation_running = False
    
    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """Interpolate between two colors"""
        try:
            # Convert hex to RGB
            c1 = color1.lstrip('#')
            c2 = color2.lstrip('#')
            
            r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
            r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
            
            # Interpolate
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except Exception:
            return color1
    
    def add_custom_keyframe(self, color: str, brightness: int, duration: float):
        """Add a keyframe for custom animation"""
        self.custom_keyframes.append({
            'color': color,
            'brightness': brightness,
            'duration': duration
        })
    
    def clear_custom_keyframes(self):
        """Clear all custom keyframes"""
        self.custom_keyframes = []
    
    def get_available_animations(self) -> List[str]:
        """Get list of available animations"""
        return list(self.animations.keys())
    
    def is_animation_running(self) -> bool:
        """Check if animation is currently running"""
        return self.animation_running
    
    def set_animation_speed(self, speed: int):
        """Set animation speed (1-100)"""
        self.animation_speed = max(1, min(100, speed))
    
    def set_animation_brightness(self, brightness: int):
        """Set animation brightness (0-100)"""
        self.animation_brightness = max(0, min(100, brightness))
    
    def get_animation_status(self) -> Dict[str, Any]:
        """Get current animation status"""
        return {
            'running': self.animation_running,
            'speed': self.animation_speed,
            'brightness': self.animation_brightness,
            'current_color': self.current_color,
            'custom_keyframes': len(self.custom_keyframes)
        }
    
    def create_color_palette(self, base_color: str, variations: int = 5) -> List[str]:
        """Create a color palette based on a base color"""
        try:
            base_color = base_color.lstrip('#')
            r, g, b = int(base_color[0:2], 16), int(base_color[2:4], 16), int(base_color[4:6], 16)
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            palette = []
            for i in range(variations):
                # Vary hue
                new_h = (h + (i / variations)) % 1.0
                new_rgb = colorsys.hsv_to_rgb(new_h, s, v)
                new_color = '#{:02x}{:02x}{:02x}'.format(
                    int(new_rgb[0]*255), int(new_rgb[1]*255), int(new_rgb[2]*255)
                )
                palette.append(new_color)
            
            return palette
            
        except Exception as e:
            self.logger.error(f"Error creating color palette: {e}")
            return [base_color]
