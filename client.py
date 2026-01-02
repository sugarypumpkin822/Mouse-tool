"""
Client application for data synchronization
"""

import socket
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import os
import shutil

# Import logger directly
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataClient:
    """Client for synchronizing data with server"""
    
    def __init__(self, server_host: str = "localhost", server_port: int = 5555, save_directory: str = "synced_data"):
        self.logger = logger
        self.server_host = server_host
        self.server_port = server_port
        self.save_directory = Path(save_directory)
        
        # Create save directory
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # Client state
        self.connected = False
        self.socket = None
        self.running = False
        self.sync_thread = None
        
        # Data cache
        self.data_cache: Dict[str, Any] = {}
        self.file_hashes: Dict[str, str] = {}
        
        # Sync statistics
        self.stats = {
            'files_synced': 0,
            'bytes_transferred': 0,
            'sync_count': 0,
            'last_sync': None,
            'errors': 0
        }
    
    def connect_to_server(self) -> bool:
        """Connect to the server"""
        try:
            self.logger.info(f"Connecting to server {self.server_host}:{self.server_port}")
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            
            # Connect to server
            self.logger.info("Establishing connection...")
            self.socket.connect((self.server_host, self.server_port))
            self.logger.info("Socket connected")
            
            # Send client info
            client_info = {
                'type': 'client_info',
                'hostname': socket.gethostname(),
                'save_directory': str(self.save_directory),
                'timestamp': time.time()
            }
            
            self.logger.info(f"Sending client info: {client_info}")
            sent = self.send_data(client_info)
            self.logger.info(f"Client info sent: {sent}")
            
            # Wait for acknowledgment
            self.logger.info("Waiting for acknowledgment...")
            response = self.receive_data()
            self.logger.info(f"Received response: {response}")
            
            if response and response.get('status') == 'connected':
                self.connected = True
                self.logger.info("Successfully connected to server")
                return True
            else:
                self.logger.error(f"Server rejected connection: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            if self.socket:
                self.send_data({'type': 'disconnect'})
                self.socket.close()
            
            self.connected = False
            self.running = False
            
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)
            
            self.logger.info("Disconnected from server")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """Send data to server"""
        try:
            if not self.socket:
                self.logger.warning("Cannot send data - no socket")
                return False
            
            message = json.dumps(data).encode('utf-8')
            self.logger.info(f"Sending {len(message)} bytes")
            
            # Send length first
            length_sent = self.socket.send(len(message).to_bytes(4, 'big'))
            self.logger.info(f"Length sent: {length_sent} bytes")
            
            # Send data
            data_sent = self.socket.send(message)
            self.logger.info(f"Data sent: {data_sent} bytes")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
            self.connected = False
            return False
    
    def receive_data(self) -> Optional[Dict[str, Any]]:
        """Receive data from server"""
        try:
            if not self.socket:
                self.logger.warning("Cannot receive data - no socket")
                return None
            
            # Receive length
            length_bytes = self.socket.recv(4)
            if not length_bytes:
                self.logger.warning("No length bytes received")
                return None
            
            length = int.from_bytes(length_bytes, 'big')
            self.logger.info(f"Expecting {length} bytes")
            
            # Receive data
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(min(4096, length - len(data)))
                if not chunk:
                    self.logger.warning("Connection closed while receiving data")
                    break
                data += chunk
            
            if len(data) == length:
                try:
                    result = json.loads(data.decode('utf-8'))
                    self.logger.info(f"Successfully received data: {result}")
                    return result
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                    return None
            else:
                self.logger.error(f"Received {len(data)} bytes, expected {length}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            self.connected = False
            return None
    
    def start_sync_loop(self):
        """Start the synchronization loop"""
        try:
            if self.running:
                return
            
            self.running = True
            self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
            self.sync_thread.start()
            
            self.logger.info("Sync loop started")
            
        except Exception as e:
            self.logger.error(f"Error starting sync loop: {e}")
    
    def sync_loop(self):
        """Main synchronization loop"""
        while self.running and self.connected:
            try:
                # Request sync
                self.send_data({'type': 'sync_request'})
                
                # Receive sync data
                sync_data = self.receive_data()
                
                if sync_data:
                    self.process_sync_data(sync_data)
                
                # Wait for next sync
                time.sleep(30)  # Sync every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                self.connected = False
                break
    
    def process_sync_data(self, sync_data: Dict[str, Any]):
        """Process synchronization data from server"""
        try:
            if sync_data.get('type') == 'sync_data':
                files = sync_data.get('files', {})
                
                for filename, file_data in files.items():
                    # Check if file needs updating
                    file_path = self.save_directory / filename
                    
                    # Calculate file hash
                    file_hash = hashlib.md5(file_data.encode('utf-8')).hexdigest()
                    
                    # Check if file exists and is different
                    if not file_path.exists() or self.file_hashes.get(filename) != file_hash:
                        # Save file
                        with open(file_path, 'w') as f:
                            f.write(file_data)
                        
                        self.file_hashes[filename] = file_hash
                        self.stats['files_synced'] += 1
                        self.stats['bytes_transferred'] += len(file_data)
                        
                        self.logger.info(f"Synced file: {filename}")
                
                self.stats['sync_count'] += 1
                self.stats['last_sync'] = time.time()
                
                # Send acknowledgment
                self.send_data({'type': 'sync_ack', 'files_synced': len(files)})
                
        except Exception as e:
            self.logger.error(f"Error processing sync data: {e}")
            self.stats['errors'] += 1
    
    def request_file(self, filename: str) -> bool:
        """Request a specific file from server"""
        try:
            if not self.connected:
                return False
            
            self.send_data({'type': 'file_request', 'filename': filename})
            
            response = self.receive_data()
            
            if response and response.get('type') == 'file_response':
                file_data = response.get('data')
                if file_data:
                    file_path = self.save_directory / filename
                    
                    with open(file_path, 'w') as f:
                        f.write(file_data)
                    
                    self.logger.info(f"Requested file saved: {filename}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error requesting file: {e}")
            return False
    
    def send_file(self, filename: str, file_path: Optional[str] = None) -> bool:
        """Send a file to the server"""
        try:
            if not self.connected:
                return False
            
            # Use provided path or default save directory
            if file_path:
                source_path = Path(file_path)
            else:
                source_path = self.save_directory / filename
            
            if not source_path.exists():
                self.logger.error(f"File not found: {source_path}")
                return False
            
            # Read file
            with open(source_path, 'r') as f:
                file_data = f.read()
            
            # Send file to server
            self.send_data({
                'type': 'file_upload',
                'filename': filename,
                'data': file_data
            })
            
            # Wait for acknowledgment
            response = self.receive_data()
            
            if response and response.get('status') == 'received':
                self.logger.info(f"File sent successfully: {filename}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending file: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        return {
            'connected': self.connected,
            'server': f"{self.server_host}:{self.server_port}",
            'save_directory': str(self.save_directory),
            'stats': self.stats.copy(),
            'cached_files': len(self.data_cache),
            'file_hashes': len(self.file_hashes)
        }
    
    def list_files(self) -> List[str]:
        """List all files in the save directory"""
        try:
            files = []
            for file_path in self.save_directory.glob('*'):
                if file_path.is_file():
                    files.append(file_path.name)
            return sorted(files)
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def export_data(self, export_path: str) -> bool:
        """Export all synchronized data"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files
            for file_path in self.save_directory.glob('*'):
                if file_path.is_file():
                    dest_path = export_dir / file_path.name
                    shutil.copy2(file_path, dest_path)
            
            # Export statistics
            stats_file = export_dir / 'sync_stats.json'
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
            
            self.logger.info(f"Data exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return False
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up old files"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            for file_path in self.save_directory.glob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    self.logger.info(f"Deleted old file: {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {e}")


def main():
    """Main client function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mouse Config Data Client")
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    parser.add_argument('--dir', default='synced_data', help='Save directory')
    parser.add_argument('--export', help='Export data to directory')
    
    args = parser.parse_args()
    
    # Create client
    client = DataClient(args.host, args.port, args.dir)
    
    # Connect to server
    if not client.connect_to_server():
        print("Failed to connect to server")
        return
    
    try:
        # Start sync loop
        client.start_sync_loop()
        
        print(f"Connected to server {args.host}:{args.port}")
        print(f"Saving to directory: {args.dir}")
        print("Synchronization started...")
        print("Press Ctrl+C to stop")
        
        # Handle export if requested
        if args.export:
            print(f"Will export data to: {args.export}")
            time.sleep(5)  # Wait for initial sync
            client.export_data(args.export)
        
        # Keep running
        while client.connected:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping client...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
