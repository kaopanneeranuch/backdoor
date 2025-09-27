#!/bin/bash
echo "================================================================"
echo "Enhanced Python Backdoor Server Setup Script for Kali Linux"
echo "Author: Enhanced Backdoor Assignment"
echo "Class: SIIT Ethical Hacking, 2023-2024"
echo "================================================================"

echo ""
echo "[1/4] Checking Python installation..."
python3 --version

echo ""
echo "[2/4] Updating package manager..."
sudo apt update

echo ""
echo "[3/4] Installing basic requirements..."
sudo apt install -y python3-pip

echo ""
echo "[4/4] Installing Python packages..."
pip3 install --user pywin32 requests psutil colorama

echo ""
echo "================================================================"
echo "Kali Linux server setup completed!"
echo "================================================================"

echo ""
echo "Finding network configuration..."
echo "Your IP addresses:"
ip addr show | grep "inet " | grep -v "127.0.0.1"

echo ""
echo "================================================================"
echo "Next Steps:"
echo "1. Note your Kali Linux IP address above"
echo "2. Update backdoor.py on Windows 7 with your Kali IP"
echo "3. Start server: python3 server.py"
echo "4. Start backdoor on Windows 7: python backdoor.py"
echo "================================================================"

echo ""
echo "Testing network connectivity..."
echo "Server will listen on all interfaces (0.0.0.0:5555)"
echo "Make sure Windows 7 VM can reach this IP!"

echo ""
echo "Ready to start server? (y/n)"
read -p "Start server now? " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Starting backdoor server..."
    python3 server.py
fi
