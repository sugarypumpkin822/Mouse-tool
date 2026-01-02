"""
Mouse detection and identification system
"""

from typing import List, Dict, Optional, Set
from ..utils.helpers import safe_execute


class MouseDetector:
    """Enhanced mouse detection with more brands and proper filtering"""
    
    VENDOR_IDS = {
        0x1532: "Razer",
        0x26CE: "iBuyPower",
        0x1B1C: "CyberpowerPC",
        0x1044: "CyberpowerPC",
        0x046D: "Logitech",
        0x045E: "Microsoft",
        0x09DA: "A4Tech",
        0x1E7D: "ZOWIE",
        0x1D57: "ZOWIE",
        0x0B05: "ASUS",
        0x0BDA: "Realtek",
        0x1926: "ROCCAT",
        0x1BCF: "Xiaomi",
        0x2EA8: "Glorious",
        0x2516: "SteelSeries",
        0x1538: "Razer",
        0x0F2D: "EVGA",
        0x0E6F: "Logic3",
        0x20A0: "NZXT",
        0x1E71: "HyperX",
        0x0DB0: "Astro",
        0x040B: "NEC",
        0x056E: "Elecom",
        0x04D9: "Hama",
        0x093A: "AIPTEK",
        0x0C45: "Sonix",
        0x099A: "Genius",
        0x17EF: "Lenovo",
        0x04F2: "Chicony",
        0x05AC: "Apple",
        0x0A5C: "Broadcom",
        0x8087: "Intel",
    }
    
    RAZER_PRODUCTS = {
        0x0084: "DeathAdder V2", 0x0070: "Viper Ultimate",
        0x007C: "Viper Mini", 0x0078: "Viper",
        0x0043: "DeathAdder Chroma", 0x0053: "Mamba Elite",
        0x006C: "Basilisk V2", 0x0071: "Basilisk Ultimate",
        0x0082: "Naga Pro", 0x008F: "Naga X",
        0x0024: "Mamba", 0x0029: "DeathAdder",
        0x00A5: "DeathAdder V3", 0x00A6: "DeathAdder V3 Pro",
        0x00A7: "Viper V2 Pro", 0x00A8: "Basilisk V3",
        0x00A9: "Naga V2 Pro", 0x00AA: "HyperPolling Wireless Dongle",
        0x00AB: "Lancehead TE", 0x00AC: "Lancehead",
        0x00AD: "Orochi", 0x00AE: "Atheris",
        0x00AF: "Naga Left-Handed", 0x00B0: "Naga Trinity",
        0x00B1: "Naga Chroma", 0x00B2: "Naga Hex V2",
        0x00B3: "Imperator", 0x00B4: "Taipan",
        0x00B5: "Ouroboros", 0x00B6: "Mamba Wireless",
        0x00B7: "Mamba Tournament Edition", 0x00B8: "Diamondback Chroma",
        0x00B9: "Naga Epic Chroma", 0x00BA: "Naga Molten",
        0x00BB: "Naga 2012", 0x00BC: "Naga 2014",
        0x00BD: "DeathAdder 2013", 0x00BE: "DeathAdder 3.5G",
        0x00BF: "DeathAdder 3G", 0x00C0: "Imperator 2012",
        0x00C1: "Lachesis 5600", 0x00C2: "Lachesis",
    }
    
    LOGITECH_PRODUCTS = {
        0xC077: "G502 HERO", 0xC082: "G703 HERO",
        0xC086: "G903 HERO", 0xC08A: "G PRO X SUPERLIGHT",
        0xC08B: "G PRO WIRELESS", 0xC08C: "G PRO",
        0xC08D: "G403 HERO", 0xC08E: "G403",
        0xC08F: "G703", 0xC090: "G903",
        0xC091: "G502 PROTEUS CORE", 0xC092: "G502",
        0xC093: "G303", 0xC094: "G302",
        0xC095: "G600", 0xC096: "G700s",
        0xC097: "G500", 0xC098: "G400",
        0xC099: "G300s", 0xC09A: "G300",
        0xC09B: "G700", 0xC09C: "G500s",
        0xC09D: "G400s", 0xC09E: "G100s",
        0xC09F: "G602", 0xC0A0: "G603",
        0xC0A1: "G305", 0xC0A2: "G Prodigy",
        0xC0A3: "G203", 0xC0A4: "G102",
        0xC0A5: "G402", 0xC0A6: "G502 LIGHTSPEED",
        0xC0A7: "G703 LIGHTSPEED", 0xC0A8: "G903 LIGHTSPEED",
        0xC0A9: "G PRO X LIGHTSPEED", 0xC0AA: "G PRO LIGHTSPEED",
        0xC0AB: "G502 X", 0xC0AC: "G502 X PLUS",
        0xC0AD: "G703 X", 0xC0AE: "G903 X",
        0xC0AF: "G PRO X SUPERLIGHT 2", 0xC0B0: "G PRO X TKL",
    }
    
    STEELSERIES_PRODUCTS = {
        0x1800: "Rival 650", 0x1801: "Rival 650 Wireless",
        0x1802: "Rival 710", 0x1803: "Rival 600",
        0x1804: "Rival 500", 0x1805: "Rival 300",
        0x1806: "Rival 110", 0x1807: "Rival 106",
        0x1808: "Rival 95", 0x1809: "Rival 3",
        0x180A: "Rival 310", 0x180B: "Rival 300S",
        0x180C: "Rival 105", 0x180D: "Rival 100",
        0x180E: "Sensei 310", 0x180F: "Sensei 300",
        0x1810: "Sensei Ten", 0x1811: "Sensei RAW",
        0x1812: "Prime", 0x1813: "Prime Wireless",
        0x1814: "Prime Mini", 0x1815: "Prime Mini Wireless",
        0x1816: "Aerox 3", 0x1817: "Aerox 3 Wireless",
        0x1818: "Aerox 5", 0x1819: "Aerox 5 Wireless",
        0x181A: "Aerox 9", 0x181B: "Aerox 9 Wireless",
        0x181C: "Rival 5", 0x181D: "Rival 3 Wireless",
        0x181E: "Rival 650", 0x181F: "Rival 650",
    }
    
    def __init__(self):
        self.detected_mice: List[Dict] = []
        
    @staticmethod
    def is_mouse_interface(device: Dict) -> bool:
        """Check if device is actually a mouse"""
        try:
            # Check usage page (0x01 = Generic Desktop, 0x02 = Mouse)
            usage_page = device.get('usage_page', 0)
            usage = device.get('usage', 0)
            
            # Mouse typically has usage_page=1 and usage=2
            # or usage_page=1 and usage=6 (keyboard+mouse combo)
            if usage_page == 0x01 and usage in [0x02, 0x06]:
                return True
            
            # Check interface number - mice usually use interface 0, 1, or 2
            # Interface 3+ are often dongles, keyboards, or other features
            interface = device.get('interface_number', -1)
            if interface > 2:
                return False
            
            # Check product string for mouse-related keywords
            product_str = (device.get('product_string', '') or '').lower()
            mouse_keywords = ['mouse', 'viper', 'deathadder', 'basilisk', 'mamba', 'naga', 
                            'rival', 'g502', 'g703', 'g903', 'g pro', 'sensei', 'prime']
            
            if any(keyword in product_str for keyword in mouse_keywords):
                return True
            
            # Exclude keyboards and dongles
            exclude_keywords = ['keyboard', 'dongle', 'receiver', 'dock', 'headset']
            if any(keyword in product_str for keyword in exclude_keywords):
                return False
            
            # If no product string but valid interface, could be a mouse
            if interface in [0, 1, 2] and not product_str:
                return True
                
        except Exception:
            pass
            
        return False
    
    def scan_devices(self) -> List[Dict]:
        """Scan and filter only actual gaming mice"""
        self.detected_mice = []
        seen_devices: Set = set()  # Track unique devices to avoid duplicates
        
        try:
            import hid
        except ImportError:
            return []
        
        try:
            devices = hid.enumerate()
            for device in devices:
                vendor_id = device['vendor_id']
                product_id = device['product_id']
                
                # Only check devices from gaming brands
                if vendor_id not in self.VENDOR_IDS:
                    continue
                
                # Check if this is actually a mouse
                if not self.is_mouse_interface(device):
                    continue
                
                # Create unique identifier to avoid duplicates
                device_key = (vendor_id, product_id, device.get('interface_number', -1))
                if device_key in seen_devices:
                    continue
                seen_devices.add(device_key)
                
                vendor_name = self.VENDOR_IDS[vendor_id]
                product_name = device.get('product_string', '')
                
                # Get proper product name from all vendor databases
                if vendor_id == 0x1532 and product_id in self.RAZER_PRODUCTS:
                    product_name = self.RAZER_PRODUCTS[product_id]
                elif vendor_id == 0x046D and product_id in self.LOGITECH_PRODUCTS:
                    product_name = self.LOGITECH_PRODUCTS[product_id]
                elif vendor_id == 0x2516 and product_id in self.STEELSERIES_PRODUCTS:
                    product_name = self.STEELSERIES_PRODUCTS[product_id]
                
                # Skip if no product name and not in known products
                if not product_name:
                    if vendor_id == 0x1532 and product_id not in self.RAZER_PRODUCTS:
                        continue
                    product_name = f"Gaming Mouse (PID: 0x{product_id:04X})"
                
                mouse_info = {
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'vendor': vendor_name,
                    'product': product_name,
                    'path': device['path'],
                    'serial': device.get('serial_number', ''),
                    'interface': device.get('interface_number', -1),
                    'usage_page': device.get('usage_page', 0),
                    'usage': device.get('usage', 0),
                    'manufacturer': device.get('manufacturer_string', ''),
                    'release': device.get('release_number', 0)
                }
                self.detected_mice.append(mouse_info)
                
        except Exception as e:
            print(f"Error scanning devices: {e}")
            
        return self.detected_mice
    
    def get_supported_brands(self) -> List[str]:
        """Get list of supported brands"""
        return list(set(self.VENDOR_IDS.values()))
    
    def get_brand_products(self, brand: str) -> Dict[int, str]:
        """Get all known products for a specific brand"""
        brand_map = {
            'Razer': self.RAZER_PRODUCTS,
            'Logitech': self.LOGITECH_PRODUCTS,
            'SteelSeries': self.STEELSERIES_PRODUCTS,
        }
        return brand_map.get(brand, {})
    
    def is_supported_device(self, vendor_id: int, product_id: int) -> bool:
        """Check if a device is supported"""
        if vendor_id not in self.VENDOR_IDS:
            return False
        
        vendor_name = self.VENDOR_IDS[vendor_id]
        if vendor_name == 'Razer' and product_id in self.RAZER_PRODUCTS:
            return True
        elif vendor_name == 'Logitech' and product_id in self.LOGITECH_PRODUCTS:
            return True
        elif vendor_name == 'SteelSeries' and product_id in self.STEELSERIES_PRODUCTS:
            return True
        
        # Generic support for other brands
        return vendor_id in self.VENDOR_IDS
