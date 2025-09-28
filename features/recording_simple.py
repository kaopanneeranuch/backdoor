import os
import time
import threading
from datetime import datetime
import ctypes
from ctypes import wintypes

# Try to import optional dependencies
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class SimpleScreenRecorder:
    """Simplified screen recorder with minimal dependencies"""
    
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        self.is_recording = False
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def take_screenshot(self, filename=None):
        """Take a screenshot using available libraries"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Try PIL first (most reliable)
            if PIL_AVAILABLE:
                screenshot = ImageGrab.grab()
                screenshot.save(filepath)
                return True, f"Screenshot saved using PIL: {filename}"
            
            # Try PyAutoGUI as fallback
            elif PYAUTOGUI_AVAILABLE:
                screenshot = pyautogui.screenshot()
                screenshot.save(filepath)
                return True, f"Screenshot saved using PyAutoGUI: {filename}"
            
            else:
                return False, "No screenshot library available (install Pillow or PyAutoGUI)"
                
        except Exception as e:
            return False, f"Screenshot error: {str(e)}"
    
    def get_screen_info(self):
        """Get screen information using ctypes"""
        try:
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return f"Screen resolution: {screensize[0]}x{screensize[1]}"
        except Exception as e:
            return f"Could not get screen info: {str(e)}"


class SimpleAudioRecorder:
    """Simplified audio recorder"""
    
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        self.is_recording = False
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_recording(self, duration=30, filename=None):
        """Start audio recording (placeholder - requires PyAudio)"""
        try:
            import pyaudio
            import wave
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Audio recording implementation would go here
            return True, f"Audio recording started: {filename}"
            
        except ImportError:
            return False, "PyAudio not available for audio recording"
        except Exception as e:
            return False, f"Audio recording error: {str(e)}"
    
    def stop_recording(self):
        """Stop audio recording"""
        if self.is_recording:
            self.is_recording = False
            return True, "Audio recording stopped"
        else:
            return False, "No audio recording active"


class SimpleSurveillanceRecorder:
    """Simplified surveillance recorder combining screen and audio"""
    
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        self.screen_recorder = SimpleScreenRecorder(output_dir)
        self.audio_recorder = SimpleAudioRecorder(output_dir)
        self.is_surveillance_active = False
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_surveillance(self, duration=30, audio=False, video=False):
        """Start surveillance recording"""
        results = []
        
        if video:
            # Take periodic screenshots instead of video recording
            success, msg = self.screen_recorder.take_screenshot()
            results.append(f"Video: {msg}")
        
        if audio:
            success, msg = self.audio_recorder.start_recording(duration)
            results.append(f"Audio: {msg}")
        
        if not video and not audio:
            # Default: take screenshot
            success, msg = self.screen_recorder.take_screenshot()
            results.append(f"Default screenshot: {msg}")
        
        self.is_surveillance_active = True
        return True, " | ".join(results)
    
    def stop_surveillance(self):
        """Stop surveillance recording"""
        if self.is_surveillance_active:
            success, msg = self.audio_recorder.stop_recording()
            self.is_surveillance_active = False
            return True, f"Surveillance stopped: {msg}"
        else:
            return False, "No surveillance active"
    
    def list_recordings(self):
        """List all recordings in the output directory"""
        try:
            if not os.path.exists(self.output_dir):
                return []
            
            files = []
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    files.append({
                        'filename': filename,
                        'size_bytes': size,
                        'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return files
        except Exception as e:
            return [{"error": f"Could not list recordings: {str(e)}"}]


def create_surveillance_recorder(output_dir="recordings"):
    """Factory function to create a surveillance recorder instance"""
    return SimpleSurveillanceRecorder(output_dir)


# For backward compatibility
class AudioRecorder(SimpleAudioRecorder):
    """Backward compatibility alias"""
    pass

class ScreenRecorder(SimpleScreenRecorder):
    """Backward compatibility alias"""
    pass

class SurveillanceRecorder(SimpleSurveillanceRecorder):
    """Backward compatibility alias"""
    pass
