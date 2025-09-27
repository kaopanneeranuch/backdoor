@echo off
echo ================================================================
echo Enhanced Python Backdoor Setup Script for Windows 7
echo Author: Enhanced Backdoor Assignment
echo Class: SIIT Ethical Hacking, 2023-2024
echo ================================================================

echo.
echo [1/5] Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found! Please install Python 3.8.10 for Windows 7
    echo Download from: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installing basic requirements...
pip install pywin32 pynput requests psutil

echo.
echo [4/5] Installing multimedia libraries...
echo Note: Some packages may fail - this is normal for Windows 7
pip install pillow pyautogui opencv-python

echo.
echo [5/5] Attempting to install audio support...
echo Note: PyAudio may require Visual C++ Build Tools
pip install pyaudio
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: PyAudio installation failed
    echo This is common on Windows 7. Audio recording will be disabled.
    echo.
    echo To fix this:
    echo 1. Install Visual C++ Build Tools
    echo 2. Or download PyAudio wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
    echo 3. Install with: pip install downloaded_wheel_file.whl
)

echo.
echo Attempting to install pyHook (Windows keylogger)...
pip install pyHook
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: pyHook installation failed
    echo This is common on Windows 7. Will use pynput fallback.
    echo.
    echo To fix this:
    echo 1. Download pyHook wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
    echo 2. Install with: pip install downloaded_wheel_file.whl
)

echo.
echo ================================================================
echo Setup completed!
echo ================================================================
echo.
echo Testing installation...
python test_system.py

echo.
echo ================================================================
echo Next Steps:
echo 1. Configure VirtualBox network settings
echo 2. Update IP address in backdoor.py (line 34)
echo 3. Test connection with Kali Linux
echo ================================================================

pause
