"""
Server for data synchronization
"""

import socket
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import os

# Import logger directly
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataServer:
    """Server for synchronizing data between clients"""
    
    def __init__(self, host: str = "localhost", port: int = 5555, data_directory: str = "server_data"):
        self.logger = logger
        self.host = host
        self.port = port
        self.data_directory = Path(data_directory)
        
        # Create data directory
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Server state
        self.running = False
        self.server_socket = None
        self.clients: Dict[str, socket.socket] = {}
        self.client_info: Dict[str, Dict[str, Any]] = {}
        
        # Data storage
        self.data_files: Dict[str, str] = {}
        self.file_hashes: Dict[str, str] = {}
        
        # Statistics
        self.stats = {
            'clients_connected': 0,
            'files_served': 0,
            'bytes_transferred': 0,
            'sync_requests': 0,
            'start_time': time.time()
        }
    
    def start_server(self):
        """Start the server"""
        try:
            self.logger.info(f"Starting server on {self.host}:{self.port}")
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            # Start accepting connections
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
            self.logger.info(f"Server started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            raise
    
    def accept_connections(self):
        """Accept client connections"""
        while self.running:
            try:
                self.logger.info("Waiting for client connection...")
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"Client connected from {client_address}")
                
                # Get client info
                self.logger.info("Receiving client info...")
                client_info = self.receive_data(client_socket)
                self.logger.info(f"Received client info: {client_info}")
                
                if client_info and client_info.get('type') == 'client_info':
                    client_id = f"{client_address[0]}:{client_address[1]}"
                    
                    self.clients[client_id] = client_socket
                    self.client_info[client_id] = client_info
                    
                    # Send acknowledgment
                    self.logger.info("Sending acknowledgment...")
                    ack_sent = self.send_data(client_socket, {'status': 'connected'})
                    self.logger.info(f"Acknowledgment sent: {ack_sent}")
                    
                    self.stats['clients_connected'] += 1
                    self.logger.info(f"Client connected: {client_id}")
                    
                    # Start client handler
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_id),
                        daemon=True
                    )
                    client_thread.start()
                else:
                    self.logger.warning(f"Invalid client info: {client_info}")
                    client_socket.close()
                    
            except Exception as e:
                self.logger.error(f"Error accepting connection: {e}")
                break
    
    def handle_client(self, client_socket: socket.socket, client_id: str):
        """Handle client communication"""
        try:
            while self.running:
                # Receive data
                data = self.receive_data(client_socket)
                
                if not data:
                    break
                
                # Process data
                response = self.process_client_data(client_id, data)
                
                # Send response
                if response:
                    self.send_data(client_socket, response)
                
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.client_info:
                del self.client_info[client_id]
            
            client_socket.close()
            self.stats['clients_connected'] -= 1
            self.logger.info(f"Client disconnected: {client_id}")
    
    def process_client_data(self, client_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process data from client"""
        try:
            data_type = data.get('type')
            
            if data_type == 'sync_request':
                return self.handle_sync_request(client_id, data)
            elif data_type == 'file_request':
                return self.handle_file_request(client_id, data)
            elif data_type == 'file_upload':
                return self.handle_file_upload(client_id, data)
            elif data_type == 'sync_ack':
                return self.handle_sync_ack(client_id, data)
            elif data_type == 'disconnect':
                return self.handle_disconnect(client_id, data)
            else:
                self.logger.warning(f"Unknown data type: {data_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing client data: {e}")
            return {'error': str(e)}
    
    def handle_sync_request(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle synchronization request"""
        try:
            self.stats['sync_requests'] += 1
            
            # Get all files
            files = {}
            for file_path in self.data_directory.glob('*'):
                if file_path.is_file():
                    filename = file_path.name
                    
                    # Read file
                    with open(file_path, 'r') as f:
                        file_data = f.read()
                    
                    files[filename] = file_data
                    self.stats['bytes_transferred'] += len(file_data)
            
            self.logger.info(f"Synced {len(files)} files to client {client_id}")
            
            return {
                'type': 'sync_data',
                'files': files,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling sync request: {e}")
            return {'error': str(e)}
    
    def handle_file_request(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file request"""
        try:
            filename = data.get('filename')
            if not filename:
                return {'error': 'No filename provided'}
            
            file_path = self.data_directory / filename
            
            if not file_path.exists():
                return {'error': f'File not found: {filename}'}
            
            # Read file
            with open(file_path, 'r') as f:
                file_data = f.read()
            
            self.stats['files_served'] += 1
            self.stats['bytes_transferred'] += len(file_data)
            
            self.logger.info(f"Served file {filename} to client {client_id}")
            
            return {
                'type': 'file_response',
                'filename': filename,
                'data': file_data
            }
            
        except Exception as e:
            self.logger.error(f"Error handling file request: {e}")
            return {'error': str(e)}
    
    def handle_file_upload(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file upload"""
        try:
            filename = data.get('filename')
            file_data = data.get('data')
            
            if not filename or file_data is None:
                return {'error': 'Invalid file data'}
            
            # Save file
            file_path = self.data_directory / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(file_data)
            
            # Update file hash
            file_hash = hashlib.md5(file_data.encode('utf-8')).hexdigest()
            self.file_hashes[filename] = file_hash
            
            self.logger.info(f"Received file {filename} from client {client_id}")
            
            return {'status': 'received'}
            
        except Exception as e:
            self.logger.error(f"Error handling file upload: {e}")
            return {'error': str(e)}
    
    def handle_sync_ack(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle synchronization acknowledgment"""
        try:
            files_synced = data.get('files_synced', 0)
            self.logger.info(f"Client {client_id} synced {files_synced} files")
            return None
        except Exception as e:
            self.logger.error(f"Error handling sync ack: {e}")
            return None
    
    def handle_disconnect(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle client disconnect"""
        try:
            self.logger.info(f"Client {client_id} disconnecting")
            return None
        except Exception as e:
            self.logger.error(f"Error handling disconnect: {e}")
            return None
    
    def send_data(self, client_socket: socket.socket, data: Dict[str, Any]) -> bool:
        """Send data to client"""
        try:
            message = json.dumps(data).encode('utf-8')
            
            # Send length first
            client_socket.send(len(message).to_bytes(4, 'big'))
            
            # Send data
            client_socket.send(message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
            return False
    
    def receive_data(self, client_socket: socket.socket) -> Optional[Dict[str, Any]]:
        """Receive data from client"""
        try:
            # Receive length
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                return None
            
            length = int.from_bytes(length_bytes, 'big')
            
            # Receive data
            data = b''
            while len(data) < length:
                chunk = client_socket.recv(min(4096, length - len(data)))
                if not chunk:
                    break
                data += chunk
            
            if len(data) == length:
                return json.loads(data.decode('utf-8'))
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'data_directory': str(self.data_directory),
            'clients_connected': self.stats['clients_connected'],
            'files_served': self.stats['files_served'],
            'bytes_transferred': self.stats['bytes_transferred'],
            'sync_requests': self.stats['sync_requests'],
            'uptime': time.time() - self.stats['start_time'],
            'client_info': self.client_info.copy()
        }
    
    def list_files(self) -> List[str]:
        """List all files in data directory"""
        try:
            files = []
            for file_path in self.data_directory.glob('*'):
                if file_path.is_file():
                    files.append(file_path.name)
            return sorted(files)
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def broadcast_to_clients(self, data: Dict[str, Any]) -> int:
        """Broadcast message to all connected clients"""
        sent_count = 0
        
        for client_id, client_socket in list(self.clients.items()):
            try:
                if self.send_data(client_socket, data):
                    sent_count += 1
            except Exception as e:
                self.logger.error(f"Error broadcasting to client {client_id}: {e}")
        
        return sent_count
    
    def stop_server(self):
        """Stop the server"""
        try:
            self.running = False
            
            # Close all client connections
            for client_socket in self.clients.values():
                try:
                    client_socket.close()
                except:
                    pass
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
            
            self.logger.info("Server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")


def main():
    """Main server function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mouse Config Data Server")
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5555, help='Server port')
    parser.add_argument('--dir', default='server_data', help='Data directory')
    
    args = parser.parse_args()
    
    # Create server
    server = DataServer(args.host, args.port, args.dir)
    
    try:
        # Start server
        server.start_server()
        
        print(f"Server started on {args.host}:{args.port}")
        print(f"Data directory: {args.dir}")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while server.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.stop_server()


if __name__ == "__main__":
    main()
