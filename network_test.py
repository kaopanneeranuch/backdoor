#!/usr/bin/env python3
################################################
# Network Connectivity Test                    #
# Enhanced Backdoor Assignment                 #
################################################

import socket
import sys
import time

def test_server_connection(host, port):
    """Test connection to backdoor server"""
    print(f"Testing connection to {host}:{port}...")
    
    try:
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # 5 second timeout
        
        # Try to connect
        result = s.connect_ex((host, port))
        s.close()
        
        if result == 0:
            print(f"✅ Connection to {host}:{port} successful!")
            return True
        else:
            print(f"❌ Connection to {host}:{port} failed!")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def scan_common_ips():
    """Scan common VirtualBox IP ranges"""
    print("\\nScanning common VirtualBox IP ranges...")
    
    # Common VirtualBox IP ranges
    ip_ranges = [
        "192.168.56.{}",  # Host-only
        "192.168.1.{}",   # NAT
        "10.0.2.{}",      # NAT Network
    ]
    
    found_hosts = []
    
    for ip_range in ip_ranges:
        print(f"\\nScanning {ip_range.format('1-10')}...")
        for i in range(1, 11):  # Scan first 10 IPs
            ip = ip_range.format(i)
            print(f"  Testing {ip}...", end="")
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex((ip, 5555))
                s.close()
                
                if result == 0:
                    print(f" ✅ Server found!")
                    found_hosts.append(ip)
                else:
                    print(f" ❌")
            except:
                print(f" ❌")
    
    return found_hosts

def main():
    """Main network test function"""
    print("🌐 Network Connectivity Test")
    print("Enhanced Python Backdoor Assignment")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Test specific IP provided as argument
        target_ip = sys.argv[1]
        test_server_connection(target_ip, 5555)
    else:
        print("Usage options:")
        print("1. python network_test.py <IP_ADDRESS>  - Test specific IP")
        print("2. python network_test.py scan          - Scan for servers")
        print("3. python network_test.py               - Show this help")
        
        if len(sys.argv) > 1 and sys.argv[1] == "scan":
            # Scan for servers
            found_hosts = scan_common_ips()
            
            if found_hosts:
                print(f"\\n✅ Found servers at: {', '.join(found_hosts)}")
                print("\\nUpdate your backdoor.py with one of these IPs:")
                for ip in found_hosts:
                    print(f"s.connect(('{ip}', 5555))")
            else:
                print("\\n❌ No backdoor servers found")
                print("\\nTroubleshooting:")
                print("1. Make sure server.py is running on Kali")
                print("2. Check VirtualBox network settings")
                print("3. Verify firewall settings")
        
        print("\\n" + "=" * 50)
        print("Network Configuration Tips:")
        print("\\n🔧 VirtualBox Setup:")
        print("1. Use NAT Network or Host-Only Network")
        print("2. Both VMs should be on same network")
        print("\\n📋 Check IPs:")
        print("- Windows 7: ipconfig")
        print("- Kali Linux: ip addr show")
        print("\\n🚀 Test Steps:")
        print("1. Start server.py on Kali")
        print("2. Run: python network_test.py <KALI_IP>")
        print("3. Update backdoor.py with working IP")

if __name__ == "__main__":
    main()
