import os
import threading
import time
import json
from datetime import datetime
import cv2
import numpy as np


class CameraRecorder:
    """Camera recording functionality for webcam surveillance"""
    
    def __init__(self, output_dir="recordings"):
        self.output_dir = output_dir
        self.is_recording = False
        self.camera_thread = None
        self.filename = None
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = None
        self.camera = None
        self.camera_index = 0  # Default camera index
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_available_cameras(self):
        """Get list of available camera devices"""
        cameras = []
        
        # Test camera indices from 0 to 5
        for i in range(6):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Try to read a frame to verify camera works
                ret, frame = cap.read()
                if ret:
                    cameras.append({
                        'index': i,
                        'name': f"Camera {i}"
                    })
                cap.release()
        
        return cameras
    
    def take_photo(self, filename=None):
        """Take a single photo from camera"""
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"camera_photo_{timestamp}.jpg"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Initialize camera
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                return False, f"Cannot access camera {self.camera_index}"
            
            # Allow camera to warm up
            time.sleep(0.5)
            
            # Capture frame
            ret, frame = cap.read()
            if ret:
                # Save image
                cv2.imwrite(filepath, frame)
                cap.release()
                return True, f"Photo saved: {filepath}"
            else:
                cap.release()
                return False, "Failed to capture frame from camera"
                
        except Exception as e:
            return False, f"Photo capture error: {str(e)}"
    
    def start_camera_recording(self, duration=None, filename=None):
        """Start camera video recording"""
        if self.is_recording:
            return False, "Already recording from camera"
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"camera_video_{timestamp}.avi"
        
        self.filename = os.path.join(self.output_dir, filename)
        self.is_recording = True
        
        def record_camera():
            try:
                # Initialize camera
                self.camera = cv2.VideoCapture(self.camera_index)
                if not self.camera.isOpened():
                    self.is_recording = False
                    return
                
                # Get camera resolution
                actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.camera.get(cv2.CAP_PROP_FPS) or 20.0  # Default to 20 if not available
                
                # Initialize video writer
                self.video_writer = cv2.VideoWriter(
                    self.filename,
                    self.fourcc,
                    fps,
                    (actual_width, actual_height)
                )
                
                start_time = time.time()
                frame_count = 0
                
                while self.is_recording:
                    # Capture frame
                    ret, frame = self.camera.read()
                    if ret:
                        # Write frame to video
                        self.video_writer.write(frame)
                        frame_count += 1
                    else:
                        print("Failed to read frame from camera")
                        break
                    
                    # Stop if duration specified and reached
                    if duration and (time.time() - start_time) >= duration:
                        break
                
                # Cleanup
                if self.video_writer:
                    self.video_writer.release()
                if self.camera:
                    self.camera.release()
                
                print(f"Camera recording completed. Frames recorded: {frame_count}")
                
            except Exception as e:
                print(f"Camera recording error: {str(e)}")
                self.is_recording = False
                if self.camera:
                    self.camera.release()
                if self.video_writer:
                    self.video_writer.release()
        
        self.camera_thread = threading.Thread(target=record_camera, daemon=True)
        self.camera_thread.start()
        
        return True, f"Camera recording started: {self.filename}"
    
    def stop_camera_recording(self):
        """Stop camera recording"""
        if not self.is_recording:
            return False, "Not currently recording from camera"
        
        self.is_recording = False
        
        # Wait for thread to complete
        if self.camera_thread:
            self.camera_thread.join(timeout=5)
        
        return True, f"Camera recording stopped: {self.filename}"
    
    def get_camera_status(self):
        """Get current camera status and information"""
        status = {
            'is_recording': self.is_recording,
            'camera_index': self.camera_index,
            'output_dir': self.output_dir,
            'current_file': self.filename if self.is_recording else None,
            'available_cameras': self.get_available_cameras()
        }
        
        return status
    
    def test_camera_connection(self, camera_index=None):
        """Test if camera is accessible"""
        if camera_index is None:
            camera_index = self.camera_index
        
        try:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    return True, f"Camera {camera_index} is working properly"
                else:
                    return False, f"Camera {camera_index} opened but cannot capture frames"
            else:
                return False, f"Cannot open camera {camera_index}"
        except Exception as e:
            return False, f"Camera test error: {str(e)}"


class CameraSurveillance:
    """Main camera surveillance controller"""
    
    def __init__(self, output_dir="recordings"):
        self.camera_recorder = CameraRecorder(output_dir)
        self.output_dir = output_dir
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_surveillance(self, duration=None, camera_index=0):
        """Start camera surveillance with specified parameters"""
        # Set camera index
        self.camera_recorder.camera_index = camera_index
        
        # Test camera connection first
        success, msg = self.camera_recorder.test_camera_connection()
        if not success:
            return False, f"Camera test failed: {msg}"
        
        # Start recording
        return self.camera_recorder.start_camera_recording(duration)
    
    def stop_surveillance(self):
        """Stop all camera surveillance"""
        return self.camera_recorder.stop_camera_recording()
    
    def take_snapshot(self):
        """Take a quick snapshot from camera"""
        return self.camera_recorder.take_photo()
    
    def get_system_status(self):
        """Get comprehensive system status"""
        camera_status = self.camera_recorder.get_camera_status()
        
        system_status = {
            'timestamp': datetime.now().isoformat(),
            'camera_recording': camera_status['is_recording'],
            'output_directory': self.output_dir,
            'available_cameras': camera_status['available_cameras'],
            'current_camera': camera_status['camera_index']
        }
        
        return system_status
    
    def list_recordings(self):
        """List all camera recordings in output directory"""
        recordings = []
        
        try:
            if os.path.exists(self.output_dir):
                for filename in os.listdir(self.output_dir):
                    if filename.startswith('camera_') and (filename.endswith('.avi') or filename.endswith('.jpg')):
                        filepath = os.path.join(self.output_dir, filename)
                        file_size = os.path.getsize(filepath)
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        recordings.append({
                            'filename': filename,
                            'filepath': filepath,
                            'size': file_size,
                            'created': file_time.isoformat(),
                            'type': 'video' if filename.endswith('.avi') else 'photo'
                        })
                
                # Sort by creation time (newest first)
                recordings.sort(key=lambda x: x['created'], reverse=True)
        
        except Exception as e:
            print(f"Error listing camera recordings: {str(e)}")
        
        return recordings
    
    def cleanup_old_recordings(self, days_old=7):
        """Delete camera recordings older than specified days"""
        deleted_count = 0
        
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)  # Convert days to seconds
            
            if os.path.exists(self.output_dir):
                for filename in os.listdir(self.output_dir):
                    if filename.startswith('camera_') and (filename.endswith('.avi') or filename.endswith('.jpg')):
                        filepath = os.path.join(self.output_dir, filename)
                        file_time = os.path.getmtime(filepath)
                        
                        if file_time < cutoff_time:
                            os.remove(filepath)
                            deleted_count += 1
                            print(f"Deleted old recording: {filename}")
        
        except Exception as e:
            print(f"Error during camera recordings cleanup: {str(e)}")
        
        return deleted_count


# Factory function to create camera surveillance instance
def create_camera_surveillance(output_dir="recordings"):
    """Create camera surveillance instance"""
    return CameraSurveillance(output_dir)


# Test the camera surveillance
if __name__ == "__main__":
    print("Testing Camera Surveillance...")
    
    camera_sys = create_camera_surveillance("test_camera_recordings")
    
    # Show system status
    status = camera_sys.get_system_status()
    print(f"\nSystem Status:")
    for key, value in status.items():
        if key != 'available_cameras':
            print(f"  {key}: {value}")
    
    # Show available cameras
    print(f"\nAvailable Cameras:")
    for camera in status['available_cameras']:
        print(f"  - Camera {camera['index']}: {camera['name']}")
    
    # Test camera connection
    print("\nTesting camera connection...")
    success, msg = camera_sys.camera_recorder.test_camera_connection()
    print(f"Camera test: {msg}")
    
    if success:
        # Test snapshot
        print("\nTesting camera snapshot...")
        success, msg = camera_sys.take_snapshot()
        print(f"Snapshot: {msg}")
        
        # Test short recording
        print("\nTesting 5-second camera recording...")
        success, msg = camera_sys.start_surveillance(duration=5)
        print(f"Start recording: {msg}")
        
        if success:
            # Wait for completion
            time.sleep(7)
            
            # Stop recording
            success, msg = camera_sys.stop_surveillance()
            print(f"Stop recording: {msg}")
        
        # List recordings
        recordings = camera_sys.list_recordings()
        print(f"\nCamera recordings created:")
        for recording in recordings:
            print(f"  - {recording['filename']} ({recording['size']} bytes, {recording['type']})")
    
    print("\nCamera surveillance test completed!")
