"""
Firmware web scraper for manufacturer websites
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import re

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    import logging
    get_logger = lambda name: logging.getLogger(name)


class FirmwareScraper:
    """Scrape manufacturer websites for firmware updates"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Manufacturer URLs and patterns
        self.manufacturers = {
            'razer': {
                'base_url': 'https://www.razer.com',
                'support_url': 'https://support.razer.com',
                'patterns': {
                    'deathadder': r'deathadderv?2?|death.*adder',
                    'viper': r'viper.*ultimate|viper.*v2?',
                    'basilisk': r'basilisk.*v2?|basilisk.*ultimate',
                    'naga': r'naga.*pro|naga.*v2?',
                    'mamba': r'mamba.*elite|mamba.*v2?'
                }
            },
            'logitech': {
                'base_url': 'https://www.logitechg.com',
                'support_url': 'https://support.logi.com',
                'patterns': {
                    'g502': r'g502.*hero|g502.*lightspeed',
                    'g703': r'g703.*hero|g703.*lightspeed',
                    'g903': r'g903.*hero|g903.*lightspeed',
                    'gpro': r'g.*pro.*superlight|g.*pro.*wireless',
                    'g403': r'g403.*hero|g403'
                }
            },
            'steelseries': {
                'base_url': 'https://steelseries.com',
                'support_url': 'https://support.steelseries.com',
                'patterns': {
                    'rival': r'rival.*650|rival.*3|rival.*5',
                    'prime': r'prime.*wireless|prime.*mini',
                    'aerox': r'aerox.*3|aerox.*5|aerox.*9'
                }
            }
        }
    
    def search_firmware(self, manufacturer: str, product_name: str, product_id: int = 0) -> Optional[Dict]:
        """Search for firmware updates for a specific product"""
        try:
            manufacturer = manufacturer.lower()
            if manufacturer not in self.manufacturers:
                self.logger.warning(f"Unsupported manufacturer: {manufacturer}")
                return None
            
            config = self.manufacturers[manufacturer]
            
            # Try different search methods
            firmware_info = None
            
            # Method 1: Direct pattern matching
            firmware_info = self._search_by_pattern(config, product_name)
            
            # Method 2: Support site search
            if not firmware_info:
                firmware_info = self._search_support_site(config, product_name)
            
            # Method 3: Generic search
            if not firmware_info:
                firmware_info = self._search_generic(manufacturer, product_name)
            
            if firmware_info:
                self.logger.info(f"Found firmware for {manufacturer} {product_name}")
                return firmware_info
            else:
                self.logger.warning(f"No firmware found for {manufacturer} {product_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching firmware: {e}")
            return None
    
    def _search_by_pattern(self, config: Dict, product_name: str) -> Optional[Dict]:
        """Search using known URL patterns"""
        try:
            product_lower = product_name.lower()
            
            for pattern_name, pattern in config['patterns'].items():
                if re.search(pattern, product_lower, re.IGNORECASE):
                    # Construct potential firmware URL
                    firmware_url = self._construct_firmware_url(config, pattern_name)
                    if firmware_url and self._verify_firmware_url(firmware_url):
                        return {
                            'url': firmware_url,
                            'version': 'Latest',
                            'filename': f"{product_name.replace(' ', '_')}_firmware.exe",
                            'source': 'pattern_match'
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in pattern search: {e}")
            return None
    
    def _search_support_site(self, config: Dict, product_name: str) -> Optional[Dict]:
        """Search manufacturer support site"""
        try:
            search_url = f"{config['support_url']}/search"
            search_query = f"{product_name} firmware"
            
            params = {
                'q': search_query,
                'type': 'downloads'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for download links
            download_links = soup.find_all('a', href=re.compile(r'download|firmware|update'))
            
            for link in download_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(config['support_url'], href)
                    if self._verify_firmware_url(full_url):
                        return {
                            'url': full_url,
                            'version': 'Latest',
                            'filename': link.get_text().strip(),
                            'source': 'support_site'
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching support site: {e}")
            return None
    
    def _search_generic(self, manufacturer: str, product_name: str) -> Optional[Dict]:
        """Generic firmware search"""
        try:
            # This would implement a more generic search approach
            # For now, return a placeholder
            return {
                'url': f"https://www.{manufacturer}.support.com/downloads",
                'version': 'Check manufacturer site',
                'filename': f"{product_name}_firmware.exe",
                'source': 'generic',
                'note': 'Manual download required'
            }
            
        except Exception as e:
            self.logger.error(f"Error in generic search: {e}")
            return None
    
    def _construct_firmware_url(self, config: Dict, pattern_name: str) -> Optional[str]:
        """Construct firmware URL based on pattern"""
        try:
            manufacturer = next(k for k, v in self.manufacturers.items() if v == config)
            
            # Known firmware URL patterns
            if manufacturer == 'razer':
                return f"https://dl.razerzone.com/drivers/{pattern_name}/{pattern_name}_FW_updater.exe"
            elif manufacturer == 'logitech':
                return f"https://download01.logi.com/web/ftp/pub/techsupport/{pattern_name}/"
            elif manufacturer == 'steelseries':
                return f"https://steelseries.com/downloads/{pattern_name}"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error constructing firmware URL: {e}")
            return None
    
    def _verify_firmware_url(self, url: str) -> bool:
        """Verify if a URL points to a valid firmware file"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            
            # Check if response is successful
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Check for common firmware file types
                firmware_types = [
                    'application/octet-stream',
                    'application/x-msdownload',
                    'application/x-executable',
                    'application/zip'
                ]
                
                return any(ft in content_type for ft in firmware_types)
            
            return False
            
        except Exception:
            return False
    
    def get_firmware_list(self, manufacturer: str) -> List[Dict]:
        """Get list of available firmware for a manufacturer"""
        try:
            manufacturer = manufacturer.lower()
            if manufacturer not in self.manufacturers:
                return []
            
            config = self.manufacturers[manufacturer]
            firmware_list = []
            
            # Scan support site for firmware downloads
            try:
                response = self.session.get(config['support_url'], timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for product categories
                product_links = soup.find_all('a', href=re.compile(r'product|mouse'))
                
                for link in product_links[:20]:  # Limit to first 20 results
                    product_name = link.get_text().strip()
                    href = link.get('href')
                    
                    if href and 'mouse' in product_name.lower():
                        full_url = urljoin(config['support_url'], href)
                        
                        firmware_info = {
                            'product': product_name,
                            'url': full_url,
                            'available': True
                        }
                        
                        firmware_list.append(firmware_info)
                
            except Exception as e:
                self.logger.error(f"Error getting firmware list: {e}")
            
            return firmware_list
            
        except Exception as e:
            self.logger.error(f"Error getting firmware list: {e}")
            return []
    
    def check_firmware_updates(self, manufacturer: str, product_name: str, current_version: str = "") -> Optional[Dict]:
        """Check if firmware updates are available"""
        try:
            firmware_info = self.search_firmware(manufacturer, product_name)
            
            if firmware_info:
                return {
                    'update_available': True,
                    'current_version': current_version or 'Unknown',
                    'latest_version': firmware_info.get('version', 'Latest'),
                    'download_url': firmware_info['url'],
                    'filename': firmware_info['filename'],
                    'size': self._get_file_size(firmware_info['url'])
                }
            else:
                return {
                    'update_available': False,
                    'message': 'No firmware updates found'
                }
                
        except Exception as e:
            self.logger.error(f"Error checking firmware updates: {e}")
            return None
    
    def _get_file_size(self, url: str) -> Optional[int]:
        """Get file size from URL"""
        try:
            response = self.session.head(url, timeout=5)
            if response.status_code == 200:
                return int(response.headers.get('content-length', 0))
        except Exception:
            pass
        return None
